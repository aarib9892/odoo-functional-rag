from dataclasses import dataclass

from app.ingestion.normalized_models import SourceIdentity


@dataclass(frozen=True)
class ChunkDraft:
    source: SourceIdentity
    document_id: str
    document_revision_id: str
    section_id: str | None
    heading_path: tuple[str, ...]
    source_block_ids: tuple[str, ...]
    renderer_version: str
    evidence_text: str
    retrieval_text: str
