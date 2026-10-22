"""Preservation checks against the human-reviewed, pinned M1.2 fixtures."""

from collections import Counter

from app.ingestion.normalized_models import Section


def walk(items):
    for item in items:
        yield item
        yield from walk(item.items if isinstance(item, Section) else item.children)


def inlines(items):
    for item in items:
        yield item
        yield from inlines(item.children)


BASE = "content/applications/inventory_and_mrp/inventory/"
POLICY = "content/applications/sales/sales/invoicing/invoicing_policy.rst"


def blocks(document, kind=None):
    return [item for item in walk(document.items) if hasattr(item, "kind")
            and (kind is None or item.kind == kind)]


def text(block):
    value = block.text or " ".join(text(child) for child in block.children)
    return " ".join(value.split())


def require(condition, message):
    if not condition:
        raise ValueError("Fixture preservation check failed: " + message)


def check_documents(documents):
    policy = documents[POLICY]
    examples = [b for b in blocks(policy, "admonition") if b.attributes["admonition_type"] == "example"]
    require([b.source.line for b in examples] == [75, 128], "example locations")
    require(all(value in text(examples[1]) for value in ("50 heads", "40 heads", "10 heads")), "partial-delivery quantities")
    warning = next(b for b in blocks(policy, "admonition") if b.attributes["admonition_type"] == "warning")
    require(warning.heading_path[-1] == "Invoice delivered quantity workflow", "warning ancestry")
    require([b.kind for b in warning.children] == ["paragraph", "image"], "warning child structure")
    require([b.source.line for b in warning.children] == [121, 124], "warning child locations")
    refs = [i for b in blocks(policy) for i in inlines(b.inlines) if i.kind == "reference"]
    quotation = [i for i in refs if i.attributes.get("target") == "sales/create_quotations/create-quotation"]
    backorder = [i for i in refs if i.attributes.get("target") == "inventory/multipack/backorders"]
    require(len(quotation) == 2 and len(backorder) == 1, "original reference targets")
    require(all(i.attributes["resolution"] == "resolved" for i in quotation + backorder), "native reference resolution")
    require(all(i.attributes["destination_path"].endswith("create_quotations.rst") for i in quotation), "quotation destination")
    require(backorder[0].attributes["destination_path"].endswith("multipack.rst"), "backorder destination")
    require(any(i.text == "Down payments" and i.attributes.get("target") == "down_payment" for i in refs), "implicit reference display title")

    product = documents[BASE + "product_management/configure/type.rst"]
    table = blocks(product, "table")[0]
    descendants = list(walk(table.children))
    head = next(b for b in descendants if b.kind == "table_head")
    body = next(b for b in descendants if b.kind == "table_body")
    require([text(cell) for cell in head.children[0].children] == ["Inventory operation", "Tracked", "Untracked"], "table headers")
    require(next(b for b in descendants if b.kind == "table_column").attributes["stub"] == 1, "table row-header column")
    rows = {text(row.children[0]): [text(cell) for cell in row.children[1:]] for row in body.children}
    require(rows["Show on-hand quantity"] == ["Yes", "No"], "on-hand column values")
    require(rows["Show forecasted quantity"] == ["Yes", "No"], "forecast column values")
    require(rows["Create transfer"] == ["Yes", "Yes"], "transfer column values")

    reservation = documents[BASE + "shipping_receiving/reservation_methods.rst"]
    tabs = blocks(reservation, "tabs")[0].children
    require([b.attributes["label"] for b in tabs] == ["At Confirmation", "Manually", "Before scheduled date"], "tab labels")
    require("only when a sales order is confirmed" in text(tabs[0]) and "stock is already available" in text(tabs[0]), "confirmation tab conditions")
    require("checked manually" in text(tabs[1]) and "reserved manually" in text(tabs[1]), "manual tab conditions")
    require("before a scheduled delivery date" in text(tabs[2]), "scheduled tab conditions")
    source_lines = [b.source.line for b in tabs]
    require(source_lines == [20, 25, 30] and all(b.source.line_origin == "node" for b in tabs), "tab directive provenance")

    flow = documents[BASE + "shipping_receiving/daily_operations.rst"]
    cards = blocks(flow, "card")
    require([b.attributes["label"] for b in cards] == ["Putaway rules", "Storage categories", "Consignment", "Dropshipping", "Picking methods", "Removal strategies", "Routes"], "card labels/order")
    require(all(b.attributes["resolution"] == "not_in_corpus" and b.attributes["target_existence"] == "not_checked" for b in cards), "unverified card target status")
    require("piece, batch, cluster, or wave" in text(cards[4]), "card body")
    toc = blocks(flow, "navigation")[0]
    require(len(toc.attributes["original_entries"]) == 9 and len(toc.attributes["processed_entries"]) == 3, "original and staged navigation")

    one_step = documents[BASE + "shipping_receiving/daily_operations/receipts_delivery_one_step.rst"]
    abbr = [i for b in blocks(one_step, "paragraph") for i in inlines(b.inlines) if i.kind == "abbreviation"]
    require(Counter(i.text for i in abbr) == {"PO": 4, "SO": 4, "RfQ": 3}, "abbreviation expansion counts")
    require({(i.text, i.attributes.get("explanation")) for i in abbr} == {("PO", "Purchase Order"), ("SO", "Sales Order"), ("RfQ", "Request for Quotation")}, "abbreviation meanings")
    shipping = documents[BASE + "shipping_receiving/setup_configuration/new_delivery_method.rst"]
    formula = blocks(shipping, "math")[0]
    require(formula.text.strip() == r"Total = Rule's~Delivery~Cost + (Margin~on~rate \times Rule's~Delivery~Cost) + Additional~margin", "formula text")
    worked = next(b for b in blocks(shipping, "admonition") if "$31" in text(b) and "$64" in text(b))
    require(worked.heading_path == formula.heading_path and formula.source.line == 158, "formula/example association")
