import unittest
import base64
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from app.ingestion.fidelity_audit import audit, checkout_evidence, inside, read_snapshot
from app.ingestion.fidelity_html import build_source_html, normalized_page
from app.ingestion.normalize_corpus import write_snapshot


class FidelityReviewTests(unittest.TestCase):
    def test_label_candidates_do_not_change_normalized_reference_state(self):
        with TemporaryDirectory() as directory:
            repository = Path(directory)
            (repository / "other.rst").write_text(".. _missing-label:\n\nOther title\n===========\n")
            reference = {"kind": "reference", "text": "original", "source": {"line": 7},
                         "attributes": {"resolution": "unresolved_label", "target": "missing-label"}, "children": []}
            documents = {"selected.rst": {"items": [{"kind": "paragraph", "heading_path": ["Selected"],
                                                       "inlines": [reference], "children": []}]}}
            manifest = {"inventory": {"source": {}, "files": [{"source_path": "selected.rst"}],
                                       "excluded_files": [{"source_path": "other.rst"}]}}
            result = audit(documents, manifest, repository)
            self.assertEqual(reference["attributes"]["resolution"], "unresolved_label")
            candidate = result["reference_occurrences"][0]["literal_label_candidates"][0]
            self.assertEqual(candidate, {"source_path": "other.rst", "line": 1})

    def test_source_paths_cannot_escape_checkout(self):
        self.assertIsNone(inside(Path("/tmp/example"), "../elsewhere.rst"))

    def test_missing_image_is_visible_in_review(self):
        document = {"title": "Images", "items": [{"kind": "image", "attributes": {"uri": "missing.png", "alt": "Important screenshot"}}]}
        html = normalized_page(document, {})
        self.assertIn("Image unavailable", html)
        self.assertIn("Important screenshot", html)

    def test_snapshot_tampering_is_rejected_before_source_read(self):
        with TemporaryDirectory() as directory:
            snapshot, reused = write_snapshot(Path(directory), {"summary.json": b"original"})
            (snapshot / "summary.json").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Snapshot bytes"):
                read_snapshot(snapshot, {}, Path(directory))

    def test_present_image_is_copied_by_the_native_html_writer(self):
        with TemporaryDirectory() as directory:
            base = Path(directory)
            repository = base / "repository"
            (repository / "content").mkdir(parents=True)
            image = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jI64AAAAASUVORK5CYII=")
            (repository / "content/picture.png").write_bytes(image)
            files = {"content/example.rst": b"Example\n=======\n\n.. image:: picture.png\n   :alt: Test image\n"}
            output, image_map, logs = build_source_html(files, repository,
                [{"source_file_present": True, "uri": "content/picture.png"}], base / "work")
            self.assertEqual((output / "_images" / image_map["content/picture.png"]).read_bytes(), image)

    def test_checkout_evidence_distinguishes_clean_and_dirty_source(self):
        with TemporaryDirectory() as directory:
            repository = Path(directory)
            def git(*args):
                return subprocess.run(["git", "-C", directory, *args], capture_output=True, text=True, check=True)
            git("init", "-q")
            (repository / "example.rst").write_text("Original")
            git("add", "example.rst")
            git("-c", "user.name=M2 Test", "-c", "user.email=m2-test@example.invalid", "commit", "-qm", "fixture")
            commit = git("rev-parse", "HEAD").stdout.strip()
            clean, tracked = checkout_evidence(repository, commit)
            self.assertTrue(clean["verified"])
            self.assertIn("example.rst", tracked)
            (repository / "example.rst").write_text("Changed")
            dirty, tracked = checkout_evidence(repository, commit)
            self.assertEqual(dirty["status"], "dirty")
            self.assertFalse(dirty["verified"])


if __name__ == "__main__":
    unittest.main()
