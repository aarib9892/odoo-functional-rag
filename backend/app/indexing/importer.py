from dataclasses import asdict
import json
from pathlib import Path

from app.chunking.records import stable_hash
from app.database import connect_database
from app.indexing.inputs import load_index_inputs

SCHEMA_VERSION = "m33-dense-index-0.1"


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


async def import_index(
    chunk_snapshot: Path,
    embedding_snapshot: Path,
    corpus_name: str = "odoo19",
) -> tuple[str, bool]:
    """Import, verify and activate a snapshot; return its ID and whether it existed."""
    if not isinstance(corpus_name, str) or not corpus_name.strip():
        raise ValueError("Corpus name must be a nonempty string")

    inputs = load_index_inputs(chunk_snapshot, embedding_snapshot)
    identity = {
        "schema_version": SCHEMA_VERSION,
        "chunk_snapshot_id": inputs.chunk_snapshot_id,
        "embedding_snapshot_id": inputs.embedding_snapshot_id,
    }
    snapshot_id = stable_hash(identity)
    header = {
        "chunk_snapshot_id": inputs.chunk_snapshot_id,
        "embedding_snapshot_id": inputs.embedding_snapshot_id,
        "embedding_config_id": inputs.config.config_id,
        "embedding_config": asdict(inputs.config),
        "expected_chunks": len(inputs.pairs),
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "chunk_summary": inputs.chunk_summary,
            "embedding_summary": inputs.embedding_summary,
        },
    }

    expected = {}
    vectors = {}
    for chunk, record in inputs.pairs:
        expected[chunk["chunk_id"]] = {
            "chunk_id": chunk["chunk_id"],
            "embedding_record_id": record["embedding_record_id"],
            "embedding_config_id": inputs.config.config_id,
            "cache_key": record["embedding_cache_key"],
            "text_sha256": record["text_sha256"],
            "retrieval_text": chunk["content"]["retrieval_text"],
            "chunk_record": chunk,
        }
        vectors[record["embedding_cache_key"]] = record

    async with connect_database() as connection:
        async with connection.transaction():
            await connection.execute("SELECT pg_advisory_xact_lock(3303001)")
            previous = await connection.fetchrow(
                """
                SELECT chunk_snapshot_id, embedding_snapshot_id,
                       embedding_config_id, embedding_config,
                       expected_chunks, metadata, published
                FROM index_snapshots WHERE snapshot_id = $1
            """,
                snapshot_id,
            )

            reused = previous is not None
            if reused:
                stored = dict(previous)
                published = stored.pop("published")
                for key in ("embedding_config", "metadata"):
                    stored[key] = json.loads(stored[key])
                if not published or stored != header:
                    raise ValueError(
                        "Existing database snapshot differs or is unpublished"
                    )
            else:
                await connection.execute(
                    """
                    INSERT INTO index_snapshots (
                        snapshot_id, chunk_snapshot_id, embedding_snapshot_id,
                        embedding_config_id, embedding_config,
                        expected_chunks, metadata
                    ) VALUES ($1, $2, $3, $4, $5::jsonb, $6, $7::jsonb)
                """,
                    snapshot_id,
                    inputs.chunk_snapshot_id,
                    inputs.embedding_snapshot_id,
                    inputs.config.config_id,
                    _json(header["embedding_config"]),
                    len(inputs.pairs),
                    _json(header["metadata"]),
                )

            for key, record in vectors.items():
                arguments = (
                    key,
                    inputs.config.config_id,
                    record["text_sha256"],
                    _json(record["vector"]),
                )
                if not reused:
                    await connection.execute(
                        """
                        INSERT INTO embeddings (
                            cache_key, embedding_config_id, text_sha256, embedding
                        ) VALUES ($1, $2, $3, $4::text::vector(1536))
                        ON CONFLICT (cache_key) DO NOTHING
                    """,
                        *arguments
                    )

                matches = await connection.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM embeddings
                        WHERE cache_key = $1 AND embedding_config_id = $2
                          AND text_sha256 = $3
                          AND embedding = $4::text::vector(1536)
                    )
                """,
                    *arguments
                )
                if not matches:
                    raise ValueError("Stored embedding differs from the saved vector")

            if not reused:
                await connection.executemany(
                    """
                    INSERT INTO index_chunks (
                        snapshot_id, chunk_id, embedding_record_id,
                        embedding_config_id, cache_key, text_sha256,
                        retrieval_text, chunk_record
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
                """,
                    [
                        (
                            snapshot_id,
                            row["chunk_id"],
                            row["embedding_record_id"],
                            row["embedding_config_id"],
                            row["cache_key"],
                            row["text_sha256"],
                            row["retrieval_text"],
                            _json(row["chunk_record"]),
                        )
                        for row in expected.values()
                    ],
                )

            rows = await connection.fetch(
                """
                SELECT chunk_id, embedding_record_id, embedding_config_id,
                       cache_key, text_sha256, retrieval_text, chunk_record
                FROM index_chunks WHERE snapshot_id = $1
            """,
                snapshot_id,
            )

            actual = {}
            for row in rows:
                data = dict(row)
                data["chunk_record"] = json.loads(data["chunk_record"])
                actual[data["chunk_id"]] = data
            if len(rows) != len(expected) or actual != expected:
                raise ValueError(
                    "Stored chunks differ from the complete input snapshot"
                )

            if not reused:
                await connection.execute(
                    """
                    UPDATE index_snapshots
                    SET published = TRUE, published_at = NOW()
                    WHERE snapshot_id = $1
                """,
                    snapshot_id,
                )

            await connection.execute(
                """
                INSERT INTO active_indexes (corpus_name, snapshot_id)
                VALUES ($1, $2)
                ON CONFLICT (corpus_name)
                DO UPDATE SET snapshot_id = EXCLUDED.snapshot_id
            """,
                corpus_name,
                snapshot_id,
            )

    return snapshot_id, reused
