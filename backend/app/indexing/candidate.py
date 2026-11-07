from pathlib import Path

from app.chunking.snapshot import save_chunk_snapshot
from app.ingestion.normalize_corpus import (
    build_corpus,
    load_inputs,
    write_snapshot,
)
from app.ingestion.repository import get_clean_commit


def prepare_candidate(
    repository: Path,
    manifest: dict,
    normalized_output: Path,
    chunk_output: Path,
    *,
    max_tokens: int = 512,
    include_policy=None,
) -> tuple[Path, Path]:
    """Build complete normalized/chunk snapshots without activating an index."""
    repository = repository.resolve()
    normalized_output = normalized_output.resolve()
    chunk_output = chunk_output.resolve()

    if type(max_tokens) is not int or max_tokens < 1:
        raise ValueError("Token budget must be a positive integer")

    outputs = (normalized_output, chunk_output)
    if any(path.is_relative_to(repository) for path in outputs):
        raise ValueError("Candidate outputs must be outside the source checkout")

    if normalized_output.is_relative_to(chunk_output) or chunk_output.is_relative_to(
        normalized_output
    ):
        raise ValueError("Candidate output directories must not overlap")

    expected_commit = manifest["inventory"]["source"]["commit"]
    if get_clean_commit(repository) != expected_commit:
        raise ValueError("Source checkout differs from the manifest commit")

    build_options = {}

    if include_policy is not None:
        build_options["include_policy"] = include_policy

    documents, _, payload = build_corpus(
        repository,
        manifest,
        **build_options,
    )
    records = manifest["inventory"]["files"]
    expected_paths = {record["source_path"] for record in records}

    if (
        len(expected_paths) != len(records)
        or set(documents) != expected_paths
        or any(document.status != "ok" for document in documents.values())
    ):
        raise ValueError("Candidate must contain every expected document successfully")

    if get_clean_commit(repository) != expected_commit:
        raise ValueError("Source checkout changed during candidate preparation")
    load_inputs(repository, manifest)

    normalized, _ = write_snapshot(normalized_output, payload)
    chunks, _, _ = save_chunk_snapshot(normalized, chunk_output, max_tokens=max_tokens)
    return normalized, chunks
