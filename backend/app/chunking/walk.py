from collections.abc import Iterator


def iter_blocks(items: list[dict]) -> Iterator[dict]:
    for item in items:
        if "section_id" in item:
            yield from iter_blocks(item["items"])
        elif "block_id" in item:
            yield item
        else:
            raise ValueError("Expected Normalized section or block")
