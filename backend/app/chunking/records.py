from dataclasses import asdict
import hashlib
import json

from app.chunking.models import ChunkDraft
from app.chunking.text import RENDERER_VERSION
from app.chunking.tokens import ENCODING_NAME, TOKENIZER_VERSION, count_tokens

SCHEMA_VERSION = "m31-chunk-0.1"
CHUNKER_VERSION = "m31-section-images-greedy-0.1"


def stable_hash(value: dict) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def finalize_chunk(draft: ChunkDraft, max_tokens: int = 512) -> dict:
    """Create a serializable chunk record without writing any files."""
    if max_tokens < 1:
        raise ValueError("Token budget must be positive")

    if draft.renderer_version != RENDERER_VERSION:
        raise ValueError("Draft renderer does not match the current renderer")

    token_count = count_tokens(draft.retrieval_text)

    if token_count > max_tokens:
        raise ValueError("Chunk exceeds the token budget")

    config = {
        "chunker_version": CHUNKER_VERSION,
        "renderer_version": RENDERER_VERSION,
        "max_tokens": max_tokens,
        "encoding_name": ENCODING_NAME,
        "tokenizer_version": TOKENIZER_VERSION,
    }

    body = {
        "schema_version": SCHEMA_VERSION,
        "chunking_config_id": stable_hash(config),
        "chunking_config": config,
        "token_count": token_count,
        "content": asdict(draft),
    }

    return {"chunk_id": stable_hash(body), **body}
