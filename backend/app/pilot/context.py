"""Reviewed dependencies for two demonstrated pilot gaps; dense ranking is unchanged.

These IDs belong to the accepted immutable corpus. A new corpus needs a new review.
No additional embedding calls, ingestion, approximate threshold, or source expansion.
"""
import json
import re

from app.database import connect_database

POLICY = "pilot-support-passages-0.1"
RETURNS = "content/applications/sales/sales/products_prices/returns.rst"
INVOICING = "content/applications/sales/sales/invoicing/invoicing_policy.rst"
MULTIPACK = "content/applications/inventory_and_mrp/inventory/shipping_receiving/setup_configuration/multipack.rst"
CREDIT_SUPPORT = (
    "788668974cfd67ce169b1caa1a406837dfedbf4a9057d5c9c45d82f26b5dfe82",  # Refund/return qualification
    "0bce0486b91b9adf2fd3bcfcae184c3a109f21cba2cf8bc53f78555a2f3e226e",  # Partial customer credit
)
BACKORDER_SUPPORT = "94e90fc817d5aa5a3b8972768febce2ef3202cef1921c46e88a05b30690587d8"


def support_ids(question: str, result: dict) -> list[str]:
    paths = {h["chunk_record"]["content"]["source"]["source_path"] for h in result["hits"][:5]}
    requested = []
    if RETURNS in paths and re.search(r"\b(return\w*|refund\w*|credit\w*)\b", question, re.I):
        requested.extend(CREDIT_SUPPORT)
    if paths & {INVOICING, MULTIPACK} and re.search(r"\bback\s?orders?\b", question, re.I):
        requested.append(BACKORDER_SUPPORT)
    existing = {h["chunk_id"] for h in result["hits"][:5]}
    return [chunk_id for chunk_id in requested if chunk_id not in existing]


def assemble(result: dict, records: list[dict]) -> dict:
    # Keep the strongest three dense hits first; reserve room for reviewed dependencies.
    extras = [{"chunk_id": r["chunk_id"], "chunk_record": r} for r in records]
    candidates = [*result["hits"][:3], *extras, *result["hits"][3:5]]
    return {**result, "context_hits": candidates[:8], "context_policy": POLICY,
            "support_chunk_ids": [r["chunk_id"] for r in records]}


async def extend_context(question: str, result: dict, settings):
    ids = support_ids(question, result)
    if result["snapshot_id"] != settings.snapshot_id:
        raise ValueError("Cannot extend an unreviewed snapshot")
    if not ids:
        return assemble(result, [])
    async with connect_database() as db:
        rows = await db.fetch("""SELECT chunk_id, chunk_record FROM index_chunks
            WHERE snapshot_id=$1 AND chunk_id=ANY($2::text[])""", settings.snapshot_id, ids)
    by_id = {r["chunk_id"]: json.loads(r["chunk_record"]) for r in rows}
    if set(by_id) != set(ids):
        raise ValueError("Reviewed pilot dependency missing from the published snapshot")
    return assemble(result, [by_id[chunk_id] for chunk_id in ids])
