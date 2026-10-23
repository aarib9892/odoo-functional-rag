"""Read-only evidence for a normalized snapshot; never expand its corpus."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess

from app.ingestion.normalize_corpus import load_inputs


def checkout_evidence(repository, expected_commit):
    def git(*args):
        return subprocess.run(["git", "-C", str(repository), *args], capture_output=True, text=True)
    try:
        top = git("rev-parse", "--show-toplevel")
        if top.returncode or Path(top.stdout.strip()).resolve() != repository.resolve():
            return {"status": "unavailable", "verified": False}, set()
        commit, status, tracked = git("rev-parse", "HEAD"), git("status", "--porcelain"), git("ls-files", "-z")
        if commit.returncode or status.returncode or tracked.returncode:
            return {"status": "unavailable", "verified": False}, set()
        actual = commit.stdout.strip()
        state = "different_commit" if actual != expected_commit else "dirty" if status.stdout else "clean_pinned"
        return {"status": state, "verified": state == "clean_pinned", "actual_commit": actual,
                "expected_commit": expected_commit}, set(tracked.stdout.split("\0"))
    except OSError:
        return {"status": "unavailable", "verified": False}, set()


def walk(items):
    for item in items:
        yield item
        yield from walk(item.get("items", item.get("children", [])))


def inline_walk(items):
    for item in items:
        yield item
        yield from inline_walk(item.get("children", []))


def inside(repository, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        return None
    candidate = (repository / path).resolve()
    return candidate if candidate.is_relative_to(repository.resolve()) else None


def read_snapshot(snapshot, manifest, repository):
    paths = {p.relative_to(snapshot).as_posix(): p for p in snapshot.rglob("*") if p.is_file()}
    hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in sorted(paths.items())}
    identity = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    if identity != snapshot.name:
        raise ValueError("Snapshot bytes do not match the snapshot directory identity.")
    summary = json.loads((snapshot / "summary.json").read_text(encoding="utf-8"))
    if summary["inventory_fingerprint"] != manifest["inventory_fingerprint"]:
        raise ValueError("Snapshot and manifest inventory fingerprints differ.")
    files, records = load_inputs(repository, manifest)
    documents = {}
    for path, record in records.items():
        document = json.loads((snapshot / "documents" / (path[:-4] + ".json")).read_text(encoding="utf-8"))
        source = document["source"]
        if (source["source_path"] != path or source["sha256"] != record["sha256"]
                or source["commit"] != manifest["inventory"]["source"]["commit"]):
            raise ValueError(f"Snapshot source identity differs from manifest: {path}")
        documents[path] = document
    return documents, files, summary


def audit(documents, manifest, repository):
    checkout, tracked = checkout_evidence(repository, manifest["inventory"]["source"].get("commit", ""))
    discovered = {record["source_path"] for record in manifest["inventory"]["files"]}
    discovered.update(record["source_path"] for record in manifest["inventory"].get("excluded_files", []))
    labels = defaultdict(list)
    available = 0
    for relative in sorted(discovered):
        path = inside(repository, relative)
        if path is None or not path.is_file():
            continue
        available += 1
        for line, content in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            match = re.match(r"^\s*\.\. _([^:]+):\s*$", content)
            if match:
                labels[" ".join(match.group(1).lower().split())].append({"source_path": relative, "line": line})
    references, images = [], []
    for relative, document in sorted(documents.items()):
        for block in walk(document["items"]):
            if "kind" not in block:
                continue
            for inline in inline_walk(block.get("inlines", [])):
                if inline["kind"] != "reference":
                    continue
                attributes = inline["attributes"]
                if attributes.get("resolution") in {"resolved", "external_not_checked"}:
                    continue
                item = {"source_path": relative, "source_line": inline["source"]["line"],
                        "heading_path": block["heading_path"], "text": inline["text"], **attributes}
                if attributes.get("resolution") == "unresolved_label":
                    key = " ".join(attributes["target"].lower().split())
                    item["literal_label_candidates"] = labels.get(key, [])
                    item["candidate_status"] = "source_matches_only_not_resolved"
                elif attributes.get("destination_path"):
                    target = attributes["destination_path"]
                    candidate = inside(repository, target)
                    item["source_file_present"] = candidate is not None and candidate.is_file()
                    item["listed_in_manifest_discovery"] = target in discovered
                references.append(item)
            if block["kind"] == "image":
                attributes = block["attributes"]
                uri = attributes["uri"]
                candidate = inside(repository, uri)
                present = candidate is not None and candidate.is_file()
                images.append({"source_path": relative, "source_line": block["source"]["line"],
                               "heading_path": block["heading_path"], "uri": uri,
                               "alt": attributes.get("alt", ""), "source_file_present": present,
                               "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest() if present else None,
                               "attributed_to_clean_pinned_checkout": bool(present and checkout["verified"] and uri in tracked),
                               "screenshot_semantics": "human_review_required"})
    return {"review_status": "pending", "source": manifest["inventory"]["source"], "checkout_evidence": checkout,
            "discovered_rst_paths": len(discovered), "available_rst_files_scanned": available,
            "unavailable_rst_files": len(discovered) - available,
            "reference_occurrences": references, "image_dependencies": images,
            "reference_states": dict(Counter(item.get("resolution", "unknown") for item in references)),
            "image_files_present": sum(item["source_file_present"] for item in images),
            "image_files_unavailable": sum(not item["source_file_present"] for item in images),
            "limitations": ["Filesystem presence and literal-label matches do not resolve a normalized reference.",
                            "An unavailable file can reflect an incomplete checkout or an invalid target; review the evidence.",
                            "Image existence/hash/alt text do not establish that screenshot-only instructions are captured.",
                            "The selected corpus and normalized snapshot are unchanged."]}
