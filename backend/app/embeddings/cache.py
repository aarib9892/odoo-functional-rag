from dataclasses import asdict
import json
import math
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from app.chunking.records import stable_hash
from app.embeddings.config import EmbeddingConfig, embedding_cache_key
from app.embeddings.inputs import EmbeddingInput


def validate_vector(vector: list[float], dimensions: int) -> list[float]:
    if len(vector) != dimensions:
        raise ValueError(f"Expected {dimensions} embedding dimensions")

    if any(type(n) not in (int, float) or not math.isfinite(n) for n in vector):
        raise ValueError("Embedding values must be finite numbers")

    if not any(vector):
        raise ValueError("Embedding vector must not be all zeros")

    return [float(n) for n in vector]


class EmbeddingCache:
    def __init__(self, directory: Path):
        self.directory = directory

    def store(
        self,
        item: EmbeddingInput,
        config: EmbeddingConfig,
        vector: list[float],
    ) -> Path:
        numbers = validate_vector(vector, config.dimensions)
        key = embedding_cache_key(item, config)
        path = self.directory / f"{key}.json"

        existing = self.load(item, config)
        if existing is not None:
            if existing != numbers:
                raise ValueError("A different vector is already cached for this key")
            return path

        body = {
            "schema_version": "m32-embedding-cache-0.1",
            "cache_key": key,
            "embedding_config_id": config.config_id,
            "embedding_config": asdict(config),
            "text_sha256": item.text_sha256,
            "vector": numbers,
        }
        record = {"record_sha256": stable_hash(body), **body}
        encoded = (
            json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False)
            + "\n"
        )

        self.directory.mkdir(parents=True, exist_ok=True)

        with TemporaryDirectory(prefix=".embedding-", dir=self.directory) as temporary:
            staging = Path(temporary) / "vector.json"
            staging.write_text(encoded, encoding="utf-8")

            try:
                os.link(staging, path)
            except FileExistsError:
                if self.load(item, config) != numbers:
                    raise ValueError(
                        "A different vector is already cached for this key"
                    )

        return path

    def load(self, item: EmbeddingInput, config: EmbeddingConfig) -> list[float] | None:
        key = embedding_cache_key(item, config)
        path = self.directory / f"{key}.json"

        try:
            data = path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return None

        record = json.loads(data)
        checksum = record.pop("record_sha256")

        if stable_hash(record) != checksum:
            raise ValueError("Cached embedding checksum mismatch")

        if (
            record["schema_version"] != "m32-embedding-cache-0.1"
            or record["cache_key"] != key
            or record["embedding_config_id"] != config.config_id
            or record["embedding_config"] != asdict(config)
            or record["text_sha256"] != item.text_sha256
        ):
            raise ValueError("Cached embedding identity mismatch")

        return validate_vector(record["vector"], config.dimensions)
