"""Map the selected corpus's structured nodes into application-owned records."""

import hashlib
import json
from pathlib import Path

from docutils import nodes
from sphinx import addnodes
from sphinx_tabs.tabs import SphinxTabsPanel, SphinxTabsTablist

from app.ingestion.normalized_models import (
    Block, Diagnostic, Inline, NormalizedDocument, Section,
    SourceIdentity, SourceLocation,
)
from app.ingestion.rst_directives import ExampleBlock
from app.ingestion.rst_structures import CardBlock, CardsBlock


SCHEMA_VERSION = "m22-0.2"
NORMALIZER_VERSION = "structures-0.2"


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode("utf-8")).hexdigest()


class Normalizer:
    def __init__(self, source: SourceIdentity, parser_id: str, source_root: Path | None = None,
                 reference_index=None):
        self.source = source
        self.parser_id = parser_id
        self.source_root = source_root.resolve() if source_root is not None else None
        self.sequence = 0
        self.issues = []
        self.reference_index = reference_index
        self.docname = source.source_path[:-4]
        self.tab_labels = {}

    def location(self, node) -> SourceLocation:
        current = node
        while current is not None:
            line = getattr(current, "line", None)
            if isinstance(line, int) and line > 0:
                return SourceLocation(self.source.source_path, line,
                                      "node" if current is node else "ancestor")
            current = current.parent
        return SourceLocation(self.source.source_path, None, "unknown")

    def next_id(self, prefix):
        self.sequence += 1
        return f"{prefix}{self.sequence:04d}"

    def issue(self, node, code):
        self.issues.append(Diagnostic("error", code,
                                     f"No structured mapping for {node.tagname}.",
                                     self.location(node)))

    def inline(self, node):
        attributes = {}
        if isinstance(node, nodes.Text):
            kind = "text"
        elif isinstance(node, addnodes.pending_xref):
            kind = "reference"
            attributes = {
                "reference_kind": node.get("reftype"),
                "domain": node.get("refdomain"),
                "target": node.get("reftarget"),
                "explicit_title": bool(node.get("refexplicit")),
                "original_text": node.astext(),
                "resolution": "not_attempted",
            }
            if self.reference_index is not None:
                attributes.update(self.reference_index.pending(self.docname, node))
        elif isinstance(node, nodes.reference):
            kind = "reference"
            attributes = {
                "reference_kind": "external" if "refuri" in node else "local",
                "target": node.get("refuri", node.get("refid")),
                "resolution": "not_attempted",
            }
            if self.reference_index is not None and "refuri" in node:
                attributes["resolution"] = "external_not_checked"
        elif isinstance(node, addnodes.pending_xref_condition):
            kind, attributes = "span", {"condition": node.get("condition")}
        elif type(node) is nodes.inline:
            classes = node.get("classes", [])
            kind = ("gui_label" if "guilabel" in classes else
                    "menu_path" if "menuselection" in classes else
                    "icon" if "odoo-icon" in classes else "span")
            attributes = {"classes": list(classes)}
            if node.get("rawtext"):
                attributes["raw_markup"] = node["rawtext"]
            if node.get("icon_name"):
                attributes["icon_name"] = node["icon_name"]
        elif isinstance(node, nodes.target):
            kind = "anchor"
            attributes = {key: node[key] for key in ("ids", "names", "refid", "refuri") if key in node}
        elif isinstance(node, nodes.math):
            kind, attributes = "math", {"format": "latex"}
        elif isinstance(node, (nodes.strong, nodes.emphasis, nodes.literal, nodes.abbreviation, nodes.title_reference)):
            kind = node.tagname
            if node.get("explanation"):
                attributes["explanation"] = node["explanation"]
        else:
            kind = "unsupported"
            attributes = {"node_type": node.tagname, "raw_source": node.rawsource}
            self.issue(node, "unsupported_inline")
        children = () if isinstance(node, nodes.Text) else tuple(self.inline(child) for child in node.children)
        if isinstance(node, addnodes.pending_xref) and attributes.get("resolution") == "resolved" and not node.get("refexplicit"):
            children = (Inline("text", attributes["resolved_text"], self.location(node)),)
        text = node.astext() if isinstance(node, nodes.Text) else "".join(child.text for child in children)
        return Inline(kind, text, self.location(node), attributes, children)

    def block(self, node, headings):
        block_id = self.next_id("b")
        kind, text, attributes, inlines, children = "", "", {}, (), ()
        if isinstance(node, (nodes.paragraph, nodes.caption, nodes.title, nodes.rubric)):
            kind = "paragraph" if isinstance(node, nodes.paragraph) else node.tagname
            inlines = tuple(self.inline(child) for child in node.children)
            text = "".join(inline.text for inline in inlines)
        elif isinstance(node, (CardBlock, CardsBlock)):
            kind = "card" if isinstance(node, CardBlock) else "cards"
            if kind == "card":
                attributes = {"label": node["label"], "target": node["target"]}
                if self.reference_index is not None:
                    attributes.update(self.reference_index.document(self.docname, node["target"]))
            children = tuple(self.block(child, headings) for child in node.children)
        elif isinstance(node, nodes.container) and "sphinx-tabs" in node.get("classes", []):
            kind = "tabs"
            labels = {label["ids"][0]: label for group in node.children
                      if isinstance(group, SphinxTabsTablist) for label in group.children}
            panels = [child for child in node.children if isinstance(child, SphinxTabsPanel)]
            if set(labels) != {panel["aria-labelledby"] for panel in panels}:
                raise ValueError("A tab label or panel is unpaired.")
            for panel in panels:
                label = labels[panel["aria-labelledby"]]
                if label["aria-controls"] not in panel["ids"]:
                    raise ValueError("Tab label/panel relationship is inconsistent.")
                self.tab_labels[id(panel)] = label
            children = tuple(self.block(child, headings) for child in node.children
                             if not isinstance(child, SphinxTabsTablist))
        elif isinstance(node, SphinxTabsPanel):
            kind = "tab"
            label = self.tab_labels[id(node)]
            attributes = {"label": label.astext(), "hidden_in_html": node.get("hidden") == "true"}
            inlines = tuple(self.inline(child) for child in label.children)
            children = tuple(self.block(child, headings) for child in node.children)
        elif isinstance(node, addnodes.toctree):
            kind = "navigation"
            originals = node.get("original_entries")
            if originals is None:
                self.issue(node, "missing_original_navigation")
                originals = []
            attributes = {"original_entries": originals, "titlesonly": node.get("titlesonly", False),
                          "processed_entries": [list(entry) for entry in node.get("entries", [])]}
            if self.reference_index is not None:
                attributes["targets"] = [{"target": entry, **self.reference_index.document(self.docname, entry)}
                                         for entry in originals]
        elif isinstance(node, (nodes.table, nodes.tgroup, nodes.colspec, nodes.thead,
                               nodes.tbody, nodes.row, nodes.entry)):
            kind = {nodes.table: "table", nodes.tgroup: "table_group", nodes.colspec: "table_column",
                    nodes.thead: "table_head", nodes.tbody: "table_body", nodes.row: "table_row",
                    nodes.entry: "table_cell"}[type(node)]
            attributes = {key: node[key] for key in ("cols", "colwidth", "stub", "align") if key in node}
            if isinstance(node, nodes.entry):
                attributes.update(rowspan=node.get("morerows", 0) + 1, colspan=node.get("morecols", 0) + 1)
            children = tuple(self.block(child, headings) for child in node.children)
        elif isinstance(node, nodes.math_block):
            kind, text = "math", node.astext()
            attributes = {"format": "latex"}
        elif isinstance(node, (nodes.figure, nodes.compound, nodes.container, nodes.block_quote,
                               nodes.field_list, nodes.field, nodes.field_body)):
            kind = node.tagname
            attributes = {"classes": list(node.get("classes", []))}
            children = tuple(self.block(child, headings) for child in node.children)
        elif isinstance(node, nodes.field_name):
            kind, text = "field_name", node.astext()
        elif isinstance(node, nodes.substitution_definition):
            kind = "substitution_definition"
            text, attributes = node.astext(), {"names": list(node.get("names", [])), "rendered": False}
            inlines = tuple(self.inline(child) for child in node.children)
        elif isinstance(node, nodes.comment):
            kind, text = "comment", node.astext()
            attributes = {"rendered": False}
        elif isinstance(node, nodes.image):
            kind = "image"
            attributes = {key: node[key] for key in
                          ("uri", "original_uri", "alt", "align", "width", "height") if key in node}
            attributes["asset_status"] = "not_checked"
        elif isinstance(node, nodes.target):
            kind = "anchor"
            attributes = {key: node[key] for key in ("ids", "names", "refid", "refuri") if key in node}
        elif isinstance(node, nodes.literal_block):
            kind, text = "literal", node.astext()
        elif isinstance(node, (nodes.bullet_list, nodes.enumerated_list, nodes.list_item, nodes.Admonition)):
            if isinstance(node, nodes.Admonition):
                kind = "admonition"
                attributes["admonition_type"] = "example" if isinstance(node, ExampleBlock) else node.tagname
            elif isinstance(node, nodes.enumerated_list):
                kind = "ordered_list"
                attributes = {key: node[key] for key in ("start", "enumtype", "prefix", "suffix") if key in node}
            else:
                kind = "bullet_list" if isinstance(node, nodes.bullet_list) else "list_item"
            children = tuple(self.block(child, headings) for child in node.children)
        else:
            kind, text = "unsupported", node.astext()
            attributes = {"node_type": node.tagname, "raw_source": node.rawsource}
            self.issue(node, "unsupported_block")
        return Block(block_id, kind, self.location(node), headings, text, attributes, inlines, children)

    def section(self, node, ancestors):
        section_id = self.next_id("s")
        title = next((child.astext() for child in node.children if isinstance(child, nodes.title)), "")
        headings = ancestors + (title,)
        items = tuple(self.section(child, headings) if isinstance(child, nodes.section)
                      else self.block(child, headings)
                      for child in node.children if not isinstance(child, nodes.title))
        return Section(section_id, title, self.location(node), headings,
                       tuple(node.get("ids", [])), tuple(node.get("names", [])), items)

    def normalize(self, tree, parser_diagnostics="", parser_messages=()):
        # A Normalizer can be reused without leaking counters or diagnostics.
        self.sequence, self.issues, self.tab_labels = 0, [], {}
        # This increment supports one source file. Refuse to misattribute nodes
        # from a second file; include/dependency provenance is a later mapping.
        for node in tree.findall():
            actual = getattr(node, "source", None)
            if actual:
                path = Path(actual)
                if path.is_absolute():
                    if self.source_root is None:
                        raise ValueError("source_root is required for absolute node source paths.")
                    path = path.relative_to(self.source_root)
                if path.as_posix() != self.source.source_path:
                    raise ValueError(f"Unexpected node source: {actual}")
        metadata = tuple({"name": node.get("name"), "content": node.get("content")}
                         for node in tree.children if isinstance(node, nodes.meta))
        items = tuple(self.section(child, ()) if isinstance(child, nodes.section)
                      else self.block(child, ())
                      for child in tree.children if not isinstance(child, nodes.meta))
        title = next((item.title for item in items if isinstance(item, Section)), "")
        document_id = digest([self.source.repository_url, self.source.odoo_version,
                              self.source.language, self.source.source_path])
        revision_id = digest([document_id, self.source.commit, self.source.sha256,
                              self.parser_id, SCHEMA_VERSION, NORMALIZER_VERSION])
        return NormalizedDocument(SCHEMA_VERSION, NORMALIZER_VERSION, self.parser_id,
                                  document_id, revision_id, self.source, title,
                                  "partial" if self.issues else "ok", metadata, items,
                                  tuple(self.issues), parser_diagnostics, tuple(parser_messages))
