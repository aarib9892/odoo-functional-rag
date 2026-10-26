from collections.abc import Iterator

from app.chunking.models import ChunkDraft
from app.chunking.text import RENDERER_VERSION, render_block
from app.chunking.walk import iter_blocks_with_sections
from app.ingestion.normalized_models import SourceIdentity


def iter_chunk_drafts(document: dict) -> Iterator[ChunkDraft]:
    if document["schema_version"] != "m22-0.2" or document["status"] != "ok":
        raise ValueError("Expected a complete m22-0.2 normalized document")

    source = SourceIdentity(**document["source"])

    for section_id, block in iter_blocks_with_sections(document["items"]):
        evidence_text = render_block(block)

        if not evidence_text.strip():
            continue

        heading_path = tuple(block["heading_path"])
        context = " > ".join(heading_path) or document["title"]
        retrieval_text = "\n\n".join(part for part in (context, evidence_text) if part)

        yield ChunkDraft(
            source=source,
            document_id=document["document_id"],
            document_revision_id=document["revision_id"],
            section_id=section_id,
            heading_path=heading_path,
            source_block_ids=(block["block_id"],),
            renderer_version=RENDERER_VERSION,
            evidence_text=evidence_text,
            retrieval_text=retrieval_text,
        )
