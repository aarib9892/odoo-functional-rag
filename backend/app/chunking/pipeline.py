from app.chunking.drafts import iter_chunk_drafts
from app.chunking.grouping import attach_images, iter_section_groups
from app.chunking.packing import pack_section
from app.chunking.records import finalize_chunk
from app.chunking.walk import iter_blocks


def build_document_chunks(document: dict, max_tokens: int = 512) -> list[dict]:
    """Build candidate chunk records from one normalized document."""
    if max_tokens < 1:
        raise ValueError("Token budget must be positive")

    drafts = list(iter_chunk_drafts(document))

    expected_ids = tuple(
        block_id for draft in drafts for block_id in draft.source_block_ids
    )
    if len(expected_ids) != len(set(expected_ids)):
        raise ValueError("Duplicate source block IDs in document")

    kinds = {
        block["block_id"]: block["kind"] for block in iter_blocks(document["items"])
    }
    records = []

    for group in iter_section_groups(drafts):
        units = attach_images(group, kinds, document["title"])
        packed = pack_section(units, document["title"], max_tokens=max_tokens)

        records.extend(finalize_chunk(chunk, max_tokens=max_tokens) for chunk in packed)

    actual_ids = tuple(
        block_id
        for record in records
        for block_id in record["content"]["source_block_ids"]
    )
    if actual_ids != expected_ids:
        raise ValueError("Chunking changed source block order or coverage")

    return records
