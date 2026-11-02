"""Retrieve documentation for one question and save a separate run report."""

import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from uuid import uuid4

from app.embeddings.cache import EmbeddingCache
from app.retrieval.query import retrieve_question


def write_report(path: Path, report: dict) -> None:
    encoded = (
        json.dumps(
            report, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False
        )
        + "\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".retrieval-run-", dir=path.parent) as temporary:
        staging = Path(temporary) / "report.json"
        staging.write_text(encoded, encoding="utf-8")
        staging.replace(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--question", required=True)
    parser.add_argument("--corpus", default="odoo19")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument(
        "--cache", type=Path, default=Path("../data/embeddings/query-cache")
    )
    parser.add_argument("--reports", type=Path, default=Path("../data/retrieval/runs"))
    args = parser.parse_args(argv)
    if not args.question.strip() or not args.corpus.strip() or args.top_k < 1:
        parser.error("Question/corpus must be nonempty and top-k must be positive")
    args.cache = args.cache.resolve()
    args.reports = args.reports.resolve()

    started = perf_counter()
    report = {
        "schema_version": "m33-retrieval-run-0.1",
        "run_id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "stage": "retrieve_question",
        "question": args.question,
        "corpus_name": args.corpus,
        "top_k": args.top_k,
        "query_cache_path": str(args.cache),
        "result": None,
        "error": None,
    }
    report_path = args.reports / f"{report['run_id']}.json"
    try:
        write_report(report_path, report)
    except OSError as error:
        parser.exit(1, f"Cannot create run report: {type(error).__name__}\n")

    retrieval_started = perf_counter()
    try:
        report["result"] = asyncio.run(
            retrieve_question(
                args.question, EmbeddingCache(args.cache), args.corpus, args.top_k
            )
        )
        report.update(status="succeeded", stage="complete")
    except Exception as error:
        report["status"] = "failed"
        report["error"] = {
            "exception": type(error).__name__,
            "http_status": getattr(error, "status_code", None),
            "api_code": getattr(error, "code", None),
            "request_id": getattr(error, "request_id", None),
        }
    report["retrieval_seconds"] = round(perf_counter() - retrieval_started, 6)
    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["duration_seconds"] = round(perf_counter() - started, 6)
    try:
        write_report(report_path, report)
    except OSError as error:
        parser.exit(1, f"Cannot finalize run report: {type(error).__name__}\n")

    print("Status:", report["status"])
    print("Run ID:", report["run_id"])
    if report["result"] is not None:
        result = report["result"]
        usage = result["query_embedding"]
        print("Database snapshot:", result["snapshot_id"])
        print("Query cache hit:", usage["cache_hit"])
        print("API requests:", usage["api_requests"])
        print("Prompt tokens:", usage["prompt_tokens"])
        for hit in result["hits"]:
            content = hit["chunk_record"]["content"]
            print(
                f"{hit['rank']}. distance={hit['distance']:.6f} "
                f"{content['source']['source_path']}"
            )
    else:
        print("Error:", json.dumps(report["error"], sort_keys=True))
    print("Retrieval seconds:", report["retrieval_seconds"])
    print("Run report:", report_path)
    return 0 if report["status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
