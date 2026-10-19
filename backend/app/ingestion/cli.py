import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from app.ingestion.discovery import discover_rst_files
from app.ingestion.inventory import build_file_records
from app.ingestion.manifest import build_manifest
from app.ingestion.repository import get_clean_commit
from app.ingestion.scope import select_scope


def load_config(path: Path) -> dict:
    config = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a JSON object.")

    if config.get("schema_version") != 1:
        raise ValueError("Unsupported configuration schema_version.")

    source = config.get("source")
    required_fields = (
        "repository_url",
        "odoo_version",
        "language",
        "commit",
    )

    if not isinstance(source, dict):
        raise ValueError("Configuration must contain a source object.")

    for field in required_fields:
        value = source.get(field)

        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"source.{field} must be a non-empty string.")

    scope = config.get("scope")

    if not isinstance(scope, dict) or not scope:
        raise ValueError("Configuration must contain a non-empty scope.")

    for application, paths in scope.items():
        if not application.strip():
            raise ValueError("Application names must not be empty.")

        if (
            not isinstance(paths, list)
            or not paths
            or any(not isinstance(path, str) or not path.strip() for path in paths)
        ):
            raise ValueError(
                f"Scope for {application!r} must be a non-empty "
                "list of path strings."
            )

    return config


def write_manifest(
    manifest: dict[str, object],
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            json.dump(
                manifest,
                temporary_file,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            temporary_file.write("\n")

        temporary_path.replace(destination)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a reproducible Odoo source inventory."
    )

    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()

    try:
        repository_root = args.repo.resolve(strict=True)
        config_path = args.config.resolve(strict=True)
        output_path = args.output.resolve()

        if output_path.is_relative_to(repository_root):
            raise ValueError("Output must be outside the documentation checkout.")

        if output_path == config_path:
            raise ValueError("Output must not overwrite configuration.")

        config = load_config(config_path)
        commit = get_clean_commit(repository_root)

        if commit != config["source"]["commit"]:
            raise ValueError(
                f"Source commit mismatch: "
                f"expected {config['source']['commit']}, "
                f"found {commit}"
            )

        paths = discover_rst_files(repository_root)
        selected = select_scope(paths, config["scope"])
        records = build_file_records(repository_root, selected)

        if get_clean_commit(repository_root) != commit:
            raise ValueError("Source commit changed during inventory creation.")

        manifest = build_manifest(
            source=config["source"],
            scope=config["scope"],
            discovered_paths=paths,
            records=records,
        )

        write_manifest(manifest, output_path)

    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or "").strip() or str(exc)
        print(f"Inventory failed: {detail}", file=sys.stderr)
        return 1

    except (OSError, ValueError) as exc:
        print(f"Inventory failed: {exc}", file=sys.stderr)
        return 1

    summary = manifest["inventory"]["summary"]

    print(f"Commit: {commit}")
    print(f"Discovered: {summary['discovered_files']}")
    print(f"Selected: {summary['selected_files']}")
    print(f"Excluded: {summary['excluded_files']}")
    print(f"Source bytes: {summary['total_size_bytes']}")
    print(f"Fingerprint: {manifest['inventory_fingerprint']}")
    print(f"Saved: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
