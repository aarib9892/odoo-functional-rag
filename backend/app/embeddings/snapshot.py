from dataclasses import asdict
import json
from pathlib import Path
from tempfile import TemporaryDirectory

from app.chunking.snapshot import fingerprint, read_files
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig
from app.embeddings.inputs import load_embedding_inputs
from app.embeddings.records import build_embedding_records


def save_embedding_snapshot(
    chunk_snapshot: Path,
    output: Path,
    config: EmbeddingConfig,
    cache: EmbeddingCache,
) -> tuple[Path, dict, bool]:
    files = read_files(chunk_snapshot)
    if fingerprint(files) != chunk_snapshot.name:
        raise ValueError("Chunk snapshot fingerprint mismatch")

    inputs = load_embedding_inputs(chunk_snapshot)
    records = build_embedding_records(inputs, config, cache)
    if not records:
        raise ValueError("No eligible embedding records to publish")

    source = json.loads(files["summary.json"])
    summary = {
        "schema_version": "m32-embedding-snapshot-0.1",
        "chunk_snapshot_id": chunk_snapshot.name,
        "normalized_snapshot_id": source["normalized_snapshot_id"],
        "inventory_fingerprint": source["inventory_fingerprint"],
        "source": source["source"],
        "normalized_documents": source["normalized_documents"],
        "chunking_config_id": source["chunking_config_id"],
        "eligibility_version": source["eligibility_version"],
        "embedding_config_id": config.config_id,
        "embedding_config": asdict(config),
        "embedding_records": len(records),
        "unique_embeddings": len({record["embedding_cache_key"] for record in records}),
    }
    payload = {
        "embeddings.jsonl": "".join(
            json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False)
            + "\n"
            for record in records
        ).encode("utf-8"),
        "summary.json": (
            json.dumps(
                summary,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            + "\n"
        ).encode("utf-8"),
    }

    output.mkdir(parents=True, exist_ok=True)
    destination = output / fingerprint(payload)
    if destination.exists():
        if read_files(destination) != payload:
            raise ValueError("Existing embedding snapshot content differs")
        return destination, summary, True

    with TemporaryDirectory(prefix=".embedding-snapshot-", dir=output) as temporary:
        staging = Path(temporary) / "snapshot"
        staging.mkdir()
        for name, data in payload.items():
            (staging / name).write_bytes(data)
        try:
            staging.rename(destination)
        except OSError:
            if not destination.is_dir() or read_files(destination) != payload:
                raise
            return destination, summary, True

    return destination, summary, False
