"""Offline browser-test server. Synthetic retrieval/provider, real auth/storage/API/UI."""
from dataclasses import replace
import tempfile

from app.pilot.api import create_app
from app.pilot.service import AnswerService
from tests.pilot_fixtures import FakeGenerator, fake_retrieve, settings

temporary = tempfile.TemporaryDirectory(prefix="odoo-pilot-browser-")
config = replace(settings(temporary.name), public_origin="http://localhost:8017")


async def readiness(_):
    return {"snapshot_id": "synthetic-browser-fixture", "chunks": 1}


app = create_app(config, AnswerService(config, FakeGenerator(), fake_retrieve), readiness)
