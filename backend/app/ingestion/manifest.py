import hashlib
import json
from dataclasses import asdict
from datetime import UTC, datetime

from app.ingestion.inventory import FileRecord


def build_manifest(
    source: dict[str, str],
    scope: dict[str, list[str]],
    discovered_paths: list[str],
    records: list[FileRecord],
) -> dict[str, object]:
    """Package inventory results and calculate their fingerprint."""

    discovered = set(discovered_paths)
    selected = {record.source_path for record in records}

    if len(selected) != len(records):
        raise ValueError("Inventory contains duplicate file records.")

    if not selected.issubset(discovered):
        raise ValueError("Inventory contains files absent from discovery.")

    excluded_paths = sorted(discovered - selected)

    inventory = {
        "schema_version": 1,
        "source": dict(source),
        "scope": {
            application: sorted(set(allowed_paths))
            for application, allowed_paths in sorted(scope.items())
        },
        "summary": {
            "discovered_files": len(discovered),
            "selected_files": len(records),
            "excluded_files": len(excluded_paths),
            "total_size_bytes": sum(record.size_bytes for record in records),
        },
        "files": [
            asdict(record)
            for record in sorted(
                records,
                key=lambda record: record.source_path,
            )
        ],
        "excluded_files": [
            {
                "source_path": path,
                "reason": "outside_configured_scope",
            }
            for path in excluded_paths
        ],
    }

    canonical_bytes = json.dumps(
        inventory,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    fingerprint = hashlib.sha256(canonical_bytes).hexdigest()

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "inventory_fingerprint": fingerprint,
        "inventory": inventory,
    }
