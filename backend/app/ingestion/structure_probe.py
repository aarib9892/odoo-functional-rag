from collections import Counter
from importlib.metadata import version
from io import StringIO
from pathlib import Path
from shutil import copyfile
from tempfile import TemporaryDirectory

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util.console import nocolor
from sphinx_tabs.tabs import SphinxTabsPanel, SphinxTabsTab

from app.ingestion.rst_directives import (
    ExampleBlock,
    ExampleDirective,
    icon_role,
)

BASE = "content/applications/inventory_and_mrp/inventory/"
SOURCES = {
    "table": Path(BASE + "product_management/configure/type.rst"),
    "tabs": Path(BASE + "shipping_receiving/reservation_methods.rst"),
    "substitutions": Path(
        BASE + "shipping_receiving/daily_operations/receipts_delivery_one_step.rst"
    ),
    "math": Path(
        BASE + "shipping_receiving/setup_configuration/new_delivery_method.rst"
    ),
}


def clean(text):
    return " ".join(text.split())


def inside_substitution_definition(node):
    parent = node.parent
    while parent is not None:
        if isinstance(parent, nodes.substitution_definition):
            return True
        parent = parent.parent
    return False


def main() -> None:
    print(
        "Versions:",
        f"Docutils {version('docutils')};",
        f"Sphinx {version('sphinx')};",
        f"sphinx-tabs {version('sphinx-tabs')}",
    )
    repository = Path("../sources/odoo-documentation").resolve()
    diagnostics = StringIO()
    nocolor()

    with TemporaryDirectory(prefix="m2-structures-") as directory:
        work = Path(directory)
        source_dir = work / "source"

        for relative in SOURCES.values():
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
                "project": "M2 structure probe",
                "root_doc": SOURCES["table"].with_suffix("").as_posix(),
                "extensions": ["sphinx_tabs.tabs"],
                "sphinx_tabs_valid_builders": ["dummy"],
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
        app.env.settings["file_insertion_enabled"] = False
        app.env.settings["raw_enabled"] = False
        app.build(force_all=True)

        trees = {
            name: app.env.get_doctree(path.with_suffix("").as_posix())
            for name, path in SOURCES.items()
        }

    errors = [
        message
        for tree in trees.values()
        for message in tree.findall(nodes.system_message)
        if message["level"] >= 3
    ]
    diagnostic_headers = [
        line
        for line in diagnostics.getvalue().splitlines()
        if ": WARNING:" in line or ": ERROR:" in line
    ]
    output = Path("../data/experiments/m2")
    output.mkdir(parents=True, exist_ok=True)
    (output / "structure_probe.diagnostics.txt").write_text(
        diagnostics.getvalue(), encoding="utf-8"
    )
    print(f"Staged documents: {len(trees)}")
    print(f"Parser errors across all staged documents: {len(errors)}")
    assert not errors, "A staged document still has parser errors."
    assert not any(": ERROR:" in line for line in diagnostic_headers)

    # Check the column meanings and selected row values together.
    table = next(trees["table"].findall(nodes.table))
    head = next(table.findall(nodes.thead))
    body = next(table.findall(nodes.tbody))
    headers = [clean(cell.astext()) for cell in head.findall(nodes.entry)]
    rows = {}
    for row in body.findall(nodes.row):
        cells = [clean(cell.astext()) for cell in row.children]
        rows[cells[0]] = cells[1:]
    assert headers == ["Inventory operation", "Tracked", "Untracked"]
    assert next(table.findall(nodes.colspec)).get("stub") == 1
    assert rows["Show on-hand quantity"] == ["Yes", "No"]
    assert rows["Show forecasted quantity"] == ["Yes", "No"]
    assert rows["Create transfer"] == ["Yes", "Yes"]
    print("Table headers:", " | ".join(headers))
    print("On-hand row:", rows["Show on-hand quantity"])
    print("Forecast row:", rows["Show forecasted quantity"])
    print("Transfer row:", rows["Create transfer"])
    print("Table header/value checks passed.")

    # Pair each tab label with its own panel, including inactive panels.
    labels = {node["ids"][0]: node for node in trees["tabs"].findall(SphinxTabsTab)}
    tabs = {}
    panels = list(trees["tabs"].findall(SphinxTabsPanel))
    for panel in panels:
        label = labels[panel["aria-labelledby"]]
        assert label["aria-controls"] in panel["ids"]
        tabs[clean(label.astext())] = clean(panel.astext())
    assert list(tabs) == ["At Confirmation", "Manually", "Before scheduled date"]
    assert "only when a sales order is confirmed" in tabs["At Confirmation"]
    assert "and if stock is already available" in tabs["At Confirmation"]
    assert "checked manually" in tabs["Manually"]
    assert "reserved manually" in tabs["Manually"]
    assert "before a scheduled delivery date" in tabs["Before scheduled date"]
    print("Tab labels:", " | ".join(tabs))
    print("All three tab label/content checks passed.")

    # Count expanded abbreviations in body content, not their definitions.
    abbreviations = [
        node
        for node in trees["substitutions"].findall(nodes.abbreviation)
        if not inside_substitution_definition(node)
    ]
    meanings = {(node.astext(), node.get("explanation")) for node in abbreviations}
    assert meanings == {
        ("PO", "Purchase Order"),
        ("SO", "Sales Order"),
        ("RfQ", "Request for Quotation"),
    }
    counts = Counter(node.astext() for node in abbreviations)
    assert counts == {"PO": 4, "SO": 4, "RfQ": 3}
    assert not list(trees["substitutions"].findall(nodes.substitution_reference))
    print("Expanded body abbreviations:", dict(sorted(counts.items())))
    print("Substitution expansion checks passed.")

    # Retain the formula verbatim and its association with the worked example.
    math_blocks = list(trees["math"].findall(nodes.math_block))
    assert len(math_blocks) == 1
    formula = math_blocks[0].astext().strip()
    assert formula == (
        r"Total = Rule's~Delivery~Cost + "
        r"(Margin~on~rate \times Rule's~Delivery~Cost) + Additional~margin"
    )
    assert math_blocks[0].line == 158
    worked = [
        block
        for block in trees["math"].findall(ExampleBlock)
        if "$31" in block.astext() and "$64" in block.astext()
    ]
    assert len(worked) == 1
    assert worked[0].parent is math_blocks[0].parent
    print("Math blocks: 1; formula and worked-example association preserved.")

    print(f"Remaining diagnostic headers: {len(diagnostic_headers)}")
    print(
        "Full diagnostics saved:",
        (output / "structure_probe.diagnostics.txt").resolve(),
    )
    print("All four structure checks passed.")


if __name__ == "__main__":
    main()
