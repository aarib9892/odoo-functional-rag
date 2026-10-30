"""Generate missing embeddings, publish a snapshot and save a run report."""

import argparse
import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from uuid import uuid4

from app.embeddings.cache import EmbeddingCache
from app.embeddings.config import EmbeddingConfig
from app.embeddings.inputs import load_embedding_inputs
from app.embeddings.job import generate_embeddings
from app.embeddings.snapshot import save_embedding_snapshot


def write_report(path: Path, report: dict) -> None:
    encoded = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".embedding-run-", dir=path.parent) as temporary:
        staging = Path(temporary) / "report.json"
        staging.write_text(encoded, encoding="utf-8")
        staging.replace(path)


async def execute(args, config: EmbeddingConfig, report: dict) -> None:
    inputs = load_embedding_inputs(args.snapshot)
    cache = EmbeddingCache(args.cache)

    report["stage"] = "generate_embeddings"
    report["generation"] = await generate_embeddings(
        inputs, config, cache, batch_size=args.batch_size
    )

    report["stage"] = "publish_snapshot"
    destination, summary, reused = save_embedding_snapshot(
        args.snapshot, args.output, config, cache
    )
    report.update(
        status="succeeded",
        stage="complete",
        embedding_snapshot_id=destination.name,
        embedding_snapshot_path=str(destination),
        embedding_records=summary["embedding_records"],
        snapshot_reused=reused,
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=Path("../data/embeddings/cache"))
    parser.add_argument(
        "--output", type=Path, default=Path("../data/embeddings/corpus")
    )
    parser.add_argument("--reports", type=Path, default=Path("../data/embeddings/runs"))
    parser.add_argument("--model", default="text-embedding-3-small")
    parser.add_argument("--dimensions", type=int, default=1536)
    parser.add_argument("--batch-size", type=int, default=64)
    args = parser.parse_args(argv)

    for name in ("snapshot", "cache", "output", "reports"):
        setattr(args, name, getattr(args, name).resolve())

    for target in (args.cache, args.output, args.reports):
        if target.is_relative_to(args.snapshot):
            parser.error("Write destinations must be outside the input snapshot")

    try:
        config = EmbeddingConfig(model=args.model, dimensions=args.dimensions)
    except ValueError as error:
        parser.error(str(error))

    if not 1 <= args.batch_size <= 2048:
        parser.error("batch-size must be between 1 and 2048")

    started = perf_counter()
    report = {
        "schema_version": "m32-embedding-run-0.1",
        "run_id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "stage": "load_inputs",
        "chunk_snapshot_id": args.snapshot.name,
        "embedding_config": asdict(config),
        "embedding_config_id": config.config_id,
        "generation": None,
        "embedding_snapshot_id": None,
        "error": None,
    }
    report_path = args.reports / f"{report['run_id']}.json"

    try:
        write_report(report_path, report)
    except OSError as error:
        parser.exit(1, f"Cannot create run report: {type(error).__name__}\n")

    try:
        asyncio.run(execute(args, config, report))
    except Exception as error:
        report["status"] = "failed"
        report["error"] = {
            "exception": type(error).__name__,
            "http_status": getattr(error, "status_code", None),
            "api_code": getattr(error, "code", None),
            "request_id": getattr(error, "request_id", None),
        }

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["duration_seconds"] = round(perf_counter() - started, 3)

    try:
        write_report(report_path, report)
    except OSError as error:
        parser.exit(1, f"Cannot finalize run report: {type(error).__name__}\n")

    print(json.dumps(report, indent=2))
    print("Run report:", report_path)
    return 0 if report["status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
