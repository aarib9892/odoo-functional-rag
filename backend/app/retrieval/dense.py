from dataclasses import asdict
import json
import math

from app.database import connect_database
from app.embeddings.cache import validate_vector
from app.embeddings.config import EmbeddingConfig


async def search_dense(
    query_vector: list[float],
    config: EmbeddingConfig,
    corpus_name: str = "odoo19",
    top_k: int = 5,
) -> dict:
    if not isinstance(corpus_name, str) or not corpus_name.strip():
        raise ValueError("Corpus name must be a nonempty string")
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    if config.dimensions != 1536:
        raise ValueError("The current database schema requires 1536 dimensions")

    vector = validate_vector(query_vector, config.dimensions)
    encoded = json.dumps(vector, allow_nan=False)

    async with connect_database() as connection:
        async with connection.transaction(isolation="repeatable_read", readonly=True):
            snapshot = await connection.fetchrow(
                """
                SELECT s.snapshot_id, s.embedding_config_id, s.embedding_config
                FROM active_indexes a
                JOIN index_snapshots s ON s.snapshot_id = a.snapshot_id
                WHERE a.corpus_name = $1 AND s.published
            """,
                corpus_name,
            )

            if snapshot is None:
                raise ValueError("No active published snapshot for this corpus")
            if snapshot["embedding_config_id"] != config.config_id or json.loads(
                snapshot["embedding_config"]
            ) != asdict(config):
                raise ValueError("Query embedding configuration differs from the index")

            rows = await connection.fetch(
                """
                SELECT c.chunk_id, c.embedding_record_id, c.cache_key,
                       c.retrieval_text, c.chunk_record,
                       e.embedding <=> $2::text::vector(1536) AS distance
                FROM index_chunks c
                JOIN embeddings e
                  ON e.cache_key = c.cache_key
                 AND e.embedding_config_id = c.embedding_config_id
                 AND e.text_sha256 = c.text_sha256
                WHERE c.snapshot_id = $1 AND c.embedding_config_id = $3
                ORDER BY distance ASC, c.chunk_id ASC
                LIMIT $4
            """,
                snapshot["snapshot_id"],
                encoded,
                config.config_id,
                top_k,
            )

    if not rows:
        raise ValueError("Active snapshot has no searchable chunks")

    hits = []
    for rank, row in enumerate(rows, start=1):
        hit = dict(row)
        if not math.isfinite(hit["distance"]):
            raise ValueError("Non-finite cosine distance; check the query vector")
        hit["chunk_record"] = json.loads(hit["chunk_record"])
        hits.append({"rank": rank, **hit})

    return {
        "schema_version": "m33-dense-search-0.1",
        "corpus_name": corpus_name,
        "snapshot_id": snapshot["snapshot_id"],
        "embedding_config_id": config.config_id,
        "embedding_config": asdict(config),
        "top_k": top_k,
        "hits": hits,
    }
