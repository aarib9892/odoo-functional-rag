# M2.2 — Structured normalization of the selected corpus

This package supersedes the first one-document starter. M2.1 remains complete; M2.2 is in progress pending user reproduction and the remaining fidelity review. The accepted source commit, manifest scope and benchmark have not changed.

## Current run

Save `m2_normalization_corpus.zip` in `/home/aarib/odoo-functional-rag/`. From `backend`:

```bash
unzip -o ../m2_normalization_corpus.zip -d .
uv run --group parser-spike python -m unittest discover -s tests -p 'test_normalization.py' -v
uv run --group parser-spike python -m app.ingestion.normalize_corpus --check-fixtures
```

No dependency changes are needed. The existing `rst_directives.py` and pinned `parser-spike` group are required. The package replaces the normalized models, normalizer, earlier demo, tests and README; it adds shared structure adapters, a controlled reader, reference index, corpus command and optional pinned-fixture checks. It does not change M1 discovery/scope/manifest modules.

Expected assistant-local results:

```text
Ran 10 tests
OK

Fixture preservation checks passed.
Manifest files verified: 30
Normalized documents: 30
Unsupported-node diagnostics: 0
Inline reference states: {'external_not_checked': 2, 'not_in_corpus': 75, 'resolved': 101, 'unresolved_label': 12}
Parser diagnostic headers: 280
Snapshot reused: False
```

The command prints the output directory under `data/normalized/corpus/<snapshot-id>/`. It contains:

- `documents/`: one normalized JSON file per selected RST file, preserving source-relative directories.
- `summary.json`: source/manifest/version identity, structure counts, reference states and diagnostic categories.
- `diagnostics.txt`: complete captured parser-message groups, ordered deterministically.

The output is an immutable local snapshot. Files are assembled in a staging directory and renamed into place after validation. Repeating identical input verifies and reuses the same snapshot. No active-index pointer is changed. A failed new snapshot write leaves earlier snapshots available; this is tested. Source bytes and inventory fingerprints are validated with explicit exceptions rather than Python assertions.

## What changed from the first increment

| Structure | Normalized representation |
|---|---|
| Table | Table/group/column/header/body/row/cell blocks; column stubs, order and row/column spans are preserved |
| Tabs | Ordered tab blocks with label, label inlines and complete panel contents, including inactive panels |
| Cards | Ordered label, original target, description blocks and explicit target status |
| Navigation | Original entries alongside Sphinx's processed entries and target statuses |
| Math | LaTeX text retained as block/inline math |
| Figures/captions | Figure parent, image and caption blocks remain related |
| Substitutions | Definitions remain explicitly non-rendered; body abbreviations retain their meanings |
| Core prose | Earlier paragraph/list/admonition/GUI/menu semantics remain supported |

The selected 30-page output includes one table, two tab groups/six tabs, seven cards, two navigation blocks, one block formula, nine figures and 164 image nodes. Eight explicit caption nodes are retained. An image can be meaningful without having a separate caption node. The optional `--check-fixtures` flag checks the reviewed product table, reservation tabs, cards/navigation, abbreviation expansions, formula/example association and invoicing-policy warning/examples/references. It is specific to the frozen M1.2 fixture set and is not a general quality score for future corpora.

Shared adapters now live in `rst_structures.py`; the corpus implementation does not import comparison-probe modules. Small wrappers around the pinned tabs directives capture declaration locations on generated tab labels/panels. Reservation tab locations are checked against source lines 20/25/30. Table internals without their own line remain explicitly ancestor-located rather than receiving invented exact spans.

Native Sphinx resolution is verified for selected-corpus `ref`/`doc` roles. Original targets and original display text remain in attributes; native display titles are retained as `resolved_text`. Implicit references use that resolved title in normalized paragraph text. For example, the original target `down_payment` displays as `Down payments` when resolved. Revision identity includes the staged inventory context so a scope/index change can invalidate normalized references even when a page's own bytes are unchanged.

| Reference status | Meaning |
|---|---|
| `resolved` | The selected-corpus index and native resolver produced a destination |
| `not_in_corpus` | The document target was not staged; whether its source file exists is unverified |
| `unresolved_label` | The selected-corpus label index has no match; it may live in an unstaged page |
| `external_not_checked` | The URL remains recorded without a network validation claim |

Card/navigation document targets also receive index-based statuses, separately from the inline-reference counts printed above. External/custom reference kinds or inconsistent structures remain explicit states/failures rather than invented destinations. No additional pages are selected to remove warnings.

Parser warnings are retained both as message text and typed records with code/severity/source/line. Unrecognized message formats are retained as unclassified messages, including error severity when present. The original local 280-header breakdown remains 164 missing-image, 75 document-reference, 12 label-reference, 23 not-included-in-toctree and 6 missing-toctree-document warnings. Images are deliberately not staged and original image assets are not validated by this command.

The contract is now schema `m22-0.2` / normalizer `structures-0.2`. Dataclasses/type hints describe the application contract, rather than providing runtime JSON schema validation. `status: ok` means no unsupported mappings were encountered; it does not certify every reference/asset or complete ingestion fidelity. Unknown structures still retain fallback text and diagnostics, and the corpus command refuses to save a complete snapshot when unsupported mappings remain.

## Remaining work

The assistant tested all 30 source hashes against the accepted reconstructed inventory and ran ten focused tests plus reviewed fixture checks. The new corpus command still needs user reproduction. The original one-document starter was explained and accepted conceptually; a separate successful user run of that starter was not reported.

After this run: inspect normalized/source/rendered examples, review unresolved targets and screenshot-dependent instructions, and complete M2 acceptance checks before chunking. Git cleanliness is not rechecked by this normalization command. Images/URLs, includes/dependency provenance and full rendered fidelity remain outside this increment. No chunks, embeddings or model answers are produced.

Read `normalized_models.py` first, then `normalization.py`. The corpus reader, reference index and CLI supply the surrounding pipeline. Section and block IDs are local to their document revision; use `revision_id` with them when referring to records externally. Source lines distinguish node-reported, ancestor-reported and unknown locations; no end spans are invented. These normalized records are not chunks.
