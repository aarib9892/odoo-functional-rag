import hashlib
from pathlib import Path

from app.ingestion.pinned_files import read_pinned_file


def load_evidence_sources(repository: Path, document: dict) -> dict:
    """Load verified source lines for one owning page and its includes."""
    if document["schema_version"] != "m22-0.2" or document["status"] != "ok":
        raise ValueError("Expected a complete normalized document")

    source = document["source"]

    groups = [
        entry["content"]
        for entry in document["metadata"]
        if entry.get("name") == "include_dependencies"
    ]

    if len(groups) > 1:
        raise ValueError("Repeated include-dependency metadata")

    dependencies = groups[0] if groups else []

    if not isinstance(dependencies, list):
        raise ValueError("Expected a list of include dependencies")

    records = [
        {
            "source_path": source["source_path"],
            "sha256": source["sha256"],
        }
    ]

    for dependency in dependencies:
        if not isinstance(dependency, dict) or set(dependency) != {
            "source_path",
            "sha256",
            "size_bytes",
        }:
            raise ValueError("Invalid include-dependency record")

        if type(dependency["size_bytes"]) is not int or dependency["size_bytes"] < 0:
            raise ValueError("Invalid include-dependency size")

        records.append(dict(dependency))

    for record in records:
        if not isinstance(record["source_path"], str):
            raise ValueError("Expected a source path string")

        sha = record["sha256"]

        if (
            not isinstance(sha, str)
            or len(sha) != 64
            or any(c not in "0123456789abcdef" for c in sha)
        ):
            raise ValueError("Invalid evidence source SHA-256")

    files = {}

    for record in sorted(
        records,
        key=lambda item: item["source_path"],
    ):
        path = record["source_path"]

        if path in files:
            raise ValueError(f"Repeated evidence source: {path}")

        data = read_pinned_file(
            repository,
            source["commit"],
            path,
        )

        if hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Evidence source hash differs: {path}")

        if "size_bytes" in record and len(data) != record["size_bytes"]:
            raise ValueError(f"Evidence source size differs: {path}")

        try:
            lines = data.decode("utf-8").splitlines()
        except UnicodeDecodeError as error:
            raise ValueError(f"Evidence source is not UTF-8: {path}") from error

        files[path] = {
            "sha256": record["sha256"],
            "line_count": len(lines),
            "lines": lines,
        }

    return files
