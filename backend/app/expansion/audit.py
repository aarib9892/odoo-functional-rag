"""Offline, per-page corpus audit. Never calls a provider or changes an index."""
import argparse
from collections import Counter
from dataclasses import asdict
import json
from pathlib import Path

from app.expansion.parsing import FullNormalizer
from app.ingestion.normalized_models import SourceIdentity
from app.ingestion.normalize_corpus import load_inputs
from app.ingestion.reference_index import ReferenceIndex
from app.ingestion.sphinx_reader import parse_diagnostics, read_corpus
from app.retrieval.cli import write_report


def audit(repository, manifest, output):
    files, records = load_inputs(repository, manifest)
    report = {"schema_version": "full-app-audit-0.2", "source": manifest["inventory"]["source"],
              "inventory_fingerprint": manifest["inventory_fingerprint"], "pages": [], "status": "running"}
    output.mkdir(parents=True, exist_ok=True)
    write_report(output / "audit.json", report)
    with read_corpus(files, full_applications=True) as (app, trees, source_root, logs):
        (output / "parser.log").write_text(logs)
        messages = parse_diagnostics(logs)
        report["parser_diagnostics"] = [asdict(m) for m, _ in messages]
        references = ReferenceIndex(app, trees, repository, content_root=True)
        for path, record in sorted(records.items()):
            row = {"source_path": path, "application": record["application"], "status": "quarantined"}
            try:
                doc = FullNormalizer(SourceIdentity(**report["source"], source_path=path,
                    sha256=record["sha256"], application=record["application"]),
                    "full-app-audit-0.2", source_root=source_root, reference_index=references).normalize(
                        trees[path[:-4]], parser_messages=[m for m, _ in messages if m.source.source_path == path])
                target = output / "documents" / (path[:-4] + ".json")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(doc.to_json())
                row.update(status=doc.status, diagnostics=[asdict(d) for d in doc.diagnostics])
            except Exception as error:
                row["error"] = {"type": type(error).__name__, "message": str(error)}
            report["pages"].append(row)
    report["summary"] = dict(Counter(p["status"] for p in report["pages"]))
    report["status"] = "audited"
    write_report(output / "audit.json", report)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", type=Path, default=Path("../sources/odoo-documentation"))
    p.add_argument("--manifest", type=Path, default=Path("../data/expansion/manifest.json"))
    p.add_argument("--output", type=Path, default=Path("../data/expansion/audit"))
    args = p.parse_args()
    result = audit(args.repo.resolve(), json.loads(args.manifest.read_text()), args.output.resolve())
    print(json.dumps(result["summary"]))


if __name__ == "__main__":
    main()
