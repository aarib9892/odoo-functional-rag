import hashlib
import json

from openai import AsyncOpenAI

from app.chunking.tokens import count_tokens
from app.database import connect_database
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig, embedding_cache_key
from app.embeddings.inputs import EmbeddingInput
from app.embeddings.job import generate_embeddings
from app.retrieval.dense import search_dense


async def retrieve_question(
    question: str,
    cache: EmbeddingCache,
    corpus_name: str = "odoo19",
    top_k: int = 5,
    *,
    client: AsyncOpenAI | None = None,
    method: str = "dense",
    expected_snapshot_id: str | None = None,
) -> dict:
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question must be a nonempty string")
    if not isinstance(corpus_name, str) or not corpus_name.strip():
        raise ValueError("Corpus name must be a nonempty string")
    if type(top_k) is not int or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    if method not in {"dense", "hybrid"}:
        raise ValueError("Unsupported retrieval method")

    tokens = count_tokens(question)
    if tokens > 8192:
        raise ValueError("Question exceeds the embedding input token limit")

    async with connect_database() as connection:
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
    if expected_snapshot_id is not None and snapshot["snapshot_id"] != expected_snapshot_id:
        raise ValueError("Active index differs from the approved release")

    config = EmbeddingConfig(**json.loads(snapshot["embedding_config"]))
    if config.dimensions != 1536 or config.config_id != snapshot["embedding_config_id"]:
        raise ValueError("Invalid active embedding configuration")

    text_hash = hashlib.sha256(question.encode("utf-8")).hexdigest()
    item = EmbeddingInput(
        chunk_id=f"query:{text_hash}",
        text=question,
        text_sha256=text_hash,
        token_count=tokens,
    )
    generation = await generate_embeddings([item], config, cache, client=client)

    vector = cache.load(item, config)
    if vector is None:
        raise ValueError("Question embedding was not cached")

    if method == "hybrid":
        from app.retrieval.hybrid import search_hybrid
        result = await search_hybrid(vector, config, question, corpus_name, top_k)
    else:
        result = await search_dense(vector, config, corpus_name, top_k)
    if result["snapshot_id"] != snapshot["snapshot_id"]:
        raise ValueError("Active snapshot changed during retrieval; retry the question")

    return {
        **result,
        "schema_version": "m33-question-retrieval-0.1",
        "query": {
            "text": question,
            "text_sha256": text_hash,
            "token_count": tokens,
        },
        "query_embedding": {
            "cache_key": embedding_cache_key(item, config),
            "cache_hit": generation["cache_hits"] == 1,
            "api_requests": generation["api_requests"],
            "prompt_tokens": generation["prompt_tokens"],
            "total_tokens": generation["total_tokens"],
            "request_ids": generation["request_ids"],
        },
    }
