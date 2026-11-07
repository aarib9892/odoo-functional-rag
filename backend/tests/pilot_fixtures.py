"""Synthetic service fixtures; no provider calls or holdout questions."""
from copy import deepcopy
from pathlib import Path

from app.chunking.models import ChunkDraft
from app.chunking.records import finalize_chunk
from app.chunking.text import RENDERER_VERSION
from app.ingestion.normalized_models import SourceIdentity
from app.pilot.models import Claim, DraftAnswer, EvidenceReference, SupportReview
from app.pilot.settings import ACCEPTED_COMMIT, ACCEPTED_INDEX, Settings

PASSAGE = "Choose Invoice what is delivered to invoice delivered quantities. Validate the delivery before creating the invoice."
KEY = "test-internal-access-key-123456789"
OTHER_KEY = "test-other-access-key-123456789"
ADMIN_KEY = "test-operator-access-key-123456789"


def settings(directory, **kwargs):
    return Settings(access_keys={"operations": KEY, "other": OTHER_KEY}, admin_key=ADMIN_KEY,
                    store_path=Path(directory) / "pilot.sqlite3", public_origin="http://testserver", **kwargs)


def retrieval():
    source = SourceIdentity(
        repository_url="https://github.com/odoo/documentation.git", odoo_version="19.0",
        language="en", commit=ACCEPTED_COMMIT,
        source_path="content/applications/sales/sales/invoicing/invoicing_policy.rst",
        sha256="a" * 64, application="sales")
    draft = ChunkDraft(source, "doc", "revision", "s1", ("Invoicing policy",),
                       ("b1",), RENDERER_VERSION, PASSAGE, "Invoicing policy\n\n" + PASSAGE)
    record = finalize_chunk(draft)
    return {"snapshot_id": ACCEPTED_INDEX, "hits": [{"rank": 1, "chunk_id": record["chunk_id"],
             "chunk_record": record, "distance": .2}],
            "query_embedding": {"cache_hit": True, "api_requests": 0, "prompt_tokens": 0, "total_tokens": 0}}


def answered():
    return DraftAnswer(status="answered", clarification_question=None,
        claims=[Claim(text="Validate the delivery before creating the invoice.",
            citations=[EvidenceReference(evidence_id="E1", quote=PASSAGE)])])


class FakeGenerator:
    def __init__(self):
        self.answer = answered()
        self.support = SupportReview(supported=True, complete=True, needs_clarification=False,
                                     clarification_question=None)
        self.calls = []

    async def draft(self, payload):
        self.calls.append(("draft", deepcopy(payload)))
        return self.answer.model_copy(deep=True), {"model": "mock-provider", "input_tokens": 100, "output_tokens": 40}

    async def review(self, payload):
        self.calls.append(("review", deepcopy(payload)))
        return self.support.model_copy(deep=True), {"model": "mock-provider", "input_tokens": 130, "output_tokens": 10}


async def fake_retrieve(*args, **kwargs):
    return retrieval()
