from dataclasses import asdict, dataclass
import json
from pathlib import Path

from app.chunking.records import stable_hash
from app.chunking.snapshot import fingerprint, read_files
from app.embeddings.cache import validate_vector
from app.embeddings.config import EmbeddingConfig, embedding_cache_key
from app.embeddings.inputs import load_embedding_inputs


@dataclass(frozen=True)
class IndexInputs:
    chunk_snapshot_id: str
    embedding_snapshot_id: str
    config: EmbeddingConfig
    chunk_summary: dict
    embedding_summary: dict
    pairs: tuple[tuple[dict, dict], ...]


def _read_snapshot(path: Path, schema: str, names: set[str]) -> tuple[dict, dict]:
    files = read_files(path)
    if fingerprint(files) != path.name:
        raise ValueError("Snapshot fingerprint mismatch")
    if set(files) != names:
        raise ValueError("Unexpected snapshot files")
    summary = json.loads(files["summary.json"])
    if summary["schema_version"] != schema:
        raise ValueError("Unsupported snapshot schema")
    return files, summary


def load_index_inputs(chunk_snapshot: Path, embedding_snapshot: Path) -> IndexInputs:
    chunk_files, chunk_summary = _read_snapshot(
        chunk_snapshot,
        "m31-chunk-snapshot-0.2",
        {"chunks.jsonl", "eligibility.jsonl", "summary.json"},
    )
    embedding_files, embedding_summary = _read_snapshot(
        embedding_snapshot,
        "m32-embedding-snapshot-0.1",
        {"embeddings.jsonl", "summary.json"},
    )
    if embedding_summary["chunk_snapshot_id"] != chunk_snapshot.name:
        raise ValueError("Embedding snapshot belongs to another chunk snapshot")
    for key in (
        "normalized_snapshot_id",
        "inventory_fingerprint",
        "source",
        "normalized_documents",
        "chunking_config_id",
        "eligibility_version",
    ):
        if chunk_summary[key] != embedding_summary[key]:
            raise ValueError(f"Snapshot lineage mismatch: {key}")

    config = EmbeddingConfig(**embedding_summary["embedding_config"])
    if config.dimensions != 1536:
        raise ValueError("The current database schema requires 1536 dimensions")
    if config.config_id != embedding_summary["embedding_config_id"]:
        raise ValueError("Embedding configuration ID mismatch")
    if (
        stable_hash(chunk_summary["chunking_config"])
        != chunk_summary["chunking_config_id"]
    ):
        raise ValueError("Chunking configuration ID mismatch")

    inputs = load_embedding_inputs(chunk_snapshot)
    if not inputs:
        raise ValueError("No eligible chunks to index")

    chunks = {}
    for line in chunk_files["chunks.jsonl"].splitlines():
        chunk = json.loads(line)
        body = {key: value for key, value in chunk.items() if key != "chunk_id"}
        if (
            chunk["schema_version"] != "m31-chunk-0.1"
            or stable_hash(body) != chunk["chunk_id"]
        ):
            raise ValueError("Chunk record identity mismatch")
        if (
            chunk["chunking_config_id"] != chunk_summary["chunking_config_id"]
            or chunk["chunking_config"] != chunk_summary["chunking_config"]
            or any(
                chunk["content"]["source"][key] != value
                for key, value in chunk_summary["source"].items()
            )
        ):
            raise ValueError("Chunk metadata differs from snapshot summary")
        chunks[chunk["chunk_id"]] = chunk

    records = [
        json.loads(line) for line in embedding_files["embeddings.jsonl"].splitlines()
    ]
    by_chunk = {record["chunk_id"]: record for record in records}
    if (
        len(by_chunk) != len(records)
        or set(by_chunk) != {item.chunk_id for item in inputs}
        or len(records) != embedding_summary["embedding_records"]
    ):
        raise ValueError("Eligible chunks and embedding records do not match")

    pairs = []
    vectors = {}
    for item in inputs:
        record = by_chunk[item.chunk_id]
        expected = {
            "schema_version": "m32-embedding-0.1",
            "chunk_id": item.chunk_id,
            "embedding_cache_key": embedding_cache_key(item, config),
            "text_sha256": item.text_sha256,
            "embedding_config_id": config.config_id,
            "embedding_config": asdict(config),
            "vector": record["vector"],
        }
        if record != {"embedding_record_id": stable_hash(expected), **expected}:
            raise ValueError("Embedding record identity or association mismatch")

        vector = validate_vector(record["vector"], config.dimensions)
        key = record["embedding_cache_key"]
        if key in vectors and vectors[key] != vector:
            raise ValueError("Conflicting vectors for one cache key")

        vectors[key] = vector
        pairs.append((chunks[item.chunk_id], record))

    if len(vectors) != embedding_summary["unique_embeddings"]:
        raise ValueError("Unique embedding count mismatch")

    return IndexInputs(
        chunk_snapshot.name,
        embedding_snapshot.name,
        config,
        chunk_summary,
        embedding_summary,
        tuple(pairs),
    )
