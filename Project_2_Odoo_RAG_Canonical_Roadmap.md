# Project 2 — Odoo Functional RAG & Implementation Assistant

Canonical roadmap v1.54\
Established: 18 October 2026\
Updated: 7 November 2026\
Status: M1/M2 and accepted embedding/dense artifacts verified in the actual repository; bounded M6/M9/M10 internal pilot implemented with 72 backend tests, two browser tests and a real browser/provider smoke. Hard-workflow answer quality and operations/client acceptance remain incomplete; M3 research gates remain open.\
Next task: Review the full-application offline estimate and choose a provider cap; then build/evaluate the isolated candidate and complete human workflow review before switching the pilot. Odoo 19 remains the only version; client exposure is still pending.


## Pilot delivery priority — 6 November 2026

Aarib discussed the project with his CEO, who wants a working version quickly for existing clients and the operations team to assess practical impact. Aarib explicitly changed the working plan from line-by-line guided implementation to Codex-led development. The immediate target is a small, reviewed internal pilot followed by limited client use, measuring correct task completion and time to useful guidance.

`CODEX_HANDOFF.md` is the concise implementation brief for the actual repository. Begin with the accepted Odoo 19 English Sales/Inventory corpus (30 documents/205 chunks), reuse the measured retriever/cache, and build the browser-to-grounded-answer path, server-validated citations and visible evidence, useful clarification/insufficient-evidence behavior, task feedback, restricted access/session isolation and a reproducible launch/deployment plan. Odoo 19 was the initial implementation assumption and was confirmed by Aarib on 7 November 2026 as the only covered version for now. The hosting target remains unknown; cohort tasks must fit the Odoo 19 scope.

Deliver a bounded slice of M6 plus essential M9/M10 work ahead of completing every M3/M4/M5 research task. Keep milestone IDs stable and all unmet original completion gates recorded. Exhaustive include/alignment edge cases, the plain-window experiment, broad hybrid/reranking comparisons, cross-version features and agent workflows are deferred from the first internal-pilot critical path unless a concrete pilot dependency makes them necessary. This sequencing change does not mark those milestones complete or waive grounded answers, citation validity, version correctness, access isolation or honest evaluation.

The current frozen K=5 baseline has 13/15 answerable-case hits and complete evidence for 9/15; it is not an answer-accuracy result. Validate generated answers on development/pilot questions and repair demonstrated retrieval gaps. Preserve baseline reports and benchmark bytes; keep holdout content sealed during implementation/tuning. Broader release gates in M10 remain for broader release, while this earlier bounded pilot is assessed and described as a pilot. Define pilot task success/measurement before reviewing outcomes.

The latest user result also verifies `load_evidence_sources()` with real temporary Git fixtures: three source files for one page/two dependencies, preserved lines/counts, deterministic replay, old-pin stability after checkout/later commits, matching hashes required for a new pin, invalid-metadata rejection, single-file support and unchanged input metadata. Cross-file alignment/scoring and full include-aware rebuild integration remain unfinished in the user repository.

An alignment v0.2/physical-span draft was started only in the assistant's verification copy after that result; it was never delivered to Aarib. Upon the plan change it was archived separately and the verification copy restored to the last shared `m3-paragraph-evidence-0.1` implementation. Codex must inspect the actual repository rather than assuming any unshared draft is present. No new production index, provider job, deployment or client message occurred during this handoff.

### Full-application implementation / v1.54 — 7 November 2026

Aarib approved the plan to expand to all 944 English application pages at the current source pin, with text and image references, an isolated candidate, and a reviewed switch. The budget choice was explicitly deferred until an offline estimate is available. This supersedes the narrow page-selection priority for the next corpus, while preserving the 30-page pilot and its frozen baseline.

Offline normalization and chunking now account for all 944 pages without fatal parser or unsupported-structure errors: 879 searchable, 65 reference-only, 11,926 chunks and 11,134 unique eligible inputs. Of these, 179 vectors already exist in cache and 10,955 require embeddings (1,341,670 tokens). Measured reference edges: 7,319; image references: 3,255. Estimated embeddings $0.026833; an 83-case generation/review run is approximately $0.3652 plus question embeddings under documented assumptions. No new provider requests or expanded index publication occurred.

Opt-in broader parser/renderer support, immutable preparation, PostgreSQL FTS/RRF search, generic cross-document context, release descriptors/session migration, dynamic UI scope, shared spending reservations, candidate publication/evaluation and human approval commands are implemented. The additive SQL migration and real hybrid query passed on the existing database with cached embeddings and provider requests forbidden. New development cases and reference excerpts remain provisional; full-corpus retrieval/answer results and human acceptance are pending. See [implementation, artifacts and gates](docs/FULL_CORPUS.md). M4/M5 now have bounded implementation work; their evaluation/completion gates remain open. No other milestone is marked complete.

### Confirmed version scope / v1.53 changelog — 7 November 2026

Aarib confirmed **Odoo 19 only for now**. Treat version 19 as the agreed product scope for documentation expansion, evaluation, internal testing and the limited client pilot. Version choice is no longer an open product decision. Cross-version ingestion/comparison under M8 remains deferred; milestone IDs and original future-work gates are preserved. Hosting, cohort selection, task coverage and answer-quality acceptance remain open.

The UI version selector has been removed at Aarib's request. A fixed Odoo 19 label is displayed and all browser questions automatically target 19.0. The production UI build and both browser tests pass, covering the first question without a version prompt, feedback/session isolation and mobile error recovery. The running local server serves the rebuilt assets.

### Pilot implementation checkpoint / v1.52 changelog — 7 November 2026

The actual repository now contains a restricted local browser pilot. [Verification and limits](docs/PILOT_VERIFICATION.md) records native checks, live smoke artifacts, separate context measurement and failures; [README](README.md) has exact commands. The FastAPI/React flow reuses dense K=5 retrieval and cached embeddings, adds structured claim-level answers and exact citation quote validation, a separate model support review, a 3,500-token context budget, isolated cookie sessions, named pilot keys, request/cost-attempt limits, task feedback and operator audit/export. No original ingestion edits, frozen benchmark or baseline reports were overwritten.

The reviewed `pilot-support-passages-0.1` assembly policy uses at most three existing dependency chunks for the demonstrated backorder/partial-credit gaps. All 23 frozen development retrieval results were replayed through the actual builder: complete required groups 11/15 (73.3%), mean group coverage 80.6%. The original dense baseline remains 9/15 complete (60%) and 74.4% coverage; this is a separate evidence-context comparison, not an answer-accuracy claim or a rerun of dense retrieval.

72 backend tests and two Chromium UI tests pass. A real browser/provider invoicing answer and operator export passed against the unchanged 205-chunk pgvector snapshot; all live smoke queries reused existing query embeddings. Earlier live runs exposed a provider timeout, a model-reviewed screen-order error and hard-workflow abstentions. The screen-order issue prompted stricter generation/review instructions, but the latest partial-delivery task still asks a packaging clarification and the return/partial-credit task still abstains. These tasks are not accepted as solved. Model support review is not sufficient evidence of semantic correctness.

This increment starts bounded M6/M9/M10 implementation and a minimal evidence-assembly slice; it does not complete M3–M10. Include-aware lifecycle/alignment work and broader ranking/version/release gates remain as recorded. Local run/configuration, rollback and a predeclared operations observation protocol are provided. At this implementation checkpoint, user versions, measured correct task completion/time, hosting target and client cohort were unknown. The subsequent v1.53 decision confirms the Odoo 19-only product scope; task results, hosting and cohort remain pending. No external publication, Odoo access/actions, customer uploads or client messages occurred. Next: operations review and targeted hard-workflow diagnosis before client exposure.

## Product objective

Build a documentation-grounded assistant for Odoo functional consultants, project managers, implementation teams, administrators, support teams, and business users.

The engineering focus is retrieval quality, trustworthy evidence, repository ingestion, and measurable assistance. The current pilot covers Odoo 19 functional Q&A. Broader configuration guidance and requirement analysis remain roadmap work, and cross-version comparisons are deferred beyond the confirmed Odoo 19-only scope. It does not connect to or modify a live Odoo instance.

Project 1 is complete according to the supplied brief. Reuse its understood runtime patterns where useful: persistence, conversation identity, streaming, cancellation, token accounting, request IDs, and error handling. Do not repeat its introductory RAG curriculum or import its whole agent runtime. Review concrete code before deciding what to copy.

## Canonical milestone index

| ID | Fixed milestone title | Main deliverable | Status |
|---|---|---|---|
| M1 | Corpus scope, provenance, and evaluation contract | Reproducible inventory and human-reviewed benchmark | Complete |
| M2 | Structure-preserving RST ingestion | Normalized documents with source provenance | Complete for the accepted corpus and reviewed fixtures |
| M3 | Chunking, incremental indexing, and dense baseline | Measurable retriever and repeatable index lifecycle | In progress — native baseline/non-include lifecycle verified; include handling, reporting, chunking comparison and M3.1 combined tests pending |
| M4 | Hybrid retrieval and retrieval debugging | Dense/lexical/hybrid comparison and inspection interface | In progress — hybrid SQL implemented/tested; full-corpus comparison pending budget |
| M5 | Reranking and evidence assembly | Evaluated ranking stage and bounded evidence packets | In progress — generic bounded reference/neighbor assembly implemented; semantic acceptance pending |
| M6 | Grounded functional Q&A and citations | Persistent assistant with verifiable source references | In progress — bounded local pilot implemented/tested; generated-answer/task acceptance incomplete |
| M7 | Configuration guidance and requirement analysis | Bounded, evidence-backed consulting workflows | Not started |
| M8 | Version-aware retrieval and comparison | Isolated Odoo 17/18/19 evidence and qualified comparisons | Deferred — outside the confirmed current Odoo 19-only scope |
| M9 | Security, reliability, and operational observability | Tested failure handling, isolation, and operational traces | In progress — essential single-host access/isolation/limits/traces tested; broader gates open |
| M10 | Deployment, release evaluation, and portfolio evidence | Reproducible deployment and measured release report | In progress — local launch, runbook and observation protocol prepared; no external deployment or task-impact result |

Milestone IDs and titles remain stable. Add tasks under their owner, such as M4.2, without renumbering later milestones. Scope or completion-gate changes require a dated changelog entry and a roadmap revision. Future sessions should read this document before changing the plan.

## Implementation checkpoint — 19 October 2026

**M1.1 is complete. M1 remains in progress.** Completion is based on the user's local CLI output, repeated manifest fingerprints, and six passing fixture tests reported in this conversation. The local source implementation has not been independently inspected by the assistant.

| Item | Recorded result |
|---|---|
| Source repository | https://github.com/odoo/documentation.git |
| Configured Odoo version / language | 19.0 / en |
| Pinned source commit | c9202e68ae702daec981b47d0b6055191084ffa2 |
| Tracked application RST files discovered | 944 |
| Candidate files selected | 143 |
| Candidate application breakdown | Inventory: 87; Sales: 56 |
| Files excluded by scope | 801 |
| Selected source bytes | 1,103,702 |
| Inventory fingerprint | d2b2ef3824b6a6c78ceaafbc95d0ab146862493d13b8709f0dd60230fcbe1e2b |

The 143 files are an application-level candidate pool. M1.2 will review and narrow this pool to the initial workflow corpus. The earlier roughly 30–50-page target remains a planning guide, not a quota or a claim that final page selection has already happened.

Implemented locally:

- `backend/app/ingestion/discovery.py`: tracked RST discovery through Git.
- `backend/app/ingestion/repository.py`: repository-root and clean-checkout validation; commit identification.
- `backend/app/ingestion/scope.py`: configured file/directory selection, missing-path detection, and application ownership.
- `backend/app/ingestion/inventory.py`: immutable file records with source path, application, byte size, and raw-byte SHA-256.
- `backend/app/ingestion/manifest.py`: source/scope metadata, sorted selected and excluded records, summary, deterministic fingerprint, and separate run timestamp.
- `backend/app/ingestion/cli.py`: configuration validation, argument handling, before/after checkout checks, atomic output replacement, and failure exit codes.
- `config/corpus.json`: pinned source metadata and Sales/Inventory candidate scope.
- `backend/tests/test_inventory_cli.py`: six tests using temporary Git fixtures.

The candidate scope includes these overview files and their corresponding directories:

- `content/applications/sales/sales.rst`
- `content/applications/sales/sales`
- `content/applications/inventory_and_mrp/inventory.rst`
- `content/applications/inventory_and_mrp/inventory`

Two independent user runs produced the same inventory fingerprint with different timestamps (2026-10-19T14:32:09.580609+00:00 and 2026-10-19T14:33:34.813433+00:00). The CLI reproduced that fingerprint and the same totals.

All six reported tests passed in 0.852 seconds:

1. Committed edits, additions, and deletions update the inventory.
2. Dirty checkout rejection preserves the previous manifest.
3. A simulated partial-write failure preserves the previous manifest and cleans temporary output.
4. Missing scope rejection preserves the previous manifest.
5. Scope changes alter selection, counts, and fingerprint.
6. Wrong-commit rejection preserves the previous manifest.

Commands, run from the user's `backend` directory:

```bash
uv run python -m app.ingestion.cli \
  --repo ../sources/odoo-documentation \
  --config ../config/corpus.json \
  --output ../data/manifests/odoo19-inventory.json

uv run python -m unittest discover -s tests -v
```

The user's generated manifest is at `/home/aarib/odoo-functional-rag/data/manifests/odoo19-inventory.json`. The user's project root is `/home/aarib/odoo-functional-rag`. These are user-local paths, not files available in the assistant's execution environment.

**M1.2 complete: source audit, package acceptance and local manifest activation recorded.**

Begin with candidate pages for invoicing policy, partial deliveries/backorders, and returns/refunds. Inspect actual RST source before choosing parsing abstractions or gold evidence. Record relevant sections, prerequisites, cross-references, warnings, tables, UI/menu roles, and dependencies on screenshots or outside-scope pages. Record the pinned checkout's license/attribution information. Then finalize the page allowlist and author the initial 30 reviewed evaluation cases. Path keyword searches only identify candidates; they do not establish relevance or answerability.

The initial candidate listing and assistant source audit have been completed. M2 parsing implementation starts only after the M1 source scope and evaluation contract are ready.

### M1.2 review checkpoint — 22 October 2026

- The supplied archive's 143 candidate RST files independently match the manifest's byte sizes and SHA-256 hashes; the 1,103,702-byte total and candidate fingerprint above reproduce exactly. Source/scope configuration agrees after normalizing array order. Git history is absent from the archive, so commit membership and checkout cleanliness remain user-reported.
- The accepted exact-page scope has 30 files: 9 Sales, 20 Inventory and **one Accounting credit-note dependency**, totaling 213,145 bytes. Aarib accepted this exact-page exception for customer returns. Broad Accounting coverage remains deferred. The user subsequently activated this scope with the existing CLI; the completion checkpoint below records the result.
- All 30 selected source texts received assistant review. The 114 deferred candidates received path/title/structure screening with recorded reasons. Whole-file inclusion brings incidental content without implying broad Purchase, POS or vendor-accounting coverage.
- The accepted m12-1.0 benchmark contains 12 direct, 8 workflow/multi-section, 5 ambiguous and 5 unanswerable cases. Aarib accepted the supplied documents as presented on 22 October 2026. Source targets use file hashes and line spans; required groups separate distinct facts.
- Frozen split: 23 development / 7 holdout, separated by question family. This holdout is author-visible, not blind. Version m12-1.0 is frozen before retrieval tuning; no retrieval performance has been measured.
- Root documentation LICENSE/COPYRIGHT were inspected and preserved with attribution in the review package. The documentation license is CC BY-SA 4.0; software/theme notices are distinguished. Selected structures include tables, tabs, substitutions, cards/toctrees and math. Screenshots remain uninspected because their bytes were absent.
- Review artifacts: `Project_2_M1_2_Review.md`, `Project_2_M1_2_Benchmark_Review.md`, `Project_2_M1_2_Review_Package.zip`, and the updated `Project_2_M1_2_Source_Audit.md`. The zip contains accepted `config/corpus.json`, `evaluation/benchmark.json` (m12-1.0), full source-selection decisions, `docs/acceptance.json` and `ACTIVATE.md`. Original draft files are preserved under history/.

**Acceptance recorded:** Aarib stated, “I reviewed the docs , looks fine to me , lets proceed”. This is package-level acceptance, including the scope/benchmark and Accounting exception; no individual corrections or live tests were supplied.

### M1.2 completion checkpoint — 22 October 2026

The user supplied successful CLI output for the accepted scope: **944 discovered / 30 selected / 914 excluded / 213,145 source bytes**, pinned commit `c9202e68ae702daec981b47d0b6055191084ffa2`. The new manifest is saved at `/home/aarib/odoo-functional-rag/data/manifests/odoo19-corpus.json`.

Active corpus fingerprint: `d359162bcd1c4785ae1f339d9b972d1bad90102e5351dc33abaebea046110d1d`.

The assistant independently reconstructed the inventory payload from the previously supplied 944-path discovery inventory, accepted exact-page scope and file sizes/hashes. Its canonical fingerprint matches the user-run output exactly. New manifest bytes and Git history were not uploaded; local checkout checks remain user-reported. The accepted benchmark remains m12-1.0, with the author-visible split limitation unchanged. M1 is complete.

**Next:** M2.1 — inspect backend/project dependencies and the pinned documentation requirements, then compare controlled Docutils and Sphinx parsing on representative audited files. Select an approach only after comparing retained structures and diagnostics.

## Initial scope and architecture decisions

- Corpus: official Odoo documentation, branch 19.0, English, selected functional pages under content/applications/. Pin an actual Git commit; the branch name alone is not a reproducible snapshot.
- First workflow slice: Sales and Inventory pages covering ordered versus delivered invoicing, partial deliveries/backorders, and returns. Record unresolved or out-of-scope dependencies rather than silently pulling in whole applications.
- Initial scale: roughly 30–50 carefully selected pages. This is a manageable starting sample, not a claim about repository size and not a permanent cap.
- Expansion: selected Purchase and Accounting pages in M7 to support replenishment, payment terms, and approval questions; CRM and POS remain optional expansions after the core release. Each new scope gets new reviewed evaluation cases.
- No assumption that documentation exhaustively describes every edition, localization, installed module, customization, or deployment. Record applicability when supported; otherwise retain unknown values and ask useful clarification questions.
- Stack: React/Vite/TypeScript, FastAPI/Pydantic/Python, PostgreSQL with pgvector and native full-text search, Docker Compose, OpenAI initially.
- Use an RST parsing library, but hand-code normalization, chunking, retrieval orchestration, context assembly, and evaluation. Learning the important application mechanics does not require writing a markup parser.
- Ingestion runs as a separate CLI or controlled job; answering reads a published index snapshot. Keep ingestion out of chat request handlers.
- No initial LangChain, LlamaIndex, LangGraph, separate search service, queue, or cache. Introduce infrastructure only for a measured need.
- Repository source is the ingestion input. Rendered documentation is useful for human verification and user-facing citation links.

Odoo's documentation guidance explicitly distinguishes headings, menu paths, UI labels, notes, and references. This is why preserving structure is part of retrieval quality, rather than treating RST as text to strip. See sources [1]–[3]. PostgreSQL already provides indexed full-text search, making it a reasonable first lexical baseline alongside pgvector [4].

## Trust contract

Evidence status belongs to individual claims or steps, not merely to a label at the top of an answer.

| Label | Required behavior |
|---|---|
| Documented capability | Cite retrieved evidence supporting this claim, for the stated version and known applicability. |
| Recommended configuration | Identify the recommendation, its assumptions, its rationale, and any documented facts used in that rationale. |
| Project-specific decision | State what depends on the customer's business process or environment and what needs confirmation. |
| Likely customization | Present a tentative assessment requiring investigation; explain the evidence and uncertainty. |
| Insufficient evidence | State what the selected corpus cannot establish and what additional evidence is needed. |

A retrieval miss does not establish that Odoo lacks a feature. “Likely customization” must never be the automatic fallback for “no relevant chunk found.” Similarity and reranker scores are ranking signals, not calibrated probabilities of factual correctness.

Record what was retrieved, what was supplied to the model, and what the answer cited separately. These records provide an audit trail; they do not prove which input causally influenced a model's internal computation.

## M1 — Corpus scope, provenance, and evaluation contract

**What we build**

A reproducible source inventory, a narrow corpus specification, and the first human-reviewed evaluation set. Record repository, requested version, checked-out commit, language, selected paths, content hashes, discovery failures, and inclusion/exclusion reasons. Record the source's license and attribution information from the pinned checkout.

Start with 30 reviewed questions: 12 direct functional questions, 8 workflow or multi-section questions, 5 ambiguous questions, and 5 unanswerable or out-of-scope questions. The numbers are a starting allocation, not statistical evidence of general performance.

Each case has an ID, question, scope/version, expected behavior, evidence targets, expected answer points when applicable, and forbidden unsupported claims. Mark whether a question should be answered, clarified, partially answered, or rejected for insufficient evidence.

**What we learn**

Corpus design, provenance, relevance judgments, answerability, and the difference between a test question and a defensible evaluation case.

**Why this comes here**

Without a fixed corpus and evidence labels, changing chunking or retrieval changes the test itself. We need something stable to measure before selecting a strategy.

**Complete means**

The source inventory is reproducible; roughly 30–50 pages are deliberately selected; all 30 cases are reviewed against that snapshot. Relevance targets point to source documents, sections, or evidence spans, not generated chunk IDs. Required evidence groups distinguish alternative sources from genuinely separate facts needed to answer a multi-part question.

Split related question families together into a development set and a small held-out set; do not scatter paraphrases across both. Record the split, limitations, and benchmark version. No retrieval accuracy claim is made yet.

**Intentionally postponed**

Embeddings, parsing implementation beyond discovery, chat UI, model-generated gold answers, broad application coverage, and numeric quality thresholds chosen without a baseline.

## M2 — Structure-preserving RST ingestion

**Current progress:** M2 complete for the accepted 30-page corpus and reviewed fixtures. Corpus normalization is user-reproduced; Aarib's exported decisions pass all eight selected fidelity checks. The backend requires Python >=3.12 and initially had no dependencies. The source website requirements pin Docutils 0.17.0 and Sphinx 4.3.2; the controlled parser implementation uses Docutils 0.21.2 / Sphinx 8.2.3 in the `parser-spike` dependency group. The accepted corpus and benchmark remain frozen.

### M2.1 parser checkpoint — 22 October 2026

- The user reproduced the invoicing-policy baseline: 6 title nodes, one important block, one warning block and 27 plain-Docutils parser errors. The errors comprise unsupported roles AND directives: 17 guilabel, 5 ref, 2 menuselection, 2 example and one seealso. Unknown-block text remains in diagnostics/literal content; that does not make it a correctly parsed semantic block.
- Bare Sphinx on the same source retained the 6/1/1 counts, recognized 17 GUI labels and 2 menu selections, and left two example-directive errors. The stored parsing tree contained 9 pending references; this is a processing-stage count, not a count of broken links.
- The user then reproduced `sphinx_probe.py` with `ExampleBlock` / `ExampleDirective`: 0 parser errors, two example blocks at source lines 75 and 128, and preserved 50/40/10-head quantities in the partial-delivery example. This is evidence for the inspected fixture, not full-corpus fidelity or completion of M2.
- The pinned `extensions/custom_admonitions/__init__.py` was read as text; its custom example node and BaseAdmonition mechanism inform the small independently controlled adapter. Repository extension/configuration Python was not executed.
- The three-page probe stages real invoicing-policy, quotation-creation and multi-package/backorder sources. Linked pages introduce the `icon` role. The supplied adapter preserves its literal identifier, source location and inline metadata. It performs no icon rendering.
- The user reproduced `reference_probe.py`: 3 files, 0 parser errors across them, 10 icon nodes, both original examples preserved, two actual resolved quotation-label links and one backorder-label link with verified target documents. The full diagnostics are saved; 35 warning headers match the local test and include missing images, unloaded targets and orphan navigation. No claim is made that all links resolve.
- Raw and resolved trees need different handling: unresolved links can become plain text after Sphinx resolution. Retain original reference targets and diagnostics rather than treating zero remaining pending nodes as success. The probe checks actual resolved reference nodes and the label index together.
- The user reproduced `structure_probe.py` on four accepted pages: product type (table), reservation methods (tabs), one-step receipt/delivery (substitutions), and delivery methods (math). Execution with separately pinned sphinx-tabs 3.5.0, Docutils 0.21.2 and Sphinx 8.2.3 passed all fixture checks with 0 parser errors. It verifies column/value meanings, all tab label/panel pairs and conditions, abbreviation expansions, and formula/worked-example association. The matching 59 diagnostic headers are saved for inspection; the user's full diagnostics have not been separately read.
- The user reproduced the controlled Docutils alternative on the five overlapping content fixtures plus the inbound/outbound-flows navigation page with 0 parser errors. It checked seven card label/target pairs and nine toctree entries, alongside the earlier content expectations. This adapter retains reference targets but implements neither a resolver nor Sphinx's missing-target/asset checks; diagnostic counts are not comparable quality scores.
- The user reproduced the final `sphinx_corpus_probe.py` over all 30 accepted files, verifying their sizes/hashes and manifest's canonical fingerprint. It stored 30 doctrees with 0 parser errors and verified seven card labels/targets/bodies/source lines. A small toctree subclass retains original entries that Sphinx otherwise omits when their destinations are unstaged: the flow page retains all 9 original targets alongside 3 staged destinations; reservation navigation retains all 3 staged destinations. No additional pages were staged. M2.1 is complete.
- The local corpus probe saved 280 diagnostic headers: 164 missing-image, 75 document-reference, 12 label-reference, 23 not-included-in-toctree and 6 missing-toctree-document warnings. Images were not copied. These diagnostics still need classification; they are not proof of harmlessness, complete reference resolution or normalization fidelity. Card targets are preserved as metadata without a card-link resolver.
- Working parser choice: Sphinx 8.2.3 / Docutils 0.21.2 plus sphinx-tabs 3.5.0 and small controlled adapters. Both approaches preserved inspected content; Sphinx already supplies the demonstrated native reference infrastructure. Keep raw targets as well as processed/resolved information. Extract reusable adapters from experiment modules when implementing the production parser.
- Complete probe archives and `Project_2_M2_Parser_Spike.md` are available. User-local modules belong under `/home/aarib/odoo-functional-rag/backend/app/ingestion/`.

### M2.2 initial normalization checkpoint — 22 October 2026 (superseded by the corpus increment below)

- Prepared application-owned dataclasses for source identity/location, diagnostics, inline semantics, blocks, ordered sections and a normalized document. Initial schema `m22-0.1` / normalizer `core-0.1` is not a frozen production contract.
- Implemented a first core mapping and end-to-end invoicing-policy example. It preserves section/child order, heading ancestry, anchors, nested warnings/examples/lists, GUI/menu/reference semantics and image metadata. References retain original targets without normalized resolution results yet; asset validation remains pending.
- Provenance distinguishes node-reported, ancestor-reported and unknown lines. The current one-source-file mapper rejects foreign-source nodes rather than attributing them to the main file. Traversal IDs are scoped to a document revision; source/parser/schema changes affect revision identity.
- Assistant-local execution passed four focused tests and the pinned source fixture: 6 sections, examples at lines 75/128, the nested warning paragraph/image at 121/124 under warning line 120, 17 GUI labels, 2 menu paths, 9 references, 4 images and 0 unsupported mappings. Two independent Sphinx processes produced identical JSON; the extracted ZIP passed its tests/demo and reproduced those bytes. User execution is pending.
- Unsupported structures retain fallback text and an error diagnostic with document status `partial`. Typed table/tab/card/navigation mappings, broader source constructs, normalized resolution results, parser-diagnostic classification, production atomic output and full-corpus normalization remain pending. The first output is `data/normalized/examples/invoicing_policy.json`, with smart quotes disabled and parser configuration recorded.

### M2.2 corpus normalization checkpoint — 22 October 2026

- The user understood the first normalized document and asked to proceed. A separate successful user run of the starter was not reported. The new corpus package supersedes it and is ready for local execution.
- Schema `m22-0.2` / normalizer `structures-0.2` now maps the observed table/header/cell relationships and spans, tabs/panels, cards/navigation, math, figures/captions, substitutions and core prose/inline structures. Shared adapters and the reader are independent of comparison-probe modules. Generated tab locations are checked against source declarations; inherited/unknown line provenance stays explicit.
- Selected-corpus native references retain original targets and native resolved display titles/destinations. Unstaged document targets, unresolved labels and unchecked external URLs remain explicit states. Source-file existence is not claimed for unstaged targets. Inventory context participates in revision identity to reflect scope/index changes.
- The corpus command verifies the inventory fingerprint and file bytes, retains typed/raw parser diagnostics and writes a complete immutable snapshot under `data/normalized/corpus/<snapshot-id>/`. Identical runs verify/reuse existing bytes; failed new snapshot writes preserve previous output. No active index is switched.
- Assistant-local extracted-package validation passed all 10 focused tests and preservation fixtures: 30 normalized documents, 0 unsupported mappings, one table, six tabs, seven cards, two navigation blocks, one block formula, nine figures, eight explicit captions and 164 image nodes. Inline reference states were 101 resolved, 75 not in the corpus with unverified existence, 12 unresolved labels and 2 unchecked external URLs. All 280 parser diagnostic headers remain categorized and retained.
- A second fresh Python process reproduced the same full snapshot and reported reuse. The earlier single-page demo also passed with updated modules. On 23 October 2026 the user reproduced the 30-document corpus command with fixture checks and exact reported snapshot ID `15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc`, matching all reference/diagnostic counts. The separate ten-test user run was not posted; unit-test results remain assistant-local. Full M2 acceptance remains pending.

### M2 fidelity-review checkpoint — 23 October 2026

- Prepared a read-only review add-on that verifies the normalized snapshot/source bytes and generates pinned-RST, direct Sphinx HTML and independently rendered normalized-JSON views for all 30 pages. Eight recommended comparisons cover the reviewed structures and screenshot-dependent credit-note journal entries. The basic theme, literal icon identifiers and offline LaTeX display are explicit rendering limits.
- The audit checks local source availability for unstaged document targets, scans available manifest-discovery RST paths for literal-label candidates, inventories image presence/observed hashes and records Git checkout evidence. Candidates remain candidates and no outside page enters the selected/searchable corpus. Image/source existence does not establish screenshot-semantic coverage.
- Assistant-local validation passed six focused tests and the final add-on's 30-page generation. The native and normalized HTML product table agree across all 14 rows / 42 cells; selection/export logic was also exercised. Browser comparison was pending at package preparation; the user's subsequent review is recorded below. The local archive provides only 144/944 discovered RST files, no original images and no source Git history; local availability/candidate counts cannot be substituted for results from the user's full checkout.
- Review decisions start pending and can be exported with snapshot/review identity and checkout/image evidence. Their scope is the eight selected checks, not automatic completion of every M2 requirement. No actual journal-entry screenshot has been inspected by the assistant; the user's screenshot-dependent check is recorded below.

### M2 completion and human fidelity acceptance — 23 October 2026

Aarib reported all six fidelity-review tests passing and generated 30 comparison pages on the complete checkout: 944/944 RST paths available, 164/164 image dependencies present, and `clean_pinned` checkout evidence at `c9202e68ae702daec981b47d0b6055191084ffa2`.

The supplied `m2-review-decisions.json` matches normalized snapshot `15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc` and reported review-evidence ID `ee17fc24f6be820a14ed6ecd944a82cbc0c8fe4015b0553f2fbbab54b1dc8be0`. Its eight unique path/check pairs exactly match the tool's eight recommended fixtures. Every status is `pass`, notes are empty, and the export reports `selected_checks_passed` with scope `eight_selected_checks_only`. Decision-file SHA-256: `2bee1019a978d6693a20922d2b55235e5aaa6f6731849d7a4afcc2cf786a8aff`.

The passed checks cover warnings/examples/invoicing workflows, table relationships, reservation tabs, cards/navigation, procedure order/substitutions, formula/worked example, moves-history tabs, and screenshot-dependent credit-note information. Aarib additionally reported that the normalized rendering made important blocks clearer. This is user-reported human comparison, including the screenshot check; the assistant validated the export's consistency and did not independently inspect those screenshots or the full user-generated review packet.

The M2 completion criteria are met for this slice: all 30 selected files normalized with zero unsupported mappings; deterministic snapshots reproduced locally across fresh processes and matched by the user's reported identity; automated preservation checks and eight human fixture comparisons passed; source/block provenance and reference diagnostics remain explicit. The accepted scope and benchmark are unchanged. No new completion gate or scope waiver was introduced.

Remaining limits stay recorded: 75 out-of-corpus inline reference occurrences, 12 unresolved-label occurrences and two unchecked external references are not silently resolved. The 280 normalization diagnostic headers remain retained; image warnings from asset-free parser staging are distinct from the user's 164/164 review asset presence. Images/alt text/captions remain dependencies, with no OCR or image-only text extraction. A human screenshot check does not turn pixels into searchable text or certify all 164 images. The accepted review covers eight fixtures, not a visual audit of every page or compatibility with arbitrary future extensions.

**Next:** M3.1 — explain and design the chunk record and section-aware boundaries, preserving source-block links, warning context, table headers, tab conditions and procedure order. Then implement and compare a token-window baseline with structure-preserving chunks under M3. Embeddings and retrieval have not begun.

**What we build**

An explicit transformation pipeline:

Raw source → parsed document tree → normalized document → later chunks.

Use a Docutils/Sphinx-compatible parsing approach. First compare a controlled Docutils adapter with a Sphinx doctree extraction spike on representative files. Prefer the smallest approach that preserves the constructs actually found; avoid a regex-only RST parser.

The normalized representation keeps document identity, source snapshot, title, ordered sections, heading ancestry, and typed content blocks: paragraphs, ordered steps, lists, tables, notes/warnings, menu paths, UI labels, links, and references. Preserve provenance down to blocks or source spans where available.

Resolve references through an index of source labels and document targets. Track includes, substitutions, conditional content, tabs, and other encountered directives explicitly. A dependency may be read to parse a selected page without automatically becoming an independently searchable document. Unknown or unsupported constructs generate diagnostics rather than disappearing.

**What we learn**

Syntax versus meaning; intermediate representations; domain-specific normalization; reference resolution; and loss-aware ingestion.

**Why this comes here**

Chunking cannot restore warnings, procedure order, table relationships, or configuration prerequisites that extraction already discarded.

**Complete means**

Every selected file has either a normalized result or a visible failure. Human-reviewed fixtures cover the difficult constructs discovered in the corpus. Repeated parsing is deterministic. Warnings stay associated with their sections; tables retain header/value relationships; broken references and unsupported nodes are reported.

A comparison against raw source and selected rendered pages shows no silent loss of answer-critical information in the reviewed fixtures. Store image paths, alt text, and captions, while flagging dependencies on screenshot-only instructions.

**Intentionally postponed**

Universal support for every Sphinx extension, screenshot OCR, image reasoning, semantic chunking, and embedding generation. Parser execution is constrained from the beginning; do not run arbitrary repository Python or unsafe includes as a shortcut.

## M3 — Chunking, incremental indexing, and dense baseline

### M3.1 start — 23 October 2026

Aarib requested collaborative coding from this point: explain the mechanics, write small increments together, and inspect behavior before adding the next part. Do not deliver ready-made implementation files or ZIPs by default. The user writes the project code locally; code shown in conversation should be a small explained increment. Keep roadmap maintenance separate from code delivery.

The first increment is a normalized-JSON section walker in the proposed `backend/app/chunking/walk.py`. It recursively visits section `items` in source order and yields each block once without descending into block `children`. This preserves composite warning/list/table/tab structure for later explicit handling. Yielded blocks are inputs to chunk design, not final chunks; content eligibility, text rendering, section identity propagation, context attachment and token bounds remain to be implemented.

Assistant-local execution against the accepted invoicing-policy snapshot produced 22 section-level blocks: 11 paragraphs, five admonitions, three images, two anchors and one bullet list. The warning at line 120 retains paragraph/image children. The user subsequently reproduced this result, the important/warning rendering, image markers, bullet/numbered lists, 9-to-10 numbering/continuation checks and the 13-row table's labeled rendering. The tabs increment was supplied; a separate user tabs run has not been posted. Scope, benchmark and normalized snapshot are unchanged.

### M3.1 complete text-renderer increment — 23 October 2026

After understanding the common mechanics, Aarib explicitly requested one complete `text.py` for the remaining kinds, one testing command and a code-level explanation, to avoid repetitive per-kind edits. This authorizes a consolidated renderer and focused test file for this increment. The general preference for collaborative coding remains in effect for subsequent chunk design.

The supplied `text.py` is renderer version `m31-text-0.1`, with the existing public `render_block`, `single_child`, `row_values` and `render_table_row` functions preserved. Common child recursion is shared across containers. Lists share marker/indentation handling; figures/captions, tabs, cards, formulas and navigation retain explicit labels. Original navigation entries and stored reference states are shown as metadata; destination pages are never read or added. Anchors, comments and substitution definitions intentionally produce no body prose and remain intact on the normalized source records. Code/formula whitespace is preserved. Unknown kinds and unsupported table/numbering layouts raise errors. Internal table layout nodes are consumed through their parent table rather than rendered independently without headers.

`test_chunking_text.py` supplies one standard-library unittest command from `backend`: `uv run python -m unittest discover -s tests -p 'test_chunking_text.py' -v`. It verifies the exact accepted snapshot identity before the corpus checks; a missing or modified snapshot fails rather than skipping tests. Assistant-local execution passed all 13 tests, covering all 30 documents / 26 observed block kinds, repeated deterministic output and input immutability, both tab groups/all six panels, table header/value relationships and ambiguous-layout rejection, warning/image nesting, partial-delivery quantities, cards/navigation targets/states, figures/captions/title/formula, nested lists/number-width transitions and explicit metadata treatment. User reproduction of the consolidated increment is pending.

This is readable block-text preparation, not completed chunking. Bracketed labels/link states/image markers are renderer notation rather than verbatim source quotes. Heading inheritance, source-block and inline/dependency metadata on final chunk records, separation of evidence/retrieval text, token limits, packing/oversize policies and retrieval measurement remain to be built. The formatter does not resolve links, inspect pixels or change any source/snapshot state. Future chunk eligibility must distinguish navigation metadata from functional instructions. No embeddings or index activation have occurred, and M3.1/M3 remain in progress.

### M3.1 source-linked drafts and token measurement — 26 October 2026

Aarib implemented and reproduced a frozen `ChunkDraft` dataclass with source identity, document/revision IDs, owning section, heading path, contributing root block IDs, renderer version, evidence text and heading-enriched retrieval text. The initial real-source example identifies important block `b0011` in section `s0001`. A new `iter_blocks_with_sections` walker carries the nearest section ID while preserving composite block children; the existing `iter_blocks` API delegates to it. The user reproduced the policy page's 22 blocks and warning block `b0033` in section `s0030`, with heading `Invoicing policies > Invoice delivered quantity workflow`.

The user then reproduced `iter_chunk_drafts` across all 30 documents: **877 candidate drafts**, including **20 on the policy page** after two empty anchor outputs are skipped. The warning candidate retains its workflow heading, paragraph, image dependency and alt text. The builder requires complete schema `m22-0.2` input, shares immutable source identity and creates one draft per nonempty rendered root block. These remain candidates: image-only records and navigation metadata still require explicit grouping/eligibility decisions before indexing. No final chunk IDs, token-bounded packing or embeddings exist. The consolidated 13-test renderer output has not been posted by the user; the successful corpus builder run is a distinct user-reported checkpoint.

The token-counting increment uses `tiktoken==0.14.0`, explicit encoding `cl100k_base` and ordinary-text encoding to count full `retrieval_text`, including heading/formatting overhead. The package version and APIs were checked against PyPI and OpenAI's maintained source, then installed/executed locally. Measurements over the same 877 candidates were **minimum 10 / median 46 / nearest-rank P95 109 / maximum 413 tokens**; **0 exceed 512 tokens**. Aarib reproduced the package/encoding identity, 30-document/877-candidate counts and every size statistic on 26 October 2026. The largest candidate is moves-history block `b0031` at 413 tokens; the product-type table is 261 tokens. The value 512 is an inspection threshold, not a validated final chunking choice or a retrieval-quality claim. Token counting makes no embedding or model request; the encoding data can be downloaded/cached on first use.

Assistant-local checks reproduced the draft counts, rejected partial input, preserved the input objects, and reran all 13 existing renderer tests after the walker refactor; all passed. Local models/walker/draft copies serve only as verification of the code developed in conversation. Next, compare section-aware grouping and context/dependency attachment using measured token sizes; define oversized-content behavior and retain a plain token-window baseline. Final chunk records must preserve source/inline/dependency references and carry configuration identity. Scope, benchmark and accepted normalized snapshot are unchanged.

Tokenization primary references checked on 26 October 2026: https://pypi.org/project/tiktoken/0.14.0/ ; https://github.com/openai/tiktoken/blob/main/tiktoken/core.py ; https://github.com/openai/tiktoken/blob/main/tiktoken/model.py .

### M3.1 ordered section grouping — 26 October 2026

The next proposed `grouping.py` increment uses `itertools.groupby` on consecutive drafts. Its key includes document ID, normalized revision ID, section ID, heading path and renderer version. It materializes each group as a list so the shared group iterator does not become empty when traversal advances. It preserves original draft order and starts a new run after a nested section rather than collecting nonconsecutive parent content into a reordered bucket. The output is a list of drafts per group, not a finalized chunk.

Assistant-local checks over all 30 documents produced **197 consecutive section groups from 877 drafts**, with no dropped or reordered candidates and no cross-document/revision/renderer/heading merges. A synthetic A/B/A section sequence remains three groups. Joining each group's evidence in source order with one heading context shows **7 groups above the provisional 512-token threshold**. Thus the maximum individual draft size of 413 does not make whole-section grouping token-bounded.

The proposed user inspection targets the six policy-page groups: s0001 has 6 drafts / 354 tokens; s0013 has 2 / 117; s0017 has 2 / 104; s0020 has 2 / 205; s0026 has 3 / 222; s0030 has 5 / 324. The delivered-quantity workflow group retains source block IDs b0031, b0032, b0033, b0036 and b0038. The helper and these source/configuration-boundary checks were executed locally; user implementation/reproduction is pending. Token-bounded packing, source dependency attachment, navigation eligibility, final chunk identities and retrieval evaluation remain to be implemented. No chunk count or retrieval-quality result is established by the section-group count.

### M3.1 packed chunks, identities, snapshots, and eligibility — 28 October 2026

Aarib reproduced the six invoicing-policy section groups and their measured sizes. The merge helper combines the five delivered-quantity workflow drafts into one 324-token draft with source root IDs `b0031`, `b0032`, `b0033`, `b0036`, and `b0038`. The warning remains present and the original first draft retains only `b0031`. Section grouping uses normalized document structure rather than AI topic detection; it does not merge nonconsecutive sections or fetch linked pages.

The user reproduced image attachment over all 30 documents: **877 initial drafts become 743 units after attaching 134 standalone images** to preceding content within their section groups. No section begins with an unattached image in this corpus. Images already nested inside warnings/examples/figures remain inside their parent structures. The largest resulting unit is 413 tokens. Here, a unit is still a `ChunkDraft`: initially a draft identifies one nonempty root block, after attachment it can identify several root blocks, and packing can combine several such units. Composite blocks retain their children throughout.

The section packer appends complete units in source order while the merged retrieval text fits the provisional **512-token budget**, counting the heading once. An oversized unit raises an error; units are neither truncated nor split to fit. Aarib reproduced **205 packed candidates from 743 units across 30 documents**, with a largest packed chunk of 512 tokens. The policy workflow remains one 324-token chunk. The user also reported all three focused packing tests passed: exact fit, a one-token-smaller budget producing two intact chunks, and rejection of an already-combined oversized unit.

Chunk record schema is `m31-chunk-0.1`; the chunker version is `m31-section-images-greedy-0.1`. Records include token count, complete chunking settings/configuration ID and the source-linked draft content. Canonical JSON/SHA-256 identities cover source/revision/block/text information and recorded settings, without timestamps or machine-specific absolute paths. Chunker/eligibility version labels must be bumped when the corresponding rules change. Aarib reproduced identical repeat records and a changed ID when the recorded token budget changes. The workflow chunk ID is `00a5c1b7f199314779915500fe69ddc7b4918c1c1b49bccbd8de88ee3e3bb379`; configuration ID is `7b009580a77a9a34259ace6cd541363e16dfd810f975ddc0f63a69321c00deef`.

The document pipeline coordinates draft creation, ordered section grouping, image attachment, packing and record finalization. It rejects duplicate contributing root IDs and checks that output source IDs exactly match input coverage/order. Aarib reproduced **205 records with 205 unique IDs**, six records on the policy page, repeated deterministic output, unchanged normalized input and the token bound. Source root IDs plus document/revision identities link back to the accepted normalized records, including their original child structures, inline references and dependency metadata; the chunker does not resolve previously unresolved targets or read screenshot pixels.

The first saved chunk snapshot, schema `m31-chunk-snapshot-0.1`, is `44baac23f054f7fad6ff208c91c88cb81a85adda7821a6ffa22be2b36ceaa53e`. It contains `chunks.jsonl` and `summary.json`. The writer verifies the normalized snapshot's full file fingerprint before parsing its documents, builds all output before publication, stages writes in a temporary directory, and renames the complete directory into a content-derived destination. Identical existing bytes are reused; mismatching existing content is rejected. Aarib reproduced the exact snapshot identity, 30 documents/205 saved records, first-write/repeat-reuse behavior and the 512-token maximum. Assistant-local checks also rejected modified inputs before parsing, rejected corrupted saved snapshots, and preserved existing snapshots under simulated write failures.

Eligibility policy `m31-body-content-0.1` recursively checks for body content, including child paragraphs inside warnings and other composite structures. Navigation/cards, see-also admonitions, headings and image markers do not qualify on their own; mixed chunks remain eligible when they contain body content. Assessments separately identify body/metadata root IDs and verify the linked document/revision. Aarib reproduced **205 eligible candidates and 0 metadata-only candidates**, plus rejection of the real standalone policy see-also fixture. This is a structural eligibility policy rather than an answerability or retrieval-quality measurement.

The classified chunk snapshot, schema **`m31-chunk-snapshot-0.2`**, is **`2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce`**. It contains `chunks.jsonl`, `eligibility.jsonl` and `summary.json`, with **205 records and 205 corresponding eligibility decisions**. Aarib reproduced its exact identity, 205 eligible/0 metadata-only counts, byte-identical chunk data relative to the prior snapshot and successful repeat reuse. The old snapshot remains intact. Assistant-local persistence checks covered decision-to-chunk links, count/version agreement, eligibility-file corruption and simulated failures while writing that file.

Aarib subsequently reproduced the `app.chunking.cli` build with explicit `--snapshot`, `--output` and `--max-tokens 512` arguments: 30 normalized documents, 205 records, 205 eligible, maximum 512 tokens, identical classified snapshot ID and `Snapshot reused: True`. Assistant-local CLI checks also confirmed nonzero exits for invalid input/budgets and preservation of existing output. The accepted normalized snapshot remains `15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc`; the frozen 30-page scope and benchmark are unchanged.

The **combined 16-test renderer/packing suite passed in the assistant-local verification copy on 28 October**. It includes the previously supplied 13 renderer tests over the exact 30-document/26-kind snapshot and three packing-boundary tests. Aarib has reported the three packing tests passed, but has not yet posted the combined suite result; that remains the next user checkpoint. The local files are verification copies of collaboratively developed code, not direct inspection or editing of Aarib's laptop checkout. The general agreement to explain small code increments remains in force.

For the user-requested comparison, the assistant inspected Project 1 at Git commit `215960b35709e64b2bd28a7c93048d5695268389` in `https://github.com/aarib9892/ai-chat-runtime`: its actual chunker uses 400-token windows with 80-token overlap and the `o200k_base` tokenizer. It persists document/chunk identities and source information; no claim is made that it lacks provenance. This was source inspection, not a runtime/API/DB test. Project 2 currently preserves normalized section/block structure before enforcing a token budget. A measured token-window comparison, embedding/indexing lifecycle, dense retrieval and retrieval-quality/cost evaluation remain under M3 and have not been implemented. M3.1 remains in progress pending the final user acceptance checkpoint; M3's completion criteria below are unchanged.

### M3.2 start — 28 October 2026

Aarib explicitly requested proceeding with M3.2 after reproducing the classified snapshot and CLI. Proceed with embedding preparation while accurately retaining the combined 16-test user run as unreported; do not infer that the user ran it or block already-authorized independent preparation on that missing report. The three packing tests and the end-to-end chunk snapshot/CLI checks remain user-confirmed. Milestone titles, scope and completion gates are unchanged.

The first guided increment is `app/embeddings/inputs.py`, with a frozen `EmbeddingInput` carrying chunk ID, exact retrieval text, an SHA-256 of that text, and the recorded chunk token count. The loader verifies the complete classified snapshot fingerprint before parsing, requires snapshot schema `m31-chunk-snapshot-0.2`, checks unique and corresponding chunk/eligibility IDs, validates boolean flags and policy-version agreement, filters ineligible entries and checks summary totals. It selects eligible chunk text without following linked destination pages. It preserves the exact saved retrieval text without further whitespace normalization.

The text fingerprint identifies embedding input rather than the source-linked chunk record. Identical text can reuse a vector only when the embedding model/provider/dimensions and other relevant settings also match; those settings must be part of the complete cache key built next. A different source/configuration chunk ID alone does not require a new embedding if the exact input and embedding settings are unchanged. No vector-cache hit/reuse implementation is claimed at this preparation stage.

Assistant-local checks produced **205 prepared inputs, 205 unique text fingerprints, 39,253 recorded tokens and a largest input of 512 tokens**. Repeated output is deterministic and the saved chunk snapshot is unchanged. Controlled loader checks excluded an ineligible fixture and rejected mismatched IDs, a nonboolean eligibility flag, a different decision version and an invalid snapshot fingerprint. Aarib subsequently reproduced all four counts and identical repeated preparation. The recorded token total is not a billed API-usage or cost measurement.

The subsequent configuration/cache-key increment is recorded below. API integration, persisted real embeddings, incremental index publication and dense retrieval remain to be built. No embedding API request, SDK installation, API-key inspection or charge was performed for this increment. The token-window comparison and measured retrieval/cost work remain under M3; the 512-token chunk budget remains provisional. Continue using small explained code increments rather than implementation ZIPs or downloaded ready-made code files.

### M3.2 embedding configuration and vector cache — 28 October 2026

The baseline `EmbeddingConfig` uses provider `openai`, model `text-embedding-3-small` and 1,536 dimensions, matching the inspected Project 1 defaults. The official embedding guide and API reference were searched and opened before implementing this configuration. Configuration validation accepts the two documented third-generation embedding models, with positive integer dimensions bounded by their native lengths of 1,536 and 3,072. The default configuration ID is `8409d0f783f63f92d3d02fe8da09b4350ed2ce50a0f13532e7892a217cade5e2`. Key schema `m32-embedding-key-0.1` hashes configuration identity together with the SHA-256 of exact input text; it checks the text hash before creating a key. Chunk IDs and recorded token counts are excluded from the key so source-reference/token-accounting changes alone do not invalidate an identical text/model/dimension embedding. Aarib reproduced the baseline settings/configuration ID, **205 unique keys**, unchanged keys after a chunk-ID change and a changed key after reducing dimensions to 768.

The next guided `EmbeddingCache` increment stores one JSON file per cache key. Each entry records cache schema `m32-embedding-cache-0.1`, key, full embedding configuration/configuration ID, input text fingerprint, vector and an SHA-256 of the entry body. Vector validation checks dimensions, finite numeric values and a nonzero vector; loading checks the body checksum and expected identities. A missing file returns `None`; malformed or mismatching saved data raises an error rather than being treated as a cache miss. Storing identical data reuses the existing file, while a different vector for the same key is rejected. The complete new file is written in a temporary directory and atomically linked to its final name without replacing an existing entry; a competing identical writer is validated and reused.

Assistant-local cache checks passed for missing lookup, persistence, byte-preserving repeat storage, reuse across chunk references, separation by dimensions, invalid vector shapes/values, conflicting vectors, corrupted checksums/identities, interrupted writes and concurrent identical writers. The saved chunk snapshot remained unchanged. Tests use a clearly identified dummy vector in a temporary directory, not a production cache or real embedding output. Aarib subsequently reproduced the initial miss, 1,536-dimension reload, byte-preserving repeated store, wrong-dimension rejection and checksum-corruption rejection. The cache increment made no embedding request or billed usage; SDK/API-adapter work is recorded below. The combined 16-test M3.1 user run remains unreported and is not a blocker to the explicitly authorized M3.2 work.

Official API references checked on 28 October 2026: https://developers.openai.com/api/docs/guides/embeddings ; https://developers.openai.com/api/reference/resources/embeddings/methods/create . These establish the model/vector settings and API parameters, not access or billing availability for the user's account.

### M3.2 OpenAI adapter — 28 October 2026

The adapter increment uses an injected `AsyncOpenAI` client and raw text batches, allowing document text and later query text to share the same API layer. A frozen `EmbeddingBatch` carries ordered vectors, returned model, API-reported prompt/total tokens and optional request ID. Empty input returns an empty zero-usage batch without invoking the client. Nonempty strings are counted from their actual text with the existing tokenizer; documented limits of 2,048 inputs, 8,192 tokens per input and 300,000 input tokens per request are checked before sending. Requests explicitly select the configured model/dimensions and floating-point response format. Responses must name the configured model and contain each expected index exactly once; vectors are reordered by index and checked using the shared dimension/finite/nonzero validator. Usage counters must be nonnegative integers with total at least prompt tokens. SDK/API errors propagate to the caller.

The assistant installed **`openai==3.40.0`** in an isolated verification dependency directory and inspected its actual async embedding interface. This SDK uses **`httpx2`** (locally resolved as 2.16.0), rather than the older `httpx` package. The user was instructed to pin the tested OpenAI SDK version and subsequently reproduced the adapter mock check on 30 October; the installed package version was not separately reported. No real API credential was inspected: client tests supply a dummy key and an intercepting mock transport.

Assistant-local tests exercised the actual SDK request serialization and response parsing through that mock transport: two deliberately reversed three-dimensional dummy vectors were returned to their original input positions, mock usage of two tokens and a mock request ID were captured, and empty input made no transport call. Invalid text/batch sizes, wrong returned model, duplicate/missing response indexes, wrong dimensions, zero vectors and negative usage were rejected. A mocked 429 propagated as `RateLimitError`. The SDK's actual network API was not contacted, no real embeddings were produced and these dummy results were not added to the production cache. A bounded live request using the user's locally configured credential, followed by the generation/cache-reuse job, is the next integration checkpoint.

Official Python API reference searched and opened on 28 October 2026: https://developers.openai.com/api/reference/python/resources/embeddings/methods/create . The 512-token chunk budget remains provisional, the source/chunk snapshots and benchmark are unchanged, and dense indexing/evaluation remain to be built.

### M3.2 adapter acceptance and one-chunk integration — 30 October 2026

Aarib reproduced the mocked SDK check: **2 vectors, 3 dimensions, input order restored, 2 mock prompt tokens and request ID `req_mock_embeddings`**. This establishes the mocked adapter path; it does not establish live account access or produce real document vectors. The adapter's role was compared with Project 1's embedding service: a separate file is an organizational choice that isolates provider request/response handling from caching and job coordination.

The guided command selects only the first verified eligible chunk from classified snapshot `2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce`, checks `data/embeddings/cache`, and uses the default `text-embedding-3-small` configuration with 1,536 dimensions. On a miss it makes one SDK request with automatic retries disabled, validates the response through the adapter, and stores/reloads the vector. On a hit it returns the saved vector without creating an API client or needing a credential. It prints run-specific API request/token counts and the request ID when returned. Aarib chose a local `backend/.env` file loaded with `uv run --env-file .env`; the key is not shown or collected in chat. An inherited `OPENAI_API_KEY` takes precedence over the dotenv value; unsetting the inherited variable was included in the troubleshooting guidance.

Assistant-local verification used mock transport and a temporary cache: the first run stored and reloaded a 1,536-dimensional dummy vector; the repeat run made zero transport calls and needed no API credential. No mock vectors were saved to the production cache. The assistant made no real API request. Aarib subsequently reported a live authentication failure with HTTP 401 / `expired_secret_key`, then a successful request after the credential troubleshooting guidance. The successful chunk ID is `788668974cfd67ce169b1caa1a406837dfedbf4a9057d5c9c45d82f26b5dfe82`; the first successful run reported a cache miss, **1 API request, 174 API-reported prompt tokens, 1,536 dimensions, identical cache reload**, and request ID `req_1836797736c44db2875e631d6cb6f225`. The separate repeat run reported the same chunk/model, **cache hit, 0 API requests, 0 prompt tokens and 1,536 dimensions**. These are user-run results; the assistant did not access the credential or independently inspect the real vector. The repeat output omitted the final reload line, so that line is not separately claimed for the repeat. Corpus generation is subsequently recorded below; index lifecycle and dense retrieval evaluation remain pending. No corpus, benchmark or milestone-gate change occurred.

Official OpenAI Python SDK and embedding guide pages were searched and opened on 30 October 2026: https://developers.openai.com/api/reference/python ; https://developers.openai.com/api/docs/guides/embeddings .

### M3.2 batch-generation job — 30 October 2026

The next explained increment is `app/embeddings/job.py` with async `generate_embeddings(inputs, config, cache, batch_size=64, client=None)`. It validates the batch-size bound, computes all exact-text/configuration cache keys, preserves the first representative of duplicate keys, and verifies existing entries before creating a client. Its `cache_hits` count refers to unique keys found at job start. An all-cached or empty job returns without client creation. Missing entries are processed sequentially in lists of up to 64 texts through the existing adapter; the adapter verifies the complete response before vectors are stored. Each completed entry remains reusable if a later API request fails. Errors propagate and no successful completion report is returned for a failed run. `AsyncExitStack` closes only a client created by the job; an injected caller-owned client remains open. The default client disables automatic retries and uses a 60-second SDK timeout.

The returned in-memory report records input chunks, unique inputs, initial cache hits, generated vectors, successful SDK-call count, summed API-reported prompt/total tokens and per-call request IDs. This increment fills the content-based vector cache; it does not yet publish an embedding snapshot or active retrieval index, persist a standalone failure/usage log, measure retrieval quality or claim a cost total. Aarib reproduced the live first job with **205 input chunks, 205 unique inputs, 1 initial cache hit, 204 generated embeddings, 4 API requests and 39,079 prompt/total tokens**, matching the planned batches (64 + 64 + 64 + 12). The verification command loaded and checked all **205 cached vectors**. The repeat job reported **205 hits, 0 generated embeddings, 0 API requests, 0 prompt/total tokens and an empty request-ID list**; cache-completeness and repeat-reuse assertions passed. Combined with the earlier 174-token one-chunk request, the recorded successful generation requests report **39,253 prompt tokens across 5 successful API calls**. This arithmetic excludes the earlier failed authentication attempt and is not a monetary cost measurement. The assistant has not independently inspected the user's real cache bytes.

The first corpus-job request IDs reported by Aarib are `req_113fe8056845487b8d7cf517a86c4bd8`, `req_4bf3858cdbe941bba50d3f24ac2603c6`, `req_1c99ed4352834a23a563888807e4662a` and `req_0c614635d92745d1a2920592f04ad057`.

Assistant-local verification used actual SDK serialization with mock HTTP transport and temporary dummy vectors: all 205 source inputs were exercised, one seeded hit led to 204 generated vectors and 4 calls, and the mock token total was 39,079. Response rows were reversed to exercise adapter reordering and each text received a distinguishable fixture vector. An offline repeat created no client and left cache bytes unchanged. A later mocked 429 preserved the first two saved vectors and a resumed job reused them. Duplicate text across chunk IDs was embedded once; corrupt-cache preflight, empty input and invalid batch bounds were checked. The source chunk snapshot remained unchanged. The assistant made no real API request and did not save dummy vectors to the production cache.

Official Python embedding API documentation was searched and opened on 30 October 2026: https://developers.openai.com/api/reference/python/resources/embeddings/methods/create . The endpoint accepts an array of texts; existing adapter bounds still apply. This guided job increment leaves the milestone gates unchanged.

### M3.2 chunk-linked embedding records — 30 October 2026

After the user-confirmed complete cache and zero-request repeat, the next small increment is `app/embeddings/records.py`. `build_embedding_records(inputs, config, cache)` returns one record per input chunk in the original order. It rejects duplicate chunk IDs, uses the existing checksum/identity/vector-validated cache loader, and raises on a missing vector instead of returning a partial collection. Schema `m32-embedding-0.1` records the chunk ID, reusable embedding cache key, exact text SHA-256, full embedding configuration/configuration ID and the vector. `embedding_record_id` hashes the complete record body using the existing canonical JSON helper. It excludes timestamps and machine paths, making repeated construction over the same inputs/cache deterministic.

The reusable cache key identifies text plus embedding settings; the record ID additionally identifies the chunk-to-vector association. Two different chunks may therefore share one cached vector while receiving distinct embedding record IDs. These in-memory records are the next input to a complete self-contained embedding snapshot. This increment makes no API call and writes no snapshot or cache data. Aarib provided the first record's metadata: schema `m32-embedding-0.1`, embedding record ID `f39dea638bb9c1630b58b9e218d040c5832cdbef809fd8e2c6820717daf43c87`, chunk ID `788668974cfd67ce169b1caa1a406837dfedbf4a9057d5c9c45d82f26b5dfe82`, cache key `b95d29d15af84a44c6e5bd2951f69fcd364e875c281b46d954408506d6aed50c`, text SHA-256 `0c1c370aaab19c246edc2f8797f217f40c75cd16d7fcb23688dc5d3db7ad5ce6` and the expected baseline embedding configuration/configuration ID. The assistant independently matched the chunk ID, text hash and cache key against the verified chunk snapshot; the vector was not supplied, so its full record ID was recorded rather than independently recomputed. The user did not paste the preceding collection-count/check headers. The subsequent publisher rebuilt the full collection from the verified inputs/cache and its user-reported acceptance is recorded below.

Assistant-local checks used temporary dummy vectors for the same 205 verified source inputs. All 205 records had unique and repeatable IDs, preserved chunk order, matching configuration and 1,536 dimensions; record-body hashes matched. Two chunk IDs sharing one text reused the same cache key/vector and received different record IDs. Missing/corrupt cache entries and duplicate chunk IDs were rejected. Source snapshot and cache bytes remained unchanged by record construction. No real credential or vector was inspected and no real API request was made by the assistant. Milestone scope and completion gates are unchanged.

### M3.2 complete embedding snapshot publisher — 30 October 2026

The next guided increment is `app/embeddings/snapshot.py` with `save_embedding_snapshot(chunk_snapshot, output, config, cache)`. It verifies the complete classified chunk-snapshot fingerprint before parsing, loads eligible inputs through the existing verifier and constructs all chunk-linked records through the validated cache. A missing vector, corrupt cache, duplicate chunk ID or empty record set prevents publication. It makes no embedding API call.

Snapshot schema `m32-embedding-snapshot-0.1` contains exactly `embeddings.jsonl` and `summary.json`. The summary records chunk/normalized snapshot IDs, original source inventory fingerprint and source identity, normalized-document count, chunking and eligibility configuration identities, full embedding configuration/configuration ID, embedding-record count and unique cache-key count. The JSONL includes the actual vectors and chunk-linked record IDs. Source text/provenance remains accessible through the referenced chunk snapshot. No machine paths, timestamps, request IDs or per-run usage counters enter these deterministic files; those execution details belong in a separate run report to be added with the CLI.

Both files are serialized before writing and their complete bytes determine the destination folder fingerprint under `data/embeddings/corpus`. An existing identical payload is reused; differing existing content is rejected. New files are written to a private staging folder under the output directory and the complete folder is renamed to its final fingerprint path. If an identical concurrent publisher wins the rename race, its complete bytes are checked and reused. Failed staging writes leave prior snapshots unchanged and do not expose a final partial folder. This publishes an embedding artifact; selecting an active database/retrieval index remains a later M3 task.

Assistant-local tests used temporary dummy vectors for all 205 real source inputs. The resulting fixture had 205 ordered, uniquely identified records at 1,536 dimensions and 30-document provenance, matched its folder fingerprint and was reused byte-for-byte. Missing-cache and pre-parse source-tampering rejection, a simulated partial second-file write with staging cleanup, four concurrent identical publishers and rejection of a corrupted existing snapshot all passed. Source and cache bytes remained unchanged. Fixture snapshots were temporary; no real user vectors/credentials were inspected and no embedding API request was made. Aarib subsequently reported schema `m32-embedding-snapshot-0.1`, **30 normalized documents, 205 embedding records, 205 unique embeddings, 1,536 dimensions, first reuse False and repeat reuse True**. Snapshot fingerprint/vector/repeat-reuse assertions passed. The user-published real-vector snapshot ID is **`6e2c657ee8cd109c40c928024916ba5f0803bbee65e6a0abadfdf47dddb4343c`**, saved at `/home/aarib/odoo-functional-rag/data/embeddings/corpus/6e2c657ee8cd109c40c928024916ba5f0803bbee65e6a0abadfdf47dddb4343c`. This ID is user-reported; the assistant has not received the real snapshot bytes and does not claim to have independently reproduced its vector-dependent fingerprint. No milestone scope or completion-gate change occurred.

### M3.2 combined CLI and per-run reports — 30 October 2026

The next explained increment is `app/embeddings/cli.py`. Its `--snapshot`, `--cache`, `--output`, `--reports`, `--model`, `--dimensions` and `--batch-size` arguments coordinate the existing verified input loader, generation job and complete snapshot publisher. Defaults retain the accepted baseline model/dimensions and batch size 64. Resolved write destinations inside the input snapshot are rejected before any mutation. Invalid configuration/argument values exit as CLI usage errors.

Each execution uses a UUID-named report under `data/embeddings/runs`, schema `m32-embedding-run-0.1`. The initial `running` report is written before generation, confirming report storage is available. `write_report` stages JSON in the same report directory and atomically replaces only that run's file. Completion records UTC timestamps, elapsed seconds, source chunk-snapshot ID, full embedding configuration/configuration ID, the successful generation report, output snapshot ID/path, record count and snapshot-reuse state. Unchanged input/cache therefore preserves the deterministic snapshot ID while each execution has a distinct operational report.

Runtime failures retain the failing stage (`load_inputs`, `generate_embeddings` or `publish_snapshot`), mark the report `failed`, record exception type/HTTP status/API code/request ID and exit nonzero. Raw exception messages, response bodies and credentials are omitted. When generation itself raises, its current function has not returned a complete report: `generation` remains JSON null, explicitly meaning unavailable rather than zero usage. Successful earlier vectors remain cached, but complete per-request partial-failure accounting remains a known observability limitation. If generation completes and publication fails, its returned usage is retained. A failure to finalize the report exits nonzero and may leave the initial `running` report; already-complete snapshot/cache data remains reusable. Process termination can likewise leave a running report and must not be interpreted as success.

Assistant-local checks used temporary dummy vectors for all 205 frozen inputs. Two cached CLI executions created no API client or requests, reused the identical snapshot and persisted distinct completed reports. Tampered input, a mocked SDK authentication exception and a publication exception produced the correct failed stages/nonzero exits; failed generation used null metrics and sensitive fixture error text was not logged. Initial report-write failure stopped before generation. Final report-write failure retained the running record, and a failed atomic report replacement preserved its prior bytes and cleaned staging. Input-directory write targets were rejected and original chunk/cache bytes remained unchanged. No real user vectors/credentials were inspected and no real API request was made by the assistant. Aarib subsequently reproduced the combined CLI with run ID `3430bf40-b3aa-41ff-955c-f4e457fab573`: **status succeeded, stage complete, 205 inputs/unique keys/cache hits, 0 generated embeddings, 0 API requests, 0 prompt/total tokens and no request IDs**, the expected configuration ID, **205 embedding records and snapshot reuse True**. The snapshot ID remained `6e2c657ee8cd109c40c928024916ba5f0803bbee65e6a0abadfdf47dddb4343c`. The report records start `2026-10-30T14:48:57.457433+00:00`, finish `2026-10-30T14:48:58.587882+00:00` and **1.13 seconds** elapsed. This measures the cached embedding CLI invocation, not retrieval latency. One original CLI run was pasted; the final temporary-copy probe subsequently verified two distinct persisted reports. The user-reported failure verification is recorded below; dense indexing/evaluation and M3.1's combined user test report remain pending.

Official OpenAI Python SDK error/request-ID documentation was searched and opened on 30 October 2026: https://developers.openai.com/api/reference/python . This supports the SDK error metadata used in the report, not any independent account or billing verification.

### M3.2 final CLI/failure verification — 30 October 2026

The final guided command is a temporary-copy verification probe, with no additional application-code changes. It reads and fingerprints the accepted chunk snapshot and the user-published embedding snapshot, copies those inputs and the vector cache into a temporary directory, and runs the actual CLI against those copies. The API-client constructor is patched to raise if invoked and is asserted never called. Two cached executions must persist distinct reports, return success and reuse the same embedding snapshot.

The probe then changes a copied chunk-summary byte and expects a nonzero `load_inputs` failure, changes a copied selected vector without updating its checksum and expects a nonzero `generate_embeddings` failure with unavailable/null generation metrics, and simulates a partial summary-file write during publication to a fresh output directory. The last case must return a nonzero `publish_snapshot` failure, retain the successful zero-request generation report, clean all staging and preserve the prior copied snapshot byte-for-byte. Original production chunk/cache/embedding-snapshot bytes are compared before/after and must remain unchanged. This reproduces the principal local integrity and failed-publication checks; earlier interrupted-job/resume, API metadata and report-write tests remain assistant-local evidence unless separately reproduced.

The assistant ran this exact probe against temporary dummy vectors and a temporary complete 205-record snapshot over the frozen real chunk inputs; all checks passed and no API client was created. The user's actual vector-dependent snapshot fingerprint remains user-reported. On **1 November 2026**, Aarib reproduced all five final output lines: **cached CLI and separate persisted reports passed; changed chunk snapshot rejected; corrupt cached vector rejected; failed publication preserved the old snapshot and cleaned staging; production bytes unchanged with no API client created**. This completes the guided M3.2 embedding-generation/cache/artifact/CLI increment for the accepted 30-document, 205-chunk baseline. It does not establish dense retrieval or answer quality; the overall M3 retrieval, lifecycle and evaluation gates remain unchanged. Complete per-request usage accounting for a failed generation job remains the previously documented observability limitation rather than a fabricated zero-usage claim.

### M3.3 start — 1 November 2026

Begin database storage and dense retrieval in the existing collaborative cadence: explain one increment, let Aarib write/run it locally, and review the result before expanding. The first step was a read-only inventory of Docker/Compose, running container ports, the local psql client and `backend/pyproject.toml`. The assistant's workspace is a verification copy and cannot establish the user's live PostgreSQL runtime independently. Aarib supplied that runtime output on 1 November: **Docker 29.1.3, Docker Compose v5.0.1 and host psql 16.15**. Running services include Project 1's `pgvector/pgvector:pg14` database with container-only `5432/tcp`, its frontend published on port 3000, and `tph-postgres-1` (`postgres:16-alpine`) published on **127.0.0.1:55432**. The backend project declares Python >=3.12, production dependencies `openai==3.40.0` and `tiktoken==0.14.0`, and the parser-spike group Docutils 0.21.2/Sphinx 8.2.3/sphinx-tabs 3.5.0; no Python PostgreSQL driver is declared yet. The new database setup is recorded below. No existing project/database was modified or queried.

The M3.3 implementation stores chunk text/source provenance and the existing 1,536-dimensional embeddings with their source snapshot and embedding configuration identities. Import verifies both frozen snapshots and their chunk/text/configuration associations before publication. Query embeddings must match the selected corpus's embedding configuration. Start with exact cosine nearest-neighbor search, as required by the existing M3 baseline; active-snapshot selection and complete transactional import keep readers on a coherent published set. Database import uses the saved vectors; fresh document embeddings are unnecessary for unchanged input. The Compose bootstrap, managed Python connection, first schema migration, real-snapshot loader and initial/repeated import/publication have been reproduced. Exact vector search is the current guided increment; real user-question retrieval and its measurements remain pending.

The official pgvector README was searched and opened on 1 November 2026: https://github.com/pgvector/pgvector . It documents cosine distance (`<=>`) and exact nearest-neighbor search by default. No approximate-index or model/scope change is introduced. Dense retrieval measurements, the plain token-window comparison, incremental added/changed/removed/failed-document behavior and complete active-index publication still belong to the unchanged M3 completion gate. M3.1's combined 16-test user report remains unreported and is not used to block already-authorized independent M3.3 preparation.

### M3.3 dedicated PostgreSQL/pgvector bootstrap — 1 November 2026

The next guided file is project-root `compose.db.yaml`, with Compose project name `odoo-functional-rag` and a single `db` service using **`pgvector/pgvector:0.8.7-pg16-bookworm`**. This selects PostgreSQL major 16 and pgvector 0.8.7 using a tag listed by the official pgvector maintainers; it is not a digest pin of every image byte. Database and bootstrap user are `odoo_rag`. The proposed host endpoint is **127.0.0.1:55433**, mapped to container port 5432. No reported container publishes this host port; other host listeners were not independently inspected, so successful startup still needs to verify availability.

The file declares only `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD` in the container environment. The password comes from required interpolation `${ODOO_RAG_DB_PASSWORD:?...}`, appended privately to the user's existing `backend/.env`. `docker compose --env-file .env` is used from `backend` for interpolation; the entire backend dotenv file is not specified as a container `env_file`. No real database password or API key is collected, printed or included in the verification copy. The project-scoped named volume `postgres_data` mounts `/var/lib/postgresql/data`, the documented PostgreSQL 16 image data path. A `pg_isready` health check uses `$${POSTGRES_USER}`/`$${POSTGRES_DB}` so variable expansion occurs inside the container.

The user-run commands first validate with `config --quiet`, then start only `db` with `up --wait --wait-timeout 60`, then execute psql inside that container with `ON_ERROR_STOP=1`. The SQL enables `CREATE EXTENSION IF NOT EXISTS vector`, identifies the database/user/server version and selects the installed vector extension version. Aarib reproduced silent successful Compose validation, creation of network `odoo-functional-rag_default`, named volume `odoo-functional-rag_postgres_data` and **healthy container `odoo-functional-rag-db-1`**. The SQL returned `CREATE EXTENSION`, database/user **`odoo_rag`/`odoo_rag`**, PostgreSQL **`16.15 (Debian 16.15-1.pgdg12+2)`** and extension **`vector` version `0.8.7`**. These user-reported internal-container SQL checks do not yet verify Python connectivity or host TCP password authentication. No application tables, vector imports, approximate indexes or active-index changes are part of this bootstrap increment.

Assistant verification parsed the Compose YAML and checked the image, localhost port binding, named-volume mount, required password interpolation, explicit DB-only environment and deferred health-check variables. Docker is not installed in the assistant's verification runtime, so the assistant started no container, executed no SQL and inspected no user's live database. Docker Compose's own configuration validation and real startup/extension verification are user-reproduced as recorded above. Existing source/chunk/embedding snapshots and milestone completion gates are unchanged.

Primary sources searched/opened on 1 November 2026: https://github.com/pgvector/pgvector (supported Docker tags and per-database extension enablement); https://hub.docker.com/_/postgres (environment/bootstrap behavior and PostgreSQL <=17 volume path); https://docs.docker.com/reference/compose-file/interpolation/ (required interpolation and `$$`); https://docs.docker.com/reference/cli/docker/compose/up/ (`--wait`/`--wait-timeout`); https://docs.docker.com/reference/cli/docker/compose/config/ (`--quiet` validation).

### M3.3 managed Python database connection — 1 November 2026

The next small explained increment installs **`asyncpg==0.32.0`** and adds `app/database.py` with async context manager `connect_database()`. The helper reads the existing `ODOO_RAG_DB_PASSWORD` only when entered, rejects a missing/empty password and invalid port before connection, and defaults to host `127.0.0.1`, port `55433`, database/user `odoo_rag`. Optional project-prefixed host/port/user/name environment overrides keep it usable in later command/container contexts. Connection keyword arguments carry the password directly instead of constructing a URL requiring password escaping. The connection timeout is 10 seconds, default query timeout 30 seconds, close timeout 5 seconds and application name `odoo-functional-rag`.

`@asynccontextmanager` exposes the connection through `yield` inside `async with`; `finally` closes it after ordinary success or failure. This first helper manages one connection per indexing/query command. Historical Project 1 source was inspected and uses an asyncpg pool plus pgvector codec registration for its API server; that lifecycle was not copied wholesale into the current CLI-oriented increment. No vector codec or separate pgvector Python package is introduced by this connection check.

The user-run verification loads `.env` with `uv run --env-file .env`, queries the database/user/server/extension identity through the host TCP connection and evaluates cosine distance between two tiny SQL test vectors. Aarib reproduced **database/user `odoo_rag`/`odoo_rag`, PostgreSQL `16.15 (Debian 16.15-1.pgdg12+2)`, pgvector `0.8.7`, cosine distance `1.0` and connection closed `True`**. This confirms the helper ran through actual host TCP/password connection, queries and context cleanup; the installed asyncpg version was not separately printed. These are read-only queries; the corpus vectors remain at 1,536 dimensions, and no application table/import or embedding request is involved.

Assistant verification installed asyncpg 0.32.0 into an isolated dependency directory and inspected the actual connect/close signatures. Mocked tests checked default/overridden connection arguments, close after successful and failing bodies, rejection of missing/empty password and malformed/out-of-range port before connecting, and propagation of a connection error. Those driver-helper tests made no real database connection or SQL query; no user credential was inspected. Official asyncpg documentation and PyPI metadata were searched and opened on 1 November 2026: https://magicstack.github.io/asyncpg/current/api/index.html ; https://magicstack.github.io/asyncpg/current/usage.html ; https://pypi.org/project/asyncpg/ . Source scope and M3 completion gates are unchanged.

### M3.3 first schema migration — 1 November 2026

Prepared one guided schema increment, `backend/migrations/001_dense_index.sql`, and a small explicit-file runner, `backend/app/migrate.py`. The four application tables are `index_snapshots` (lineage/configuration, expected chunk count and publication state), `embeddings` (reusable cache-key vectors), `index_chunks` (per-snapshot chunk membership, exact retrieval text and complete original JSON record), and `active_indexes` (corpus name to published snapshot). The vector column is deliberately `VECTOR(1536)` for the accepted configuration and rejects zero norms. Composite foreign keys enforce snapshot/configuration and vector/configuration/text-hash associations. Row checks verify the retrieval-text SHA-256 and agreement between typed chunk ID/text and the preserved JSON record. A published timestamp must match publication state, and the active pointer can reference only a row marked published. Ordinary primary/unique constraint indexes are present; no approximate vector index is introduced.

Completeness is an importer responsibility: `expected_chunks` records the intended size, but this migration does not itself count child rows or make published content immutable. The later importer must verify all frozen records, count/membership and configuration consistency before publishing and switching the active pointer in one transaction. The full chunk JSON preserves existing source/section/block citation information. Saved artifact identities remain authoritative; eventual import must account for pgvector's single-precision storage rather than rehashing rounded database vectors as original embedding artifacts.

`apply_migration(path)` hashes exact SQL bytes, opens the managed connection and one transaction, obtains advisory transaction lock `3301001`, and checks a `schema_migrations` registry. A matching filename/checksum returns reused `True`; a changed already-applied file raises before application DDL; a new file executes and records its checksum atomically, returning `False`. Application DDL intentionally omits `IF NOT EXISTS` so the registry handles repeats without concealing unrelated existing-table drift. Future schema edits use a new migration file. The runner applies only the explicitly passed file; it is not yet a discovery CLI.

Assistant-local SQL integration checks ran against a temporary embedded PGlite **PostgreSQL 18.6 / pgvector 0.8.7** engine, not Aarib's PostgreSQL 16 database. They passed actual four-table creation, valid 1,536-dimensional fixture insertion and self-cosine distance, rejection of wrong dimensions/zero vectors/configuration links/text hashes/JSON identity, publication-pointer guards and rollback of failed DDL/data transactions. Four mocked Python runner tests passed: first application/registration, identical reuse without rerunning DDL, checksum-change rejection and DDL-failure propagation without registration. PostgreSQL 16's primary documentation was checked for composite foreign keys, built-in SHA-256/UTF-8 conversion and advisory transaction locks. No user database, real vectors, credentials or API calls were used in these local tests. Aarib subsequently reproduced the migration on his PostgreSQL 16 database: **first call reused False, repeat reused True, checksum/repeat checks passed and all four application tables had zero records**. A preceding missing-relative-file error was resolved before successful application.

The schema is now user-verified and empty. Source/normalized/chunk/embedding snapshots, the benchmark and M3 completion gates are unchanged. Snapshot loading/import, active publication, exact dense queries and retrieval/lifecycle evaluation remain outstanding.

Primary sources checked on 1 November 2026: https://www.postgresql.org/docs/16/ddl-constraints.html ; https://www.postgresql.org/docs/16/functions-binarystring.html ; https://www.postgresql.org/docs/16/functions-admin.html ; https://pglite.dev/extensions/ ; https://github.com/pgvector/pgvector .

### M3.3 verified snapshot-pair loader — 1 November 2026

Prepared `backend/app/indexing/__init__.py` and `backend/app/indexing/inputs.py` as the next explained increment. `load_index_inputs(chunk_snapshot, embedding_snapshot)` reads exact file sets, verifies both content fingerprints and schema versions, matches the embedding snapshot's parent chunk ID and shared normalized/source/inventory/chunking/eligibility lineage, reconstructs and checks the embedding configuration, and requires the migration's 1,536 dimensions. It reuses the existing classified eligibility loader, validates chunk record/configuration identities and source metadata, and matches embeddings to exactly the eligible chunk-ID set. Missing, extra or duplicate membership is rejected. Each original embedding record must equal the independently expected schema/chunk/text-hash/cache-key/configuration metadata plus its validated original vector and recomputed record ID. Conflicting vectors for one cache key and inconsistent summary counts are rejected. The returned `IndexInputs` contains summaries/configuration/IDs and ordered `(chunk, embedding)` pairs; embedding-file order need not match chunk-file order. It reads saved artifacts without opening a database, constructing an API client or changing source files. No new snapshot identity or database row is published by this increment.

Assistant-local checks used all **205 accepted chunk records** with temporary dummy 1,536-dimensional vectors and a separately generated embedding snapshot. Repeated loads were identical, chunk order and exact pair membership were preserved, and reversed embedding-file order was restored. Thirteen independently re-fingerprinted invalid lineage/configuration/membership/association/vector/count cases were rejected; byte tampering and a forged chunk record identity were rejected. A temporary eligibility variant correctly excluded one metadata-only chunk and returned the matching 204 pairs. Original source/fixture embedding snapshot bytes remained unchanged. These checks did not inspect Aarib's real vector bytes or reproduce his real embedding snapshot ID, and made no database/API calls. Aarib subsequently reproduced the real-snapshot loader: **30 documents, 205 verified chunk/vector pairs, 205 unique embeddings, 1,536 dimensions, repeated load identical True, tampered copy rejected True and original snapshot bytes unchanged True**. Transactional import/publication, exact dense retrieval and existing evaluation/lifecycle gates remain outstanding.

### M3.3 transactional database importer — 1 November 2026

Added the guided file `backend/app/indexing/importer.py`, with `import_index(chunk_snapshot, embedding_snapshot, corpus_name="odoo19") -> (snapshot_id, reused)`. It calls the verified loader before opening a connection. The database snapshot ID hashes import schema `m33-dense-index-0.1` and both complete input snapshot IDs. For the accepted pair, the derived and now user-reported database snapshot ID is **`e8f661333130c61d51f1a68908ef2038c9a5d24575369bbaa3bccf0bb2b97818`**.

One managed connection/transaction obtains advisory lock `3303001`, validates an existing published snapshot header or inserts a new unpublished header, inserts missing vectors without overwriting cache-key conflicts, and verifies vector/configuration/text-hash equality. Comparison casts expected vectors to the same pgvector 1,536-dimensional single-precision representation; it does not rehash rounded database vectors as original artifacts. A new snapshot's chunk membership is inserted with parameterized `executemany`. Every run reads back the full membership, typed identities/retrieval text and preserved chunk JSON, and checks them against all expected rows. After successful verification, a new snapshot is marked published and `active_indexes` is inserted/updated in the same transaction. Existing published snapshot contents/timestamps are not rewritten; reuse still verifies all vectors and chunks before activation. Unexpected existing unpublished data is rejected. Import exceptions propagate and roll back all transaction changes. The advisory lock serializes cooperating importer calls; real concurrent-driver behavior has not been independently exercised.

Assistant-local integration tests ran the actual Python importer and SQL through a test-only request bridge to temporary embedded **PostgreSQL 18.6 / pgvector 0.8.7**, using all 205 accepted chunks and dummy vectors. They passed initial publication, exact metadata/chunk readback, float32 vector comparison, identical reuse without duplicate rows, rollback after seven inserted chunks and after updating the active pointer, rejection of conflicting cache-key vectors and changed stored vector/chunk metadata, and pre-connection rejection of tampered snapshot bytes. A second complete fixture snapshot retained 205 reusable vectors with 410 chunk memberships; reactivating the earlier verified snapshot passed. Artifact bytes remained unchanged. The bridge adapts results to asyncpg's default JSON-string behavior but does not test native asyncpg transport or Aarib's PostgreSQL 16 runtime. No user database, real vectors, credentials or API calls were used by the assistant. Aarib subsequently reproduced the native import: **first reused False, repeat reused True, published True, stored chunks 205, unique embeddings 205, active snapshot matches True and original snapshot bytes unchanged True**, with the exact expected database snapshot ID. Native failure-injection/concurrency verification remains unreported; exact retrieval and the unchanged M3 lifecycle/evaluation gates remain outstanding.

The completed user command imported twice, queried publication/counts/active membership, and confirmed that original snapshot bytes remained unchanged. Primary documentation checked on 1 November 2026: https://www.postgresql.org/docs/16/tutorial-transactions.html ; https://magicstack.github.io/asyncpg/current/api/index.html ; https://magicstack.github.io/asyncpg/current/usage.html ; https://github.com/pgvector/pgvector .

### M3.3 exact cosine vector search — 1 November 2026

Prepared `backend/app/retrieval/__init__.py` and `backend/app/retrieval/dense.py`. `search_dense(query_vector, config, corpus_name="odoo19", top_k=5)` validates positive integer K, corpus name, 1,536 dimensions and a finite nonzero query vector. A read-only repeatable-read transaction selects the active published snapshot and checks its complete embedding configuration and configuration ID against the query. The search is restricted to that selected snapshot/configuration, joins vectors by cache key/configuration/text hash, ranks by pgvector cosine distance (`<=>`) ascending and chunk ID as a deterministic tie-break, and returns at most K hits. Results retain the chosen snapshot/configuration, ranks/distances, embedding/cache identities, retrieval text and complete original chunk JSON with source/heading/block metadata. Missing published corpora, incompatible models/configurations, empty searchable snapshots and non-finite distance results are explicit errors. No approximate vector index, embedding request or generated answer is introduced.

Assistant-local SQL integration used temporary embedded **PostgreSQL 18.6 / pgvector 0.8.7** through the existing test-only async bridge, all 205 accepted chunks and known dummy unit/opposite vectors. All 205 distances and ranks matched an independent 0/1/2-distance expectation, including deterministic ties; top-K, identical repeats, full source metadata and unchanged database state passed. Invalid inputs, missing corpus, wrong model/dimensions and a tiny query that rounds to zero at storage precision were rejected. A temporary eligibility variant excluded one chunk while the old 205-row snapshot remained stored: search returned exactly the new active snapshot's 204 members, and reactivation restored the original results. This tests snapshot isolation of membership, not the complete future source-deletion lifecycle. No user database, real vectors or API calls were used; original artifact bytes were unchanged.

The user command reused the saved vector for the invoicing-policy warning chunk. Aarib reproduced the expected database snapshot ID, **5 hits, self-match near zero True, repeated search identical True and matching saved source metadata True**. The first hit was `invoicing_policy.rst` / `Invoicing policies > Invoice delivered quantity workflow`, distance **0.000000**. Subsequent distances were **0.181054** (same file, `Invoicing policies > Invoice ordered quantity workflow > Invoicing what is delivered`), **0.219554** (same file, ordered quantity workflow), **0.297932** (same file, page heading) and **0.305397** (`inventory/product_management/configure/type.rst`, Product type > Configure goods > Invoicing policy). This establishes native search mechanics and provenance, not benchmark relevance or question-answer quality. Real semantic question retrieval, Hit@K/MRR/evidence coverage/latency/cost, token-window comparison and existing M3 lifecycle gates remain outstanding. Source corpus and benchmark scope are unchanged.

The second hit's unusual breadcrumb was checked against the pinned RST and normalized `invoicing_policy.json`. Section `s0026` at source line 88 already has that path: the page first introduces an underline-only `-` heading, then underline-only `=` headings, so the parsed section hierarchy nests the delivered-policy section under the preceding ordered-workflow section. The normalizer/chunker faithfully retained that source hierarchy. Record it as a source-structure quirk for retrieval review; no source edit, inferred hierarchy rewrite, snapshot replacement or benchmark change was made.

Primary documentation checked on 1 November 2026: https://github.com/pgvector/pgvector (cosine operator and exact search default); https://magicstack.github.io/asyncpg/current/api/index.html (transaction options); https://www.postgresql.org/docs/16/transaction-iso.html (repeatable-read view).

### M3.3 question embeddings and retrieval — 1 November 2026

Prepared `backend/app/retrieval/query.py` with `retrieve_question(question, cache, corpus_name="odoo19", top_k=5, *, client=None)`. It checks nonempty input/corpus, positive K and the existing 8,192-token embedding limit before opening a database connection. It reads the active published snapshot's exact configuration, validates its ID and 1,536 dimensions, wraps the unchanged question text in one existing `EmbeddingInput` with a `query:<text hash>` label, and reuses `generate_embeddings` plus `EmbeddingCache`. Cache identity still depends on exact text/configuration, not that label. The resulting vector goes to `search_dense`; if the active snapshot changed between configuration selection and search, the wrapper raises and asks the caller to retry. It returns ranked evidence with snapshot/configuration provenance, question text/hash/token count and current-call query embedding cache key/hit/API requests/usage/request IDs. Cached calls construct no owned API client. A separate user cache directory `data/embeddings/query-cache` keeps these query artifacts apart from document-vector generation. No answer generation or database publication occurs in the wrapper.

Assistant-local integration exercised the actual OpenAI 3.40.0 adapter/job using HTTP mock transport and actual dense SQL in temporary embedded PostgreSQL 18.6/pgvector 0.8.7 with dummy document vectors. The first mocked question made one request with the active model/dimensions, reported expected token usage/request ID and cached its vector; repeated and client-constructor-blocked cached calls made zero requests and returned identical hits. Empty/oversized/invalid questions, missing corpus and a corrupt query cache stopped without API requests; a mocked snapshot-change guard rejected inconsistent request context; a mocked SDK 503 propagated without storing a vector. Database and original artifact bytes were unchanged by retrieval. No real API request, real vector/credential inspection or user database access occurred. Failure-report/partial-usage limitations inherited from the existing embedding job remain as previously recorded; this wrapper is not yet a persisted run-report CLI.

The user command used exact accepted **development case `M12-DRAFT-003`**: `Can I enable Automatic Invoice on online payment while using Invoice what is delivered?`. Aarib reproduced model **`text-embedding-3-small`**, **1,536 dimensions**, query cache key **`3f9195abbd2aba73a0f6a5e169e0380af617171c082171c065c4ef6f151d9ca7`**, first-call cache hit **False**, **1 API request / 15 prompt and total tokens**, request ID **`req_9cd7924110e84e02a36124f23278bade`**; repeat cache hit **True**, **0 requests/tokens** and no request IDs. Repeated ranked retrieval was identical. Rank 1 was the invoicing-policy root chunk at **0.395706**, and its displayed evidence retained the IMPORTANT block explicitly stating that Automatic Invoice cannot be activated with Invoice what is delivered. Following distances were **0.435787** (delivered quantity workflow), **0.437504** (delivered-policy section with the previously noted source-native breadcrumb), **0.439774** (`sales_quotations/get_paid_to_validate.rst`, Activate online payments) and **0.455813** (ordered-policy section). This is one manually inspected successful development example, not a measured benchmark aggregate. The question's 15 tokens are separate from the previously recorded document-generation usage. Only development question text was consulted for demo selection; no holdout case content/labels or measured outcomes were consulted or tuned. Source scope, accepted artifacts, benchmark split and M3 completion gates are unchanged.

Primary sources checked on 1 November 2026: https://developers.openai.com/api/reference/python/resources/embeddings/methods/create (embedding input/model/dimensions/encoding and usage); https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#sections (RST section styles). The local pinned SDK/adapter/job code was inspected before constructing the integration.

### M3.3 persisted retrieval CLI — 1 November 2026

Prepared the next explained increment, `backend/app/retrieval/cli.py`, runnable with `python -m app.retrieval.cli`. Arguments are `--question`, `--corpus`, `--top-k`, `--cache` and `--reports`; defaults use the existing query cache and `data/retrieval/runs`. Each call creates a new UUID report with an initial running state before invoking retrieval. It saves the full returned evidence/configuration/snapshot/query/cache/usage data under `result`, plus UTC timestamps, status and timing. Report JSON uses a temporary file and atomic replacement in the destination directory. The terminal prints a compact status/usage/ranked-path summary and saved report path. Repeated identical questions get distinct run IDs while reusing the question vector and returning the same evidence when the index is unchanged.

`retrieval_seconds` measures the wrapper invocation through `asyncio.run`, including event-loop setup/cleanup, database connections/reads, query cache and any embedding request; it excludes the initial/final report file writes. `duration_seconds` starts before initial report creation and ends before final report serialization/replacement and terminal output. These are CLI measurements, not standalone SQL timings. Reports retain cache-hit/API-usage context so cached and API-generating runs can be distinguished during later evaluation. Runtime exceptions record safe exception/HTTP/API-code/request-ID metadata and exit nonzero. A failed wrapper leaves `result` null, meaning unavailable rather than zero API usage; existing partial-failure usage limitations remain. Initial report-write failure stops before retrieval; final write failure exits nonzero and may leave the initial running report. Process termination may also leave running state. No complete failure accounting or crash-recovery claim is made.

Assistant-local tests mocked the already-tested question wrapper and used temporary report directories, with API-client construction blocked. Two successful CLI calls produced distinct completed files with full source evidence/configuration/usage and nonnegative timing. Validation and mocked SDK authentication failures produced safe metadata/nonzero return values without logging raw fixture error text. Initial/final report-write failures and failed atomic replacement were exercised: retrieval did not start after initial failure, final failure retained running state, and a partial staged write preserved the previous report bytes and cleaned staging. All tests passed. No real API request, database connection, source mutation or user report/cache write was made. Aarib subsequently reported two native successful CLI runs, recorded below; aggregate benchmark scoring, lifecycle tests and other unchanged M3 gates remain outstanding.

The native CLI runs used the same already-cached development question. **`a336d237-68ab-4783-8e6a-251d591f68d4`** reported `succeeded`, cache hit True, 0 API requests/prompt tokens and **0.034745 seconds** retrieval time; **`a9533be3-3026-437b-977e-50e531b296c5`** reported the same status/usage and **0.040389 seconds**. Both selected database snapshot `e8f661333130c61d51f1a68908ef2038c9a5d24575369bbaa3bccf0bb2b97818` and printed the identical five ranks/distances recorded above. Report paths were `/home/aarib/odoo-functional-rag/data/retrieval/runs/<run_id>.json`. These are two cached CLI wrapper observations, not benchmark latency percentiles or standalone SQL timings. The assistant has not independently read those native report bytes; the next offline command will load one for scoring. An earlier attempt to paste expected output as shell commands did not run the CLI and is not counted as a retrieval run. The active snapshot/ranking and original artifacts are unchanged.

### M3 offline evidence alignment and per-case scoring — 1 November 2026

Prepared `backend/app/evaluation/__init__.py` and `backend/app/evaluation/evidence.py`. `build_evidence_index(normalized, chunks, repository)` verifies both snapshot fingerprints and normalized/chunk lineage, loads the classified eligible reference chunks, verifies all 30 raw source hashes and safe repository-relative paths, and maps explicit normalized paragraph source positions to their owning section-level block IDs. Paragraph continuation lines extend to a blank line or the next root-block boundary. This handles gold spans beginning inside a wrapped paragraph, such as `credit_notes.rst` lines 19–22: the evidence is owned by note root `b0013`, whose paragraph starts on line 18. Nested paragraphs/lists/admonitions count through their complete owning root because current M3.1 chunks preserve those roots atomically. This is versioned **paragraph-to-root structural alignment (`m3-paragraph-evidence-0.1`)**, not character-level annotation or proof of factual entailment. Targets with no paragraph alignment raise for review rather than silently becoming retrieval misses. Image-only/other unsupported alignment needs a separate policy if introduced into positive-answer targets.

`score_case(case, result, index, k=5)` checks the exact question, pinned source identity, sufficient requested retrieval depth, expected eligible hit count, unique/consecutive ranks and full chunk/text agreement with the frozen reference snapshot. Each reviewed target span maps to the paragraph-bearing root blocks overlapping it; all those units must be present for that target to be covered. The accepted benchmark's `target_match=all`/`any` determines coverage of alternatives, every required group contributes to completeness, and optional context is excluded. Hit@K means any required evidence unit appeared; reciprocal rank@K uses the first such hit (0 if absent); required-group coverage is the fraction of fully covered required groups. Reciprocal rank is per case; a later aggregate will calculate MRR. Ambiguous/unanswerable behavior cases return `scorable=False` and are not assigned positive-answer recall metrics. Gold source-span labels and case IDs are unchanged; no generated chunk IDs were added to the benchmark.

Assistant-local offline checks aligned all **31 required targets of development answer cases** using 30 verified documents and 205 reference chunks. Tests passed rank-1/rank-2/miss/cutoff behavior, rejection of another chunk from the same source page as sufficient evidence, all/any alternatives, incomplete/complete groups, optional context and behavior-only exclusion. Tampered, unknown, duplicate or incomplete hits, question/hash mismatches, unmapped targets and insufficient retrieval depth were rejected. No database/API calls or benchmark/source/artifact writes occurred; holdout case content was not inspected. Tests use constructed rankings from real frozen chunk records, not claimed native benchmark outcomes.

The user command loaded benchmark m12-1.0 development case M12-DRAFT-003 and the native report `a9533be3-3026-437b-977e-50e531b296c5.json`. Aarib reproduced **scorable True, K=5, alignment m3-paragraph-evidence-0.1, Hit True, reciprocal rank 1.0, evidence-group coverage 1.0 and all required groups covered True**. The single Explicit restriction group maps to `invoicing_policy.rst` root **b0011** and was covered. This is one native per-case score; no aggregate quality result, holdout result, currency cost estimate or milestone completion is claimed. Full development evaluation, source lifecycle tests, plain token-window comparison and unchanged M3 gates remain outstanding.

When Aarib asked for `benchmark.json`, the accepted review archive was resolved in Library as `Project_2_M1_2_Review_Package.zip`, stable ID `libfile_b7d126a896c48191b671505523fd1264`, version 2. Its exact member `m12-review/evaluation/benchmark.json` was extracted byte-for-byte and matched the existing accepted working copy. The standalone **benchmark.json** is now also available as Library ID **`libfile_1ac69818523c819191fea7a3343fb63c`**, 68,674 bytes, raw SHA-256 **`e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425`**. Version remains m12-1.0 with 30 cases / 23 development / 7 holdout. Expected laptop path is `/home/aarib/odoo-functional-rag/evaluation/benchmark.json`. Extraction/validation inspected version/split counts and byte identity, without reading holdout question content/labels. No benchmark edits occurred.

### M3 development evaluation batch — 1 November 2026

Prepared `backend/app/evaluation/batch.py` with `evaluate_development(benchmark, normalized, chunks, repository, cache, output, corpus_name="odoo19", k=5)`. It uses the existing atomic run-report writer and saves a UUID checkpoint report before preflight. Write destinations are rejected inside read-only corpus/source inputs. The benchmark must match the accepted raw SHA-256 above, version m12-1.0, 23 unique development IDs and accepted review states. It builds the verified evidence index, checks benchmark source identity and pre-aligns all required positive-answer targets before any query embedding call. It pins the active published database snapshot and embedding configuration, requiring the referenced chunk snapshot to match the frozen input.

The ordered development loop retrieves all **23 questions** and scores the **15 answerable cases (8 direct / 7 workflow)**. The remaining **8 cases (4 ambiguous / 4 unanswerable)** retain retrieved context and `scorable=False` for later behavior evaluation. Per-case full results, source evidence, scores, returned usage, stage/status/error and wrapper retrieval seconds are checkpointed. Every result must match the batch's pinned database snapshot/configuration; runtime, scoring or context errors stop the run. Earlier query vectors remain reusable. Completed and partially returned case data is preserved, but aggregate quality metrics are null unless the whole batch succeeds. Usage is explicitly summed only from returned results; failed calls without a returned result are counted separately as unavailable, preserving the existing partial-failure accounting limitation.

Successful summaries report answer-case Hit@K, MRR@K, mean per-case required-group coverage and complete-evidence rate, plus direct/workflow breakdowns. Behavior-only types have null quality metrics. Latency summarizes all returned wrapper calls and separates cache hits from API-generated calls, with sample count, median and nearest-rank P95 (`ceil(0.95*n)`). Per-case retrieval timing excludes source preflight, scoring and report writes; it includes the existing wrapper's database/cache/API work. Whole-run duration includes setup, scoring and checkpoints and is not the per-query latency statistic. No currency price is assumed. The runner fixes the development split and provides no holdout option.

Assistant-local integration used the actual scorer, question wrapper/SDK adapter/cache and cosine SQL, HTTP mock transport and temporary embedded PostgreSQL 18.6/pgvector 0.8.7 with dummy document vectors. One seeded cached query yielded 22 mocked first-pass requests; all 23 cases completed, 15/8 score eligibility and per-type denominators were correct, token/request accounting matched the mock requests and full reports serialized correctly. A second run created no API client, reused all 23 vectors, produced a distinct report and identical quality scores. Mocked SDK 503, pinned-context mismatch and modified benchmark tests stopped safely with null incomplete quality metrics, preserved known returned usage and unchanged database/source artifacts. All tests passed. These fixture rankings are not actual benchmark quality outcomes. No user database, real API or holdout-question access occurred.

The user ran the batch with the accepted laptop artifacts and shared query cache and reported a complete native result, recorded below. The cache-only repeat and six-case missing-rank inspection are now user-verified as recorded in the 2 November checkpoints. Complete source lifecycle tests, plain token-window comparison and other unchanged M3 gates remain pending. Holdout cases remain unused for tuning/evaluation.

### First measured development baseline — 1 November 2026

Aarib reported **23/23 completed, status succeeded, 0 failed cases and 0 unavailable failed results**, with report path **`/home/aarib/odoo-functional-rag/data/evaluations/development/a63c69cd-c64c-4d07-97e6-0869efe8342c.json`**. Execution success means retrieval/scoring completed; quality metrics cover the 15 answerable development questions only. The full native case report/context has not been independently read by the assistant; the provided console summary is the evidence for these measurements.

| Scored set | Cases | Hit@5 | MRR@5 | Mean required-group coverage | Complete required evidence |
|---|---:|---:|---:|---:|---:|
| All answerable development | 15 | 0.8666666666666667 = 13/15 | 0.8 | 0.7444444444444444 | 0.6 = 9/15 |
| Direct | 8 | 0.75 = 6/8 | 0.75 | 0.75 | 0.75 = 6/8 |
| Workflow | 7 | 1.0 = 7/7 | 0.8571428571428571 | 0.7380952380952381 | 0.42857142857142855 = 3/7 |

Ambiguous and unanswerable type quality metrics were null, as intended for behavior-only cases. Arithmetic implies **two direct misses and four workflow cases with partial judged evidence**, six incomplete answerable cases overall. Their IDs and missing groups were subsequently supplied on 2 November and are recorded below. Workflow Hit@5 is perfect on these seven development cases while complete-evidence coverage is 3/7, so first-relevant-hit ranking alone does not establish sufficient workflow evidence. Coverage here remains relative to the reviewed source spans and paragraph-to-root alignment, not exhaustive semantic entailment or correctness of generated answers. Inspect passages and mappings before attributing every shortfall to ranking or changing labels/configuration. No quality threshold was added, and this result alone neither completes nor fails the unchanged M3 milestone gate.

Observed first-run latency: all 23 returned calls median **0.67491 s**, nearest-rank P95 **1.786175 s**; the one cache hit **0.033476 s** for both median/P95; 22 API-generated calls median **0.6843455 s**, P95 **1.786175 s**. These are wrapper timings including query cache/API and database work. The first batch is predominantly API-generating; one cached sample does not establish a cache-only latency distribution or standalone SQL performance.

Reported usage was **1 cache hit, 22 API requests, 543 prompt tokens and 543 total tokens**, with 22 request IDs in the native report excerpt and no unavailable failed results. This is query-embedding usage. Together with the earlier single development-question request (15 tokens), the 23 unique development question vectors used **558 reported prompt tokens** across those two recorded successful generation stages; document-generation usage remains separately recorded. No currency estimate was made.

The review command reads the saved baseline, reruns the same K/split/corpus/input snapshots and cache under a blocked owned-API-client constructor, then reloads both persisted JSON reports for comparison. Reloading normalizes tuple/list serialization in evidence groups. It checks unchanged context/benchmark/alignment, all case rankings/scores, 23 cache hits, zero new request/token usage, a separate run ID and unchanged original baseline bytes. It prints the cache-only timing and each incomplete answerable case's question, uncovered group names and ranked source paths/block IDs. Aarib reproduced these checks on 2 November, as recorded below. Existing M3 lifecycle/comparison gates and author-visible holdout limitations remain unchanged.

### Cached development repeat and six-case evidence review — 2 November 2026

After an earlier connection-refused interruption, Aarib reported a complete repeat at **`/home/aarib/odoo-functional-rag/data/evaluations/development/02f7df9d-8c30-4559-bedc-de53c1b4f167.json`**. All 23 cases succeeded. Assertions confirmed **23 cached query vectors, zero new API requests, identical rankings and scores, unchanged baseline bytes and separate persisted report identity**. The command blocks owned API-client construction. Cache-only wrapper timing across 23 queries was **median 0.029287 seconds (29.287 ms), P95 0.04 seconds (40 ms)**. This is observed local wrapper latency, including connection/cache/database work, not isolated SQL time or a general performance guarantee. The assistant has the user-reported console output, not the full native report file.

The output identifies the two direct misses and four incomplete workflows:

| Development case | Type | Required-group coverage at five | Uncovered groups |
|---|---|---:|---|
| M12-DRAFT-004 | Workflow | 75% | Backorder policy condition |
| M12-DRAFT-010 | Workflow | 1/3 | Partial credit; If refunding money |
| M12-DRAFT-012 | Direct | 0% | 100% down-payment distinction |
| M12-DRAFT-016 | Direct | 0% | Independent step counts |
| M12-DRAFT-017 | Workflow | 1/3 | Open delivery; Regular invoice prerequisite |
| M12-DRAFT-021 | Workflow | 75% | Pick |

Assistant-local inspection used the unchanged accepted development judgments, raw source files, verified normalized snapshot and classified 205-chunk snapshot. The source spans and paragraph-to-root mappings for all eight missing groups have owning eligible chunks:

- Case 004: `operation_type.rst` lines 35–38, root `b0011`, contains the Ask/Always/Never backorder setting.
- Case 010: accounting `credit_notes.rst` lines 29–38 maps to `b0017`, `b0018`, `b0019`; lines 19–22 maps to the note root `b0013` whose paragraph begins on line 18. The first target covers partial-credit creation and the second covers registering a payment if refunding money.
- Case 012: `down_payment.rst` lines 76–80 maps to `b0034`, the distinction between a 100% down payment and completing the order through another invoice. Five same-page chunks in the supplied top-five result did not contain this root.
- Case 016: `receipts_delivery_one_step.rst` lines 13–17 maps to tip root `b0006`, explicitly describing independent incoming/outgoing step counts.
- Case 017: `receipts_delivery_one_step.rst` lines 118–122 maps to `b0040`, `b0041`; `invoicing_policy.rst` lines 109–122 maps to `b0031`, `b0032`, `b0033`.
- Case 021: `receipts_delivery_two_steps.rst` lines 184–204 maps to `b0061`, `b0062`, `b0063`, `b0064`, `b0066`, `b0067`, within the process-picking chunk.

This establishes that the judged missing units were retained and eligible but absent from the supplied top-five results. Their native ranks were subsequently measured below; this check does not exclude other semantically relevant passages. No benchmark label or source mapping was changed to improve scores.

The diagnostic command retrieves the full 205-chunk dense ranking for only these six development questions with cached vectors and API-client construction blocked. It pins the original snapshot/configuration, checks that the first five hits and scores still match the saved baseline, and validates full ranked membership with the actual scorer. For each missing group it reports the first depth where its all/any target condition is met, plus the first depth covering every required group. It leaves the original report and production retrieval configuration unchanged. Command syntax and completion-depth calculations were checked against the actual scorer on constructed complete rankings for all six cases, followed by the user-reported native measurements below. This diagnostic subset is not a new aggregate benchmark or a chosen production K. Holdout evaluation, hybrid/reranking implementation and the unchanged remaining M3 gates remain pending.

### Native missing-evidence ranks and source-change planning — 2 November 2026

Aarib reproduced the six-case full-ranking audit with **zero new API requests and unchanged original baseline bytes**. All assertions passed, including the original top-five hits/scores, pinned database snapshot/configuration and coverage with complete ranked membership. The console output gives these native completion depths:

| Development case | Missing fact group completion ranks | First depth covering all required groups |
|---|---|---:|
| M12-DRAFT-004 | Backorder policy condition: 106 | 106 |
| M12-DRAFT-010 | Partial credit: 8; If refunding money: 13 | 13 |
| M12-DRAFT-012 | 100% down-payment distinction: 6 | 6 |
| M12-DRAFT-016 | Independent step counts: 10 | 10 |
| M12-DRAFT-017 | Open delivery: 13; Regular invoice prerequisite: 14 | 14 |
| M12-DRAFT-021 | Pick: 14 | 14 |

Five incomplete cases have complete judged evidence within the first 14 chunks; the backorder-policy condition is the distant outlier at rank 106. This is a useful retained example for later investigation of configuration terms and cross-page evidence, without establishing which future retrieval technique will improve it. The frozen baseline remains **K=5**, Hit@5 13/15 and complete required evidence 9/15. The audit does not justify sending 106 chunks to generation or changing benchmark targets. No holdout case, lexical/hybrid retriever, reranker, production parameter or active index was changed. M3's source-lifecycle and plain token-window comparison requirements remain open.

The next small guided implementation is `backend/app/indexing/changes.py`. Frozen dataclass `SourceChanges` contains sorted immutable path tuples for `added`, `changed`, `unchanged` and `removed`. `plan_source_changes(previous, current)` takes complete validated inventories represented as `source_path -> raw-byte SHA-256`. Set differences identify presence changes; shared-path hash comparisons identify edits. Deterministic ordering makes reports independent of input mapping order. This describes raw file changes; parser/chunker configuration and include-dependency invalidation remain additional lifecycle work. An unchanged raw file is not automatic permission to reuse derivative records with stale source/snapshot metadata.

The planner must receive a complete source inventory, not a list of successful parser outputs. A parse failure leaves that file present in the inventory and must be handled by the subsequent build/publication stage, preserving the prior valid active snapshot on failure. This initial helper does not implement parsing, dependency invalidation or publication and does not complete the failure/deletion gate by itself.

Assistant-local checks used the accepted 30-file manifest and in-memory fixture changes. Identical inventories yielded 30 unchanged paths and no additions/edits/removals. One simulated addition, edit and removal yielded exactly 1/1/1 and 28 unchanged paths. Full old/new membership partitions, reversed input ordering, initial import and empty inventory behavior passed. The manifest's original bytes remained unchanged; no database, API or source-file mutation was involved. Aarib reproduced the unchanged/mutation/order checks: 30 unchanged on repeat; 1 added, 1 changed, 28 unchanged and 1 removed in the simulation; deterministic ordering, complete membership and unchanged original manifest all passed. Source-change planning is user-verified; the complete lifecycle/comparison gates remain pending.

### Complete candidate preparation — 2 November 2026

The next guided file is `backend/app/indexing/candidate.py`, exposing `prepare_candidate(repository, manifest, normalized_output, chunk_output, *, max_tokens=512) -> (normalized_path, chunk_path)`. It validates a positive integer budget and separate output directories outside the checkout; checks the clean source commit against the manifest; invokes the existing full-corpus normalizer; requires every expected unique path and `status="ok"`; rechecks commit/cleanliness and selected source bytes; then uses the existing immutable normalized/chunk snapshot writers. It imports no database or embedding adapter and performs no active-index publication.

Candidate preparation currently rebuilds the complete selected corpus so cross-page references are evaluated together. The existing parser identity already records versions, adapter configuration and the inventory reference context. File-change planning supplies lifecycle accounting; it does not independently authorize reuse of stale normalized records. The later embedding stage can still reuse identical retrieval text through the existing cache. If chunking fails after normalization, a complete immutable normalized artifact may remain, while no candidate is returned and no database pointer is changed.

Source inspection also confirmed an explicit remaining gate: `sphinx_reader.read_corpus` sets `file_insertion_enabled=False`, and `Normalizer.normalize` rejects nodes attributed to a second source file. Include dependencies are not currently collected. Enabling includes and tracking their transitive hashes/source provenance require a controlled implementation and tests; this coordinator does not claim that support. The include-related M3 completion requirement remains open.

Assistant-local tests used frozen accepted parser output, actual source-byte verification and actual snapshot writers/chunking. They reproduced normalized snapshot `15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc` and chunk snapshot `2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce`, including identical reuse. Parser exceptions, missing/partial document sets, wrong/changed commit, changed selected bytes, invalid budget and unsafe/overlapping output paths were rejected; earlier temporary snapshots and original manifest bytes remained unchanged. Parser and clean-Git hooks were controlled fixtures; no live Sphinx run, native user checkout, database or API was exercised by the assistant. Aarib then reproduced the real-parser temporary check: **30 candidate documents, 205 chunks, both snapshot IDs matching the baseline, parser failure rejected before saving, earlier candidate snapshots unchanged and original manifest unchanged**. Candidate preparation is user-verified. Full embedding/publication lifecycle integration, controlled include provenance and the plain token-window comparison remain pending.

### Candidate embedding and database publication coordinator — 2 November 2026

The next guided file is `backend/app/indexing/publish.py`, exposing async `publish_candidate(chunk_snapshot, embedding_output, config, cache, *, corpus_name, batch_size=64, client=None)`. An explicit nonempty corpus name makes the activation destination part of every call. It rejects dimensions other than the current database's 1536 and write paths inside the input chunk snapshot before generation; loads eligible inputs; invokes the existing cache-aware embedding job; saves a complete immutable embedding snapshot; and calls `import_index` last. It returns generation statistics, embedding record count/path/ID, snapshot reuse and database ID/reuse. Exceptions propagate to the future lifecycle runner rather than reporting partial completion as success.

The existing importer validates complete chunk/vector membership and lineage, then imports/readbacks/publishes/updates the named active pointer in one transaction. This coordinator adds call ordering, not a second SQL implementation. An embedding or file-publication error prevents the importer call. A database failure uses the importer's rollback. Valid cached vectors or complete local snapshots may remain available for a later retry. Unified lifecycle run reports and added/changed/removed/failed source fixture integration remain pending.

Assistant-local integration used all 205 accepted chunks, temporary dummy 1536-dimensional vectors, the actual embedding cache/job/snapshot code and importer SQL, plus embedded PostgreSQL 18.6/pgvector 0.8.7. The owned API-client constructor was blocked. First cached publication, identical repeat/reuse and unchanged database state passed. Injected generation and embedding-write failures stopped before import; an actual SQL failure injected after a changed candidate's active-pointer upsert rolled the transaction back to the earlier complete state. Corpus/configuration/output guards and unchanged input bytes also passed. This did not exercise the user's native PostgreSQL connection or real API.

The user-facing check pins the saved baseline, reads native database state/counts, and calls the coordinator twice with the existing real-vector cache, temporary embedding output and a UUID corpus name `m3-publication-probe-...`, with API-client construction blocked. Aarib reproduced **205 cached embeddings reused per call, zero new API requests, successful temporary publication/repeat, unchanged database row counts after cleanup and unchanged `odoo19` active snapshot**. The command also asserts original embedding/database IDs and existing index reuse, verifies the temporary pointer and removes only that UUID pointer in `finally`. Cached native publication is user-verified. This reversible probe does not complete the remaining M3 gates.

### Combined source rebuild function — 2 November 2026

The next guided file is `backend/app/indexing/rebuild.py`. `_file_hashes(manifest)` validates the inventory's canonical fingerprint and rejects duplicate selected paths. Async `rebuild_corpus(repository, manifest, previous_manifest, data_root, config, cache, *, corpus_name, max_tokens=512, client=None)` validates output locations, reads the active published corpus's stored inventory fingerprint, and requires `previous_manifest` to match it. `previous_manifest=None` is accepted only for a corpus without an active snapshot; a previous manifest supplied for an unindexed corpus is rejected. This ties source-change accounting to the declared active source history at run start.

The function then calls `plan_source_changes`, `prepare_candidate` and `publish_candidate` in order. Outputs use the existing `normalized/corpus`, `chunks/corpus` and `embeddings/corpus` layout under the supplied data root. It returns source changes, prior database ID, inventory identity, artifact paths/IDs and publication/generation statistics. Exceptions propagate, so candidate failure cannot be treated as a successful partial inventory or reach publication. The full candidate is rebuilt even when raw bytes are unchanged, retaining parser/reference-context consistency and content-based embedding reuse. Persisted lifecycle run reports and a concurrent-writer comparison at activation are not newly implemented by this function; the existing importer transaction remains the publication boundary.

Assistant-local integration used frozen accepted parser output, actual source-byte/snapshot/chunk/cache helpers, temporary dummy vectors and embedded PostgreSQL 18.6/pgvector 0.8.7. Initial rebuild reported 30 added paths and 205 cache hits; a repeat reported 30 unchanged paths and byte-identical SQL state/index reuse. Simulated parser failure never invoked publication and preserved the prior database state. Missing, mismatched or corrupt previous-manifest histories were rejected before candidate preparation, and invalid current inventory fingerprints were rejected. No user checkout, live parser, native user database or real API was accessed.

The user-facing native probe runs the complete function with the real parser, temporary artifacts and a UUID corpus name `m3-rebuild-probe-...`, with owned API-client construction blocked. Aarib reproduced **30 documents, 205 cached vectors, an initial plan of 30 added files, parser failure stopping before publication, preservation of the earlier temporary active snapshot, unchanged database counts/production pointer after cleanup, unchanged original manifest and zero new API requests**. The assertions also verify the existing database snapshot ID and that publication is never awaited after the injected parser error. Cleanup removes only the UUID active pointer. The combined native rebuild is user-verified; real addition/edit/deletion fixtures, lifecycle reporting, include provenance and the plain-window comparison remain pending. No production activation, quality threshold, source snapshot, benchmark or retrieval configuration change occurred.

### Actual source-update lifecycle fixture — 2 November 2026

Prepared the guided verification module `backend/app/indexing/lifecycle_probe.py`, run explicitly with the parser-spike group and database dotenv. It creates a temporary Git repository, locally configured fixture author, unique fixture repository URL and UUID corpus name. The first commit contains `edited.rst`, `kept.rst` and `removed.rst`. A second real commit edits the first, leaves the second unchanged, deletes the third and adds `added.rst`. Minimal complete fixture manifests record actual commit IDs, file bytes/hashes and canonical inventory fingerprints; the official Odoo checkout/configuration is not used as a mutable fixture.

The probe prepares each candidate to inspect embedding-text cache membership, seeds deterministic dummy 1536-dimensional vectors only for missing fixture text, and then invokes the actual combined rebuild. Expected update accounting is one path in each source-change category, one reusable text vector and two newly seeded fixture vectors. The embedding job therefore runs with a complete fixture cache; these are zero-request lifecycle checks, not live generation, semantic-quality measurements or additions to recorded real API usage. The owned API-client constructor is blocked throughout.

Assertions verify that the updated snapshot differs from the first and is active, its source-path set exactly matches the new complete inventory, the deleted page is absent from the active index but retained in the historical snapshot, and actual dense retrieval returns updated text with only the new commit's metadata. A further unchanged rebuild must reuse the same database snapshot and all three fixture vectors. A third real commit introduces an unknown RST directive; the subsequent rebuild must fail and leave the prior active pointer, database counts and active membership unchanged.

Cleanup is restricted to the UUID corpus pointer and snapshots whose stored source repository URL equals this probe's unique URL. It gathers those snapshots' vector keys, removes their chunk/snapshot rows, and removes only gathered vectors that have no remaining chunk reference. Final production `odoo19` pointer and table counts must equal the initial state. All fixture source/cache/artifact files are temporary. This cleanup is test-specific ownership cleanup, not a production history/garbage-collection policy.

Assistant-local verification used real temporary Git commits/files, actual manifest/hash/snapshot/chunk/cache/rebuild/importer/dense SQL code, a controlled minimal parser/Git adapter and embedded PostgreSQL 18.6/pgvector 0.8.7. The probe passed, including repeat/failure preservation and exact survival of an unrelated 205-chunk sentinel index after cleanup. Aarib then reproduced the probe with native Sphinx/PostgreSQL: **1 added, 1 changed, 1 unchanged and 1 removed; one text reused and two fixture vectors seeded; deletion absent from active index and retained in history; dense results containing edited text and only the new commit; unchanged repeat and real parser-error preservation; fixture records cleaned with production pointer/counts unchanged; zero real API requests**. These non-include lifecycle fixtures are user-verified. Lifecycle reporting, controlled include provenance and the plain-window comparison remain pending; no source scope, production index, model, benchmark, holdout or retrieval setting was changed.

### Pinned source-file reader for include handling — 2 November 2026

The next small guided module is `backend/app/ingestion/pinned_files.py` with `read_pinned_file(repository, commit, source_path) -> bytes`. It requires this project's full lowercase SHA-1 commit format and a canonical repository-relative POSIX path; rejects absolute paths, parent traversal and path aliases; verifies that the supplied Git object is a commit; finds one exact tree entry with `ls-tree --full-tree -z`; accepts regular-file modes only; and reads the identified blob with `cat-file blob`. Literal pathspecs prevent filename patterns from selecting other entries, and replacement refs are disabled so the requested commit's own objects are used. Symlinks, directories and files absent from that commit are rejected. The helper reads committed object bytes independently of later checkout edits; existing build-level clean-checkout checks still apply.

This is the byte-loading foundation, not enabled include parsing. A later resolver must convert an RST include argument into a canonical repository path, stage/read that dependency, record its hash and preserve cross-file node provenance. The current reader's file insertion remains disabled and no normalization/chunk/index schema, parser policy, accepted snapshot or active production pointer was changed by this helper.

Assistant-local tests ran with real Git 2.51.1 and temporary SHA-1 repositories, without a parser mock or database. They verified stable old-commit reads after dirty checkout edits and a new commit; unchanged main-page bytes while fragment bytes changed; literal wildcard/tab/newline filenames; regular executable files; rejection of invalid paths, symlinks, directories, untracked paths and non-commit object IDs; and unchanged pinned reads after adding a replacement ref. All passed. Aarib reproduced the core native checks: **pinned bytes survive checkout edits/later commits; main page unchanged while fragment changed; invalid paths, links and untracked files rejected; temporary Git fixture only, with no database or API used**. The pinned reader is user-verified; parser/include integration remains pending.

Primary Git documentation opened on 2 November 2026: https://git-scm.com/docs/git-ls-tree (tree metadata, NUL-separated raw paths and full-tree paths); https://git-scm.com/docs/git-cat-file (object types and raw object contents); https://git-scm.com/docs/git (literal pathspecs and disabled replacement refs). Only established commands/options used by the tested local Git were introduced; no network fetch, package upgrade or real API/database access was performed by this helper's tests.

### Opt-in pinned nested-include parser adapter — 2 November 2026

Prepared `backend/app/ingestion/rst_includes.py` with policy version `m3-pinned-relative-utf8-0.1`. `IncludeSources` verifies selected bytes against the pinned commit, resolves each include relative to its actual including file, stages verified regular-file bytes, and records a deterministic per-owning-page transitive set of source path/SHA-256/size records. A nested including file must already belong to that owner's recorded dependencies. Traversal outside the repository/staging root, URLs, absolute paths, standard-definition angle-bracket syntax, symlinks and conflicting staged bytes are rejected. A per-page cap of 64 include requests bounds recursive/repeated inclusion. Repeated source paths are deduplicated in dependency metadata while their authored content can still be inserted repeatedly.

`PinnedInclude` is a narrow Docutils directive for plain UTF-8 relative includes without options. It fetches/stages through `IncludeSources`, records the Sphinx dependency, and inserts the verified text lines into Docutils' state machine with the staged source filename. It does not turn on generic file insertion or raw markup. The parser is expected to retain the included file's own source path/line, including nested admonitions; actual doctree positions require the native probe below.

`read_corpus(files, *, repository=None, commit=None)` now permits explicit opt-in by supplying both values. The pair is validated; the store is attached to `app.env.pinned_include_sources`, and the custom directive is registered only in this mode. Existing callers with neither argument keep their existing policy. Dependency files are staged on demand while parsing; the probe checks that they do not become additional selected documents. No normalizer call currently enables this mode, and its existing cross-file rejection remains in place. This is parser-layer support, not completed ingestion of includes or a new published corpus.

Local tests used real temporary Git commits and staging files with a directive/state-machine test double. Nested relative resolution, pinned-byte reads despite checkout mutation, per-page ownership, hash/size records, deduplication, staged-byte conflicts, path/link/UTF-8 failures and the request cap passed. Directive insertion/source-label calls and unchanged generic parser settings were checked; Python source and the native command compile. No live Sphinx parser was run by the assistant.

The user-facing probe commits one selected page and two nested fragments, changes the checkout's nested fragment afterward, and calls the opt-in Sphinx reader. It requires one selected doctree, two dependency records with exact pinned hashes/sizes, zero parser errors, an important block, and paragraph locations `pages/main.rst:4`, `shared/outer.rst:1`, `shared/nested.txt:2`. The tree must contain the pinned nested rule rather than the uncommitted replacement. Repository escapes/absolute paths/URLs must be rejected, and generic file insertion/raw settings remain false. This lower-level read test deliberately uses pinned bytes despite a dirty fragment; full rebuilds retain their clean-checkout requirement. Native reproduction, normalized dependency identities, cross-file location mapping, evidence alignment and the remaining M3 gates are pending; all accepted corpus/index artifacts and retrieval settings remain unchanged.

Primary Docutils documentation was opened on 2 November 2026: https://docutils.sourceforge.io/docs/ref/rst/directives.html#include documents relative include resolution and insertion in the current document context. Official state-machine source was retrieved at https://docutils.sourceforge.io/docutils/statemachine.py, although follow-up source windows and pinned-version GitHub source retrieval were unavailable. Accordingly, actual pinned-version parser behavior and line positions are explicitly left to the user's native probe, not claimed from the local test double.


### Native include parser result and dependency-aware normalization — 6 November 2026

Aarib ran the real nested-include parser probe successfully: **one selected document, two recorded dependencies, preserved nested text and important block, preserved paragraph source paths/lines, pinned fragment bytes despite a checkout edit, verified dependency hashes/sizes, rejected unsupported paths and retained parser settings**. This completes the parser-level reproduction that was pending in v1.46. It does not yet enable include mode in the normal corpus build.

Prepared a backward-compatible, explicit include mode in `backend/app/ingestion/normalization.py`. `Normalizer(..., dependencies=(), include_policy=None)` retains the previous single-file defaults. The opt-in path requires the existing include policy and a staged source root; verifies unique canonical dependency records against staged regular-file bytes and SHA-256/size; and permits node sources only from the owning page or those verified dependencies. Locations use the actual node/ancestor source file, and inherited line numbers are accepted only for that same file. An included node with no usable line does not borrow an unrelated main-page line. Existing image/reference attributes are mapped by the existing code; included image/reference semantics have not been separately validated by this text/admonition fixture.

The normalized document keeps its owning main-page SourceIdentity and document ID. Include-enabled outputs use normalizer version `structures-includes-0.1`, record the include policy in parser identity, retain deterministic dependency records in the existing generic metadata field, and include those records in revision identity. Default outputs remain `m22-0.2` / `structures-0.2` with the previous revision input sequence. No normalized model/schema expansion or publication is introduced at this step.

Assistant-local checks exercised the actual Normalizer with parser-node test doubles: old/new default normalized JSON was byte-identical for controlled main-file fixtures; nested block/inline locations and same-file ancestor-line behavior passed; metadata and repeated output were stable and independent of caller record mutation; changing verified dependency bytes with the main identity and tree held fixed changed the revision while retaining the document ID; undeclared/outside paths, bad/duplicate/self records, stale hashes/sizes, linked staged files and unsupported policy were rejected. The module and native fixture command compile. No native Sphinx run, Odoo corpus re-normalization, database operation or real API call was performed by the assistant.

The next user-facing temporary-Git probe parses one main page and two nested fragments through Sphinx into the Normalizer, verifies dependency metadata and block/inline paths/lines, repeat determinism and rejection behavior, then commits a fragment-only edit and requires unchanged main bytes/document ID with a changed dependency hash/revision. Native Normalizer reproduction was pending at v1.47; the successful user result is recorded below. Corpus-builder/candidate opt-in wiring, cross-file evidence alignment and dependent-update integration remain pending, as do persisted lifecycle reports, the plain token-window comparison and the unreported combined M3.1 tests. All accepted 30-document/205-chunk artifacts, production pointer and K=5 dense baseline remain unchanged.

Official Docutils source consulted on 6 November 2026: https://docutils.sourceforge.io/docutils/nodes.py describes node source/line and parent linkage; https://docutils.sourceforge.io/docutils/parsers/rst/directives/admonitions.py assigns admonition source/line from the state machine. These live source pages support the mapping approach; they are not claimed as a run of the installed Docutils 0.21.2/Sphinx 8.2.3 environment, which remains the native probe's responsibility.


### Native normalized-include result and corpus/candidate wiring — 6 November 2026

Aarib reproduced the real Sphinx-to-Normalizer fixture successfully: **one normalized document per build, two dependencies per document, preserved included block/inline file and line positions, identical repeated normalization, fragment-only update with unchanged main bytes/document ID and changed dependency hash/revision, rejection of bad hashes/undeclared sources/default-mode cross-file input, temporary Git fixture only with no snapshot publication, database or API use**. Dependency-aware normalization is now native-verified for this nested text/important-block fixture.

Prepared the next bounded integration in `backend/app/ingestion/normalize_corpus.py`: `build_corpus(repository, manifest, *, include_policy=None)` validates the explicit policy, supplies repository/manifest pin to the reader when enabled, and passes each owner's actual dependency records into its Normalizer while staging is still available. Recognized diagnostics from recorded dependency files are associated with their owning pages. The include-enabled summary records the policy, per-owner dependency records and `structures-includes-0.1`; the default path retains its previous summary fields/values. The existing diagnostic parser still treats non-`.rst` source headers as global/unclassified messages; their raw text and error severity remain available and parser errors still reject the build.

Prepared `--pinned-includes` on the normalization CLI and an optional `include_policy` keyword in `prepare_candidate()`. Candidate preparation forwards the option to the corpus builder while retaining complete membership/status checks, clean-pinned-checkout checks before/after parsing, selected-byte revalidation and immutable normalized/chunk snapshot writers. Only selected pages become documents; included fragments remain dependencies contributing content to their owning document. The higher rebuild/publish entry point has not yet been wired to this option. No database/index activation is added here.

Assistant-local integration checks used actual Git objects, IncludeSources, Normalizer, corpus builder, candidate flow, chunking implementation and snapshot writers with controlled parser nodes, a deterministic test token counter and a Git-backed substitute for the unavailable local repository helper. The old/new default corpus documents/summary/payload/snapshot ID matched for a controlled main-file fixture. CLI flag/default routing and unsupported-policy rejection passed. The complete temporary candidate probe passed under these substitutes: one document/two dependencies, nested important content in saved chunks, repeat reuse of both snapshots, changed normalized/chunk snapshots after a fragment-only commit, invalid included RST rejected before saving, and unchanged earlier snapshot/input-manifest bytes. Python modules and the native command compile. This is not a native Sphinx/tiktoken or accepted Odoo-corpus rerun by the assistant.

The user-facing command runs that candidate probe through the installed parser/tokenizer and real repository helper using only a temporary Git/output tree. Native candidate reproduction is pending. Cross-file evidence alignment, include-aware rebuild option/reporting/change-plan integration, dependent-update publication checks, lifecycle run reports, plain token-window comparison and the unreported combined M3.1 tests remain pending. All accepted Odoo artifacts, the active production snapshot, K=5 dense baseline, model and benchmark remain unchanged; no database or real API call occurred in these local checks.


### Native repeat diagnostic and Sphinx namespace isolation fix — 6 November 2026

The native candidate probe stopped at its unchanged-repeat assertion, before reaching that probe's fragment-update and parser-failure gates. Aarib supplied a byte-level diagnostic in `Pasted text(4).txt`. It confirms that the repeated normalized snapshot changed only `diagnostics.txt` and `summary.json`: the second Sphinx application emitted duplicate directive/node/role registration warnings for built-in extensions, sphinx-tabs and project nodes. Normalized document files were identical. The repeated chunk snapshot changed only `summary.json`, specifically its parent normalized snapshot ID; chunk records and eligibility bytes were identical. This is a parser registration-lifetime defect affecting diagnostic reproducibility, not evidence of changed document/chunk content.

Prepared a two-line fix in `backend/app/ingestion/sphinx_reader.py`: import `docutils_namespace` from `sphinx.util.docutils` and use `with TemporaryDirectory(prefix="m22-corpus-") as directory, docutils_namespace():` around the existing reader body. The context starts before constructing Sphinx, covers extension and project registration, building, doctree retrieval and the yielded consumer's normalization, and exits when the reader context closes. Sphinx's helper restores directive/role mappings and unregisters temporary additional nodes, including on exceptions. The configured mappings, diagnostic capture and source-warning preservation stay in the existing reader flow; no warning filter or snapshot identity shortcut is introduced.

Assistant-local checks loaded the actual old/new reader with a stateful Sphinx/registry test double. The old reader reproduced extra warnings on repeat. The fixed reader kept setup/build/yield inside the namespace, restored registrations after successful/pinned calls, parser failure and consumer failure, retained a genuine source warning and produced identical cold/repeated diagnostics in this controlled model. The reader compiles. This is a context-lifetime/registry simulation, not a run of native Sphinx 8.2.3. The original stateless parser double could not expose this registration leak; the new local regression deliberately models it.

Aarib should apply those two reader edits and rerun the complete diagnostic candidate command already provided. The required native result is identical normalized/chunk snapshots and empty changed-file lists for repeat, followed by successful content, fragment-update and parser-failure preservation checks. Until that output arrives, the candidate integration and this fix remain native-pending. All accepted Odoo snapshots, production database pointer, retrieval configuration and remaining M3 completion gates remain unchanged; no production rebuild, database operation or real API call was performed by the assistant.

Primary source checked on 6 November 2026: https://www.sphinx-doc.org/en/master/_modules/sphinx/util/docutils.html documents the namespace helper's registry-copy/finally cleanup behavior and recommends scoping registrations to prevent side effects. Retrieval of a pinned 8.2 source page/raw GitHub file was unavailable, so the installed-version behavior is explicitly left to the native rerun.


### Native include candidate success and pinned evidence-source tables — 6 November 2026

Aarib applied the per-reader Docutils namespace fix and reran the full native candidate diagnostic successfully. **Both normalized/chunk repeat IDs matched with empty changed-file lists; one selected document retained two dependencies; nested important content reached saved chunks; unchanged candidate calls reused both snapshots; a fragment-only commit changed normalized/chunk snapshots; invalid included RST was rejected before saving; earlier snapshots and input-manifest bytes stayed unchanged; only temporary Git/output fixtures were used, with no database or API access.** The namespace fix and candidate normalization/chunk integration are now native-verified for this fixture. The observed fixture IDs were normalized `03624ccdb785c06399b81298a4040f5b262a3109277a617f8ccae34f3a25998a` and chunks `7af8d15f98752e707c544b583102bd2302563a40dba23c20462ff904b086e43e`; these are temporary-fixture observations, not replacements for the accepted Odoo corpus snapshots.

The next guided increment prepares `backend/app/evaluation/source_files.py` with `load_evidence_sources(repository, document)`. For an `m22-0.2` document with status `ok`, it collects the owning main page and the one optional `include_dependencies` metadata group; validates dependency record shapes/sizes, source-path string types and lowercase SHA-256 values; rejects duplicate groups/paths; reads each declared file through the existing pinned Git reader at `document.source.commit`; verifies hashes and available dependency sizes; decodes UTF-8 and returns deterministic physical-path-keyed SHA/line-count/source-line tables. The pinned reader supplies canonical-path/regular-file/commit validation. Three evidence files can belong to one normalized document; fragment files do not become new selected documents.

The loader is deliberately independent of Docutils/Sphinx and is not yet called by `build_evidence_index()`. Existing alignment/scoring still uses `m3-paragraph-evidence-0.1`. The next increment must map paragraph locations against the appropriate physical source table while preserving the owning document/root block identity used in chunks, and account for shared/repeated fragment occurrences without conflating block IDs across documents. No benchmark target or score was changed here.

Assistant-local checks ran the actual helper and pinned Git reader with real temporary Git commits and a minimal normalized-metadata contract fixture, with no parser/tokenizer doubles or database/API. They verified three source files, exact nested lines/counts, deterministic repeated tables, stable original-pin evidence after dirty checkout edits and a later commit, rejection of stale dependency hashes when a pin changes, acceptance of correctly updated dependency records, unchanged main-file evidence for a fragment-only edit, rejection of forged hashes/sizes/boolean sizes/escaping paths/duplicate records/groups/partial documents, support for a single-file document, and unchanged caller metadata. The module compiles and the user-facing temporary-Git command passed locally. User reproduction of this loader is pending; no claim is made that cross-file paragraph scoring is integrated yet.

Include-aware evidence alignment, rebuild option/change-plan/report integration, dependent-update publication/cache checks, lifecycle run reports, the plain token-window comparison and the unreported combined M3.1 tests remain pending. Accepted Odoo artifacts, the active production index, K=5 baseline, model and benchmark remain unchanged. No new external technical API/library behavior is introduced by this helper; it uses the project's already-verified pinned reader and Python standard-library hashing/UTF-8/line splitting.

**What we build**

A section-aware, token-bounded chunker with heading inheritance, followed by embeddings and a dense retriever in PostgreSQL/pgvector. Each chunk links back to its document revision, source blocks, and parent section.

Compare a plain token-window baseline with structure-preserving chunking. Then vary one factor at a time: token budget, overlap, contextual headings, or parent relationships. Keep raw evidence text separate from additional retrieval text so enrichment cannot become a fabricated source quote.

Implement a minimal index lifecycle: added, changed, unchanged, removed, and failed documents; content-based embedding reuse; parser/chunker/embedding configuration identifiers; and an active published snapshot. Rebuild and activate a complete validated snapshot rather than serving a mixture of incompatible configurations.

**What we learn**

Retrieval units, embedding inputs, reproducibility, idempotency, incremental updates, and the quality/storage/cost tradeoff.

**Why this comes here**

We now have reliable source structure and stable relevance labels. A simple measurable retriever is needed before hybrid search or reranking.

**Complete means**

A command runs retrieval evaluations and produces a reproducible baseline with Hit@K, MRR, evidence coverage for multi-part questions, latency, and embedding cost. Inspect failures by query type.

Re-running unchanged input does not duplicate chunks or repeat unnecessary embedding calls. Edits invalidate affected derivatives, including dependents of changed includes. Confirmed deletions disappear from the active index; parse failures do not masquerade as deletions. An interrupted indexing run leaves the previous valid snapshot available.

Start with exact vector search on the small corpus. Introduce an approximate index only when scale/latency warrants it, then measure retrieval loss against the exact baseline.

**Intentionally postponed**

Hybrid search, learned reranking, generating answers, automatic source polling, and large-scale indexing infrastructure.

## M4 — Hybrid retrieval and retrieval debugging

**What we build**

Three comparable retrieval modes: dense-only, lexical-only, and hybrid. Begin lexical retrieval with PostgreSQL full-text search. Evaluate rank-based fusion, such as reciprocal rank fusion, without treating unrelated raw scores as directly comparable.

Apply explicit version/language/scope constraints consistently. Treat inferred application/topic as a possible boost initially, not a mandatory filter that can hide cross-application evidence.

Build the retrieval inspection interface: original query, explicit and inferred metadata, any rewritten query, dense candidates, lexical candidates, fusion ranks, source text, timings, and reasons for exclusions. Extend the structured trace already introduced with the M3 CLI.

**What we learn**

Semantic versus lexical matching, candidate recall, rank fusion, metadata precision, and failure diagnosis.

**Why this comes here**

The dense baseline makes it possible to identify which exact terms, UI labels, or cross-application questions benefit from lexical retrieval.

**Complete means**

One evaluation run compares all three modes on the same snapshot and benchmark. Exact-label, paraphrase, and multi-section query slices are reported separately. The inspection interface makes failed retrieval explainable.

Experiment with query classification or rewriting only for a documented failure category. Retain the original query and explicit constraints. Keep a hybrid default only when the measured benefit justifies its complexity; the implemented alternatives remain available for comparison.

**Intentionally postponed**

A separate search cluster, calling PostgreSQL's native rank function “BM25,” unrestricted multi-query expansion, and authority-based ranking while every source has the same authority.

## M5 — Reranking and evidence assembly

**What we build**

A bounded second-stage reranker and a deterministic evidence assembler. Compare reranking enabled and disabled over the same candidate pools.

Select evidence under a token budget, deduplicate overlapping source spans, retain necessary prerequisites and warnings, order related sections coherently, and optionally expand a retrieved child to useful parent context. Re-check version and access eligibility during any expansion.

Create evidence packets with server-assigned IDs and a trusted mapping to the exact source snapshot, source spans, and displayed content. Include reasons for selecting or excluding candidates in the debugging interface.

**What we learn**

Candidate recall versus ranking quality; relevance versus diversity; retrieval granularity versus generation context; and budget allocation.

**Why this comes here**

A reranker cannot recover evidence missing from the candidate set. Context assembly becomes meaningful after candidate retrieval can be inspected and measured.

**Complete means**

Report candidate recall before reranking, final-context evidence coverage, ranking quality, token use, and latency/cost. Compare parent expansion and deduplication against a fixed baseline. No mandatory prerequisite or warning is dropped in reviewed fixture cases solely because its sibling chunk had a slightly higher score.

The reranker has a timeout and a tested fallback to the prior ranking. Calibration on development cases informs any relevance/abstention threshold; scores are never presented as truth probabilities. Retain a reranker in the default path only if its benefit justifies the additional cost and latency.

**Intentionally postponed**

Always-on multi-query retrieval, model-written chunk summaries, complicated routing policies, and an autonomous retrieval loop.

## M6 — Grounded functional Q&A and citations

**What we build**

The first usable assistant: question → eligible evidence → bounded context → structured answer → validated citations.

Add FastAPI endpoints and a React interface. Reuse or adapt Project 1's conversation IDs, persistence, streaming, cancellation, request IDs, and error handling. Store the active version and relevant conversation facts separately from retrieved evidence.

Resolve follow-up references when needed, but retrieve fresh evidence for factual claims. Previous assistant answers and conversation summaries do not become trusted documentation.

The model selects evidence IDs supplied by the server. The server owns citation titles, URLs, version metadata, and source mappings. Link to versioned documentation for readability and commit-pinned source evidence for reproducibility. Do not invent an anchor when none has been verified.

**What we learn**

Claim grounding, structured generation, citation validity versus citation support, conversational RAG, and abstention.

**Why this comes here**

Answer generation now sits on an inspectable, evaluated evidence pipeline. A fluent answer cannot hide every retrieval failure.

**Complete means**

Questions and follow-ups work with persistence, cancellation, and explicit insufficient-evidence behavior. Unsupported citation IDs fail validation. The interface can show the supplied evidence and the subset cited.

Evaluate citation support, citation coverage, factual grounding, answer completeness, answerability decisions, and version correctness. Use human review as the reference; a model judge may assist only after checking its agreement with reviewed examples.

Streaming text is provisional until citation validation finishes. Schema and ID checks do not prove factual support; semantic support remains a separate evaluation and review responsibility. Diagnose generation failures by also testing with known-good evidence.

**Intentionally postponed**

Configuration plans, requirement decomposition, general tool calling, live Odoo access, and open-ended agents.

## M7 — Configuration guidance and requirement analysis

**What we build**

Two workflows using the same retrieval and evidence infrastructure.

Configuration guidance produces applicable apps/features, prerequisites, a proposed setup sequence, dependencies, decisions, caveats, and source-backed validation steps.

Requirement analysis decomposes a requirement, retrieves evidence for each part, identifies standard capabilities, separates decisions and recommendations, asks material clarification questions, and marks uncertainty or potential customization.

Add selected Purchase and Accounting pages only after expanding corpus manifests and reviewed evaluation cases. Capture edition, localization, deployment, installed apps, and business constraints when they materially affect the answer. Do not infer missing environment details.

Use a bounded workflow: understand request → clarify if necessary → retrieve → assemble evidence → produce structured output. Set limits on subquestions and model calls.

**What we learn**

Evidence-backed synthesis, workflow orchestration, clarification, multi-part coverage, and separating consulting judgment from documented capability.

**Why this comes here**

Multi-step implementation advice compounds missing evidence. It depends on reliable Q&A, citations, and a tested trust contract.

**Complete means**

Human-reviewed scenarios cover a wholesale setup and approval requirements, including incomplete information and no-evidence cases. Every factual setup assertion has supporting evidence; recommendations state assumptions; unresolved requirements remain visible.

There are zero accepted fixture cases in which “retrieval found nothing” becomes a confident claim that customization is required. Workflow traces show bounded calls and evidence coverage for each requirement.

**Intentionally postponed**

Executing configuration changes, connecting to client databases, writing custom Odoo modules, CRM/POS breadth, and a general planning agent.

## M8 — Version-aware retrieval and comparison

**What we build**

Deferred future milestone: the 7 November 2026 scope decision keeps the current product on Odoo 19 only. The original future deliverable remains explicitly isolated Odoo 17, 18, and 19 corpora for a bounded set of comparable topics. Use version-aware identities from M1–M3; now activate multiple versions.

Normal questions retrieve only the selected version. Comparison requests retrieve separately for each requested version and keep evidence attributed throughout context assembly and output.

Align related concepts across versions using reviewed mappings where paths or headings changed. Show documented differences, apparently consistent behavior, and areas without enough evidence. A source-text diff alone is not proof of a product behavior change.

**What we learn**

Temporal provenance, cross-version alignment, missing-evidence reasoning, and contradiction handling.

**Why this comes here**

The single-version system must work before introducing a new source of near-duplicate and contradictory evidence.

**Complete means**

Version-specific and comparison benchmarks pass their defined gates. Wrong-version evidence is excluded in normal answers. Comparison claims cite the relevant evidence from each version or explicitly state the missing side.

Renamed pages, missing pages, similar wording with different applicability, and conflicting documentation have reviewed cases. The UI shows the selected version and source snapshot. Existing conversations retain a stable version until the user changes it.

**Intentionally postponed**

Every Odoo version, every application across every version, automatic migration prescriptions, and claims that missing documentation proves a feature was introduced or removed.

## M9 — Security, reliability, and operational observability

**What we build**

Harden the controls introduced earlier: treat retrieved content as data, enforce safe rendering and citation URLs, test adversarial document instructions, and constrain ingestion capabilities.

Isolate user conversations and traces. Implement document-level authorization for an intentionally small test corpus of restricted documents, with server-derived identity and tenant context. Enforce eligibility before candidate selection and re-check parent expansion, citation lookup, and debug access. Public official docs can remain shared.

Add timeout and retry budgets, bounded concurrency, request limits, provider error handling, reranker fallback, indexing recovery, privacy-aware logging, stage latency, token/cost reporting, and operational alerts. Authentication is required before exposing private state, even if deployment happens before this milestone.

**What we learn**

Defense in depth, permission-aware retrieval, production failure modes, operational diagnosis, and cost control.

**Why this comes here**

The complete product path now exists and can be hardened end to end. This milestone expands and verifies controls; it does not postpone basic safety until the end.

**Complete means**

Security and failure scenarios are documented and tested: document injection, unauthorized retrieval, conversation access, invalid source links, provider timeout, cancellation, indexing interruption, and stale/incompatible index selection.

Two test users/tenants cannot obtain each other's restricted evidence through any endpoint, expansion, or trace. A failed reranker or ingestion job produces a defined safe fallback. Operational traces connect requests to source snapshots, pipeline versions, stage timings, evidence, and errors without logging unnecessary sensitive content.

**Intentionally postponed**

Enterprise identity federation, a customer-document upload product, a full tenant administration console, large-scale queues, and compliance certification.

## M10 — Deployment, release evaluation, and portfolio evidence

**What we build**

A reproducible deployment with pinned dependencies, migrations, secrets management, health/readiness checks, controlled ingestion jobs, backups, restore instructions, and rollback.

Run the full release suite on a pinned corpus/index. Publish an honest engineering report showing baseline and selected pipeline results, representative failures, known limitations, evaluation methodology, latency, cost, and workload assumptions.

Create a concise architecture explanation and a demonstration of both the assistant and retrieval debugging interface. Deployment target selection remains open until operational requirements and budget are known.

**What we learn**

Release gating, reproducibility, operating costs, service expectations, and communicating engineering evidence.

**Why this comes here**

The release claim should reflect the behavior of the complete system, rather than only a local happy-path demonstration.

**Complete means**

A clean environment can reproduce the system and source snapshot. The deployed smoke test, migration process, backup restoration, and rollback have been exercised.

A versioned release report satisfies numeric quality/latency/cost gates frozen before running the held-out release evaluation. Numeric thresholds are based on the baseline and intended workload, not arbitrary numbers invented now. Report denominators, query slices, and uncertainty where practical.

Security invariants have no known failing release cases: unauthorized evidence access, invalid citation IDs accepted as valid, or wrong-version evidence in a single-version response. A finite passing suite is evidence, not a universal correctness guarantee.

**Intentionally postponed**

Project 3's agent control center, training models, additional frameworks without demonstrated benefit, and multi-region enterprise infrastructure.

## Evaluation plan

Evaluation starts in M1 and remains part of every milestone; M10 packages the evidence for release.

| Measure | What it answers | Introduction and cautions |
|---|---|---|
| Hit@K | Did at least one relevant evidence unit appear in the first K results? | M3. Good initial retrieval signal; not sufficient for multi-part questions. |
| MRR | How high was the first relevant result? | M3. Useful for focused questions; does not measure complete workflow coverage. |
| Recall@K / evidence-group coverage | How much of the judged required evidence was retrieved? | M3 onward for questions with multiple required evidence groups. Treat recall as relative to reviewed judgments, not an unknowable exhaustive corpus gold set. |
| Precision@K | How much of the retrieved set was useful? | M4–M5 when candidate judgments are sufficiently complete. Track redundancy separately. |
| NDCG@K | Are highly useful results ranked above partially useful ones? | M5 only after consistent graded labels exist. Binary judgments alone may not justify adding it. |
| Answerability and abstention | Does the system reject unsupported questions without refusing answerable ones? | Labels in M1; end-to-end measurement in M6. Report both false answers and false refusals. |
| Citation validity, support, and coverage | Do IDs resolve, do cited passages support claims, and are factual claims covered? | M6. These are different checks; a valid URL proves little about support. |
| Groundedness and completeness | Are factual claims supported, and are required answer points included? | M6–M7. Keep these separate so short evasive answers cannot score well merely by saying little. |
| Version correctness | Is evidence restricted to the intended version, and are comparisons attributed correctly? | Identity checks from M3; multi-version evaluation in M8. |
| Latency and cost | What does each stage cost at the intended workload? | Embeddings/retrieval in M3; generation in M6; p50/p95, concurrency, time to first token, total completion, and operational budgets by M9–M10. |

Use stable document/section/evidence labels so chunk-size changes do not redefine relevance. Deduplicate overlapping chunks for evaluation. Compare final evidence under a fixed token budget as well as retrieval at fixed K: otherwise large chunks may appear better simply because they carry more text.

Record benchmark version, source commits, corpus/index snapshot, parser/chunker configuration, embedding model, retrieval/reranker parameters, prompt/model versions, timings, and costs with each run.

The experiment cycle is: state a hypothesis → change one important variable → run on the same development cases → compare query slices → inspect regressions → retain or revert. Grow the benchmark from actual failures, keeping new labels human-reviewed. Freeze decisions before held-out release evaluation; retire or refresh a holdout if repeated inspection makes it a tuning set.

## Minimal metadata policy

| Metadata | Concrete purpose |
|---|---|
| Source repository, path, commit, content hash | Traceability, reproducibility, update detection, immutable source references |
| Odoo version and language | Mandatory corpus selection and leakage prevention |
| Application and reviewed topic mapping | Inspection and optional retrieval guidance; not an automatic hard exclusion |
| Title, section hierarchy, source labels/spans | Chunk context, evidence mapping, citation display, parent expansion |
| Normalizer/chunker/embedding versions and index snapshot | Safe cache reuse, reindexing, and comparable experiments |
| Ingestion outcome and run time | Operational diagnosis and freshness reporting |
| Applicability such as edition/localization | Store only when supported; unknown is a legitimate value |
| Visibility/tenant/ACL identifiers | Add when restricted-document retrieval is implemented, enforced by trusted server context |

“Official Odoo documentation” can initially be corpus-level authority metadata. It provides no useful ranking distinction when every result shares it. Avoid inventing a precise technical module identity from a broad functional folder.

## Exact first implementation task: M1.1

**Build a deterministic source-inventory CLI.**

Status: complete on 19 October 2026; see the implementation checkpoint above. The original task contract below is retained for reference.

The engineering question is: “What exact source files are eligible for this corpus, and can we identify that same input later?”

Inputs:

- A local checkout of the official documentation repository.
- Requested Odoo version 19.0 and the checkout's actual Git commit.
- English source content.
- A configuration containing allowed Sales and Inventory paths.
- A destination for a machine-readable manifest.

Implementation boundaries:

1. Discover tracked .rst files under content/applications/ in a clean pinned checkout.
2. Apply the configured allowlist. Verify actual repository paths during implementation; do not infer a complete module taxonomy from folder names.
3. Emit sorted records containing repository-relative path, configured application, byte size, and SHA-256 of raw bytes.
4. Record repository URL, requested version, actual commit, manifest format version, and the scope configuration. Keep the run timestamp separate from the deterministic inventory fingerprint.
5. Report included and excluded totals, selection reasons, and explicit read/discovery failures. Keep diagnostics distinct from successful inventory output.
6. Reject a dirty checkout for the initial implementation so the commit really identifies the recorded bytes. Reject missing/empty scope paths instead of silently calling them a successful ingestion.
7. Keep traversal within the checkout. Do not execute the repository's build configuration.

Acceptance checks:

- Two runs over the same commit and scope yield identical ordered file records and inventory fingerprint.
- Changing scope changes the selected set predictably.
- A new fixture commit with an edited file changes its hash; a removed file leaves the inventory.
- An unreadable selected file or missing configured path is visible and causes a failure status.
- Unselected applications are not eligible for the corpus.

Deliverable: a small CLI, its generated inventory manifest/report, and a short note recording the chosen scope. We review these before beginning M1.2: human source audit, page selection, and benchmark authoring.

Do not build a parser, vector database, embedding job, FastAPI endpoint, or chat UI in M1.1. This task establishes the source contract all later stages depend on.

## Working agreement

For each meaningful feature: explain the problem and consequences; compare viable approaches and tradeoffs; recommend one; let the user implement it; review and test consequential behavior; evaluate against the baseline; then advance.

From 23 October 2026, use small explained code increments that Aarib writes and runs locally. Review each result together before expanding the implementation. Avoid ready-made files, ZIP packages and large code dumps unless the user explicitly requests a change to this approach. Do not treat this teaching cadence as permission to implement later increments in advance.

Aarib explicitly requested consolidated delivery of the repetitive remaining text-renderer kinds, with tests and explanation, after completing the earlier small increments. Apply that exception to this renderer increment; continue explaining the mechanics and developing subsequent chunking steps together.

Do not provide an entire implementation unless requested. Do not move to the next milestone merely because a more advanced component is interesting. Completion requires evidence, including a justified decision not to enable a feature that failed to improve quality.

## Sources and verification boundary

This is an engineering plan with recorded M1 implementation/acceptance and M2 normalization/fidelity checkpoints. M1.1 test results are user-reported; candidate file bytes and manifest fingerprint were independently checked against the supplied archive. Git history was not supplied to the assistant; the user's fidelity command and export report a clean checkout at the pinned commit. Assistant source review and the accepted 30-case benchmark cover the 30-page slice. Human scope acceptance and local CLI activation were recorded on 22 October 2026; the corpus fingerprint independently reproduces. M2 records the parser comparison, automated structure checks, deterministic 30-document normalization, matching user-reported snapshot identity, six user-passed fidelity tests and an uploaded export passing eight selected human comparisons on 23 October. The assistant did not independently inspect the user's screenshots/full review packet, and this acceptance does not establish retrieval or answer quality. The status of Project 1 is taken from the supplied brief, not an independent code review.

1. Official Odoo documentation repository: https://github.com/odoo/documentation (target branch: 19.0).
2. Odoo 19 documentation contribution guidance: https://www.odoo.com/documentation/19.0/pl/contributing/documentation.html (retrieved official guidance explains that the sources use RST).
3. Odoo 19 RST guidelines: https://www.odoo.com/documentation/19.0/fr/contributing/documentation/rst_guidelines.html (retrieved official guide includes UI/menu and formatting conventions).
4. PostgreSQL full-text search introduction: https://www.postgresql.org/docs/18/textsearch-intro.html.
5. Sphinx reStructuredText documentation: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html.

Sources consulted on 18 October 2026. Some direct GitHub and English Odoo page fetches were unavailable; no repository-wide inspection is claimed.

## Changelog

- 2026-11-07 — v1.54: Implemented offline preparation for all 944 application pages and candidate/runtime infrastructure. Recorded verified artifacts, provisional development cases and provider cost estimate; new billable batches await a cap, and activation awaits human review. Preserved the original pilot and frozen evaluations.

- 2026-11-07 — v1.53: Recorded Aarib’s confirmation that Odoo 19 is the only covered version for now. Removed version choice from open pilot decisions, constrained corpus expansion/evaluation to version 19, and explicitly deferred M8 without changing milestone IDs. Hosting, cohort and task-quality acceptance remain pending.
- 2026-11-06 — v1.51: Aarib explicitly changed priority to rapid Codex-led implementation for CEO/operations/client validation. Added a bounded pilot delivery track drawing forward grounded Q&A, essential access/observability and launch preparation while retaining milestone IDs, unfinished gates, baseline/holdout integrity and broader-release requirements. Recorded native evidence-source loader success and the fact that the unshared alignment draft was not applied to the user repository. Prepared CODEX_HANDOFF.md; pilot versions/hosting remain to be confirmed.

- 2026-11-06 — v1.50: Recorded native parser namespace/candidate success for repeat IDs, nested content, fragment updates and failed-parse preservation. Prepared a dependency-aware pinned evidence-source loader and verified it locally with real Git commits, stable historical bytes and invalid-metadata rejection. User loader reproduction and cross-file paragraph/scoring/rebuild integration remain pending; accepted artifacts and production pointer are unchanged.

- 2026-11-06 — v1.49: Recorded native include-candidate repeat failure and the supplied diff: document/chunk records matched, while duplicate Sphinx registration warnings changed diagnostics/summary and cascaded to the chunk parent snapshot ID. Prepared per-reader Docutils namespace isolation; stateful registry/lifetime checks passed locally, native rerun pending. Later candidate update/failure gates have not yet run, and accepted artifacts/production pointer remain unchanged.

- 2026-11-06 — v1.48: Recorded native nested-include normalization success. Prepared explicit include-policy wiring through corpus builds, the normalization CLI and candidate preparation, with per-owner dependency summaries. Controlled local integration checks passed for default byte/identity preservation, CLI routing, candidate repeat/update and parser-failure preservation. Native candidate reproduction and cross-file evidence/rebuild integration remain pending; accepted artifacts, production pointer and retrieval settings are unchanged.

- 2026-11-06 — v1.47: Recorded native nested-include parser success for content, dependencies and source positions. Prepared opt-in dependency-aware normalization with deterministic metadata/revision identity and cross-file locations; local real-Normalizer checks with parser-node doubles passed, including default byte preservation and dependency-only revision sensitivity. Native normalization reproduction and corpus/evidence integration remain pending; no accepted snapshot, production pointer or retrieval setting changed.

- 2026-11-02 — v1.46: Recorded native pinned-file reader success. Prepared the opt-in nested-include store/directive and reader keyword arguments with per-page pinned dependency records, bounded relative-path resolution and preserved generic parser settings. Local real-Git/staging and directive-call tests passed; real Sphinx nested parsing/line positions and subsequent normalization/evidence integration remain pending. No accepted snapshot, production pointer, model, benchmark, holdout or retrieval setting changed.

- 2026-11-02 — v1.45: Recorded native source-update fixture success for addition/edit/unchanged/deletion, cache membership, active/historical membership, updated dense results, repeat, real parser failure and complete fixture cleanup with zero real API requests. Began controlled include work with a real-Git-tested pinned regular-file reader; native reader reproduction and parser/include integration remain pending. Remaining reporting/comparison/M3.1 test gates and the K=5 baseline are unchanged.

- 2026-11-02 — v1.44: Recorded native combined rebuild success/failure preservation at 30 documents/205 cached vectors, zero new requests and unchanged production/count/manifest state after cleanup. Prepared the real Git source-update fixture probe, including one addition/edit/unchanged/removal, cache membership checks, active/historical deletion behavior, dense retrieval metadata/text, unchanged repeat and invalid-RST preservation. Local checks passed with controlled parser output and embedded SQL, preserving an unrelated 205-chunk sentinel. Native fixture reproduction and remaining M3 reporting/include/comparison gates remain pending.

- 2026-11-02 — v1.43: Recorded user-confirmed cached native publication/repeat with 205 hits, zero API requests and unchanged counts/production pointer after cleanup. Prepared and locally verified a combined rebuild function with active-manifest history checks, initial/repeat source plans and parser-failure publication prevention using frozen parser output, dummy vectors and embedded SQL. Native combined probe and remaining M3 lifecycle/include/comparison gates remain pending; no production activation or benchmark/model/retrieval change occurred.

- 2026-11-02 — v1.42: Recorded user-confirmed real-parser candidate preparation and failure preservation at the frozen 30/205 snapshot IDs. Prepared the cache-aware embedding/publication coordinator and verified success/reuse, pre-import failures and transaction rollback using dummy vectors with embedded SQL. Prepared a native zero-API probe under a temporary corpus name with pointer cleanup and production/count checks; native reproduction remains pending. Source lifecycle, include provenance and plain-window comparison gates remain open; no production activation or benchmark/model/retrieval change occurred.

- 2026-11-02 — v1.41: Recorded user-confirmed source planning (30 unchanged; simulated 1 added/1 changed/28 unchanged/1 removed, stable ordering/membership, unchanged manifest). Prepared and locally tested complete candidate coordination using actual byte/snapshot helpers with frozen parser output; native real-parser temporary verification remains pending. Explicitly recorded that includes are disabled and cross-file provenance is unsupported, leaving that M3 gate open. No benchmark, production snapshot/index, model or retrieval configuration changed.

- 2026-11-02 — v1.40: Recorded the native cached six-case rank audit: complete-evidence depths 106/13/6/10/14/14 for cases 004/010/012/016/017/021, zero new API requests and unchanged baseline. Kept the K=5 baseline and existing gates. Prepared and locally verified the guided pure source-change planner over the accepted inventory plus in-memory addition/edit/removal fixtures; user reproduction and lifecycle integration remain pending. No holdout, benchmark, source snapshot or production index/configuration change occurred.

- 2026-11-02 — v1.39: Recorded the user-verified cache-only repeat 02f7df9d-8c30-4559-bedc-de53c1b4f167, 23 hits/zero API requests, unchanged rankings/scores and local wrapper median/P95 29.287/40 ms. Recorded the six incomplete development cases and eight missing groups; verified their source mappings and presence in eligible chunks. Prepared and scorer-checked a cached full-ranking diagnostic for these six cases; native missing ranks remain pending. No benchmark, snapshot, production K, quality threshold, holdout use or milestone-gate change occurred.

- 2026-11-01 — v1.38: Recorded native development report a63c69cd-c64c-4d07-97e6-0869efe8342c: all 23 executions succeeded; 15 scored cases yielded Hit@5 13/15, MRR 0.8, mean group coverage 0.7444444444444444 and full required evidence 9/15. Recorded type breakdowns, mixed API/cache timings and 22 query requests/543 tokens. Prepared cached repeat and six-case inspection with API-client construction blocked; their native results remain pending. No quality threshold, holdout use, benchmark, retrieval configuration or milestone-gate change occurred.

- 2026-11-01 — v1.37: Recorded native per-case scoring of development case M12-DRAFT-003 and documented the unchanged standalone accepted benchmark file/identity/hash. Prepared the full development batch with frozen-input preflight, index/configuration pinning, per-case checkpoints, answer-only/by-type metrics, cache-aware latency and explicit incomplete-usage/quality handling. SDK-mocked/embedded-SQL first/repeat/failure checks passed. Native aggregate results, remaining M3 lifecycle/comparison gates and holdout evaluation remain pending; no benchmark or active-index change occurred.

- 2026-11-01 — v1.36: Recorded two native successful cached retrieval CLI runs, distinct report IDs, identical rankings and 34.745/40.389 ms wrapper observations. Prepared offline paragraph-to-root evidence alignment and per-case scoring against unchanged source-span judgments. All 31 required development targets aligned; constructed-ranking and invalid-input tests passed. Native saved-report scoring, aggregate evaluation and remaining M3 lifecycle/comparison gates remain pending. No holdout content, benchmark labels or active-index configuration were changed.

- 2026-11-01 — v1.35: Recorded successful native retrieval for development case M12-DRAFT-003, its 15-token first request, zero-request repeat, actual ranks/distances and the supporting IMPORTANT block in rank 1. Prepared the retrieval CLI with separate atomic UUID reports, full evidence/usage/context and explicitly defined timing. Local success/failure/write-preservation tests passed with mocked retrieval and blocked API construction. Native CLI reports and benchmark/lifecycle evaluation remain pending; no holdout tuning, corpus, active-index or milestone-gate change was made.

- 2026-11-01 — v1.34: Recorded native five-hit self-retrieval, stable ranks and source metadata, including the observed distances. Checked the unusual breadcrumb against the unchanged source/normalized section tree and recorded its source-native origin. Prepared the query-embedding/cache/dense-search wrapper and passed SDK-mocked/embedded-SQL integration, zero-request repeat, validation and failure checks. Selected one existing development question for the native next command; holdout outcomes were not inspected. Real question retrieval, persisted reports/evaluation and unchanged M3 lifecycle gates remain pending.

- 2026-11-01 — v1.33: Recorded native import/publication/reuse of all 205 chunks and the matching active database snapshot ID. Prepared exact cosine search with configuration checks, active-snapshot scope, deterministic ranks and source metadata. Local embedded SQL tests passed known distances/ranks, rejected invalid inputs and excluded historical-only membership after activation. Native self-retrieval, real-question embedding/search and M3 measurements/lifecycle gates remain pending. No benchmark, corpus or milestone-gate change was made.

- 2026-11-01 — v1.32: Recorded the user's successful 205-pair real-snapshot loader and unchanged-source/tamper checks. Prepared the guided transactional importer and locally exercised actual SQL in embedded PostgreSQL 18.6/pgvector 0.8.7, including publication/reuse, stored-data validation, vector reuse across snapshots and rollback after partial membership or pointer update. Native asyncpg/PostgreSQL 16 import verification remains user-pending. No real database/API, source/benchmark or milestone-gate change was made by the assistant.

- 2026-11-01 — v1.31: Recorded successful user first/repeated migration, matching checksum and four empty application tables. Prepared and locally checked the read-only snapshot-pair loader over all 205 chunks with dummy vectors, including reordered inputs, eligibility filtering and invalid association/identity/membership rejection. The real-snapshot user loader run, database import/publication and dense retrieval/evaluation remain pending. No source, benchmark or milestone-gate change was made.

- 2026-11-01 — v1.30: Recorded Aarib's successful Python host TCP/password connection, database/extension identity, cosine calculation and connection closure. Prepared the four-table dense-index SQL migration and transactional checksum/advisory-lock runner. Actual DDL/constraint/rollback checks passed in temporary embedded PostgreSQL 18.6/pgvector 0.8.7, and four mocked runner checks passed; application/repeat checks on the user's PostgreSQL 16 remain pending. Completeness/publication validation belongs to the future importer. No source, benchmark, milestone-gate or real database/API change was made by the assistant.

- 2026-11-01 — v1.29: Recorded successful user Compose validation, healthy dedicated database and SQL-confirmed PostgreSQL 16.15/pgvector 0.8.7. Prepared the guided asyncpg 0.32.0 managed-connection helper and locally checked its actual driver signatures and mocked settings/resource-cleanup/error behavior. User host TCP/password/query verification, schema/import/retrieval and existing M3 evaluation/lifecycle gates remain pending. No real database credential was inspected by the assistant.

- 2026-11-01 — v1.28: Recorded the user's Docker/Compose/psql versions, running database port mappings and backend dependency declarations. Prepared and statically checked a dedicated PostgreSQL 16/pgvector 0.8.7 Compose service on localhost:55433 with persistent storage, private password interpolation and readiness checks. User Compose/startup/extension verification is pending; the assistant has no Docker executable and made no database connection. Schema/import/retrieval and the existing M3 evaluation/lifecycle gates remain pending and unchanged.

- 2026-11-01 — v1.27: Recorded Aarib's passing final temporary-copy CLI/integrity/failure checks and marked M3.2 complete for the accepted 30-document/205-chunk embedding pipeline. Began M3.3 with read-only runtime/dependency inspection and the existing exact dense-search/database-publication plan. Retained the partial-failure usage limitation, unreported combined M3.1 tests and all outstanding M3 retrieval/lifecycle/evaluation gates. Source corpus, benchmark and milestone titles are unchanged.

- 2026-10-30 — v1.26: Recorded Aarib's successful combined CLI run `3430bf40-b3aa-41ff-955c-f4e457fab573`, 205 cache hits, zero API usage, unchanged embedding snapshot and 1.13-second cached CLI duration. Prepared and locally checked the final temporary-copy verification of separate reports, input/cache integrity rejection and failed-publication preservation/cleanup with the API constructor blocked. User final-probe reproduction remains pending before dense-index implementation. Source scope and milestone gates are unchanged.

- 2026-10-30 — v1.25: Recorded Aarib's complete 205-record real embedding snapshot `6e2c657ee8cd109c40c928024916ba5f0803bbee65e6a0abadfdf47dddb4343c`, first publication and identical reuse. Prepared and locally checked the combined CLI with separate atomic UUID run reports, stage-specific runtime failures, nonzero exits and safe SDK error metadata. Documented unavailable usage for failed generation and running-report behavior if finalization/interruption fails. User CLI/report checks, indexing and evaluation remain pending; source scope and milestone gates are unchanged.

- 2026-10-30 — v1.24: Recorded the first user-reported embedding-record metadata and independently matched its chunk/text/cache identities. Prepared and locally validated the complete two-file embedding snapshot publisher, including byte-identical reuse, missing/corrupt input rejection, failed-write preservation and concurrent identical publication. User snapshot execution and its real-vector content ID, combined CLI/run report, indexing and evaluation remain pending. Source scope and milestone gates are unchanged.

- 2026-10-30 — v1.23: Recorded Aarib's live generation of the remaining 204 vectors in four requests, 39,079 API-reported prompt/total tokens, complete verification of all 205 cache entries and a zero-request repeat. The recorded successful generation total is 39,253 prompt tokens including the earlier one-chunk request. Prepared and locally checked deterministic chunk-linked embedding records with temporary dummy vectors. User record-builder reproduction, complete embedding snapshot/report, indexing and evaluation remain pending. Source scope and milestone gates are unchanged.

- 2026-10-30 — v1.22: Recorded the user-reported expired-key diagnostic, subsequent one-chunk live embedding success (174 prompt tokens, 1,536 dimensions) and zero-request cache reuse in a separate run. Prepared and mock-validated the batch-generation job over all 205 inputs, including duplicate-text reuse, full-cache offline repeat and preservation/resume after a later request failure. User corpus-job execution, persisted embedding snapshot, indexing and evaluation remain pending. The assistant accessed no real credential and made no real API request; source scope and milestone gates are unchanged.

- 2026-10-30 — v1.21: Recorded Aarib's successful mock adapter output and clarified its relationship to Project 1's embedding service. Prepared and mock-validated a one-chunk API/cache integration command with 1,536 dimensions, one request on a miss and credential-free reuse on a hit. Live execution remains user-pending; no real API request, credential inspection, production vector generation, scope change or milestone-gate change occurred.

- 2026-10-28 — v1.20: Recorded Aarib's successful disk-cache checks. Prepared the async OpenAI adapter and verified SDK 3.40.0/httpx2 behavior using mock transport, ordered-response/usage validation, request bounds and propagated API errors. User SDK installation and adapter check are pending. No real API request, credential inspection, production-vector publication, scope change or milestone-gate change occurred; the live request/job and dense indexing/evaluation remain pending.

- 2026-10-28 — v1.19: Recorded user-confirmed embedding-input counts and the default model/configuration/cache-key results. Prepared and locally validated the disk-cache increment with checksum/identity/vector validation, immutable repeat storage and temporary-file publication; user cache reproduction is pending. All cache test vectors are temporary dummy fixtures. No real embedding/API charge, credential inspection, corpus change or milestone-gate change occurred; the real API adapter/job, indexing and retrieval evaluation remain pending.

- 2026-10-28 — v1.18: Started M3.2 at Aarib's explicit request while retaining the unreported combined M3.1 test result. Prepared and locally checked verified eligible-text loading and exact-text fingerprints: 205 inputs/205 unique hashes, 39,253 recorded tokens and a 512-token maximum. User input-preparation reproduction, embedding configuration/cache/API, index lifecycle and retrieval measurement remain pending. No API request, credential inspection, scope expansion or milestone-gate change occurred.

- 2026-10-28 — v1.17: Recorded user-reproduced grouping/merging, 134 image attachments, 743 units, 205 bounded chunk records, three packing tests, reproducible record/configuration IDs, candidate and classified snapshots, structural eligibility and CLI reuse. The classified snapshot is `2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce`. All 16 renderer/packing tests pass locally; the combined user run is pending. Recorded the actual Project 1 source comparison. Scope, benchmark, normalized snapshot and milestone completion gates are unchanged; embedding, index lifecycle and measured retrieval remain to be built.

- 2026-10-26 — v1.16: Recorded Aarib's exact token-measurement reproduction. Prepared the guided consecutive-section grouping helper and locally checked all 877 candidates, 197 groups, preserved order and source/configuration boundaries. Seven joined section groups exceed the provisional 512-token threshold; user grouping reproduction and actual bounded packing remain pending. M3.1 remains in progress.

- 2026-10-26 — v1.15: Recorded user-reproduced source-linked draft records, section tracking and 877 candidates across 30 documents. Added locally verified token-counting proposal/results with pinned tiktoken 0.14.0 and cl100k_base; all 13 renderer checks still pass after walker refactoring. User token measurements, grouping/eligibility, token-bounded packing and retrieval evaluation remain pending. No scope or milestone completion-gate changes.

- 2026-10-23 — v1.14: Recorded user-reproduced walker, prose/admonition/image, list-boundary and table results. At Aarib's explicit request, consolidated the remaining renderer kinds into `text.py` with one test-file/command and a code-level explanation. All 13 assistant-local tests passed across the exact 30-document snapshot and 26 block kinds. User consolidated reproduction and actual chunk records/token bounds remain pending; M3 stays in progress.

- 2026-10-23 — v1.13: Began M3.1 under Aarib's explicit collaborative-coding preference. Recorded the proposed small section walker and its assistant-local fixture inspection; user implementation is pending. No chunker, embedding/indexing implementation or code bundle was delivered, and milestone completion criteria remain unchanged.

- 2026-10-23 — v1.12: Validated Aarib's eight-pass fidelity decision export against the exact fixture list and reported snapshot/review identities; recorded six user-passed tests, complete source/image availability and clean pinned checkout evidence. Assessed the existing M2 criteria and marked M2 complete for the accepted corpus and reviewed fixtures. Reconciled the milestone table; M3.1 chunk design is next. Reference/image limitations, frozen scope and benchmark remain unchanged.

- 2026-10-23 — v1.11: Recorded the user's matching 30-document normalized snapshot and fixture-check output. Prepared and locally validated the source/rendered/normalized fidelity packet with dependency/asset/checkout evidence, six tests and eight pending human checks. The snapshot/corpus are unchanged; M2 acceptance remains pending.

- 2026-10-22 — v1.10: Added the locally validated 30-document normalized-corpus implementation with structured mappings, native reference results, explicit unresolved states, categorized diagnostics and immutable/reusable snapshots. Ten focused tests and reviewed fixtures passed; independent processes produced identical full output. User reproduction and fidelity review remain pending.

- 2026-10-22 — v1.9: Marked M2.1 complete from the user's matching 30-file Sphinx corpus run. Began M2.2 with a locally tested normalized-record contract, core mapping, one-document demo and four focused tests. Independent fixture parses and the extracted package produced matching JSON. User reproduction and broader normalization remain pending; M2 is in progress.

- 2026-10-22 — v1.8: Recorded the user's successful controlled Docutils probe. Locally validated the final Sphinx spike over all 30 accepted file hashes, including cards and original navigation-target preservation. Selected Sphinx with controlled adapters as the working implementation choice. Final user reproduction and M2.2 normalization remain pending; M2 is in progress.

- 2026-10-22 — v1.7: Recorded the user's successful four-document structure probe. Prepared and locally validated a six-file controlled Docutils adapter/probe with explicit reference-target metadata and cards/navigation preservation. The adapter has no reference resolver or asset validation; user reproduction and the remaining Sphinx/full-corpus fidelity work are pending.

- 2026-10-22 — v1.6: Recorded the user's successful three-page reference probe. Prepared and locally validated a four-file structure probe with sphinx-tabs 3.5.0, checking table semantics, tab context, substitutions and math. Expanded user-run verification, controlled Docutils comparison and production parser selection remain pending.

- 2026-10-22 — v1.5: Recorded user-reproduced Docutils/Sphinx/example-adapter results and the pinned experiment versions. Prepared and locally validated a three-page reference probe with literal icon preservation; expanded user-run verification and representative-structure comparison remain pending. M2 is in progress.

- 2026-10-22 — v1.4: Marked M1 complete from the accepted scope/benchmark and user-run 30-file CLI output. Independently reproduced active fingerprint d359162bcd1c4785ae1f339d9b972d1bad90102e5351dc33abaebea046110d1d from supplied inventory data. M2.1 starts with dependency inspection and a controlled parser comparison.

- 2026-10-22 — v1.3: Recorded Aarib’s acceptance of the supplied M1.2 documents, froze selection/benchmark m12-1.0 and accepted the exact credit-note dependency. Prepared local activation instructions; manifest execution evidence remains pending before M2.

- 2026-10-22 — v1.2: Recorded archive byte/fingerprint verification, the proposed 30-page scope with one exact Accounting dependency, full 30-case draft and provisional family split. Preserved the human-review and local activation gates; M1.2 remains in progress.

- 2026-10-19 — v1.1: Marked M1 in progress and M1.1 complete based on user-reported runs and six passing tests; recorded the source snapshot, candidate inventory, fingerprint, implemented files, and M1.2 next step. Milestone numbering and scope gates remain unchanged.

- 2026-10-18 — v1.0: Established canonical M1–M10, initial scope, trust contract, evaluation policy, and M1.1 task.
