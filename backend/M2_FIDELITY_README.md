# M2 fidelity review

Aarib's 23 October 2026 corpus command passed all 30 selected files and fixture checks, with zero unsupported mappings. Its reported snapshot ID matches the independent local result:

`15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc`

This add-on prepares source/rendered/normalized comparisons and an evidence audit. It does not modify the accepted scope, benchmark, source files, normalized snapshot or reference-resolution states. M2 remains in progress until the remaining fidelity checks have been assessed.

## Run

Download `m2_fidelity_review.zip` to `/home/aarib/odoo-functional-rag/`. From `backend`:

```bash
unzip -o ../m2_fidelity_review.zip -d .
uv run --group parser-spike python -m unittest discover -s tests -p 'test_fidelity_review.py' -v
uv run --group parser-spike python -m app.ingestion.fidelity_review
xdg-open ../data/reviews/m2-fidelity/index.html
```

There are six focused tests. No dependency changes are needed. The existing M2.2 corpus modules, adapters and pinned parser-spike group are required. The default input is the reported snapshot above; `--snapshot`, `--repo`, `--manifest` and `--output` allow explicit paths.

The tool verifies the snapshot's complete file-content identity, validates its manifest fingerprint association and checks the selected source bytes. It builds 30 review pages and recommends eight checks. The UI shows pinned RST, controlled Sphinx HTML generated directly from that RST, and a separate rendering of normalized JSON.

Open the first eight documents in the selector. Each has a specific review prompt. Compare procedure order, prerequisites, table headers/cells, every tab panel, warning/example placement, card/navigation targets and the formula/worked example. In the source rendering, click through all tabs; the normalized view expands every panel. Hover over normalized reference text for the original target/status.

Use **Pass**, **Difference found**, or **Blocked / assets unavailable**, with notes. Everything starts pending. Export `m2-review-decisions.json` before closing the page. Decisions are held in the current page session and do not auto-save to source or normalized files. The export records these eight selected checks and their evidence ID; it does not automatically mark all of M2 complete. Remaining documents can be opened for additional inspection.

## Review outputs

The printed review directory is immutable and contains:

- `index.html`: comparison UI and decision export.
- `review.json`: image dependencies, unresolved-reference occurrences, available source candidates and checkout evidence.
- `source/`, `source_html/`, `normalized/`: the three independent views.
- `source-render.diagnostics.txt`: retained HTML-builder diagnostics.
- `ATTRIBUTION.txt` and available source notices: documentation provenance/licensing.

The stable launcher `data/reviews/m2-fidelity/index.html` opens the newest generated review. Previous reviews and all normalized snapshots remain intact. Review IDs can differ when available images/source candidates or review rendering change; the normalized snapshot identity remains unchanged.

## What the audit proves

- For document targets outside the corpus, it records whether a corresponding source file is available locally and whether its path was in the manifest's original RST discovery inventory. Presence does not include the document in the corpus.
- For unresolved labels, it scans available RST files named in the manifest's discovery inventory for literal label declarations. These are source candidates, not Sphinx resolution results. Duplicates remain visible. The existing 12 unresolved-label occurrences are not rewritten.
- For each of 164 image dependencies, it records path, alt text, location, local presence and observed SHA-256 when available. Present images are copied into the temporary HTML rendering; unavailable images produce explicit placeholders in the normalized view.
- Git evidence distinguishes a clean checkout at the manifest commit from a dirty/different/unavailable checkout. An image is attributed to the clean pinned checkout only when the checkout verifies and the image path is tracked. Source candidates and asset content from an unverified checkout remain provisional evidence.

Image existence, hashes and alt text do not prove that image-only instructions were captured in normalized text. In particular, inspect the credit-note journal-entry screenshots and record any answer-critical information that exists only in images. OCR/image reasoning is not part of this project increment. Missing assets can block this selected check; do not treat a placeholder as an inspected screenshot.

## Rendering limits

The source HTML uses the pinned RST and controlled adapters with Sphinx's basic theme. It is independent of the normalized-JSON renderer, but both rely on the chosen parser/adapters. It is a structural/content comparison, not a pixel comparison with the public Odoo website. Original RST remains visible as an additional check.

Icons remain literal identifiers. Formulas show their LaTeX text for offline review rather than typeset mathematical notation. Original website styling is not reproduced. External links are not network-validated. Existing reference/asset diagnostics remain recorded.

Assistant-local validation used the supplied partial archive: 144 of the 944 discovered RST files were available, and no original images were included. It found literal candidates for five unresolved-label occurrences and local files for 48 unstaged document-reference occurrences. These counts describe that archive only; your complete checkout can produce different availability counts. A dedicated synthetic-image test verified successful native HTML image copying. No real journal-entry screenshot was reviewed locally.

Six tests and the 30-page generator passed locally. Document selection and decision-export logic were exercised separately. Browser visual inspection and the actual eight human comparisons remain pending. Share the command output and exported decisions/differences after reviewing; the project notes can then record the actual acceptance evidence.
