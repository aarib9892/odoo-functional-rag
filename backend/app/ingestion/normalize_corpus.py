"""Normalize manifest-verified files and save an immutable local snapshot."""

import argparse
from collections import Counter
import hashlib
from importlib.metadata import version
import json
import os
from pathlib import Path, PurePosixPath
import shutil
from tempfile import mkdtemp

from docutils import nodes

from app.ingestion.normalized_models import SourceIdentity
from app.ingestion.normalization import Normalizer, NORMALIZER_VERSION, SCHEMA_VERSION
from app.ingestion.reference_index import ReferenceIndex
from app.ingestion.sphinx_reader import parse_diagnostics, read_corpus


def load_inputs(repository, manifest):
    inventory = manifest["inventory"]
    canonical = json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(canonical).hexdigest() != manifest["inventory_fingerprint"]:
        raise ValueError("The inventory fingerprint does not match its payload.")
    records, files = {}, {}
    for record in inventory["files"]:
        relative = PurePosixPath(record["source_path"])
        if relative.is_absolute() or ".." in relative.parts or relative.suffix != ".rst":
            raise ValueError(f"Invalid source path: {relative}")
        path = relative.as_posix()
        if path in files:
            raise ValueError(f"Duplicate source path: {path}")
        data = (repository / path).read_bytes()
        if len(data) != record["size_bytes"] or hashlib.sha256(data).hexdigest() != record["sha256"]:
            raise ValueError(f"Source bytes do not match manifest: {path}")
        files[path], records[path] = data, record
    if not files:
        raise ValueError("The manifest has no selected files.")
    return files, records


def write_snapshot(output, payload):
    """Rename a complete directory into place; never edit an existing run."""
    inventory = {name: hashlib.sha256(data).hexdigest() for name, data in sorted(payload.items())}
    snapshot_id = hashlib.sha256(json.dumps(inventory, sort_keys=True).encode()).hexdigest()
    output.mkdir(parents=True, exist_ok=True)
    destination = output / snapshot_id
    if destination.exists():
        actual = {path.relative_to(destination).as_posix() for path in destination.rglob("*") if path.is_file()}
        if actual != set(payload) or any((destination / name).read_bytes() != data for name, data in payload.items()):
            raise ValueError("Existing snapshot content does not match its identity.")
        return destination, True
    staging = Path(mkdtemp(prefix=".normalizing-", dir=output))
    try:
        for name, data in sorted(payload.items()):
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        os.rename(staging, destination)
    finally:
        shutil.rmtree(staging, ignore_errors=True)
    return destination, False


def walk(items):
    for item in items:
        yield item
        yield from walk(item.items if hasattr(item, "items") else item.children)


def inlines(items):
    for inline in items:
        yield inline
        yield from inlines(inline.children)


def build_corpus(repository, manifest):
    files, records = load_inputs(repository, manifest)
    versions = {name: version(name) for name in ("docutils", "sphinx", "sphinx-tabs")}
    parser_id = json.dumps({"versions": versions, "adapters": "structures-0.2", "smartquotes": False,
                            "reference_context": manifest["inventory_fingerprint"]}, sort_keys=True)
    documents = {}
    with read_corpus(files) as (app, trees, source_root, logs):
        messages = sorted(parse_diagnostics(logs),
                          key=lambda pair: (pair[0].source.source_path, pair[0].source.line or 0,
                                            pair[0].code, pair[0].message))
        errors = [node for tree in trees.values() for node in tree.findall(nodes.system_message)
                  if node["level"] >= 3]
        if errors or any(message.severity == "error" for message, raw in messages):
            raise ValueError("Corpus parsing has errors; no normalized snapshot was saved.\n" + logs)
        references = ReferenceIndex(app, trees, repository)
        for path, record in sorted(records.items()):
            source = SourceIdentity(**manifest["inventory"]["source"], source_path=path,
                                    sha256=record["sha256"], application=record["application"])
            own_messages = [(message, raw) for message, raw in messages if message.source.source_path == path]
            normalizer = Normalizer(source, parser_id, source_root=source_root, reference_index=references)
            document = normalizer.normalize(trees[path[:-4]], "\n".join(raw for message, raw in own_messages),
                                            [message for message, raw in own_messages])
            documents[path] = document
    issues = [(path, issue) for path, document in documents.items() for issue in document.diagnostics]
    if issues:
        details = "\n".join(f"{path}:{issue.source.line}: {issue.code}: {issue.message}" for path, issue in issues)
        raise ValueError("Unsupported structures remain; no complete snapshot was saved.\n" + details)
    blocks, reference_states = Counter(), Counter()
    for document in documents.values():
        for item in walk(document.items):
            if hasattr(item, "kind"):
                blocks[item.kind] += 1
                for inline in inlines(item.inlines):
                    if inline.kind == "reference":
                        reference_states[inline.attributes["resolution"]] += 1
    summary = {
        "schema_version": SCHEMA_VERSION, "normalizer_version": NORMALIZER_VERSION,
        "inventory_fingerprint": manifest["inventory_fingerprint"], "versions": versions,
        "source": manifest["inventory"]["source"], "normalized_documents": len(documents),
        "unsupported_node_diagnostics": len(issues), "block_kinds": dict(sorted(blocks.items())),
        "inline_reference_states": dict(sorted(reference_states.items())),
        "parser_diagnostic_types": dict(sorted(Counter(message.code for message, raw in messages).items())),
        "global_parser_messages": [message.message for message, raw in messages if not message.source.source_path],
        "limitations": ["Git cleanliness is not rechecked; selected bytes match the inventory.",
                        "Image assets and external URLs are not validated.",
                        "Targets not in the corpus have unverified existence; unresolved labels are not declared broken.",
                        "Rendered-page fidelity and full ingestion acceptance remain pending."],
    }
    payload = {"documents/" + path[:-4] + ".json": document.to_json().encode("utf-8")
               for path, document in documents.items()}
    payload["summary.json"] = (json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()
    payload["diagnostics.txt"] = ("\n".join(raw for message, raw in messages) + "\n").encode()
    return documents, summary, payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("../sources/odoo-documentation"))
    parser.add_argument("--manifest", type=Path, default=Path("../data/manifests/odoo19-corpus.json"))
    parser.add_argument("--output", type=Path, default=Path("../data/normalized/corpus"))
    parser.add_argument("--check-fixtures", action="store_true", help="Check the pinned M1.2 preservation fixtures.")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    documents, summary, payload = build_corpus(args.repo.resolve(), manifest)
    if args.check_fixtures:
        from app.ingestion.normalization_checks import check_documents
        check_documents(documents)
        print("Fixture preservation checks passed.")
    destination, reused = write_snapshot(args.output.resolve(), payload)
    print("Manifest files verified:", len(documents))
    print("Normalized documents:", summary["normalized_documents"])
    print("Unsupported-node diagnostics:", summary["unsupported_node_diagnostics"])
    print("Inline reference states:", summary["inline_reference_states"])
    print("Parser diagnostic headers:", sum(summary["parser_diagnostic_types"].values()))
    print("Snapshot reused:", reused)
    print("Saved:", destination)


if __name__ == "__main__":
    main()
