import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from app.chunking.eligibility import ELIGIBILITY_VERSION, assess_chunk
from app.chunking.pipeline import build_document_chunks


def read_files(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def fingerprint(files: dict[str, bytes]) -> str:
    hashes = {
        name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())
    }
    encoded = json.dumps(hashes, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def save_chunk_snapshot(
    normalized_snapshot: Path,
    output: Path,
    max_tokens: int = 512,
) -> tuple[Path, dict, bool]:
    if max_tokens < 1:
        raise ValueError("Token budget must be positive")

    files = read_files(normalized_snapshot)
    if fingerprint(files) != normalized_snapshot.name:
        raise ValueError("Normalized snapshot fingerprint mismatch")

    source_summary = json.loads(files["summary.json"])
    names = sorted(
        name
        for name in files
        if name.startswith("documents/") and name.endswith(".json")
    )
    if not names or len(names) != source_summary["normalized_documents"]:
        raise ValueError("Normalized document count mismatch")

    records = []
    decisions = []

    for name in names:
        document = json.loads(files[name])
        if any(
            document["source"][key] != value
            for key, value in source_summary["source"].items()
        ):
            raise ValueError(f"Document source differs from summary: {name}")

        document_records = build_document_chunks(document, max_tokens=max_tokens)
        records.extend(document_records)

        decisions.extend(assess_chunk(record, document) for record in document_records)
    if not records:
        raise ValueError("Snapshot produced no chunk records")

    ids = [record["chunk_id"] for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate chunk IDs across documents")

    summary = {
        "schema_version": "m31-chunk-snapshot-0.2",
        "normalized_snapshot_id": normalized_snapshot.name,
        "inventory_fingerprint": source_summary["inventory_fingerprint"],
        "source": source_summary["source"],
        "normalized_documents": len(names),
        "chunk_records": len(records),
        "chunking_config_id": records[0]["chunking_config_id"],
        "chunking_config": records[0]["chunking_config"],
        "largest_chunk_tokens": max(record["token_count"] for record in records),
        "retrieval_eligibility": "classified",
        "eligibility_version": ELIGIBILITY_VERSION,
        "eligible_chunk_records": sum(d["eligible_for_retrieval"] for d in decisions),
        "metadata_only_chunk_records": sum(
            not d["eligible_for_retrieval"] for d in decisions
        ),
    }

    payload = {
        "chunks.jsonl": "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
            for record in records
        ).encode("utf-8"),
        "eligibility.jsonl": "".join(
            json.dumps(decision, ensure_ascii=False, sort_keys=True) + "\n"
            for decision in decisions
        ).encode("utf-8"),
        "summary.json": (
            json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        ).encode("utf-8"),
    }

    output.mkdir(parents=True, exist_ok=True)
    destination = output / fingerprint(payload)

    if destination.exists():
        if read_files(destination) != payload:
            raise ValueError("Existing chunk snapshot content differs")
        return destination, summary, True

    with TemporaryDirectory(prefix=".chunking-", dir=output) as temporary:
        staging = Path(temporary)
        for name, data in payload.items():
            (staging / name).write_bytes(data)

        staging.rename(destination)

    return destination, summary, False
