from dataclasses import asdict
import hashlib
import json
from pathlib import Path

from openai import AsyncOpenAI

from app.database import connect_database
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig
from app.indexing.candidate import prepare_candidate
from app.indexing.changes import plan_source_changes
from app.indexing.publish import publish_candidate


def _file_hashes(manifest: dict) -> dict[str, str]:
    inventory = manifest["inventory"]
    encoded = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )

    if hashlib.sha256(encoded).hexdigest() != manifest["inventory_fingerprint"]:
        raise ValueError("Manifest inventory fingerprint mismatch")

    records = inventory["files"]
    hashes = {record["source_path"]: record["sha256"] for record in records}
    if len(hashes) != len(records):
        raise ValueError("Manifest contains duplicate source paths")

    return hashes


async def rebuild_corpus(
    repository: Path,
    manifest: dict,
    previous_manifest: dict | None,
    data_root: Path,
    config: EmbeddingConfig,
    cache: EmbeddingCache,
    *,
    corpus_name: str,
    max_tokens: int = 512,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Compare the active source inventory, prepare and publish a complete rebuild."""
    repository = repository.resolve()
    data_root = data_root.resolve()

    if not isinstance(corpus_name, str) or not corpus_name.strip():
        raise ValueError("Corpus name must be nonempty")

    if any(
        path.resolve().is_relative_to(repository)
        for path in (data_root, cache.directory)
    ):
        raise ValueError("Rebuild outputs must be outside the source checkout")

    current = _file_hashes(manifest)
    previous = {} if previous_manifest is None else _file_hashes(previous_manifest)

    async with connect_database() as connection:
        active = await connection.fetchrow(
            """
            SELECT s.snapshot_id,
                   s.metadata #>> '{chunk_summary,inventory_fingerprint}'
                       AS inventory_fingerprint
            FROM active_indexes a
            JOIN index_snapshots s ON s.snapshot_id = a.snapshot_id
            WHERE a.corpus_name = $1 AND s.published
        """,
            corpus_name,
        )

    if active is None:
        if previous_manifest is not None:
            raise ValueError("No active corpus matches the previous manifest")
    elif (
        previous_manifest is None
        or active["inventory_fingerprint"] != previous_manifest["inventory_fingerprint"]
    ):
        raise ValueError("Previous manifest differs from the active corpus")

    changes = plan_source_changes(previous, current)

    normalized, chunks = prepare_candidate(
        repository,
        manifest,
        data_root / "normalized/corpus",
        data_root / "chunks/corpus",
        max_tokens=max_tokens,
    )

    publication = await publish_candidate(
        chunks,
        data_root / "embeddings/corpus",
        config,
        cache,
        corpus_name=corpus_name,
        client=client,
    )

    return {
        "source_changes": asdict(changes),
        "previous_database_snapshot_id": (
            None if active is None else active["snapshot_id"]
        ),
        "inventory_fingerprint": manifest["inventory_fingerprint"],
        "normalized_snapshot_id": normalized.name,
        "normalized_snapshot_path": str(normalized),
        "chunk_snapshot_id": chunks.name,
        "chunk_snapshot_path": str(chunks),
        **publication,
    }
