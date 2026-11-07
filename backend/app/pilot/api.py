"""Run one worker behind HTTPS for a restricted, single-host pilot."""
import asyncio
from contextlib import asynccontextmanager
import hmac
import json
import logging
import os
from time import perf_counter
from urllib.parse import urlsplit
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import APITimeoutError, AsyncOpenAI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.database import connect_database
from app.pilot.generation import Generator
from app.pilot.models import FeedbackInput, LoginInput, QuestionInput
from app.pilot.service import AnswerService
from app.pilot.settings import Settings
from app.pilot.store import QuotaExceeded, Store, digest

logger = logging.getLogger("odoo.pilot")
COOKIE = "odoo_pilot_session"


class BodyLimit:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        body = bytearray()
        while True:
            event = await receive()
            if event["type"] == "http.disconnect":
                return
            body.extend(event.get("body", b""))
            if len(body) > 16384:
                return await JSONResponse({"detail": "Request body too large"}, status_code=413)(scope, receive, send)
            if not event.get("more_body", False):
                break
        delivered = False

        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, bounded_receive, send)


async def check_readiness(settings):
    async with connect_database() as db:
        row = await db.fetchrow("""SELECT s.snapshot_id, s.expected_chunks,
            (SELECT count(*) FROM index_chunks c WHERE c.snapshot_id=s.snapshot_id) AS actual
            FROM active_indexes a JOIN index_snapshots s USING(snapshot_id)
            WHERE a.corpus_name='odoo19' AND s.published""")
    if not row or row["snapshot_id"] != settings.snapshot_id or row["actual"] != row["expected_chunks"]:
        raise ValueError("Reviewed pilot index unavailable")
    return {"snapshot_id": row["snapshot_id"], "chunks": row["actual"]}


def create_app(settings=None, service=None, readiness=None):
    settings = settings or Settings.from_env()
    store = Store(settings.store_path)
    slots = asyncio.Semaphore(settings.max_concurrent)
    injected_service = service is not None

    @asynccontextmanager
    async def lifespan(app):
        client = AsyncOpenAI(timeout=45, max_retries=0) if os.environ.get("OPENAI_API_KEY") else None
        app.state.client = client
        app.state.service = service or AnswerService(settings, Generator(settings.model, client, settings.reasoning_effort))
        try:
            yield
        finally:
            if client:
                await client.close()

    app = FastAPI(title="Odoo 19 pilot", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(BodyLimit)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[urlsplit(settings.public_origin).hostname])
    app.state.store = store

    @app.middleware("http")
    async def boundaries(request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            if request.headers.get("origin") != settings.public_origin:
                return JSONResponse({"detail": "Request origin not allowed"}, status_code=403)
        response = await call_next(request)
        response.headers.update({
            "Cache-Control": "no-store", "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY", "Referrer-Policy": "no-referrer",
            "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
        })
        return response

    async def session(request: Request):
        found = store.session(request.cookies.get(COOKIE), settings)
        if not found:
            raise HTTPException(401, "Sign in with your pilot access key")
        return found

    def quota(rules):
        try:
            store.charge(rules)
        except QuotaExceeded:
            raise HTTPException(429, "Pilot request limit reached; try again later", headers={"Retry-After": "60"}) from None

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    @app.post("/api/login")
    async def login(body: LoginInput, request: Request, response: Response):
        ip = request.client.host if request.client else "unknown"
        quota([(f"login:{ip}", 60, 10), ("login:global", 60, 60)])
        token = store.login(body.access_key, settings)
        if token is None:
            raise HTTPException(401, "Invalid pilot access key")
        response.set_cookie(COOKIE, token, max_age=settings.session_hours * 3600,
                            httponly=True, secure=settings.secure_cookie, samesite="strict", path="/api")
        return {"status": "signed_in"}

    @app.post("/api/logout")
    async def logout(request: Request, response: Response, current=Depends(session)):
        store.logout(request.cookies[COOKIE])
        response.delete_cookie(COOKIE, path="/api", secure=settings.secure_cookie, httponly=True, samesite="strict")
        return {"status": "signed_out"}

    @app.get("/api/session")
    async def current_session(current=Depends(session)):
        return {"name": current["principal"], "supported_version": "19.0", "topics": ["Sales", "Inventory"],
                "history": store.history(current["id"])}

    @app.get("/api/ready")
    async def ready(current=Depends(session)):
        try:
            async with asyncio.timeout(12):
                result = await (readiness or check_readiness)(settings)
            if not injected_service and app.state.client is None:
                raise ValueError("Provider not configured")
            return {"status": "ready", **result}
        except Exception:
            raise HTTPException(503, "Pilot dependencies unavailable; ask the operator") from None

    @app.post("/api/answers")
    async def answer(body: QuestionInput, response: Response, current=Depends(session)):
        quota([(f"answers:minute:{current['principal']}", 60, settings.answers_per_minute),
               (f"answers:day:{current['principal']}", 86400, settings.answers_per_day),
               ("answers:day:global", 86400, settings.total_answers_per_day)])
        if slots.locked():
            raise HTTPException(429, "The pilot is busy; try again shortly", headers={"Retry-After": "10"})
        request_id = str(uuid4())
        response.headers["X-Request-ID"] = request_id
        history = store.history(current["id"])
        store.start(request_id, current["id"], current["principal"], body.question, body.odoo_version)
        started = perf_counter()
        telemetry = {"generation_model": settings.model}
        try:
            async with slots, asyncio.timeout(settings.request_timeout):
                if not injected_service and app.state.client is None:
                    raise RuntimeError("Provider not configured")
                result = await app.state.service.answer(body.question, body.odoo_version, history,
                                                        request_id, client=app.state.client, telemetry=telemetry)
            store.finish(request_id, response=result, audit=telemetry.get("_audit"))
            logger.info("pilot_request id=%s state=%s latency_ms=%s", request_id, result["status"], result["trace"]["latency_ms"])
            return result
        except asyncio.CancelledError:
            store.finish(request_id, error="cancelled")
            raise
        except Exception as error:
            code = "timeout" if isinstance(error, (TimeoutError, APITimeoutError)) else "dependency_failure"
            store.finish(request_id, response={"trace": {**{k: v for k, v in telemetry.items() if not k.startswith("_")},
                "latency_ms": round((perf_counter()-started)*1000), "usage_complete": False}},
                error=code, audit=telemetry.get("_audit"))
            logger.warning("pilot_failure id=%s kind=%s exception=%s", request_id, code, type(error).__name__)
            raise HTTPException(504 if code == "timeout" else 503,
                {"message": "The pilot could not complete this request. Please retry or contact the operator.",
                 "request_id": request_id}, headers={"X-Request-ID": request_id}) from None

    @app.post("/api/requests/{request_id}/feedback")
    async def feedback(request_id: str, body: FeedbackInput, current=Depends(session)):
        quota([(f"feedback:{current['principal']}", 60, 30)])
        if not store.feedback(request_id, current["id"], body):
            raise HTTPException(404, "Request not found in this session")
        return {"status": "saved"}

    @app.get("/api/admin/export")
    async def export(request: Request):
        supplied = request.headers.get("authorization", "").removeprefix("Bearer ")
        if not hmac.compare_digest(digest(supplied), digest(settings.admin_key)):
            raise HTTPException(401, "Operator authentication required")
        return StreamingResponse((json.dumps(item, ensure_ascii=False) + "\n" for item in store.export()),
            media_type="application/x-ndjson", headers={"Content-Disposition": 'attachment; filename="pilot-review.jsonl"'})

    if settings.frontend.is_dir():
        app.mount("/assets", StaticFiles(directory=settings.frontend / "assets"), name="assets")

        @app.get("/")
        async def index():
            return FileResponse(settings.frontend / "index.html")

    return app
