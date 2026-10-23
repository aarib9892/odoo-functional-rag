"""Behavior checks plus rendering of the exact accepted 30-document snapshot."""

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import unittest

from app.chunking.text import render_block, render_table_row
from app.chunking.walk import iter_blocks

SNAPSHOT_ID = "15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc"
PROJECT = Path(__file__).resolve().parents[2]
SNAPSHOT = PROJECT / "data/normalized/corpus" / SNAPSHOT_ID
BASE = "content/applications/inventory_and_mrp/inventory/"
POLICY = "content/applications/sales/sales/invoicing/invoicing_policy.rst"


def block(kind, text="", attributes=None, children=()):
    return {
        "kind": kind,
        "text": text,
        "attributes": attributes or {},
        "children": list(children),
        "source": {"source_path": "fixture.rst", "line": 7},
    }


def walk(items):
    for item in items:
        if "section_id" in item:
            yield from walk(item["items"])
        else:
            yield item
            yield from walk(item["children"])


class TextBehaviorTests(unittest.TestCase):
    def test_numbered_start_marker_and_nested_content(self):
        nested = block(
            "bullet_list",
            children=[block("list_item", children=[block("paragraph", "Nested item")])],
        )
        numbered = block(
            "ordered_list",
            attributes={
                "enumtype": "arabic",
                "start": 9,
                "prefix": "(",
                "suffix": ")",
            },
            children=[
                block(
                    "list_item",
                    children=[
                        block("paragraph", "First"),
                        nested,
                        block("paragraph", "First continuation"),
                    ],
                ),
                block(
                    "list_item",
                    children=[
                        block("paragraph", "Second"),
                        block("paragraph", "Second continuation"),
                    ],
                ),
            ],
        )
        text = render_block(numbered)
        self.assertTrue(text.startswith("(9) First"))
        self.assertIn("\n    - Nested item", text)
        self.assertIn("\n    First continuation", text)
        self.assertIn("\n(10) Second", text)
        self.assertIn("\n     Second continuation", text)

    def test_prose_vs_literal_math_whitespace(self):
        self.assertEqual(render_block(block("paragraph", "One\n  two")), "One two")
        for kind, attributes in (("literal", {}), ("math", {"format": "latex"})):
            with self.subTest(kind=kind):
                original = "  first\n    second\n\n"
                result = render_block(block(kind, original, attributes))
                self.assertEqual(result.split("\n", 1)[1], original)

    def test_metadata_only_records_stay_unchanged(self):
        for kind in ("anchor", "substitution_definition", "comment"):
            with self.subTest(kind=kind):
                record = block(kind, "Metadata", {"names": ["example"]})
                before = deepcopy(record)
                self.assertEqual(render_block(record), "")
                self.assertEqual(record, before)

    def test_unknown_and_table_layout_nodes_fail(self):
        with self.assertRaisesRegex(ValueError, r"new_directive.*fixture.rst:7"):
            render_block(block("new_directive"))
        with self.assertRaisesRegex(ValueError, "parent table"):
            render_block(block("table_body"))
        row = block(
            "table_row",
            children=[
                block(
                    "table_cell",
                    attributes={"rowspan": 1, "colspan": 1},
                    children=[block("paragraph", "Yes")],
                ),
            ],
        )
        with self.assertRaises(ValueError):
            render_table_row(["Tracked", "Untracked"], row)

    def test_field_containers_absent_from_current_corpus(self):
        field = block(
            "field_list",
            children=[
                block(
                    "field",
                    children=[
                        block("field_name", "Description"),
                        block(
                            "field_body", children=[block("paragraph", "Example text")]
                        ),
                    ],
                )
            ],
        )
        self.assertEqual(render_block(field), "Description:\n\nExample text")

    def test_bad_list_children_and_numbering_fail(self):
        for record in (
            block("bullet_list", children=[block("paragraph", "Misplaced")]),
            block("ordered_list", attributes={"enumtype": "loweralpha"}),
            block("tabs", children=[block("paragraph", "Missing tab label")]),
        ):
            with self.subTest(kind=record["kind"]):
                with self.assertRaises(ValueError):
                    render_block(record)


class CorpusRenderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not SNAPSHOT.is_dir():
            raise FileNotFoundError(
                f"Accepted normalized snapshot not found: {SNAPSHOT}"
            )
        hashes = {
            path.relative_to(SNAPSHOT)
            .as_posix(): hashlib.sha256(path.read_bytes())
            .hexdigest()
            for path in sorted(SNAPSHOT.rglob("*"))
            if path.is_file()
        }
        identity = hashlib.sha256(
            json.dumps(hashes, sort_keys=True).encode()
        ).hexdigest()
        if identity != SNAPSHOT_ID:
            raise ValueError(
                "Normalized snapshot bytes do not match the accepted identity"
            )
        cls.summary = json.loads(
            (SNAPSHOT / "summary.json").read_text(encoding="utf-8")
        )
        cls.documents = {}
        for path in sorted((SNAPSHOT / "documents").rglob("*.json")):
            document = json.loads(path.read_text(encoding="utf-8"))
            source = document["source"]["source_path"]
            if source in cls.documents:
                raise ValueError(f"Duplicate source document: {source}")
            cls.documents[source] = document
        if len(cls.documents) != 30:
            raise ValueError(
                f"Expected 30 normalized documents; found {len(cls.documents)}"
            )

    def blocks(self, path, kind=None):
        return [
            b
            for b in walk(self.documents[path]["items"])
            if kind is None or b["kind"] == kind
        ]

    def test_all_documents_render_deterministically_and_preserve_input(self):
        counts = Counter()
        for path, document in self.documents.items():
            with self.subTest(source=path):
                self.assertEqual(document["schema_version"], "m22-0.2")
                self.assertEqual(document["status"], "ok")
                before = deepcopy(document)
                roots = list(iter_blocks(document["items"]))
                first = [render_block(b) for b in roots]
                self.assertTrue(any(first))
                self.assertEqual(first, [render_block(b) for b in roots])
                self.assertEqual(document, before)
                counts.update(b["kind"] for b in self.blocks(path))
        self.assertEqual(dict(counts), self.summary["block_kinds"])
        self.assertEqual(len(counts), 26)
        print(
            f"\nCorpus check: {len(self.documents)} documents; {len(counts)} block kinds; "
            "deterministic rendering; input unchanged."
        )

    def test_policy_warning_and_partial_delivery_example(self):
        admonitions = self.blocks(POLICY, "admonition")
        warning = next(
            b for b in admonitions if b["attributes"]["admonition_type"] == "warning"
        )
        text = render_block(warning)
        self.assertTrue(text.startswith("WARNING:\nIf a user attempts"))
        self.assertIn("[Image dependency:", text)
        self.assertIn("[Alt text: If Delivered Quantities", text)
        self.assertLess(text.index("system returns"), text.index("[Image dependency:"))
        example = next(b for b in admonitions if b["source"]["line"] == 128)
        for quantity in ("50 heads", "40 heads", "10 heads"):
            self.assertIn(quantity, render_block(example))

    def test_table_header_value_relationships(self):
        table = self.blocks(BASE + "product_management/configure/type.rst", "table")[0]
        rows = render_block(table).splitlines()
        self.assertEqual(len(rows), 13)
        self.assertIn(
            "Inventory operation: Show on-hand quantity; Tracked: Yes; Untracked: No",
            rows,
        )
        self.assertIn(
            "Inventory operation: Show forecasted quantity; Tracked: Yes; Untracked: No",
            rows,
        )
        self.assertIn(
            "Inventory operation: Create transfer; Tracked: Yes; Untracked: Yes", rows
        )

    def test_both_tab_groups_include_hidden_panels(self):
        count = 0
        for path in (
            BASE + "shipping_receiving/reservation_methods.rst",
            BASE + "warehouses_storage/reporting/moves_history.rst",
        ):
            for group in self.blocks(path, "tabs"):
                text = render_block(group)
                positions = []
                for tab in group["children"]:
                    label = f"[Tab: {tab['attributes']['label']}]"
                    self.assertEqual(text.count(label), 1)
                    positions.append(text.index(label))
                    count += 1
                self.assertEqual(positions, sorted(positions))
        self.assertEqual(count, 6)
        reservation = self.blocks(
            BASE + "shipping_receiving/reservation_methods.rst", "tabs"
        )[0]
        text = render_block(reservation)
        self.assertIn(
            "only when a sales order is confirmed, and if stock is already available.",
            text,
        )
        self.assertIn("quantity must be reserved manually", text)
        self.assertIn("maximum number of days before a scheduled delivery date", text)

    def test_cards_and_original_navigation_targets(self):
        path = BASE + "shipping_receiving/daily_operations.rst"
        cards = self.blocks(path, "card")
        self.assertEqual(len(cards), 7)
        for card in cards:
            text = render_block(card)
            self.assertIn(f"[Card: {card['attributes']['label']}]", text)
            self.assertIn(card["attributes"]["target"], text)
            self.assertIn("reference state: not_in_corpus", text)
        navigation = self.blocks(path, "navigation")[0]
        text = render_block(navigation)
        self.assertEqual(len(text.splitlines()), 10)
        self.assertEqual(text.count("reference state: not_in_corpus"), 6)
        self.assertEqual(text.count("reference state: resolved"), 3)
        for target in navigation["attributes"]["original_entries"]:
            self.assertIn(f"- {target} [reference state:", text)

    def test_figures_captions_titles_and_formula(self):
        figures = [b for path in self.documents for b in self.blocks(path, "figure")]
        self.assertEqual(len(figures), 9)
        for figure in figures:
            text = render_block(figure)
            self.assertTrue(text.startswith("[Figure]\n"))
            for child in figure["children"]:
                if child["kind"] == "caption":
                    self.assertIn("[Caption]\n" + " ".join(child["text"].split()), text)
                elif child["kind"] == "image":
                    self.assertIn(child["attributes"]["uri"], text)
        path = BASE + "shipping_receiving/reservation_methods/at_confirmation.rst"
        title = self.blocks(path, "title")[0]
        self.assertEqual(render_block(title), "[Title: Forecasted Report]")
        path = BASE + "shipping_receiving/setup_configuration/new_delivery_method.rst"
        formula = self.blocks(path, "math")[0]
        self.assertEqual(render_block(formula), "[Math: latex]\n" + formula["text"])

    def test_ambiguous_table_layouts_fail_visibly(self):
        original = self.blocks(BASE + "product_management/configure/type.rst", "table")[
            0
        ]
        for case in (
            "multiple_headers",
            "merged_cell",
            "missing_cell",
            "duplicate_body",
        ):
            with self.subTest(case=case):
                table = deepcopy(original)
                group = table["children"][0]
                head = next(b for b in group["children"] if b["kind"] == "table_head")
                body = next(b for b in group["children"] if b["kind"] == "table_body")
                if case == "multiple_headers":
                    head["children"].append(deepcopy(head["children"][0]))
                elif case == "merged_cell":
                    body["children"][0]["children"][0]["attributes"]["rowspan"] = 2
                elif case == "missing_cell":
                    body["children"][0]["children"].pop()
                else:
                    group["children"].append(deepcopy(body))
                with self.assertRaises(ValueError):
                    render_block(table)


if __name__ == "__main__":
    unittest.main()
