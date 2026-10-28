from dataclasses import asdict, dataclass
import hashlib

from app.chunking.records import stable_hash
from app.embeddings.inputs import EmbeddingInput

DIMENSION_LIMITS = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
}


@dataclass(frozen=True)
class EmbeddingConfig:
    provider: str = "openai"
    model: str = "text-embedding-3-small"
    dimensions: int = 1536

    def __post_init__(self):
        if self.provider != "openai" or self.model not in DIMENSION_LIMITS:
            raise ValueError("Unsupported embedding provider or model")

        if (
            type(self.dimensions) is not int
            or not 1 <= self.dimensions <= DIMENSION_LIMITS[self.model]
        ):
            raise ValueError("Invalid embedding dimensions for this model")

    @property
    def config_id(self) -> str:
        return stable_hash(asdict(self))


def embedding_cache_key(item: EmbeddingInput, config: EmbeddingConfig) -> str:
    actual_hash = hashlib.sha256(item.text.encode("utf-8")).hexdigest()
    if actual_hash != item.text_sha256:
        raise ValueError("Embedding input text hash mismatch")

    return stable_hash(
        {
            "schema_version": "m32-embedding-key-0.1",
            "embedding_config_id": config.config_id,
            "text_sha256": item.text_sha256,
        }
    )
