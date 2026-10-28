from app.chunking.grouping import merge_drafts
from app.chunking.models import ChunkDraft
from app.chunking.tokens import count_tokens


def pack_section(
    units: list[ChunkDraft],
    document_title: str,
    max_tokens: int = 512,
) -> list[ChunkDraft]:
    """Pack one section's units in order, without splitting a unit."""
    if max_tokens < 1:
        raise ValueError("Token budget must be positive")

    packed: list[ChunkDraft] = []
    pending: ChunkDraft | None = None
    seen: set[str] = set()

    for unit in units:
        if seen.intersection(unit.source_block_ids):
            raise ValueError("Duplicate source block IDs")
        seen.update(unit.source_block_ids)

        unit_tokens = count_tokens(unit.retrieval_text)

        if unit_tokens > max_tokens:
            raise ValueError(
                f"Unit {unit.source_block_ids} in {unit.source.source_path} "
                f"needs {unit_tokens} tokens; budget is {max_tokens}"
            )

        if pending is None:
            pending = unit
            continue

        candidate = merge_drafts([pending, unit], document_title)

        if count_tokens(candidate.retrieval_text) <= max_tokens:
            pending = candidate
        else:
            packed.append(pending)
            pending = unit

    if pending is not None:
        packed.append(pending)

    return packed
