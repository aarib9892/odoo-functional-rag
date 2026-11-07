"""Metered development-only live smoke. Never reads holdout questions for selection."""
import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from openai import AsyncOpenAI

from app.pilot.generation import Generator
from app.pilot.service import AnswerService
from app.pilot.settings import ROOT, Settings
from app.retrieval.cli import write_report

CASES = ("M12-DRAFT-001", "M12-DRAFT-004", "M12-DRAFT-010", "M12-DRAFT-007", "M12-DRAFT-027")


async def run(limit, offset=0):
    settings = Settings.from_env()
    benchmark_bytes = (ROOT / "evaluation/benchmark.json").read_bytes()
    if hashlib.sha256(benchmark_bytes).hexdigest() != "e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425":
        raise ValueError("Benchmark bytes changed")
    development = {c["id"]: c for c in json.loads(benchmark_bytes)["cases"] if c["split"] == "development"}
    run_id = str(uuid4())
    path = ROOT / "data/pilot/smoke" / f"{run_id}.json"
    report = {"run_id": run_id, "created_at": datetime.now(timezone.utc).isoformat(),
              "kind": "live_development_smoke_not_accuracy_evaluation", "model": settings.model,
              "retrieval_k": 5, "cases": []}
    async with AsyncOpenAI(timeout=45, max_retries=0) as client:
        service = AnswerService(settings, Generator(settings.model, client, settings.reasoning_effort))
        for case_id in CASES[offset:offset + limit]:
            case = development[case_id]
            row = {"case_id": case_id, "question": case["question"], "expected_behavior": case["expected_behavior"]}
            try:
                telemetry = {}
                async with asyncio.timeout(settings.request_timeout):
                    row["response"] = await service.answer(case["question"], "19.0", [], str(uuid4()), client=client, telemetry=telemetry)
                row["audit"] = telemetry.get("_audit")
                print(case_id, row["response"]["status"], row["response"]["trace"]["validation"], flush=True)
            except Exception as error:
                row["error"] = {"kind": type(error).__name__, "status_code": getattr(error, "status_code", None)}
                print(case_id, "failed", type(error).__name__, flush=True)
            report["cases"].append(row)
            write_report(path, report)
            if row.get("error"):
                break  # Do not spend further on a misconfigured provider.
    print("Saved:", path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, choices=range(1, 6), default=1)
    parser.add_argument("--offset", type=int, choices=range(5), default=0)
    args = parser.parse_args()
    load_dotenv(ROOT / "backend/.env")
    load_dotenv(ROOT / "backend/.env.pilot")
    asyncio.run(run(args.limit, args.offset))


if __name__ == "__main__":
    main()
