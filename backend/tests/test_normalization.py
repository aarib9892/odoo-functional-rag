import unittest
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from docutils import nodes
from docutils.utils import new_document

from app.ingestion.normalized_models import SourceIdentity
from app.ingestion.normalization import Normalizer
from app.ingestion.normalize_corpus import load_inputs, write_snapshot
from app.ingestion.reference_index import ReferenceIndex
from app.ingestion.sphinx_reader import parse_diagnostics


class UnknownDirective(nodes.General, nodes.Element):
    pass


class NormalizationTests(unittest.TestCase):
    def normalizer(self, commit="commit-a"):
        return Normalizer(SourceIdentity("https://example.test/docs.git", "19.0", "en",
                                        commit, "content/example.rst", "source-hash", "sales"), "parser-v1")

    def test_unknown_directive_is_visible_with_fallback_text(self):
        tree = new_document("content/example.rst")
        unknown = UnknownDirective()
        unknown += nodes.paragraph("", "Answer-critical directive contents")
        tree += unknown
        document = self.normalizer().normalize(tree)
        self.assertEqual(document.status, "partial")
        self.assertEqual(document.items[0].kind, "unsupported")
        self.assertIn("Answer-critical", document.items[0].text)
        self.assertEqual(document.diagnostics[0].code, "unsupported_block")

    def test_inherited_line_is_not_marked_as_a_node_line(self):
        tree = new_document("content/example.rst")
        paragraph = nodes.paragraph("", "Text without a child line")
        paragraph.line = 12
        tree += paragraph
        document = self.normalizer().normalize(tree)
        block = document.items[0]
        self.assertEqual(block.source.line_origin, "node")
        self.assertEqual(block.inlines[0].source.line, 12)
        self.assertEqual(block.inlines[0].source.line_origin, "ancestor")

    def test_identity_is_stable_and_revision_tracks_source_commit(self):
        tree = new_document("content/example.rst")
        tree += nodes.paragraph("", "Hello")
        normalizer = self.normalizer()
        first = normalizer.normalize(tree)
        self.assertEqual(first.to_json(), normalizer.normalize(tree).to_json())
        changed = self.normalizer("commit-b").normalize(tree)
        self.assertEqual(first.document_id, changed.document_id)
        self.assertNotEqual(first.revision_id, changed.revision_id)

    def test_foreign_source_is_rejected_instead_of_misattributed(self):
        tree = new_document("content/example.rst")
        paragraph = nodes.paragraph("", "Included from a second file")
        paragraph.source = "content/other.rst"
        paragraph.line = 5
        tree += paragraph
        with self.assertRaisesRegex(ValueError, "Unexpected node source"):
            self.normalizer().normalize(tree)

    def test_table_spans_and_stub_column_are_preserved(self):
        tree = new_document("content/example.rst")
        table, group, head, row = nodes.table(), nodes.tgroup(cols=2), nodes.thead(), nodes.row()
        group += nodes.colspec(colwidth=1, stub=True)
        cell = nodes.entry(morecols=1, morerows=2)
        cell += nodes.paragraph("", "Header spanning cells")
        row += cell
        head += row
        group += head
        table += group
        tree += table
        result = self.normalizer().normalize(tree)
        children = result.items[0].children[0].children
        self.assertEqual(children[0].attributes["stub"], True)
        mapped_cell = children[1].children[0].children[0]
        self.assertEqual(mapped_cell.attributes["colspan"], 2)
        self.assertEqual(mapped_cell.attributes["rowspan"], 3)
        self.assertEqual(mapped_cell.children[0].text, "Header spanning cells")

    def test_unclassified_parser_error_remains_an_error(self):
        messages = parse_diagnostics("<unknown>: ERROR: expansion failed\n  details retained\n")
        self.assertEqual(messages[0][0].severity, "error")
        self.assertIn("details retained", messages[0][0].message)

    def test_unstaged_document_does_not_claim_the_source_is_missing(self):
        with TemporaryDirectory() as directory:
            app = SimpleNamespace(env=SimpleNamespace(get_domain=lambda name: object()))
            index = ReferenceIndex(app, {}, Path(directory))
            result = index.document("content/example", "other")
            self.assertEqual(result["resolution"], "not_in_corpus")
            self.assertEqual(result["target_existence"], "not_checked")

    def test_identical_snapshot_is_reused(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            first, reused = write_snapshot(base, {"documents/example.json": b"original"})
            second, reused = write_snapshot(base, {"documents/example.json": b"original"})
            self.assertEqual(first, second)
            self.assertTrue(reused)

    def test_failed_snapshot_rename_preserves_existing_output(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            first, reused = write_snapshot(base, {"example.json": b"original"})
            with patch("app.ingestion.normalize_corpus.os.rename", side_effect=OSError("simulated failure")):
                with self.assertRaises(OSError):
                    write_snapshot(base, {"example.json": b"changed"})
            self.assertEqual((first / "example.json").read_bytes(), b"original")
            self.assertEqual(list(base.iterdir()), [first])

    def test_source_edit_is_rejected_even_with_a_valid_manifest_fingerprint(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            (base / "example.rst").write_bytes(b"changed")
            inventory = {"files": [{"source_path": "example.rst", "size_bytes": 8,
                                    "sha256": hashlib.sha256(b"original").hexdigest()}]}
            canonical = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode()
            manifest = {"inventory": inventory, "inventory_fingerprint": hashlib.sha256(canonical).hexdigest()}
            with self.assertRaisesRegex(ValueError, "Source bytes do not match"):
                load_inputs(base, manifest)


if __name__ == "__main__":
    unittest.main()
