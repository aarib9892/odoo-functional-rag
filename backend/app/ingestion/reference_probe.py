from io import StringIO
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.console import nocolor

from app.ingestion.rst_directives import (
    ExampleBlock,
    ExampleDirective,
    icon_role,
)

POLICY = Path("content/applications/sales/sales/invoicing/invoicing_policy.rst")
QUOTATIONS = Path(
    "content/applications/sales/sales/sales_quotations/create_quotations.rst"
)
BACKORDERS = Path(
    "content/applications/inventory_and_mrp/inventory/"
    "shipping_receiving/setup_configuration/multipack.rst"
)
SOURCES = (POLICY, QUOTATIONS, BACKORDERS)


def main() -> None:
    repository = Path("../sources/odoo-documentation").resolve()
    main_doc = POLICY.with_suffix("").as_posix()
    diagnostics = StringIO()
    resolved = {}
    nocolor()

    def capture_resolved(app, tree, docname):
        if docname == main_doc:
            resolved[docname] = tree.deepcopy()

    with TemporaryDirectory(prefix="m2-references-") as directory:
        work = Path(directory)
        source_dir = work / "source"

        for relative in SOURCES:
            destination = source_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            copyfile(repository / relative, destination)

        app = Sphinx(
            srcdir=str(source_dir),
            confdir=None,
            outdir=str(work / "build"),
            doctreedir=str(work / "doctrees"),
            buildername="dummy",
            confoverrides={
                "project": "M2 reference probe",
                "root_doc": main_doc,
                "extensions": [],
                "nitpicky": True,
                "keep_warnings": True,
            },
            status=StringIO(),
            warning=diagnostics,
            freshenv=True,
        )
        app.add_node(ExampleBlock)
        app.add_directive("example", ExampleDirective)
        app.add_role("icon", icon_role)
        app.connect("doctree-resolved", capture_resolved)
        app.env.settings["file_insertion_enabled"] = False
        app.env.settings["raw_enabled"] = False
        app.build(force_all=True)

        trees = [
            app.env.get_doctree(path.with_suffix("").as_posix()) for path in SOURCES
        ]
        errors = [
            message
            for tree in trees
            for message in tree.findall(nodes.system_message)
            if message["level"] >= 3
        ]
        icons = [
            node
            for tree in trees
            for node in tree.findall(nodes.inline)
            if "odoo-icon" in node.get("classes", [])
        ]
        examples = list(trees[0].findall(ExampleBlock))
        resolved_tree = resolved[main_doc]
        references = list(resolved_tree.findall(nodes.reference))
        labels = app.env.get_domain("std").labels

        print(f"Staged documents: {len(SOURCES)}")
        print(f"Parser errors across all staged documents: {len(errors)}")
        print(f"Example blocks on invoicing-policy page: {len(examples)}")
        print(f"Icon nodes across staged documents: {len(icons)}")

        # Verify actual resolved nodes AND each label's source document.
        checks = (
            ("sales/create_quotations/create-quotation", QUOTATIONS, 2),
            ("inventory/multipack/backorders", BACKORDERS, 1),
        )
        for label, expected_path, expected_count in checks:
            target_doc, target_id, title = labels[label]
            assert target_doc == expected_path.with_suffix("").as_posix()
            uri = app.builder.get_relative_uri(main_doc, target_doc)
            target_uri = f"{uri}#{target_id}"
            count = sum(node.get("refuri") == target_uri for node in references)
            print(f"Resolved references to {label}: {count}")
            assert count == expected_count, f"Reference check failed: {label}"

    headers = [
        line
        for line in diagnostics.getvalue().splitlines()
        if ": ERROR:" in line or ": WARNING:" in line
    ]
    error_headers = [line for line in headers if ": ERROR:" in line]
    warning_headers = [line for line in headers if ": WARNING:" in line]

    output = Path("../data/experiments/m2/reference_probe.diagnostics.txt")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(diagnostics.getvalue(), encoding="utf-8")

    print(f"Remaining warning headers: {len(warning_headers)}")
    print(f"Full diagnostics saved: {output.resolve()}")
    print("\nFirst six diagnostic headers:")
    for line in headers[:6]:
        print(line)

    assert not errors and not error_headers, "Parsing still has errors."
    assert len(icons) == 10, "Expected ten preserved icon nodes."
    assert len(examples) == 2, "Expected the two invoicing examples."
    assert [block.line for block in examples] == [75, 128]
    assert all(
        quantity in examples[1].astext()
        for quantity in ("50 heads", "40 heads", "10 heads")
    )
    print("\nReference checks and example-content checks passed.")


if __name__ == "__main__":
    main()
