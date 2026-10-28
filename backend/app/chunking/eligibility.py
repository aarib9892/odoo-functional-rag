from app.chunking.walk import iter_blocks

ELIGIBILITY_VERSION = "m31-body-content-0.1"

METADATA_KINDS = {
    "anchor",
    "comment",
    "substitution_definition",
    "image",
    "navigation",
    "card",
    "cards",
    "title",
    "rubric",
}


def has_body_content(block: dict) -> bool:
    if block["kind"] in METADATA_KINDS:
        return False

    if (
        block["kind"] == "admonition"
        and block["attributes"].get("admonition_type") == "seealso"
    ):
        return False

    return bool(block["text"].strip()) or any(
        has_body_content(child) for child in block["children"]
    )


def assess_chunk(record: dict, document: dict) -> dict:
    content = record["content"]

    if (
        content["document_id"] != document["document_id"]
        or content["document_revision_id"] != document["revision_id"]
    ):
        raise ValueError("Chunk and normalized document identities differ")

    blocks = {block["block_id"]: block for block in iter_blocks(document["items"])}

    body_ids, metadata_ids = [], []

    for block_id in content["source_block_ids"]:
        target = body_ids if has_body_content(blocks[block_id]) else metadata_ids
        target.append(block_id)

    eligible = bool(body_ids)

    return {
        "chunk_id": record["chunk_id"],
        "eligibility_version": ELIGIBILITY_VERSION,
        "eligible_for_retrieval": eligible,
        "reason": "contains_body_content" if eligible else "metadata_only",
        "body_block_ids": body_ids,
        "metadata_block_ids": metadata_ids,
    }
