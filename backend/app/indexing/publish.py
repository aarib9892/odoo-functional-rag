from pathlib import Path

from openai import AsyncOpenAI

from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig
from app.embeddings.inputs import load_embedding_inputs
from app.embeddings.job import generate_embeddings
from app.embeddings.snapshot import save_embedding_snapshot
from app.indexing.importer import import_index


async def publish_candidate(
    chunk_snapshot: Path,
    embedding_output: Path,
    config: EmbeddingConfig,
    cache: EmbeddingCache,
    *,
    corpus_name: str,
    batch_size: int = 64,
    client: AsyncOpenAI | None = None,
) -> dict:
    """Prepare complete embeddings, then import and activate the candidate."""
    chunk_snapshot = chunk_snapshot.resolve()
    embedding_output = embedding_output.resolve()

    if not isinstance(corpus_name, str) or not corpus_name.strip():
        raise ValueError("Corpus name must be nonempty")

    if config.dimensions != 1536:
        raise ValueError("The current database schema requires 1536 dimensions")

    if any(
        target.resolve().is_relative_to(chunk_snapshot)
        for target in (embedding_output, cache.directory)
    ):
        raise ValueError("Embedding outputs must be outside the chunk snapshot")

    inputs = load_embedding_inputs(chunk_snapshot)
    if not inputs:
        raise ValueError("No eligible chunks to publish")

    generation = await generate_embeddings(
        inputs,
        config,
        cache,
        batch_size=batch_size,
        client=client,
    )

    embeddings, summary, embedding_reused = save_embedding_snapshot(
        chunk_snapshot, embedding_output, config, cache
    )

    database_id, index_reused = await import_index(
        chunk_snapshot,
        embeddings,
        corpus_name=corpus_name,
    )

    return {
        "generation": generation,
        "embedding_records": summary["embedding_records"],
        "embedding_snapshot_id": embeddings.name,
        "embedding_snapshot_path": str(embeddings),
        "embedding_snapshot_reused": embedding_reused,
        "database_snapshot_id": database_id,
        "index_reused": index_reused,
    }
