from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from app.chunking.snapshot import fingerprint, read_files


@dataclass(frozen=True)
class EmbeddingInput:
    chunk_id: str
    text: str
    text_sha256: str
    token_count: int


def load_embedding_inputs(snapshot: Path) -> list[EmbeddingInput]:
    files = read_files(snapshot)
    if fingerprint(files) != snapshot.name:
        raise ValueError("Chunk snapshot fingerprint mismatch")

    summary = json.loads(files["summary.json"])
    if summary["schema_version"] != "m31-chunk-snapshot-0.2":
        raise ValueError("Expected a classified chunk snapshot")

    records = [json.loads(line) for line in files["chunks.jsonl"].splitlines()]
    decisions = [json.loads(line) for line in files["eligibility.jsonl"].splitlines()]

    ids = [record["chunk_id"] for record in records]
    if (
        ids != [decision["chunk_id"] for decision in decisions]
        or len(ids) != len(set(ids))
        or len(records) != summary["chunk_records"]
    ):
        raise ValueError("Chunk and eligibility records do not match")

    inputs = []

    for record, decision in zip(records, decisions, strict=True):
        eligible = decision["eligible_for_retrieval"]

        if (
            not isinstance(eligible, bool)
            or decision["eligibility_version"] != summary["eligibility_version"]
        ):
            raise ValueError("Invalid eligibility decision")

        if not eligible:
            continue

        text = record["content"]["retrieval_text"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Embedding text must be a nonempty string")

        inputs.append(
            EmbeddingInput(
                chunk_id=record["chunk_id"],
                text=text,
                text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                token_count=record["token_count"],
            )
        )

    if (
        len(inputs) != summary["eligible_chunk_records"]
        or len(records) - len(inputs) != summary["metadata_only_chunk_records"]
    ):
        raise ValueError("Eligibility totals differ from the snapshot summary")

    return inputs
