import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.ingestion.cli import write_manifest

BACKEND_ROOT = Path(__file__).resolve().parents[1]


class InventoryCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)

        self.root = Path(temporary.name)
        self.repo = self.root / "repository"
        self.repo.mkdir()

        self.git("init", "--quiet")

        self.sales_root = "content/applications/sales/sales"
        self.page_path = f"{self.sales_root}/example.rst"
        self.other_path = f"{self.sales_root}/other.rst"
        self.excluded_path = "content/applications/sales/crm/example.rst"

        for relative_path in (
            self.page_path,
            self.other_path,
            self.excluded_path,
        ):
            path = self.repo / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Original content.\n", encoding="utf-8")

        commit = self.commit()

        self.config = {
            "schema_version": 1,
            "source": {
                "repository_url": "local-test-fixture",
                "odoo_version": "19.0",
                "language": "en",
                "commit": commit,
            },
            "scope": {
                "sales": [self.sales_root],
            },
        }

        self.config_path = self.root / "corpus.json"
        self.output = self.root / "inventory.json"
        self.save_config()

        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        self.original_output = self.output.read_bytes()

    def git(self, *arguments):
        result = subprocess.run(
            ["git", "-C", str(self.repo), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return result.stdout.strip()

    def commit(self):
        self.git("add", "-A")

        self.git(
            "-c",
            "user.name=Inventory Test",
            "-c",
            "user.email=inventory@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--quiet",
            "-m",
            "Test snapshot",
        )

        return self.git("rev-parse", "HEAD")

    def save_config(self):
        self.config_path.write_text(
            json.dumps(self.config),
            encoding="utf-8",
        )

    def run_cli(self):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "app.ingestion.cli",
                "--repo",
                str(self.repo),
                "--config",
                str(self.config_path),
                "--output",
                str(self.output),
            ],
            cwd=BACKEND_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def read_manifest(self):
        return json.loads(self.output.read_text(encoding="utf-8"))

    def assert_rejected_without_overwrite(self, error_fragment):
        result = self.run_cli()

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn(error_fragment, result.stderr)
        self.assertEqual(
            self.output.read_bytes(),
            self.original_output,
        )

    def test_wrong_commit_preserves_manifest(self):
        self.config["source"]["commit"] = "0" * 40
        self.save_config()

        self.assert_rejected_without_overwrite("commit mismatch")

    def test_missing_scope_preserves_manifest(self):
        self.config["scope"]["sales"] = ["content/applications/sales/missing"]
        self.save_config()

        self.assert_rejected_without_overwrite("matched no tracked RST files")

    def test_dirty_checkout_preserves_manifest(self):
        (self.repo / self.page_path).write_text(
            "Uncommitted change.\n",
            encoding="utf-8",
        )

        self.assert_rejected_without_overwrite("local changes")

    def test_failed_write_preserves_manifest(self):
        def fail_during_write(_manifest, stream, **_kwargs):
            stream.write('{"incomplete":')
            raise OSError("Simulated write failure")

        with patch(
            "app.ingestion.cli.json.dump",
            side_effect=fail_during_write,
        ):
            with self.assertRaises(OSError):
                write_manifest({"example": True}, self.output)

        self.assertEqual(
            self.output.read_bytes(),
            self.original_output,
        )

        leftover_files = list(self.output.parent.glob(f".{self.output.name}.*.tmp"))
        self.assertEqual(leftover_files, [])

    def test_scope_change_changes_selection(self):
        self.config["scope"]["sales"] = [self.page_path]
        self.save_config()

        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest = self.read_manifest()
        inventory = manifest["inventory"]

        self.assertEqual(
            [record["source_path"] for record in inventory["files"]],
            [self.page_path],
        )
        self.assertEqual(inventory["summary"]["discovered_files"], 3)
        self.assertEqual(inventory["summary"]["selected_files"], 1)
        self.assertEqual(inventory["summary"]["excluded_files"], 2)

        original = json.loads(self.original_output)
        self.assertNotEqual(
            manifest["inventory_fingerprint"],
            original["inventory_fingerprint"],
        )

    def test_committed_edits_additions_and_deletions(self):
        original = self.read_manifest()
        original_records = {
            record["source_path"]: record for record in original["inventory"]["files"]
        }

        (self.repo / self.page_path).write_text(
            "Updated content with additional information.\n",
            encoding="utf-8",
        )
        (self.repo / self.other_path).unlink()

        added_path = f"{self.sales_root}/added.rst"
        (self.repo / added_path).write_text(
            "New document.\n",
            encoding="utf-8",
        )

        self.config["source"]["commit"] = self.commit()
        self.save_config()

        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)

        manifest = self.read_manifest()
        records = {
            record["source_path"]: record for record in manifest["inventory"]["files"]
        }

        self.assertEqual(
            set(records),
            {self.page_path, added_path},
        )
        self.assertNotEqual(
            records[self.page_path]["sha256"],
            original_records[self.page_path]["sha256"],
        )
        self.assertEqual(
            manifest["inventory"]["source"]["commit"],
            self.config["source"]["commit"],
        )


if __name__ == "__main__":
    unittest.main()
