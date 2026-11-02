import hashlib
import json
from pathlib import Path

from app.chunking.eligibility import has_body_content
from app.chunking.snapshot import fingerprint, read_files
from app.chunking.walk import iter_blocks
from app.embeddings.inputs import load_embedding_inputs

ALIGNMENT_VERSION = "m3-paragraph-evidence-0.1"


def _nodes(block):
    yield block
    for child in block["children"]:
        yield from _nodes(child)


def build_evidence_index(normalized: Path, chunks: Path, repository: Path) -> dict:
    normalized_files, chunk_files = read_files(normalized), read_files(chunks)
    if (
        fingerprint(normalized_files) != normalized.name
        or fingerprint(chunk_files) != chunks.name
    ):
        raise ValueError("Evidence snapshot fingerprint mismatch")

    summary = json.loads(normalized_files["summary.json"])
    chunk_summary = json.loads(chunk_files["summary.json"])
    if (
        chunk_summary["schema_version"] != "m31-chunk-snapshot-0.2"
        or chunk_summary["normalized_snapshot_id"] != normalized.name
        or chunk_summary["source"] != summary["source"]
        or chunk_summary["inventory_fingerprint"] != summary["inventory_fingerprint"]
    ):
        raise ValueError("Evidence snapshot lineage mismatch")

    records = [json.loads(line) for line in chunk_files["chunks.jsonl"].splitlines()]
    by_id = {record["chunk_id"]: record for record in records}
    if len(by_id) != len(records) or len(records) != chunk_summary["chunk_records"]:
        raise ValueError("Invalid reference chunk membership")
    eligible_ids = {item.chunk_id for item in load_embedding_inputs(chunks)}

    repository = repository.resolve()
    files = {}
    names = sorted(
        name
        for name in normalized_files
        if name.startswith("documents/") and name.endswith(".json")
    )
    if len(names) != summary["normalized_documents"]:
        raise ValueError("Normalized document count mismatch")

    for name in names:
        document = json.loads(normalized_files[name])
        source = document["source"]
        relative = source["source_path"]
        path = (repository / relative).resolve()
        if not path.is_relative_to(repository):
            raise ValueError("Source path escapes the repository")

        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != source["sha256"]:
            raise ValueError("Source file differs from normalized evidence")
        if any(source[key] != value for key, value in summary["source"].items()):
            raise ValueError("Document source differs from corpus")

        lines = data.decode("utf-8").splitlines()
        roots = list(iter_blocks(document["items"]))
        starts = {}
        for root in roots:
            anchors = [
                node["source"]["line"]
                for node in _nodes(root)
                if node["source"]["line_origin"] == "node"
                and node["source"]["source_path"] == relative
                and type(node["source"]["line"]) is int
            ]
            if anchors:
                starts[root["block_id"]] = min(anchors)

        spans = []
        for root in roots:
            if not has_body_content(root):
                continue
            for node in _nodes(root):
                if node["kind"] != "paragraph":
                    continue
                location = node["source"]
                start = location["line"]
                if (
                    location["line_origin"] != "node"
                    or location["source_path"] != relative
                    or type(start) is not int
                    or not 1 <= start <= len(lines)
                    or not lines[start - 1].strip()
                ):
                    raise ValueError("Paragraph has no reliable source position")

                stop = (
                    min(
                        [
                            line
                            for block_id, line in starts.items()
                            if block_id != root["block_id"] and line > start
                        ]
                        + [len(lines) + 1]
                    )
                    - 1
                )
                end = start
                while end < stop and lines[end].strip():
                    end += 1
                spans.append((root["block_id"], start, end))

        if relative in files:
            raise ValueError("Duplicate normalized source path")
        files[relative] = {
            "sha256": source["sha256"],
            "line_count": len(lines),
            "spans": spans,
        }

    return {
        "alignment_version": ALIGNMENT_VERSION,
        "source": summary["source"],
        "normalized_snapshot_id": normalized.name,
        "chunk_snapshot_id": chunks.name,
        "chunks": by_id,
        "eligible_ids": eligible_ids,
        "files": files,
    }


def target_units(target: dict, index: dict) -> set[tuple[str, str]]:
    path = target["source_path"]
    source = index["files"][path]
    start, end = target["line_start"], target["line_end"]

    if source["sha256"] != target["sha256"]:
        raise ValueError("Benchmark source hash differs from evidence")
    if (
        type(start) is not int
        or type(end) is not int
        or not 1 <= start <= end <= source["line_count"]
    ):
        raise ValueError("Invalid benchmark source span")

    units = {
        (path, block_id)
        for block_id, first, last in source["spans"]
        if first <= end and start <= last
    }
    if not units:
        raise ValueError("Target has no paragraph alignment; review it before scoring")
    return units


def score_case(case: dict, result: dict, index: dict, k: int = 5) -> dict:
    if type(k) is not int or k < 1:
        raise ValueError("k must be a positive integer")
    if result["query"]["text"] != case["question"]:
        raise ValueError("Retrieval question differs from benchmark case")

    for case_key, source_key in (
        ("source_commit", "commit"),
        ("language", "language"),
        ("odoo_version", "odoo_version"),
    ):
        if case[case_key] != index["source"][source_key]:
            raise ValueError("Benchmark source identity differs from evidence")

    if case["expected_behavior"] != "answer":
        return {
            "case_id": case["id"],
            "scorable": False,
            "reason": "requires_behavior_evaluation",
            "k": k,
        }
    if result["top_k"] < k:
        raise ValueError("Retrieval depth is smaller than scoring cutoff")
    if len(result["hits"]) != min(result["top_k"], len(index["eligible_ids"])):
        raise ValueError("Retrieved hit count differs from requested depth")

    hit_units = []
    seen = set()
    for rank, hit in enumerate(result["hits"], start=1):
        chunk = index["chunks"].get(hit["chunk_id"])
        if (
            chunk is None
            or hit["chunk_id"] not in index["eligible_ids"]
            or hit["rank"] != rank
            or hit["chunk_id"] in seen
            or chunk != hit["chunk_record"]
            or hit["retrieval_text"] != chunk["content"]["retrieval_text"]
        ):
            raise ValueError("Retrieved evidence differs from reference chunks")

        seen.add(hit["chunk_id"])
        path = chunk["content"]["source"]["source_path"]
        hit_units.append(
            {(path, block_id) for block_id in chunk["content"]["source_block_ids"]}
        )

    hit_units = hit_units[:k]
    retrieved = set().union(*hit_units)
    groups, relevant = [], set()

    for group in case["evidence_groups"]:
        if not group["required"]:
            continue
        if group["target_match"] not in ("all", "any") or not group["targets"]:
            raise ValueError("Invalid required evidence group")

        targets = [target_units(target, index) for target in group["targets"]]
        relevant.update(set().union(*targets))
        covered = [units <= retrieved for units in targets]
        complete = all(covered) if group["target_match"] == "all" else any(covered)
        groups.append(
            {
                "fact": group["fact"],
                "covered": complete,
                "target_units": [sorted(units) for units in targets],
            }
        )

    if not groups:
        raise ValueError("Answerable case has no required evidence groups")

    first = next(
        (rank for rank, units in enumerate(hit_units, start=1) if units & relevant),
        None,
    )
    covered_count = sum(group["covered"] for group in groups)
    return {
        "case_id": case["id"],
        "scorable": True,
        "k": k,
        "alignment_version": index["alignment_version"],
        "hit_at_k": first is not None,
        "reciprocal_rank_at_k": 0.0 if first is None else 1.0 / first,
        "evidence_group_coverage": covered_count / len(groups),
        "all_required_groups_covered": covered_count == len(groups),
        "groups": groups,
    }
