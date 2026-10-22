"""M2.2 first normalized document: the pinned invoicing-policy fixture."""

from collections import Counter
import hashlib
from importlib.metadata import version
from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.console import nocolor

from app.ingestion.normalized_models import Block, Section, SourceIdentity
from app.ingestion.normalization import Normalizer
from app.ingestion.rst_directives import ExampleBlock, ExampleDirective


PATH = "content/applications/sales/sales/invoicing/invoicing_policy.rst"


def walk(items):
    for item in items:
        yield item
        yield from walk(item.items if isinstance(item, Section) else item.children)


def walk_inlines(inlines):
    for inline in inlines:
        yield inline
        yield from walk_inlines(inline.children)


def main():
    repository = Path("../sources/odoo-documentation").resolve()
    manifest = json.loads(Path("../data/manifests/odoo19-corpus.json").read_text(encoding="utf-8"))
    record = next(item for item in manifest["inventory"]["files"] if item["source_path"] == PATH)
    data = (repository / PATH).read_bytes()
    if len(data) != record["size_bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
        raise ValueError("The source file does not match its manifest record.")
    identity = SourceIdentity(**manifest["inventory"]["source"], source_path=PATH,
                              sha256=record["sha256"], application=record["application"])
    diagnostics = StringIO()
    nocolor()
    with TemporaryDirectory(prefix="m22-normalize-") as directory:
        work = Path(directory)
        source_dir = work / "source"
        staged = source_dir / PATH
        staged.parent.mkdir(parents=True)
        staged.write_bytes(data)
        app = Sphinx(
            srcdir=str(source_dir), confdir=None,
            outdir=str(work / "build"), doctreedir=str(work / "doctrees"),
            buildername="dummy", confoverrides={
                "project": "M2.2 first document", "root_doc": PATH[:-4],
                "extensions": [], "nitpicky": True, "keep_warnings": True,
                "smartquotes": False,
            }, status=StringIO(), warning=diagnostics, freshenv=True,
        )
        app.add_node(ExampleBlock)
        app.add_directive("example", ExampleDirective)
        app.env.settings["file_insertion_enabled"] = False
        app.env.settings["raw_enabled"] = False
        app.build(force_all=True)
        tree = app.env.get_doctree(PATH[:-4])
        parse_errors = [message for message in tree.findall(nodes.system_message) if message["level"] >= 3]
        if parse_errors or ": ERROR:" in diagnostics.getvalue() or ": CRITICAL:" in diagnostics.getvalue():
            raise ValueError("The source still has parser errors.")
        # Keep logs, but remove the variable temporary-source prefix from JSON.
        stable_logs = diagnostics.getvalue().replace(str(source_dir) + "/", "")
        parser_id = f"sphinx-{version('sphinx')}/docutils-{version('docutils')}/example-v1/smartquotes-off"
        normalizer = Normalizer(identity, parser_id, source_root=source_dir)
        document = normalizer.normalize(tree, stable_logs)
        serialized = document.to_json()
        assert serialized == normalizer.normalize(tree, stable_logs).to_json()
        assert str(work) not in serialized

    sections = [item for item in walk(document.items) if isinstance(item, Section)]
    blocks = [item for item in walk(document.items) if isinstance(item, Block)]
    inlines = [inline for block in blocks for inline in walk_inlines(block.inlines)]
    examples = [block for block in blocks if block.attributes.get("admonition_type") == "example"]
    warning = next(block for block in blocks if block.attributes.get("admonition_type") == "warning")
    assert document.status == "ok" and not document.diagnostics
    assert len(sections) == 6
    assert [block.source.line for block in examples] == [75, 128]
    example_text = " ".join(child.text for child in examples[1].children)
    assert all(value in example_text for value in ("50 heads", "40 heads", "10 heads"))
    assert warning.heading_path[-1] == "Invoice delivered quantity workflow"
    assert warning.source.line == 120 and warning.source.line_origin == "node"
    assert [child.kind for child in warning.children] == ["paragraph", "image"]
    assert warning.children[1].source.line == 124
    assert sum(item.kind == "gui_label" for item in inlines) == 17
    assert sum(item.kind == "menu_path" for item in inlines) == 2
    references = [item for item in inlines if item.kind == "reference"]
    assert len(references) == 9
    assert all(item.attributes["resolution"] == "not_attempted" for item in references)
    assert sum(block.kind == "image" for block in blocks) == 4
    output = Path("../data/normalized/examples/invoicing_policy.json").resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(serialized, encoding="utf-8")
    print("Document:", document.title)
    print("Normalization status:", document.status)
    print("Sections:", len(sections))
    print("Examples: 2; source lines: [75, 128]")
    print("Warning retains its paragraph, image and heading ancestry.")
    print("GUI labels: 17; menu paths: 2; reference targets: 9; images: 4")
    print("Reference resolution: not attempted in this first normalizer.")
    print("Unsupported-node diagnostics:", len(document.diagnostics))
    print("Source-line origins:", dict(sorted(Counter(block.source.line_origin for block in blocks).items())))
    print("Repeated normalization produced identical JSON.")
    print("Saved:", output)


if __name__ == "__main__":
    main()
