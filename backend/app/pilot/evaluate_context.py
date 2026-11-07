"""Re-score assembled evidence on frozen development retrieval; no provider calls."""
from datetime import datetime, timezone
import hashlib
import json
from statistics import fmean
from uuid import uuid4

from app.evaluation.evidence import build_evidence_index, score_case
from app.pilot.context import POLICY, assemble, support_ids
from app.pilot.evidence import build_evidence
from app.pilot.settings import ACCEPTED_INDEX, ROOT
from app.retrieval.cli import write_report
from types import SimpleNamespace
from app.pilot.settings import ACCEPTED_COMMIT


def main():
    normalized = ROOT / "data/normalized/corpus/15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc"
    chunks = ROOT / "data/chunks/corpus/2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce"
    baseline = ROOT / "data/evaluations/development/a63c69cd-c64c-4d07-97e6-0869efe8342c.json"
    data = (ROOT / "evaluation/benchmark.json").read_bytes()
    if hashlib.sha256(data).hexdigest() != "e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425":
        raise ValueError("Frozen benchmark changed")
    cases = {c["id"]: c for c in json.loads(data)["cases"] if c["split"] == "development"}
    index = build_evidence_index(normalized, chunks, ROOT / "sources/odoo-documentation")
    by_id = {r["chunk_id"]: r for r in (json.loads(line) for line in (chunks / "chunks.jsonl").read_text().splitlines())}
    config = SimpleNamespace(snapshot_id=ACCEPTED_INDEX, source_commit=ACCEPTED_COMMIT)
    rows = []
    report = json.loads(baseline.read_text())
    if report["status"] != "succeeded" or report["split"] != "development" or len(report["cases"]) != 23:
        raise ValueError("Unexpected frozen development report")
    for row in report["cases"]:
        case = cases[row["case_id"]]
        result = row["result"]
        ids = support_ids(case["question"], result)
        context = assemble(result, [by_id[chunk_id] for chunk_id in ids])
        evidence = build_evidence(context, config)
        selected = {e["chunk_id"] for e in evidence}
        hits = [h for h in context["context_hits"] if h["chunk_id"] in selected]
        scored_hits = [{**hit, "rank": rank, "retrieval_text": hit["chunk_record"]["content"]["retrieval_text"]}
                       for rank, hit in enumerate(hits, start=1)]
        if not scored_hits:
            raise ValueError("Unexpected empty accepted-corpus context")
        score = score_case(case, {**result, "hits": scored_hits, "top_k": len(scored_hits)},
                           index, k=len(scored_hits))
        rows.append({"case_id": case["id"], "baseline": row["score"], "context_score": score,
                     "support_chunk_ids": ids, "evidence_chunk_ids": [h["chunk_id"] for h in hits]})
    scored = [r for r in rows if r["context_score"]["scorable"]]
    outcome = {"schema_version": "pilot-context-development-0.1", "policy": POLICY,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "method": "Frozen K=5 dense results replayed with bounded support passages and the actual 3500-token context builder. Not new retrieval or answer-accuracy measurements.",
        "baseline_sha256": hashlib.sha256(baseline.read_bytes()).hexdigest(),
        "cases": rows, "summary": {"development_cases": len(rows), "answerable_cases": len(scored),
            "complete_evidence_rate": fmean(r["context_score"]["all_required_groups_covered"] for r in scored),
            "mean_evidence_group_coverage": fmean(r["context_score"]["evidence_group_coverage"] for r in scored)}}
    output = ROOT / "data/pilot/context-evaluation" / f"{uuid4()}.json"
    write_report(output, outcome)
    print(json.dumps(outcome["summary"]))
    print("Saved:", output)


if __name__ == "__main__":
    main()
