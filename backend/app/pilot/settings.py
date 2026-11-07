from dataclasses import dataclass, field
import json
import os
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
ACCEPTED_INDEX = "e8f661333130c61d51f1a68908ef2038c9a5d24575369bbaa3bccf0bb2b97818"
ACCEPTED_COMMIT = "c9202e68ae702daec981b47d0b6055191084ffa2"


@dataclass(frozen=True)
class Settings:
    access_keys: dict[str, str] = field(repr=False)
    admin_key: str = field(repr=False)
    model: str = "gpt-4.1-mini"
    reasoning_effort: str | None = None
    public_origin: str = "http://localhost:8000"
    secure_cookie: bool = False
    store_path: Path = ROOT / "data/pilot/pilot.sqlite3"
    query_cache: Path = ROOT / "data/embeddings/query-cache"
    frontend: Path = ROOT / "frontend/dist"
    snapshot_id: str = ACCEPTED_INDEX
    source_commit: str = ACCEPTED_COMMIT
    request_timeout: float = 60
    session_hours: int = 8
    answers_per_minute: int = 5
    answers_per_day: int = 100
    total_answers_per_day: int = 500
    max_concurrent: int = 2

    def __post_init__(self):
        secrets = [*self.access_keys.values(), self.admin_key]
        if not self.access_keys or any(
            not isinstance(k, str) or not k.strip() or len(k) > 80
            for k in self.access_keys
        ):
            raise ValueError("Configure named PILOT_ACCESS_KEYS before starting")
        if any(not isinstance(s, str) or len(s) < 24 for s in secrets):
            raise ValueError("Pilot access/admin keys must have at least 24 characters")
        if len(secrets) != len(set(secrets)):
            raise ValueError("Each pilot/admin key must be distinct")
        origin = urlsplit(self.public_origin)
        if (origin.scheme not in {"http", "https"} or not origin.hostname
                or origin.path or origin.query or origin.fragment or origin.username):
            raise ValueError("PILOT_PUBLIC_ORIGIN must be an origin without a path")
        if origin.hostname not in {"localhost", "127.0.0.1", "::1", "testserver"}:
            if origin.scheme != "https" or not self.secure_cookie:
                raise ValueError("Remote pilot access requires HTTPS and secure cookies")
        if not self.model.strip():
            raise ValueError("Configure PILOT_GENERATION_MODEL")
        if self.reasoning_effort not in {None, "none", "low", "medium", "high", "xhigh", "max"}:
            raise ValueError("Invalid PILOT_REASONING_EFFORT")
        for value in (self.session_hours, self.answers_per_minute, self.answers_per_day,
                      self.total_answers_per_day, self.max_concurrent, self.request_timeout):
            if value <= 0:
                raise ValueError("Pilot limits must be positive")

    @classmethod
    def from_env(cls):
        model = os.environ.get("PILOT_GENERATION_MODEL") or os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
        return cls(
            access_keys=json.loads(os.environ.get("PILOT_ACCESS_KEYS", "{}")),
            admin_key=os.environ.get("PILOT_ADMIN_KEY", ""),
            model=model,
            reasoning_effort=os.environ.get("PILOT_REASONING_EFFORT") or ("low" if model == "gpt-6-luna" else None),
            public_origin=os.environ.get("PILOT_PUBLIC_ORIGIN", "http://localhost:8000"),
            secure_cookie=os.environ.get("PILOT_SECURE_COOKIE", "false").lower() == "true",
            store_path=Path(os.environ.get("PILOT_STORE_PATH", str(ROOT / "data/pilot/pilot.sqlite3"))),
            request_timeout=float(os.environ.get("PILOT_REQUEST_TIMEOUT", "60")),
            answers_per_day=int(os.environ.get("PILOT_ANSWERS_PER_DAY", "100")),
            total_answers_per_day=int(os.environ.get("PILOT_TOTAL_ANSWERS_PER_DAY", "500")),
        )
