from collections.abc import Iterable, Iterator
from itertools import groupby
from dataclasses import replace
from app.chunking.models import ChunkDraft


def section_key(draft: ChunkDraft) -> tuple:
    return (
        draft.document_id,
        draft.document_revision_id,
        draft.section_id,
        draft.heading_path,
        draft.renderer_version,
    )


def iter_section_groups(
    drafts: Iterable[ChunkDraft],
) -> Iterator[list[ChunkDraft]]:
    for _, group in groupby(drafts, key=section_key):
        yield list(group)


def merge_drafts(
    drafts: list[ChunkDraft],
    document_title: str,
) -> ChunkDraft:
    if not drafts:
        raise ValueError("Cannot merge an empty group")

    first = drafts[0]
    expected_key = section_key(first)

    if any(
        section_key(draft) != expected_key or draft.source != first.source
        for draft in drafts
    ):
        raise ValueError("Drafts must share source and section context")

    block_ids = tuple(
        block_id for draft in drafts for block_id in draft.source_block_ids
    )

    if len(block_ids) != len(set(block_ids)):
        raise ValueError("Duplicate source block IDs")

    evidence = "\n\n".join(draft.evidence_text for draft in drafts)
    context = " > ".join(first.heading_path) or document_title
    retrieval = "\n\n".join(part for part in (context, evidence) if part)

    return replace(
        first,
        source_block_ids=block_ids,
        evidence_text=evidence,
        retrieval_text=retrieval,
    )
