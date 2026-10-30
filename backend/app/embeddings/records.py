from dataclasses import asdict

from app.chunking.records import stable_hash
from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig, embedding_cache_key
from app.embeddings.inputs import EmbeddingInput

SCHEMA_VERSION = "m32-embedding-0.1"


def build_embedding_records(
    inputs: list[EmbeddingInput],
    config: EmbeddingConfig,
    cache: EmbeddingCache,
) -> list[dict]:
    chunk_ids = [item.chunk_id for item in inputs]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Duplicate chunk IDs in embedding inputs")

    records = []
    for item in inputs:
        vector = cache.load(item, config)
        if vector is None:
            raise ValueError(f"Missing cached embedding for chunk {item.chunk_id}")

        body = {
            "schema_version": SCHEMA_VERSION,
            "chunk_id": item.chunk_id,
            "embedding_cache_key": embedding_cache_key(item, config),
            "text_sha256": item.text_sha256,
            "embedding_config_id": config.config_id,
            "embedding_config": asdict(config),
            "vector": vector,
        }
        records.append(
            {
                "embedding_record_id": stable_hash(body),
                **body,
            }
        )

    return records
