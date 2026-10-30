from dataclasses import dataclass

from openai import AsyncOpenAI

from app.chunking.tokens import count_tokens
from app.embeddings.cache import validate_vector
from app.embeddings.config import EmbeddingConfig


@dataclass(frozen=True)
class EmbeddingBatch:
    vectors: list[list[float]]
    model: str
    prompt_tokens: int
    total_tokens: int
    request_id: str | None = None


async def embed_texts(
    client: AsyncOpenAI,
    texts: list[str],
    config: EmbeddingConfig,
) -> EmbeddingBatch:
    if not texts:
        return EmbeddingBatch([], config.model, 0, 0)

    if len(texts) > 2048:
        raise ValueError("Embedding batch exceeds 2048 inputs")

    total_input_tokens = 0

    for text in texts:
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Embedding text must be a nonempty string")

        tokens = count_tokens(text)
        if tokens > 8192:
            raise ValueError("Embedding input exceeds 8192 tokens")

        total_input_tokens += tokens

    if total_input_tokens > 300_000:
        raise ValueError("Embedding batch exceeds 300000 input tokens")

    response = await client.embeddings.create(
        model=config.model,
        input=texts,
        dimensions=config.dimensions,
        encoding_format="float",
    )

    if response.model != config.model:
        raise ValueError("Returned embedding model differs from configuration")

    indexes = [row.index for row in response.data]
    if any(type(index) is not int for index in indexes) or sorted(indexes) != list(
        range(len(texts))
    ):
        raise ValueError("Embedding response indexes do not match the inputs")

    rows = sorted(response.data, key=lambda row: row.index)
    vectors = [validate_vector(row.embedding, config.dimensions) for row in rows]

    prompt_tokens = response.usage.prompt_tokens
    total_tokens = response.usage.total_tokens

    if (
        type(prompt_tokens) is not int
        or type(total_tokens) is not int
        or not 0 <= prompt_tokens <= total_tokens
    ):
        raise ValueError("Invalid embedding token usage")

    return EmbeddingBatch(
        vectors=vectors,
        model=response.model,
        prompt_tokens=prompt_tokens,
        total_tokens=total_tokens,
        request_id=getattr(response, "_request_id", None),
    )
