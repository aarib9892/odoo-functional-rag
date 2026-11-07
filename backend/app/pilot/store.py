"""Small single-host pilot store. Transactions own quotas and session isolation."""
from contextlib import contextmanager
import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import sqlite3
import time


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class QuotaExceeded(RuntimeError):
    pass


class Store:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connection() as db:
            db.executescript("""
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY, principal TEXT NOT NULL,
                    key_hash TEXT NOT NULL, expires REAL NOT NULL
                );
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY, session_id TEXT NOT NULL,
                    created REAL NOT NULL, principal TEXT NOT NULL, question TEXT NOT NULL,
                    version TEXT NOT NULL, response TEXT, error TEXT, audit TEXT
                );
                CREATE INDEX IF NOT EXISTS request_sessions ON requests(session_id, created);
                CREATE TABLE IF NOT EXISTS feedback (
                    request_id TEXT PRIMARY KEY, updated REAL NOT NULL,
                    outcome TEXT NOT NULL, comment TEXT NOT NULL, task_minutes REAL,
                    FOREIGN KEY(request_id) REFERENCES requests(id)
                );
                CREATE TABLE IF NOT EXISTS quotas (
                    key TEXT NOT NULL, window INTEGER NOT NULL, count INTEGER NOT NULL,
                    PRIMARY KEY(key, window)
                );
            """)
        os.chmod(path, 0o600)

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def charge(self, rules: list[tuple[str, int, int]]):
        now = time.time()
        with self.connection() as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute("DELETE FROM quotas WHERE window < ?", (int(now) - 172800,))
            for key, seconds, maximum in rules:
                window = int(now // seconds) * seconds
                row = db.execute("SELECT count FROM quotas WHERE key=? AND window=?", (key, window)).fetchone()
                if row and row[0] >= maximum:
                    raise QuotaExceeded()
                db.execute("""INSERT INTO quotas VALUES (?, ?, 1)
                    ON CONFLICT(key, window) DO UPDATE SET count=count+1""", (key, window))

    def login(self, access_key, settings):
        principal = None
        for label, configured in settings.access_keys.items():
            if hmac.compare_digest(digest(access_key), digest(configured)):
                principal = label
        if principal is None:
            return None
        token = secrets.token_urlsafe(32)
        with self.connection() as db:
            db.execute("DELETE FROM sessions WHERE expires < ?", (time.time(),))
            db.execute("INSERT INTO sessions VALUES (?, ?, ?, ?)",
                       (digest(token), principal, digest(access_key), time.time() + settings.session_hours * 3600))
        return token

    def session(self, token, settings):
        if not token or len(token) > 100:
            return None
        with self.connection() as db:
            row = db.execute("SELECT * FROM sessions WHERE id=? AND expires>?",
                             (digest(token), time.time())).fetchone()
        if not row:
            return None
        key = settings.access_keys.get(row["principal"])
        if not key or not hmac.compare_digest(row["key_hash"], digest(key)):
            return None
        return dict(row)

    def logout(self, token):
        with self.connection() as db:
            db.execute("DELETE FROM sessions WHERE id=?", (digest(token),))

    def start(self, request_id, session_id, principal, question, version):
        with self.connection() as db:
            db.execute("INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL)",
                       (request_id, session_id, time.time(), principal, question, version))

    def finish(self, request_id, response=None, error=None, audit=None):
        with self.connection() as db:
            db.execute("UPDATE requests SET response=?, error=?, audit=? WHERE id=?",
                       (json.dumps(response, ensure_ascii=False) if response else None, error,
                        json.dumps(audit, ensure_ascii=False) if audit else None, request_id))

    def history(self, session_id):
        with self.connection() as db:
            rows = db.execute("""SELECT r.*, f.outcome, f.comment, f.task_minutes
                FROM requests r LEFT JOIN feedback f ON f.request_id=r.id
                WHERE r.session_id=? ORDER BY r.created DESC LIMIT 30""", (session_id,)).fetchall()
        return [{"request_id": r["id"], "created_at": r["created"],
                 "question": r["question"], "odoo_version": r["version"],
                 "response": json.loads(r["response"]) if r["response"] else None,
                 "error": r["error"],
                 "feedback": {"outcome": r["outcome"], "comment": r["comment"],
                              "task_minutes": r["task_minutes"]} if r["outcome"] else None}
                for r in reversed(rows)]

    def feedback(self, request_id, session_id, feedback):
        with self.connection() as db:
            row = db.execute("SELECT response FROM requests WHERE id=? AND session_id=? AND error IS NULL",
                             (request_id, session_id)).fetchone()
            if not row or not row["response"]:
                return False
            db.execute("""INSERT INTO feedback VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(request_id) DO UPDATE SET updated=excluded.updated,
                outcome=excluded.outcome, comment=excluded.comment, task_minutes=excluded.task_minutes""",
                (request_id, time.time(), feedback.outcome, feedback.comment, feedback.task_minutes))
        return True

    def export(self):
        with self.connection() as db:
            rows = db.execute("""SELECT r.id AS request_id, r.created, r.question, r.version,
                r.response, r.error, r.audit, r.principal, f.updated AS feedback_at,
                f.outcome, f.comment, f.task_minutes FROM requests r
                LEFT JOIN feedback f ON f.request_id=r.id ORDER BY r.created""").fetchall()
        for row in rows:
            item = dict(row)
            item["response"] = json.loads(item["response"]) if item["response"] else None
            item["audit"] = json.loads(item["audit"]) if item["audit"] else None
            yield item
