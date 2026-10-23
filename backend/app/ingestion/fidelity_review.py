"""Generate a read-only source/rendered/normalized review and dependency audit."""

import argparse
from html import escape
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from app.ingestion.fidelity_audit import audit, read_snapshot
from app.ingestion.fidelity_html import build_source_html, normalized_page, source_page
from app.ingestion.normalize_corpus import write_snapshot


SNAPSHOT = "15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc"
BASE = "content/applications/inventory_and_mrp/inventory/"
FIXTURES = [
    ("content/applications/sales/sales/invoicing/invoicing_policy.rst", "Warnings, examples and invoicing flow", "Compare the important/warning blocks and nested image, ordered/delivered workflows and 50/40/10 quantities."),
    (BASE + "product_management/configure/type.rst", "Table relationships", "Check Tracked/Untracked headers, row labels and Yes/No cells; inspect the surrounding prerequisites."),
    (BASE + "shipping_receiving/reservation_methods.rst", "All tab panels", "Open all three source tabs and compare each label, conditions and explanation with its expanded normalized panel."),
    (BASE + "shipping_receiving/daily_operations.rst", "Cards and navigation", "Compare seven card labels/descriptions/targets and original navigation metadata; unstaged pages remain outside the corpus."),
    (BASE + "shipping_receiving/daily_operations/receipts_delivery_one_step.rst", "Procedure order and substitutions", "Check PO/SO/RfQ meanings, confirmation versus delivery validation and step order."),
    (BASE + "shipping_receiving/setup_configuration/new_delivery_method.rst", "Formula and worked example", "Compare the complete formula and its association with the $31/$64 example. Formula views show LaTeX text, not typeset math."),
    (BASE + "warehouses_storage/reporting/moves_history.rst", "Second tab group", "Check every tab's filters/grouping/favorites instructions and UI labels."),
    ("content/applications/finance/accounting/customer_invoices/credit_notes.rst", "Screenshot-dependent information", "Inspect journal-entry screenshots. Record any answer-critical information available only in images; missing assets leave this check blocked."),
]


def index_html(entries, report):
    data = json.dumps({"entries": entries, "snapshot_id": report["normalized_snapshot_id"], "checkout_evidence": report["checkout_evidence"], "image_files_present": report["image_files_present"], "image_dependencies": len(report["image_dependencies"])}, ensure_ascii=False).replace("<", "\\u003c")
    options = ''.join(f'<option value="{i}">{escape(entry["title"])}</option>' for i, entry in enumerate(entries))
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>M2 fidelity review</title><style>
*{box-sizing:border-box}body{margin:0;background:#eef3f3;color:#17333b;font:14px/1.5 system-ui}
header{padding:18px 24px;background:#173c46;color:#fff}h1{margin:0;font-size:25px}header p{margin:6px 0;max-width:1150px}
.controls{padding:14px 24px;background:white;display:flex;flex-wrap:wrap;gap:12px;align-items:center}select,input,button{font:inherit;padding:8px;border:1px solid #acc1c3;border-radius:4px}
button{background:#176c71;color:#fff;cursor:pointer}a{color:#146c71}.notice{padding:12px 24px;background:#fff4d9}
.panes{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;padding:12px;height:67vh;min-height:480px}
.pane{display:flex;flex-direction:column;background:#fff;border:1px solid #c5d4d5;min-width:0}.pane h2{font-size:14px;margin:0;padding:10px;background:#deebeb}
iframe{border:0;flex:1;width:100%;background:white}.decision{padding:14px 24px;background:white}textarea{display:block;width:100%;font:inherit;padding:10px;margin-top:8px}
.links{padding:12px 24px}code{overflow-wrap:anywhere}@media(max-width:1050px){.panes{grid-template-columns:1fr;height:auto}.pane{height:65vh}}
</style><header><h1>M2 fidelity review</h1><p>Compare the pinned RST, a controlled Sphinx HTML rendering, and an independent rendering of the normalized records.</p>
<p>Content and structure are the review target. The source view uses a basic theme, literal icon names and offline LaTeX text; it does not reproduce Odoo's website theme.</p></header>
<div class="notice">Review is pending. Source images may be unavailable. A successful build and a matching snapshot ID do not automatically pass these checks.</div>
<div class="controls"><label>Document <select id="document">''' + options + '''</select></label><button id="export">Export review decisions</button></div>
<div class="links"><a href="review.json" target="_blank">Dependency audit</a> · <a href="source-render.diagnostics.txt" target="_blank">HTML rendering diagnostics</a> · <a href="ATTRIBUTION.txt" target="_blank">Source attribution</a><p id="prompt"></p><code id="path"></code></div>
<div class="panes"><section class="pane"><h2>Pinned RST source</h2><iframe id="source" title="Pinned source"></iframe></section>
<section class="pane"><h2>Rendered directly from RST</h2><iframe id="rendered" title="Sphinx source rendering"></iframe></section>
<section class="pane"><h2>Rendered from normalized JSON</h2><iframe id="normalized" title="Normalized rendering"></iframe></section></div>
<div class="decision"><label>Review result <select id="status"><option value="pending">Pending</option><option value="pass">Pass</option><option value="fail">Difference found</option><option value="blocked">Blocked / assets unavailable</option></select></label>
<textarea id="notes" rows="3" placeholder="Record differences, missing image-only information, or why the check is blocked."></textarea><p>Decisions start pending and stay in this page session. Export the JSON before closing; no source or normalized file is modified.</p></div>
<script>const data=''' + data + ''';
const decisions=data.entries.filter(e=>e.recommended).map(e=>({source_path:e.path,check:e.check,status:'pending',notes:''}));
const select=document.getElementById('document'),status=document.getElementById('status'),notes=document.getElementById('notes');let previous=null;
function save(){if(previous===null)return;const e=data.entries[previous],d=decisions.find(d=>d.source_path===e.path);if(d){d.status=status.value;d.notes=notes.value;}}
function show(){save();const i=Number(select.value),e=data.entries[i],d=decisions.find(d=>d.source_path===e.path);previous=i;
document.getElementById('source').src=e.source;document.getElementById('rendered').src=e.rendered;document.getElementById('normalized').src=e.normalized;
document.getElementById('prompt').textContent=e.prompt;document.getElementById('path').textContent=e.path;status.value=d?d.status:'pending';notes.value=d?d.notes:'';status.disabled=!d;notes.disabled=!d;}
select.addEventListener('change',show);document.getElementById('export').onclick=()=>{save();const result={normalized_snapshot_id:data.snapshot_id,review_evidence_id:location.pathname.split('/').slice(-2)[0],scope:'eight_selected_checks_only',checkout_evidence:data.checkout_evidence,image_files_present:data.image_files_present,image_dependencies:data.image_dependencies,review_status:decisions.every(d=>d.status==='pass')?'selected_checks_passed':'incomplete',decisions};const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));a.download='m2-review-decisions.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};show();
</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("../sources/odoo-documentation"))
    parser.add_argument("--manifest", type=Path, default=Path("../data/manifests/odoo19-corpus.json"))
    parser.add_argument("--snapshot", type=Path, default=Path("../data/normalized/corpus") / SNAPSHOT)
    parser.add_argument("--output", type=Path, default=Path("../data/reviews/m2-fidelity"))
    args = parser.parse_args()
    repository, snapshot = args.repo.resolve(), args.snapshot.resolve()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    documents, files, summary = read_snapshot(snapshot, manifest, repository)
    report = audit(documents, manifest, repository)
    report["normalized_snapshot_id"] = snapshot.name
    report["review_tool_version"] = "m23-0.1"
    report["rendering_limits"] = ["Basic controlled Sphinx rendering, not the Odoo website theme.",
                                  "Icons remain literal identifiers and formulas remain LaTeX text.",
                                  "Source-label matches and asset presence are audit evidence, not corpus expansion."]
    payload = {"review.json": (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode()}
    fixture_map = {path: (label, prompt) for path, label, prompt in FIXTURES}
    order = [path for path, label, prompt in FIXTURES if path in documents]
    order += sorted(set(documents) - set(order))
    entries = []
    with TemporaryDirectory(prefix="m23-review-") as directory:
        source_html, image_map, logs = build_source_html(files, repository, report["image_dependencies"], Path(directory))
        for path in source_html.rglob("*"):
            if path.is_file():
                payload["source_html/" + path.relative_to(source_html).as_posix()] = path.read_bytes()
        payload["source-render.diagnostics.txt"] = logs.encode()
        for i, relative in enumerate(order):
            document = documents[relative]
            name = f"{i:03d}.html"
            payload["source/" + name] = source_page(relative, files[relative]).encode()
            payload["normalized/" + name] = normalized_page(document, image_map).encode()
            label, prompt = fixture_map.get(relative, ("Additional page", "Compare source order, labels, prerequisites, warnings and source locations."))
            entries.append({"path": relative, "title": document["title"], "recommended": relative in fixture_map,
                            "check": label, "prompt": prompt, "source": "source/" + name,
                            "rendered": "source_html/" + relative[:-4] + ".html", "normalized": "normalized/" + name})
    payload["index.html"] = index_html(entries, report).encode()
    source = manifest["inventory"]["source"]
    attribution = f"Source: {source['repository_url']}\nOdoo {source['odoo_version']} / {source['language']}\nReported source commit: {source['commit']}\nDocumentation: CC BY-SA 4.0; see the source checkout's licensing/attribution notices.\nReview rendering adapts the provided documentation; application-code licensing is separate.\n"
    payload["ATTRIBUTION.txt"] = attribution.encode()
    for name in ("LICENSE", "COPYRIGHT"):
        candidate = repository / name
        if candidate.is_file(): payload["source-notices/" + name] = candidate.read_bytes()
    destination, reused = write_snapshot(args.output.resolve(), payload)
    # This launcher opens the newest review; normalized data and prior reviews remain immutable.
    launcher = '<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=' + destination.name + '/index.html"><a href="' + destination.name + '/index.html">Open fidelity review</a>'
    with NamedTemporaryFile("w", encoding="utf-8", dir=args.output.resolve(), delete=False) as handle:
        handle.write(launcher)
        temporary = Path(handle.name)
    try:
        os.replace(temporary, args.output.resolve() / "index.html")
    finally:
        temporary.unlink(missing_ok=True)
    print("Normalized snapshot verified:", snapshot.name)
    print("Review pages:", len(documents))
    print("Recommended checks:", sum(entry["recommended"] for entry in entries))
    print("RST files available for label-candidate scan:", report["available_rst_files_scanned"], "/", report["discovered_rst_paths"])
    print("Image dependencies present:", report["image_files_present"], "/", len(report["image_dependencies"]))
    print("Source checkout evidence:", report["checkout_evidence"]["status"])
    print("Review status: pending human comparison")
    print("Saved:", destination)
    print("Open:", args.output.resolve() / "index.html")


if __name__ == "__main__":
    main()
