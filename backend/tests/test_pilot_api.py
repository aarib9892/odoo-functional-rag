import asyncio
from dataclasses import replace
import json
from pathlib import Path
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import unittest

from fastapi.testclient import TestClient

from app.pilot.api import COOKIE, create_app
from app.pilot.service import AnswerService
from tests.pilot_fixtures import ADMIN_KEY, KEY, OTHER_KEY, FakeGenerator, fake_retrieve, settings

ORIGIN = {"Origin": "http://testserver"}


async def ready(_):
    return {"snapshot_id": "fixture", "chunks": 1}


class PilotApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.settings = settings(self.temporary.name)
        self.service = AnswerService(self.settings, FakeGenerator(), fake_retrieve)
        self.app = create_app(self.settings, self.service, ready)
        self.client = TestClient(self.app, headers=ORIGIN)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.temporary.cleanup()

    def login(self, key=KEY):
        return self.client.post("/api/login", json={"access_key": key})

    def ask(self, **kwargs):
        return self.client.post("/api/answers", json={"question": "How do I invoice delivered quantities?", "odoo_version": "19.0", **kwargs})

    def test_health_is_public_and_data_and_cost_paths_require_access(self):
        self.assertEqual(self.client.get("/health").status_code, 200)
        for path in ["/api/session", "/api/ready", "/api/admin/export"]:
            self.assertEqual(self.client.get(path).status_code, 401)
        self.assertEqual(self.ask().status_code, 401)
        self.assertEqual(self.client.post("/api/requests/unknown/feedback", json={"outcome": "solved"}).status_code, 401)

    def test_login_cookie_logout_and_security_headers(self):
        self.assertEqual(self.login("incorrect").status_code, 401)
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("HttpOnly", response.headers["set-cookie"])
        self.assertIn("SameSite=strict", response.headers["set-cookie"])
        self.assertNotIn(KEY, response.text)
        self.assertEqual(self.client.get("/api/session").json()["name"], "operations")
        self.assertEqual(self.client.get("/api/ready").status_code, 200)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])
        self.client.post("/api/logout", json={})
        self.assertEqual(self.client.get("/api/session").status_code, 401)

    def test_cross_origin_missing_origin_and_host_rejected(self):
        for origin in ["https://attacker.test", "null", ""]:
            self.assertEqual(self.client.post("/api/login", headers={"Origin": origin}, json={"access_key": KEY}).status_code, 403)
        self.assertEqual(self.client.get("/health", headers={"Host": "attacker.test"}).status_code, 400)

    def test_answer_history_feedback_and_operator_export(self):
        self.login()
        response = self.ask()
        self.assertEqual(response.status_code, 200, response.text)
        answer = response.json(); request_id = answer["request_id"]
        self.assertEqual(answer["status"], "answered")
        self.assertNotIn("_audit", response.text)
        self.assertEqual(response.headers["X-Request-ID"], request_id)
        saved = self.client.post(f"/api/requests/{request_id}/feedback", json={"outcome": "partially_solved", "comment": "Need backorder steps", "task_minutes": 4})
        self.assertEqual(saved.status_code, 200)
        history = self.client.get("/api/session").json()["history"]
        self.assertEqual(history[0]["feedback"]["outcome"], "partially_solved")
        self.assertEqual(self.client.get("/api/admin/export").status_code, 401)
        export = self.client.get("/api/admin/export", headers={"Authorization": f"Bearer {ADMIN_KEY}"})
        row = json.loads(export.text)
        self.assertEqual(row["request_id"], request_id)
        self.assertEqual(row["principal"], "operations")
        self.assertEqual(row["audit"]["draft"]["status"], "answered")
        self.assertEqual(row["response"]["trace"]["generation"][0]["model"], "mock-provider")
        self.assertNotIn(COOKIE, export.text)

    def test_rejected_draft_is_operator_only(self):
        self.service.generator.answer.claims[0].text = "Unsafe rejected draft for operator review"
        self.service.generator.support.supported = False
        self.login(); response = self.ask()
        self.assertEqual(response.json()["status"], "insufficient_evidence")
        self.assertNotIn("Unsafe rejected", response.text)
        self.assertNotIn("Unsafe rejected", self.client.get("/api/session").text)
        export = self.client.get("/api/admin/export", headers={"Authorization": f"Bearer {ADMIN_KEY}"})
        self.assertIn("Unsafe rejected", export.text)

    def test_sessions_isolate_history_and_feedback_even_for_same_access_key(self):
        self.login(); request_id = self.ask().json()["request_id"]
        self.client.cookies.clear(); self.login()
        self.assertEqual(self.client.get("/api/session").json()["history"], [])
        response = self.client.post(f"/api/requests/{request_id}/feedback", json={"outcome": "solved"})
        self.assertEqual(response.status_code, 404)
        self.client.cookies.clear(); self.login(OTHER_KEY)
        self.assertEqual(self.client.get("/api/session").json()["history"], [])

    def test_expiry_and_key_revocation(self):
        self.login()
        with self.app.state.store.connection() as db:
            db.execute("UPDATE sessions SET expires=?", (time.time() - 1,))
        self.assertEqual(self.client.get("/api/session").status_code, 401)
        self.login(); self.settings.access_keys["operations"] = "rotated-test-key-of-sufficient-length"
        self.assertEqual(self.client.get("/api/session").status_code, 401)

    def test_request_validation_and_body_limit(self):
        self.login()
        for payload in [{"question": ""}, {"question": "x" * 1801}, {"question": "test", "session_id": "spoofed"}]:
            self.assertEqual(self.client.post("/api/answers", json=payload).status_code, 422)
        self.assertEqual(self.client.post("/api/answers", content="x" * 17000).status_code, 413)

    def test_per_user_quota_survives_new_session_and_restart(self):
        self.login()
        for _ in range(5): self.assertEqual(self.ask().status_code, 200)
        self.client.cookies.clear(); self.login()
        self.assertEqual(self.ask().status_code, 429)
        app = create_app(self.settings, self.service, ready)
        with TestClient(app, headers=ORIGIN) as client:
            client.post("/api/login", json={"access_key": KEY})
            self.assertEqual(client.post("/api/answers", json={"question": "test"}).status_code, 429)

    def test_login_bruteforce_is_bounded(self):
        for _ in range(10): self.assertEqual(self.login("wrong").status_code, 401)
        self.assertEqual(self.login().status_code, 429)

    def test_provider_failure_does_not_leak_secrets(self):
        async def failure(*args, **kwargs): raise RuntimeError("secret-provider-key")
        self.service.answer = failure
        self.login(); response = self.ask()
        self.assertEqual(response.status_code, 503)
        self.assertNotIn("secret-provider-key", response.text)
        self.assertIn("request_id", response.json()["detail"])
        row = self.client.get("/api/session").json()["history"][0]
        self.assertEqual(row["error"], "dependency_failure")
        self.assertNotIn("secret-provider-key", str(row))

    def test_timeout_is_bounded_and_recorded(self):
        async def slow(*args, **kwargs): await asyncio.sleep(.1)
        app = create_app(replace(self.settings, request_timeout=.01), type("Slow", (), {"answer": staticmethod(slow)})(), ready)
        with TestClient(app, headers=ORIGIN) as client:
            client.post("/api/login", json={"access_key": KEY})
            response = client.post("/api/answers", json={"question": "test"})
            self.assertEqual(response.status_code, 504)
            self.assertEqual(client.get("/api/session").json()["history"][0]["error"], "timeout")

    def test_global_daily_budget_applies_across_users(self):
        app = create_app(replace(self.settings, total_answers_per_day=1), self.service, ready)
        with TestClient(app, headers=ORIGIN) as client:
            client.post("/api/login", json={"access_key": KEY})
            self.assertEqual(client.post("/api/answers", json={"question": "test", "odoo_version": "19.0"}).status_code, 200)
            client.cookies.clear(); client.post("/api/login", json={"access_key": OTHER_KEY})
            self.assertEqual(client.post("/api/answers", json={"question": "test"}).status_code, 429)

    def test_concurrent_requests_are_bounded(self):
        entered = Event()
        async def slow(*args, **kwargs):
            entered.set()
            await asyncio.sleep(.2)
            return {"status": "insufficient_evidence", "trace": {"latency_ms": 200}}
        app = create_app(replace(self.settings, max_concurrent=1), type("Slow", (), {"answer": staticmethod(slow)})(), ready)
        with TestClient(app, headers=ORIGIN) as client, ThreadPoolExecutor(max_workers=1) as pool:
            client.post("/api/login", json={"access_key": KEY})
            first = pool.submit(client.post, "/api/answers", json={"question": "first"})
            self.assertTrue(entered.wait(2))
            self.assertEqual(client.post("/api/answers", json={"question": "second"}).status_code, 429)
            self.assertEqual(first.result().status_code, 200)


if __name__ == "__main__": unittest.main()
