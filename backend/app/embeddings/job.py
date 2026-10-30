from contextlib import AsyncExitStack

from openai import AsyncOpenAI

from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig, embedding_cache_key
from app.embeddings.inputs import EmbeddingInput
from app.embeddings.openai_adapter import embed_texts


async def generate_embeddings(
    inputs: list[EmbeddingInput],
    config: EmbeddingConfig,
    cache: EmbeddingCache,
    *,
    batch_size: int = 64,
    client: AsyncOpenAI | None = None,
) -> dict:
    if type(batch_size) is not int or not 1 <= batch_size <= 2048:
        raise ValueError("batch_size must be an integer between 1 and 2048")

    unique = {}
    for item in inputs:
        key = embedding_cache_key(item, config)
        unique.setdefault(key, item)

    missing = [item for item in unique.values() if cache.load(item, config) is None]
    report = {
        "input_chunks": len(inputs),
        "unique_inputs": len(unique),
        "cache_hits": len(unique) - len(missing),
        "generated_embeddings": 0,
        "api_requests": 0,
        "prompt_tokens": 0,
        "total_tokens": 0,
        "request_ids": [],
    }
    if not missing:
        return report

    async with AsyncExitStack() as stack:
        if client is None:
            client = await stack.enter_async_context(
                AsyncOpenAI(timeout=60.0, max_retries=0)
            )

        for start in range(0, len(missing), batch_size):
            items = missing[start : start + batch_size]
            batch = await embed_texts(client, [item.text for item in items], config)

            for item, vector in zip(items, batch.vectors, strict=True):
                cache.store(item, config, vector)

            report["generated_embeddings"] += len(items)
            report["api_requests"] += 1
            report["prompt_tokens"] += batch.prompt_tokens
            report["total_tokens"] += batch.total_tokens
            report["request_ids"].append(batch.request_id)

    return report
