"""Readable text from m22-0.2 normalized blocks, before chunk packing.

Labels in brackets are formatting/metadata markers, not verbatim RST.
Input dictionaries retain provenance, links and image metadata unchanged.
Tables currently require one group, one header row and unmerged cells;
ordered lists currently require Arabic numbering. Unknown shapes fail.
"""

RENDERER_VERSION = "m31-text-0.1"

PROSE_KINDS = {"paragraph", "caption", "title", "rubric", "field_name"}
CONTAINER_KINDS = {
    "compound",
    "container",
    "list_item",
    "field_list",
    "field",
    "field_body",
}
METADATA_ONLY_KINDS = {"anchor", "substitution_definition", "comment"}
TABLE_LAYOUT_KINDS = {
    "table_group",
    "table_column",
    "table_head",
    "table_body",
    "table_row",
}


def prose(text: str) -> str:
    """Remove line wrapping from prose, while preserving its words."""
    return " ".join(text.split())


def render_children(block: dict, separator: str = "\n\n") -> str:
    """Render children in order, omitting explicitly metadata-only output."""
    parts = [render_block(child) for child in block["children"]]
    return separator.join(part for part in parts if part)


def labeled(label: str, body: str) -> str:
    return f"[{label}]\n{body}" if body else f"[{label}]"


def single_child(block: dict, kind: str) -> dict:
    matches = [child for child in block["children"] if child["kind"] == kind]
    if len(matches) != 1:
        raise ValueError(f"Expected exactly one {kind}; found {len(matches)}")
    return matches[0]


def require_children(block: dict, allowed: set[str]) -> None:
    unexpected = [
        child["kind"] for child in block["children"] if child["kind"] not in allowed
    ]
    if unexpected:
        raise ValueError(f"Unexpected children in {block['kind']}: {unexpected}")


def row_values(row: dict) -> list[str]:
    if row["kind"] != "table_row":
        raise ValueError("Expected a table row")
    require_children(row, {"table_cell"})
    return [render_block(cell) for cell in row["children"]]


def render_table_row(headers: list[str], row: dict) -> str:
    values = row_values(row)
    return "; ".join(
        f"{header}: {value}" for header, value in zip(headers, values, strict=True)
    )


def render_table(block: dict) -> str:
    require_children(block, {"table_group"})
    group = single_child(block, "table_group")
    require_children(group, {"table_column", "table_head", "table_body"})
    head = single_child(group, "table_head")
    body = single_child(group, "table_body")
    require_children(head, {"table_row"})
    require_children(body, {"table_row"})

    if len(head["children"]) != 1:
        raise ValueError("Only one header row is supported so far")
    headers = row_values(head["children"][0])
    columns = [child for child in group["children"] if child["kind"] == "table_column"]
    if not headers or any(not header.strip() for header in headers):
        raise ValueError("Table columns need nonempty headers")
    if not len(headers) == len(columns) == group["attributes"]["cols"]:
        raise ValueError("Headers, column records and declared count disagree")
    if not body["children"]:
        raise ValueError("Expected at least one table data row")

    return "\n".join(render_table_row(headers, row) for row in body["children"])


def render_list(block: dict) -> str:
    require_children(block, {"list_item"})
    numbered = block["kind"] == "ordered_list"
    attributes = block["attributes"]
    if numbered and attributes.get("enumtype") != "arabic":
        raise ValueError("Unsupported ordered-list numbering style")
    start = attributes.get("start", 1) if numbered else 1
    prefix = attributes.get("prefix", "")
    suffix = attributes.get("suffix", ".")

    items = []
    for number, child in enumerate(block["children"], start=start):
        marker = f"{prefix}{number}{suffix} " if numbered else "- "
        body = render_block(child)
        padding = " " * len(marker)
        items.append(marker + body.replace("\n", "\n" + padding))
    return "\n".join(items)


def render_navigation(block: dict) -> str:
    """Describe original links and states without reading destination pages."""
    attributes = block["attributes"]
    entries = attributes["original_entries"]
    targets = attributes["targets"]
    lines = ["[Navigation metadata]"]
    for entry, target in zip(entries, targets, strict=True):
        if target["target"] != entry:
            raise ValueError("Navigation target order differs from original entries")
        lines.append(f"- {entry} [reference state: {target['resolution']}]")
    return "\n".join(lines)


def render_block(block: dict) -> str:
    """Render one block, keeping its nested content and labels together."""
    kind = block["kind"]

    if kind in METADATA_ONLY_KINDS:
        # Definitions are already expanded in body inlines. Anchors/comments
        # remain available on the original records; they are not body prose.
        return ""

    if kind in PROSE_KINDS:
        text = prose(block["text"])
        if kind == "caption":
            return labeled("Caption", text)
        if kind in {"title", "rubric"}:
            return labeled("Title: " + text, "")
        return text + ":" if kind == "field_name" else text

    if kind in CONTAINER_KINDS:
        return render_children(block)

    if kind in {"literal", "math"}:
        # Preserve line breaks and indentation in code/formulas.
        label = (
            "Literal block"
            if kind == "literal"
            else "Math: " + block["attributes"]["format"]
        )
        return labeled(label, block["text"])

    if kind == "image":
        attributes = block["attributes"]
        alt = prose(attributes.get("alt", ""))
        marker = f"[Image dependency: {attributes['uri']}]"
        return marker + (f"\n[Alt text: {alt}]" if alt else "\n[Alt text unavailable]")

    if kind == "admonition":
        label = block["attributes"]["admonition_type"].upper()
        body = render_children(block)
        return f"{label}:\n{body}" if body else f"{label}:"

    if kind in {"bullet_list", "ordered_list"}:
        return render_list(block)

    if kind == "table_cell":
        spans = block["attributes"]
        if spans["rowspan"] != 1 or spans["colspan"] != 1:
            raise ValueError("Merged table cells need explicit handling")
        return render_children(block)

    if kind == "table":
        return render_table(block)

    if kind in TABLE_LAYOUT_KINDS:
        raise ValueError(f"Render {kind} through its parent table to retain headers")

    if kind == "tab":
        return labeled("Tab: " + block["attributes"]["label"], render_children(block))

    if kind in {"tabs", "cards"}:
        require_children(block, {"tab" if kind == "tabs" else "card"})
        return render_children(block)

    if kind in {"figure", "block_quote"}:
        label = "Figure" if kind == "figure" else "Block quote"
        return labeled(label, render_children(block))

    if kind == "card":
        attributes = block["attributes"]
        body = render_children(block)
        target = attributes["target"]
        state = attributes.get("resolution", "not_attempted")
        link = f"[Related document: {target}; reference state: {state}]"
        return labeled(
            "Card: " + attributes["label"],
            "\n\n".join(part for part in (body, link) if part),
        )

    if kind == "navigation":
        return render_navigation(block)

    location = block.get("source", {})
    raise ValueError(
        f"Unsupported block kind {kind!r} at "
        f"{location.get('source_path', '?')}:{location.get('line', '?')}"
    )
