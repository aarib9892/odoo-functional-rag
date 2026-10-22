from io import StringIO
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.util.console import nocolor

from app.ingestion.rst_directives import ExampleBlock, ExampleDirective


def main() -> None:
    repository = Path("../sources/odoo-documentation").resolve()
    relative = Path("content/applications/sales/sales/invoicing/invoicing_policy.rst")
    docname = relative.with_suffix("").as_posix()

    diagnostics = StringIO()
    nocolor()

    with TemporaryDirectory(prefix="m2-sphinx-") as directory:
        work = Path(directory)
        source_dir = work / "source"
        destination = source_dir / relative

        destination.parent.mkdir(parents=True)
        copyfile(repository / relative, destination)

        app = Sphinx(
            srcdir=str(source_dir),
            confdir=None,
            outdir=str(work / "build"),
            doctreedir=str(work / "doctrees"),
            buildername="dummy",
            confoverrides={
                "project": "M2 parser comparison",
                "root_doc": docname,
                "extensions": [],
                "nitpicky": True,
                "keep_warnings": True,
            },
            status=StringIO(),
            warning=diagnostics,
            freshenv=True,
        )

        # Register the example block before parsing the document.
        app.add_node(ExampleBlock)
        app.add_directive("example", ExampleDirective)

        app.env.settings["file_insertion_enabled"] = False
        app.env.settings["raw_enabled"] = False

        app.build(force_all=True)
        tree = app.env.get_doctree(docname)

    errors = [
        message
        for message in tree.findall(nodes.system_message)
        if message["level"] >= 3
    ]
    inlines = list(tree.findall(nodes.inline))

    gui_labels = sum("guilabel" in node.get("classes", []) for node in inlines)
    menu_selections = sum(
        "menuselection" in node.get("classes", []) for node in inlines
    )

    print(f"Titles: {len(list(tree.findall(nodes.title)))}")
    print(f"Important blocks: {len(list(tree.findall(nodes.important)))}")
    print(f"Warning blocks: {len(list(tree.findall(nodes.warning)))}")
    print(f"Parser errors: {len(errors)}")
    print(f"GUI labels: {gui_labels}")
    print(f"Menu selections: {menu_selections}")
    print(
        "Pending references in stored tree:",
        len(list(tree.findall(addnodes.pending_xref))),
    )

    print("\nDiagnostic headers:")
    for line in diagnostics.getvalue().splitlines():
        if ": ERROR:" in line or ": WARNING:" in line:
            print(line)

    examples = list(tree.findall(ExampleBlock))

    print(f"\nExample blocks: {len(examples)}")
    print("Example source lines:", [block.line for block in examples])

    # These checks target the pinned source inspected during M1.2.
    assert not errors, "The probe still contains parser errors."
    assert len(examples) == 2, "Expected two example blocks."
    assert [block.line for block in examples] == [75, 128]

    partial_delivery_example = examples[1].astext()
    assert all(
        quantity in partial_delivery_example
        for quantity in ("50 heads", "40 heads", "10 heads")
    ), "The partial-delivery example lost expected quantities."

    print("Partial-delivery example quantities preserved.")


if __name__ == "__main__":
    main()
