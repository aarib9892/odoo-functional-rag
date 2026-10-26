from collections.abc import Iterator


def iter_blocks_with_sections(
    items: list[dict],
    section_id: str | None = None,
) -> Iterator[tuple[str | None, dict]]:
    """Yield owning section IDs and blocks in source order."""
    for item in items:
        if "section_id" in item:
            yield from iter_blocks_with_sections(
                item["items"],
                item["section_id"],
            )
        elif "block_id" in item:
            yield section_id, item
        else:
            raise ValueError("Expected a normalized section or block")


def iter_blocks(items: list[dict]) -> Iterator[dict]:
    for _, block in iter_blocks_with_sections(items):
        yield block
