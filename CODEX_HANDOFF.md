# Codex handoff — Odoo Functional RAG client pilot

Date: 6 November 2026 (Asia/Calcutta)
Owner: Aarib Meterwala
Delivery mode: Codex-led implementation; Aarib reviews working features, scope and answer quality.

## Full-application expansion checkpoint — 7 November 2026

Aarib approved implementing the full-application plan: all 944 English Odoo 19 application pages at the current pin, text/captions/image references only, separate candidate and reviewed switch. He explicitly chose **estimate before selecting a provider budget**. No new provider batch is authorized until he chooses a cap. See [FULL_CORPUS.md](docs/FULL_CORPUS.md) for measured artifacts, cost assumptions, commands and gates.

Offline audit/preparation completed: 944 normalized pages, zero fatal parser/unsupported-node errors, 879 searchable pages, 65 reference-only pages, 11,926 chunks, 11,134 eligible unique inputs, 179 cached vectors, 10,955 missing embeddings (1,341,670 tokens), 7,319 reference links and 3,255 image references. Estimated new embeddings $0.026833; planned 83-case answer evaluation about $0.3652 plus query embeddings, approximately $0.41 total under recorded assumptions. No new embeddings or live generation were executed. The original index and frozen benchmark remain intact.

Implemented opt-in full parsing/chunking, generic reference/neighbor packets, PostgreSQL FTS/RRF retrieval, release descriptors, release-bound sessions, dynamic UI coverage, isolated preview settings, shared budget reservations, candidate publication/evaluation and human-review approval commands. The additive SQL migration and hybrid SQL path were verified on the existing project DB using a cached query with provider calls forbidden. Sixty new development cases have provisional source excerpts; expected answer points/gold groups still require human review. No full candidate index or generated-answer comparison exists yet; these depend on the budget choice.

**Next:** obtain the user's cap choice from the concrete offline estimate, then run metered candidate publication and evaluation. Do not reset the ledger or switch the pilot automatically. Human review of the six workflow families is required before activation. The original 30-page pilot remains the fallback.

## Confirmed version scope — 7 November 2026

Aarib confirmed that **only Odoo 19 is covered for now**. This is the agreed product scope, superseding the earlier implementation assumption. Keep documentation expansion, evaluation and pilot answers within Odoo 19; cross-version ingestion/comparison is deferred. Hosting and the pilot cohort still need selection.

The browser UI now shows a fixed Odoo 19 label with no version selector. Every browser question automatically submits version 19.0, including after reload or sign-out/sign-in. Backend guards for explicitly unsupported versions remain in place. The updated build and both browser tests pass.

## Verified implementation checkpoint — 7 November 2026

The bounded internal pilot is now implemented on branch `pilot/grounded-browser`. Read [README.md](README.md), [verification](docs/PILOT_VERIFICATION.md), [runbook](docs/PILOT_RUNBOOK.md) and [observation protocol](docs/PILOT_PROTOCOL.md) before continuing. The original delivery brief below is retained as historical context; its “not verified” runtime boundary is superseded by this checkpoint.

- Existing 30-document/205-vector artifacts, source Git hashes and active database index verified. Preexisting backend changes remain byte-identical; the stopped existing DB container was restarted with its persisted volume.
- FastAPI answers, configurable structured generation, bounded evidence packets, exact citation-ID/quote validation, model support/completeness review, React/Vite UI, isolated cookie sessions, restricted named access, persistent limits, feedback and operator-only JSONL/audit export implemented.
- 72 backend tests and two browser tests pass. A real browser-to-provider answer and operator export passed using the existing cached query/vector index. Local pilot runs at `http://localhost:8000`; generated keys are private in `backend/.env.pilot`. Launch again from `backend` with `uv run python -m app.pilot` after building the frontend.
- Separate bounded support-passage policy repairs two demonstrated context gaps without changing dense K=5 retrieval or corpus embeddings. Replay of all 23 frozen development results: complete groups 11/15 and mean group coverage 80.6%, versus 9/15 and 74.4% in the unchanged frozen dense baseline. These are evidence-packet measurements, not answer accuracy.
- Live checks show a supported invoicing answer, useful clarification and unsupported-data abstention. Hard partial-delivery and partial-credit workflows still clarify/abstain unreliably; an earlier model-approved screen transition was caught manually. No client-readiness claim. Rejected drafts/review issues are operator-only; ordinary API/history never expose them.
- No external deployment, client messages, source expansion, bulk embeddings, holdout tuning or completion of the deferred research gates occurred.

**Next continuation:** keep the confirmed Odoo 19-only scope, diagnose the documented hard-workflow false abstentions with the operator audits, and run the predefined operations task observations. Preserve the frozen baseline and current ingestion edits. Review a concrete hosting target/cohort before any external publication.

## Objective

Turn the existing `odoo-functional-rag` repository into a small, usable documentation-grounded assistant for an internal operations pilot, followed by a limited pilot with the CEO's existing clients. Learn whether it helps users complete real Odoo tasks correctly and faster.

Implement in the actual repository. The known local root is `/home/aarib/odoo-functional-rag`; Python commands run from `backend`. A Git remote URL has not been supplied in this handoff. Read repository instructions and inspect the code and working tree before making assumptions. Preserve uncommitted user work. The accompanying `Project_2_Odoo_RAG_Canonical_Roadmap.md` v1.54 records the changed delivery priority and detailed history.

Work through implementation, tests and a runnable demonstration rather than stopping after an audit or plan. Give concise progress updates and explain completed features at module level; line-by-line teaching is no longer the default. Resolve routine implementation choices autonomously. Ask for missing product decisions only when they materially affect the outcome.

## First pilot scope

- Start with public Odoo 19 English Sales/Inventory workflows and the existing accepted corpus. The corpus includes one Accounting support page; this is not comprehensive Accounting coverage.
- Odoo 19 is the confirmed version scope. Display that version and the covered topics clearly; expand documentation and test cases within version 19. Other versions and cross-version comparisons are deferred.
- First deliverable: a usable internal browser-based question/answer flow with retrieved evidence, validated citations and explicit insufficient-evidence/clarification behavior.
- Then add restricted pilot access, isolated sessions, task feedback and deployment instructions for a small client trial.
- Keep the initial 30-page corpus for the first working vertical slice. Expand selected public documentation only for concrete pilot-question gaps, with versioned ingestion and appropriate checks. Do not silently ingest the entire documentation repository.
- Live Odoo connections, client database writes, customer document uploads, autonomous actions and configuration changes are outside this pilot scope.

## Existing implementation — inspect and verify before extending

User-reported successful native runs establish:

- Reproducible Git-pinned discovery, scope selection, file hashes, manifests and ingestion CLI.
- Structure-preserving RST ingestion and reviewed normalized documents.
- 30 accepted documents, 205 eligible chunks, a 512-token maximum and complete cached embeddings.
- OpenAI `text-embedding-3-small`, 1,536 dimensions, content/configuration-keyed cache, repeat reuse and persisted job reports.
- PostgreSQL/pgvector dense index import, immutable snapshots, active-index publication and exact cosine retrieval.
- Question embedding/cache, dense retrieval CLI and a development benchmark runner.
- Temporary source-update lifecycle checks for additions/edits/unchanged/removal, cache reuse, history and preservation of an earlier index after parser failure.
- Opt-in pinned nested includes through parser, normalization and candidate chunk creation. A per-reader `docutils_namespace()` fixes repeated-build registration warnings; native repeat/update/failure tests passed.
- `app/evaluation/source_files.py::load_evidence_sources()` loads verified main/include lines at the normalized document's commit. Its temporary real-Git tests passed on Aarib's machine.

Repository verification is still required: these are reported checkpoints, not a substitute for inspecting the checked-out implementation and running its tests.

## Current boundaries and quality evidence

The usable answer-generation API and browser UI have not been verified as implemented. Inspect the repository to determine whether any scaffolding already exists.

The existing evidence alignment is `m3-paragraph-evidence-0.1`. The new pinned source loader has not yet been wired into cross-file paragraph alignment or scoring. An include-aware alignment v0.2 was drafted only in the previous assistant's verification workspace and was never handed to Aarib. Do not assume that draft is present or complete in this repository.

Other unfinished work includes include-policy forwarding through the full rebuild entry point, include-aware change/report/publication checks, unified lifecycle reports, the plain token-window comparison and a consolidated M3.1 test report. Keep these recorded as unfinished. They need not all block the first internal pilot using the already accepted corpus. Finish anything that the actual pilot path requires for correctness.

The frozen dense baseline at K=5 completed 23 development cases, including 15 answerable cases:

- Hit@5: 13/15, or 86.7%.
- MRR@5: 0.80.
- Mean required evidence-group coverage: 74.4%.
- Complete evidence: 9/15, or 60%; multi-step workflows were weaker.

These are retrieval measurements, not answer-accuracy or client-readiness claims. Evaluate generated answers separately. Preserve the baseline and benchmark bytes. Develop on the development split; keep holdout questions sealed during implementation/tuning. Broader release evaluation remains governed by the canonical roadmap.

## Delivery order

### 1. Establish the actual repository state

Inspect `AGENTS.md`, README, dependencies, backend modules, database migrations, configuration, available frontend and tests. Run the appropriate existing checks and establish a Git checkpoint/isolated branch without overwriting user changes. Record missing pieces briefly, then implement.

Known test entry point from `backend`:

```bash
uv run --group parser-spike python -m unittest discover -s tests -v
```

Inspect individual test requirements before running database/live-service checks. Use configured secrets without printing their values. Use the project's existing database/compose setup; do not recreate or reset unrelated containers/databases.

### 2. Deliver one complete question-to-answer slice

Reuse the existing query embedding/cache and dense retriever. Add a FastAPI answer endpoint and a bounded evidence context builder with server-issued evidence IDs. Implement structured generation with states equivalent to `answered`, `needs_clarification` and `insufficient_evidence`.

Require factual claims to be supported by the supplied passages. Keep conversation context distinct from trusted source evidence. Ask useful clarification questions when version, invoicing policy or workflow conditions are missing. An uncalibrated cosine-distance threshold alone is not an answerability policy.

The server validates returned citation IDs against supplied evidence and owns citation titles, version, links and excerpts. Show versioned documentation links and commit-pinned source evidence where available. Never invent unverified anchors. Valid citation IDs do not alone prove that a claim is supported; review semantic support and completeness.

Make the generation model configurable. Inspect the installed SDK/repository patterns and current official documentation when needed. Reuse the current embeddings and cache. Keep live smoke checks small and metered; do not bulk regenerate embeddings as part of building the answer endpoint.

### 3. Add the pilot interface

Use the existing frontend if present; otherwise a simple React/Vite/TypeScript interface fits Aarib's stack. Include a question input, answer area, expandable cited evidence, clear supported-version/topic information, clarification/insufficient-evidence states and useful errors/loading behavior.

Capture task feedback linked to a request: task solved, partially solved or unresolved, plus optional correction/comment. Support feedback review/export. Add restricted pilot access and session isolation. Keep provider keys server-side, add request limits/timeouts and record latency/model/token usage. Reuse sound Project 1 runtime patterns where available instead of rebuilding the entire previous project. Streaming is optional for the first working slice.

### 4. Validate and prepare a controlled pilot

Run focused endpoint/UI/integration checks, including invalid citations, unsupported questions, missing workflow conditions, wrong-version questions, empty evidence and multi-step answers. Use mocked provider responses for repeatable tests, plus a small configured live smoke check. Review representative development answers for correctness, support and complete prerequisites; include the known difficult workflows.

Recompute development results for any changed retrieval configuration and keep it distinguishable from the frozen baseline. Make targeted retrieval improvements when required by pilot failures; a full hybrid/reranking research matrix is not a prerequisite to the first internal pilot.

Collect a short task set from operations before client exposure. Define acceptance and measurement before reviewing results: correct task completion, time compared with the current process, unresolved/escalated tasks and user feedback. Inspect unsupported/confidently wrong answers explicitly. Query counts or thumbs-up alone are not a business-impact measure.

Provide a reproducible local launch, environment example without secrets, deployment configuration/runbook, health check and rollback steps. Prepare and review a concrete deployment target before external publication; no external deployment or client messaging is authorized by this handoff alone. Start with internal operations review, then a limited client cohort once the reviewed pilot is ready.

## Keep out of the critical path

Comprehensive cross-version comparison, agents/tool execution, exhaustive include edge cases beyond the supported pilot path, broad chunking experiments, learned reranking without demonstrated need, enterprise administration and a large analytics dashboard. Keep existing milestone IDs and unfinished research tasks intact; pilot delivery is a parallel, deliberately smaller track, not a claim that M3–M10 are complete.

## Accepted artifact identifiers — verify against local files

- Source commit: `c9202e68ae702daec981b47d0b6055191084ffa2`.
- Manifest inventory fingerprint: `d359162bcd1c4785ae1f339d9b972d1bad90102e5351dc33abaebea046110d1d`.
- Normalized snapshot: `15fce1c26f99a9d986c792aeae260e329519a830ee329c1aa263ad962196c7cc`.
- Chunk snapshot: `2648e24f59b6233ba8417f79a9607a663c714aef00057193767e4383c6b85dce`.
- Embedding snapshot: `6e2c657ee8cd109c40c928024916ba5f0803bbee65e6a0abadfdf47dddb4343c`.
- Database snapshot: `e8f661333130c61d51f1a68908ef2038c9a5d24575369bbaa3bccf0bb2b97818`.
- Benchmark SHA-256: `e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425`.
- Native baseline report: `data/evaluations/development/a63c69cd-c64c-4d07-97e6-0869efe8342c.json`.
- Main source/config: `sources/odoo-documentation`, `config/corpus.json`, `data/manifests/odoo19-corpus.json`.
- Existing DB: PostgreSQL 16/pgvector, project compose file `compose.db.yaml`, host port previously `127.0.0.1:55433`; inspect current configuration rather than hardcoding credentials.

## First task and completion report

Start by inspecting the repository and confirming the reported baseline. Implement the smallest working browser-to-grounded-answer slice, then add feedback/access and run the focused checks. Continue through a runnable local pilot, not just a scaffold or plan. Keep this handoff and the roadmap updated with verified results.

At completion report: what a user can do, exact launch/test commands, checks actually run, unresolved answer-quality/scope limits, deployment readiness and the next pilot observation to collect. Distinguish real services from mocks and do not call the product production-ready solely because tests pass.
