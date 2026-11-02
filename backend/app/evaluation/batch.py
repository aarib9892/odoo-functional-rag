from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
from statistics import fmean, median
from time import perf_counter
from uuid import uuid4

from app.database import connect_database
from app.embeddings.cache import EmbeddingCache
from app.evaluation.evidence import build_evidence_index, score_case, target_units
from app.retrieval.cli import write_report
from app.retrieval.query import retrieve_question

BENCHMARK_SHA256 = "e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425"


def _error(error) -> dict:
    return {
        "exception": type(error).__name__,
        "http_status": getattr(error, "status_code", None),
        "api_code": getattr(error, "code", None),
        "request_id": getattr(error, "request_id", None),
    }


def _metrics(rows: list[dict]) -> dict | None:
    scores = [row["score"] for row in rows if row["score"]["scorable"]]
    if not scores:
        return None
    return {
        "cases": len(scores),
        "hit_at_k": fmean(score["hit_at_k"] for score in scores),
        "mrr_at_k": fmean(score["reciprocal_rank_at_k"] for score in scores),
        "mean_evidence_group_coverage": fmean(
            score["evidence_group_coverage"] for score in scores
        ),
        "complete_evidence_rate": fmean(
            score["all_required_groups_covered"] for score in scores
        ),
    }


def _timing(rows: list[dict]) -> dict:
    values = sorted(row["retrieval_seconds"] for row in rows)
    return {
        "count": len(values),
        "median_seconds": median(values) if values else None,
        "p95_seconds": values[math.ceil(0.95 * len(values)) - 1] if values else None,
    }


def _summary(report: dict) -> dict:
    rows = report["cases"]
    done = [row for row in rows if row["status"] == "succeeded"]
    returned = [row for row in rows if row["result"] is not None]
    usage = [row["result"]["query_embedding"] for row in returned]
    complete = report["status"] == "succeeded"
    return {
        "planned_cases": report.get("planned_cases"),
        "completed_cases": len(done),
        "failed_cases": sum(row["status"] == "failed" for row in rows),
        "metrics_at_k": _metrics(done) if complete else None,
        "metrics_by_type": (
            {
                kind: _metrics([row for row in done if row["type"] == kind])
                for kind in sorted({row["type"] for row in done})
            }
            if complete
            else None
        ),
        "latency_seconds": {
            "all_returned": _timing(returned),
            "cache_hit": _timing(
                [
                    row
                    for row in returned
                    if row["result"]["query_embedding"]["cache_hit"]
                ]
            ),
            "api_generated": _timing(
                [
                    row
                    for row in returned
                    if not row["result"]["query_embedding"]["cache_hit"]
                ]
            ),
        },
        "usage_from_returned_results": {
            "cache_hits": sum(item["cache_hit"] for item in usage),
            "api_requests": sum(item["api_requests"] for item in usage),
            "prompt_tokens": sum(item["prompt_tokens"] for item in usage),
            "total_tokens": sum(item["total_tokens"] for item in usage),
            "request_ids": [
                request_id for item in usage for request_id in item["request_ids"]
            ],
        },
        "failed_results_unavailable": sum(
            row["status"] == "failed" and row["result"] is None for row in rows
        ),
    }


async def evaluate_development(
    benchmark: Path,
    normalized: Path,
    chunks: Path,
    repository: Path,
    cache: EmbeddingCache,
    output: Path,
    corpus_name: str = "odoo19",
    k: int = 5,
) -> tuple[Path, dict]:
    if (
        type(k) is not int
        or k < 1
        or not isinstance(corpus_name, str)
        or not corpus_name.strip()
    ):
        raise ValueError("Use a positive K and nonempty corpus name")
    for target in (cache.directory, output):
        if any(
            target.resolve().is_relative_to(root.resolve())
            for root in (normalized, chunks, repository)
        ):
            raise ValueError(
                "Write destinations must be outside source snapshots/repository"
            )

    started = perf_counter()
    report = {
        "schema_version": "m3-development-evaluation-0.1",
        "run_id": str(uuid4()),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "running",
        "stage": "preflight",
        "split": "development",
        "k": k,
        "corpus_name": corpus_name,
        "cases": [],
        "error": None,
        "benchmark_path": str(benchmark.resolve()),
        "benchmark_sha256": None,
        "query_cache_path": str(cache.directory.resolve()),
    }
    destination = output.resolve() / f"{report['run_id']}.json"
    write_report(destination, report)
    current, retrieval_started = None, None

    try:
        data = benchmark.read_bytes()
        benchmark_hash = hashlib.sha256(data).hexdigest()
        report["benchmark_sha256"] = benchmark_hash
        if benchmark_hash != BENCHMARK_SHA256:
            raise ValueError("Benchmark differs from accepted m12-1.0 bytes")

        specification = json.loads(data)
        cases = [
            case for case in specification["cases"] if case["split"] == "development"
        ]
        if (
            specification["benchmark_version"] != "m12-1.0"
            or len(cases) != 23
            or len({case["id"] for case in cases}) != 23
        ):
            raise ValueError("Unexpected development benchmark")
        if any(case["review_status"] != "accepted_by_user" for case in cases):
            raise ValueError("Development cases must be reviewed")

        index = build_evidence_index(normalized, chunks, repository)
        if specification["source"] != index["source"]:
            raise ValueError("Benchmark and corpus source differ")
        for case in cases:
            if case["expected_behavior"] == "answer":
                for group in case["evidence_groups"]:
                    if group["required"]:
                        for target in group["targets"]:
                            target_units(target, index)

        report["stage"] = "pin_index"
        async with connect_database() as connection:
            snapshot = await connection.fetchrow(
                """
                SELECT s.snapshot_id, s.chunk_snapshot_id, s.embedding_snapshot_id,
                       s.embedding_config_id, s.embedding_config
                FROM active_indexes a
                JOIN index_snapshots s ON s.snapshot_id = a.snapshot_id
                WHERE a.corpus_name = $1 AND s.published
            """,
                corpus_name,
            )
        if snapshot is None or snapshot["chunk_snapshot_id"] != chunks.name:
            raise ValueError("Active index differs from the reference chunk snapshot")

        context = dict(snapshot)
        context["embedding_config"] = json.loads(context["embedding_config"])
        report.update(
            context=context,
            benchmark_sha256=benchmark_hash,
            benchmark_version=specification["benchmark_version"],
            normalized_snapshot_id=normalized.name,
            alignment_version=index["alignment_version"],
            planned_cases=len(cases),
        )

        for number, case in enumerate(cases, start=1):
            current = {
                "case_id": case["id"],
                "type": case["type"],
                "status": "running",
                "stage": "retrieve_question",
                "result": None,
                "score": None,
                "retrieval_seconds": None,
                "error": None,
            }
            report["cases"].append(current)
            report["stage"] = "evaluate_cases"
            retrieval_started = None
            write_report(destination, report)

            retrieval_started = perf_counter()
            result = await retrieve_question(case["question"], cache, corpus_name, k)
            current["retrieval_seconds"] = round(perf_counter() - retrieval_started, 6)
            current["result"] = result
            current["stage"] = "verify_context_and_score"

            if (
                result["snapshot_id"] != context["snapshot_id"]
                or result["embedding_config_id"] != context["embedding_config_id"]
            ):
                raise ValueError("Index context changed during the evaluation")

            current["score"] = score_case(case, result, index, k)
            current.update(status="succeeded", stage="complete")
            write_report(destination, report)
            print(f"[{number}/{len(cases)}] {case['id']}: succeeded", flush=True)

        report.update(status="succeeded", stage="complete")
    except Exception as error:
        report.update(status="failed", error=_error(error))
        if current is not None and current["status"] == "running":
            current.update(status="failed", error=_error(error))
            if current["retrieval_seconds"] is None and retrieval_started is not None:
                current["retrieval_seconds"] = round(
                    perf_counter() - retrieval_started, 6
                )

    report["finished_at"] = datetime.now(timezone.utc).isoformat()
    report["duration_seconds"] = round(perf_counter() - started, 6)
    report["summary"] = _summary(report)
    write_report(destination, report)
    return destination, report
