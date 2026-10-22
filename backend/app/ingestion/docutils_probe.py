"""Compare controlled Docutils parsing with the recorded Sphinx fixtures."""

from collections import Counter
from importlib.metadata import version
from io import StringIO
from pathlib import Path

from docutils import nodes
from docutils.core import publish_doctree

from app.ingestion.docutils_adapter import (
    CardBlock,
    CardsBlock,
    TabBlock,
    ToctreeBlock,
    register_probe_adapter,
)
from app.ingestion.rst_directives import ExampleBlock

INVENTORY = "content/applications/inventory_and_mrp/inventory/"
SOURCES = {
    "policy": "content/applications/sales/sales/invoicing/invoicing_policy.rst",
    "table": INVENTORY + "product_management/configure/type.rst",
    "tabs": INVENTORY + "shipping_receiving/reservation_methods.rst",
    "substitutions": INVENTORY
    + "shipping_receiving/daily_operations/receipts_delivery_one_step.rst",
    "math": INVENTORY
    + "shipping_receiving/setup_configuration/new_delivery_method.rst",
    "navigation": INVENTORY + "shipping_receiving/daily_operations.rst",
}


def clean(text):
    return " ".join(text.split())


def in_definition(node):
    parent = node.parent
    while parent is not None:
        if isinstance(parent, nodes.substitution_definition):
            return True
        parent = parent.parent
    return False


def main():
    print(f"Docutils version: {version('docutils')}")
    repository = Path("../sources/odoo-documentation").resolve()
    output = Path("../data/experiments/m2/docutils_probe").resolve()
    output.mkdir(parents=True, exist_ok=True)
    register_probe_adapter()
    trees = {}
    diagnostics = StringIO()
    for name, relative in SOURCES.items():
        path = repository / relative
        tree = publish_doctree(
            path.read_text(encoding="utf-8"),
            source_path=str(path),
            settings_overrides={
                "warning_stream": diagnostics,
                "report_level": 2,
                "halt_level": 6,
                "file_insertion_enabled": False,
                "raw_enabled": False,
                "doctitle_xform": False,
                "sectsubtitle_xform": False,
            },
        )
        trees[name] = tree
        (output / f"{name}.doctree.txt").write_text(tree.pformat(), encoding="utf-8")
    (output / "diagnostics.txt").write_text(diagnostics.getvalue(), encoding="utf-8")
    errors = [
        message
        for tree in trees.values()
        for message in tree.findall(nodes.system_message)
        if message["level"] >= 3
    ]
    print(f"Documents parsed: {len(trees)}")
    print(f"Parser errors: {len(errors)}")
    assert not errors, f"Inspect diagnostics at {output}"

    policy = trees["policy"]
    examples = list(policy.findall(ExampleBlock))
    assert [block.line for block in examples] == [75, 128]
    assert all(
        value in clean(examples[1].astext())
        for value in (
            "50 heads",
            "40 heads",
            "10 heads",
        )
    )
    inline = list(policy.findall(nodes.inline))
    counts = Counter(node.get("rst_role") for node in inline)
    assert counts["guilabel"] == 17
    assert counts["menuselection"] == 2
    references = [node for node in inline if node.get("rst_role") in {"ref", "doc"}]
    assert len(references) == 9
    targets = Counter(node["target"] for node in references)
    assert targets["sales/create_quotations/create-quotation"] == 2
    assert targets["inventory/multipack/backorders"] == 1
    assert all(node.source and node.line for node in references)
    print(
        "Policy: 2 examples; 17 GUI labels; 2 menu paths; 9 reference targets retained."
    )

    table = next(trees["table"].findall(nodes.table))
    head, body = next(table.findall(nodes.thead)), next(table.findall(nodes.tbody))
    headers = [clean(cell.astext()) for cell in head.findall(nodes.entry)]
    rows = {}
    for row in body.findall(nodes.row):
        values = [clean(cell.astext()) for cell in row.children]
        rows[values[0]] = values[1:]
    assert headers == ["Inventory operation", "Tracked", "Untracked"]
    assert next(table.findall(nodes.colspec)).get("stub") == 1
    assert rows["Show on-hand quantity"] == ["Yes", "No"]
    assert rows["Show forecasted quantity"] == ["Yes", "No"]
    assert rows["Create transfer"] == ["Yes", "Yes"]
    print("Table header/value checks passed.")

    tabs = {
        node["label"]: clean(node.astext()) for node in trees["tabs"].findall(TabBlock)
    }
    assert list(tabs) == ["At Confirmation", "Manually", "Before scheduled date"]
    assert "only when a sales order is confirmed" in tabs["At Confirmation"]
    assert "and if stock is already available" in tabs["At Confirmation"]
    assert "checked manually" in tabs["Manually"]
    assert "reserved manually" in tabs["Manually"]
    assert "before a scheduled delivery date" in tabs["Before scheduled date"]
    print("All three tab label/content checks passed.")

    abbreviations = [
        node
        for node in trees["substitutions"].findall(nodes.abbreviation)
        if not in_definition(node)
    ]
    assert Counter(node.astext() for node in abbreviations) == {
        "PO": 4,
        "SO": 4,
        "RfQ": 3,
    }
    assert {(node.astext(), node.get("explanation")) for node in abbreviations} == {
        ("PO", "Purchase Order"),
        ("SO", "Sales Order"),
        ("RfQ", "Request for Quotation"),
    }
    assert not list(trees["substitutions"].findall(nodes.substitution_reference))
    print("Substitution expansion checks passed.")

    math = list(trees["math"].findall(nodes.math_block))
    assert len(math) == 1 and math[0].line == 158
    assert math[0].astext().strip() == (
        r"Total = Rule's~Delivery~Cost + "
        r"(Margin~on~rate \times Rule's~Delivery~Cost) + Additional~margin"
    )
    worked = [
        block
        for block in trees["math"].findall(ExampleBlock)
        if "$31" in block.astext() and "$64" in block.astext()
    ]
    assert len(worked) == 1 and worked[0].parent is math[0].parent
    print("Formula/worked-example checks passed.")

    cards = list(trees["navigation"].findall(CardBlock))
    assert len(list(trees["navigation"].findall(CardsBlock))) == 3
    assert [(node["label"], node["target"]) for node in cards] == [
        ("Putaway rules", "daily_operations/putaway"),
        ("Storage categories", "daily_operations/storage_category"),
        ("Consignment", "daily_operations/owned_stock"),
        ("Dropshipping", "daily_operations/dropshipping"),
        ("Picking methods", "picking_methods"),
        ("Removal strategies", "removal_strategies"),
        ("Routes", "daily_operations/use_routes"),
    ]
    assert "piece, batch, cluster, or wave" in clean(cards[4].astext())
    assert all(node.source and node.line and node.children for node in cards)
    toc = list(trees["navigation"].findall(ToctreeBlock))
    assert len(toc) == 1 and toc[0]["titlesonly"]
    assert toc[0]["entries"] == [
        "daily_operations/" + name
        for name in (
            "use_routes",
            "receipts_delivery_one_step",
            "receipts_delivery_two_steps",
            "receipts_three_steps",
            "delivery_three_steps",
            "putaway",
            "storage_category",
            "owned_stock",
            "dropshipping",
        )
    ]
    print("Navigation: 7 card labels/targets/bodies and 9 toctree entries retained.")
    print("Reference resolution: not implemented by this adapter.")
    print("Diagnostics and readable trees saved:", output)
    print("All controlled-Docutils fixture checks passed.")


if __name__ == "__main__":
    main()
