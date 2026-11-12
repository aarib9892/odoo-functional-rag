# Odoo 19 full-application candidate

The expanded source scope is all **944 English application pages** at the existing source commit `c9202e68ae702daec981b47d0b6055191084ffa2`. Developer/API, installation and contribution documentation remain outside this collection. Screenshots are referenced, not interpreted.

The existing 30-page pilot remains the active release. Preparing this corpus does not authorize provider spending, activate the candidate, publish a website or approve client use.

## Verified offline result

All 944 pages normalize without fatal parser errors or unsupported-node diagnostics. The full-corpus adapters are opt-in: spoilers/exercises, HTML layout containers, richer cards, line blocks, definitions, footnotes and inline formatting retain their content; raw inline graphics become explicit reference-only markers. The legacy parser/renderer path is preserved.

| Item | Result |
|---|---:|
| Searchable pages | 879 |
| Reference-only/navigation pages | 65 |
| Chunk records, maximum 512 tokens | 11,926 |
| Eligible unique embedding inputs | 11,134 |
| Existing cached vectors reused | 179 |
| New embedding inputs | 10,955 |
| Uncached embedding tokens | 1,341,670 |
| Verified reference edges | 7,319 |
| Image references | 3,255 |

Large structures use versioned fragments with rendered offsets; merged table cells retain their headers/spans. Images are never treated as visual evidence. Normalized/chunk fingerprints and the existing source-evidence loader passed on the full corpus. This is structural verification, not a human review of every paragraph or generated workflow.

Artifacts are under ignored `data/expansion/`: `audit/audit.json`, `audit/parser.log`, `chunk-audit.json`, immutable `normalized/` and `chunks/` snapshots, `links.json`, and `estimate.json`. The final normalized snapshot is `a156be5548b73cf3351090d0f0b09cab328870d7cf5149a4ac68dec04f37621b`; chunk snapshot is `8a9c768b04f352d129cb5fa15d401786fb3d94b1e296b9df8c4001386b000c99`. Earlier diagnostic snapshots are retained separately.

## Checks performed

The full backend suite passed 87 tests; after adding the final approval-gate test, all 16 expansion tests passed separately (88 backend test cases in total). Three Playwright tests and the production UI build pass, including dynamic candidate coverage and fixed Odoo 19 behavior. PostgreSQL hybrid retrieval and the additive migration passed against the existing database with provider calls forbidden. Full normalized/chunk fingerprints and source-evidence alignment load successfully; the frozen benchmark and baseline bytes remain unchanged.

The pilot store was backed up before its additive release-ID migration. The updated localhost runtime still reports the original `pilot-30` release, 30 documents and 205 indexed chunks. Its authentication/readiness checks passed without generation. No expanded embeddings, candidate index, live evaluation results or approval descriptor exist yet.

## Reproduce offline preparation

From `backend`:

```bash
uv run --group parser-spike python -m app.ingestion.cli \
  --repo ../sources/odoo-documentation --config ../config/corpus.full.json \
  --output ../data/expansion/manifest.json
uv run --group parser-spike python -m app.expansion.audit
uv run --group parser-spike python -m app.expansion.prepare
```

Run these sequentially: preparation refuses an incomplete/mismatched audit or any quarantined page. No database or provider call is made by these commands. Parser warnings about unstaged image files and outside-collection references are reported explicitly. Reference-only pages remain accounted for rather than silently disappearing from coverage counts.

## Provider estimate and budget gate

Verified standard USD prices are recorded in `config/expansion.pricing.json`, with official source links and verification date. [Embedding pricing](https://developers.openai.com/api/docs/models/text-embedding-3-small) is $0.02/million input tokens; [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) is $0.10/million input and $0.50/million output tokens at standard short-context rates.

- New corpus embeddings: approximately **$0.026833**.
- Planned 83-case evaluation: up to 166 draft/review calls, estimated **$0.3652**, assuming 10,000 input tokens and up to 2,400 output tokens per call.
- Conservative question-embedding allowance: **$0.013599** (83 inputs at the embedding input limit; actual questions are much shorter and existing questions are cached).
- Combined planning estimate: approximately **$0.41**, before any additional diagnostic repeats or pricing changes. This is an estimate, not a guaranteed bill. No caching discounts are assumed for generation.

**The user chose to review an estimate before choosing a cap. No cap has been authorized as part of preparation.** Do not run the following billable steps until the user chooses one. The private budget ledger is shared by publication, evaluation and candidate preview. It reserves estimated cost before each request, settles known usage and retains reservations when usage is unknown after failure. Unknown/unpriced models and missing/exhausted budgets fail before sending requests. Provider-account spending limits remain useful because local reservations cannot control provider-side billing after a timeout.

After a cap is explicitly chosen, record that amount once (the CLI refuses to overwrite an existing ledger):

```bash
# Replace <approved-amount> with the amount the user actually chose.
uv run python -m app.expansion.budget \
  --path ../data/expansion/budget.sqlite3 --limit-usd <approved-amount>
uv run python -m app.expansion.publish --budget ../data/expansion/budget.sqlite3
uv run --group parser-spike python -m app.expansion.evaluate --budget ../data/expansion/budget.sqlite3
```

Publication reuses the existing embedding pipeline/cache, verifies saved inputs, applies an additive FTS/link migration and imports under its own `odoo19-full-<snapshot>` namespace. The existing `odoo19` active index is never replaced. Cache writes survive interrupted jobs so repeats reuse completed vectors. Do not delete or reset the budget ledger to retry a job.

The FTS/link migration was tested on the existing database. A real cached query returned 20 dense hits, 20 lexical hits and 33 fused candidates without provider calls. This demonstrates the SQL path, not retrieval-quality improvement on the expanded corpus.

## Candidate retrieval, preview and review

Hybrid retrieval combines 20 exact dense and 20 PostgreSQL English full-text candidates with equal-weight RRF (constant 60). Natural-language lexical terms use OR with English stop-word removal. The packet starts with eight candidates and adds at most four same-snapshot reference/neighbor passages under a 6,000-token budget. No application filter hides cross-application dependencies.

The evaluator compares dense and hybrid assembled packets, using the original reviewed development evidence targets. Fragmented source blocks receive evidence credit only when their selected fragments cover the entire rendered block; this conservative rule avoids counting a small fragment as a complete prerequisite. It selects hybrid only when mean group coverage improves without reducing complete-evidence coverage. New development cases stay provisional and do not create an answer-accuracy or release-acceptance percentage. The original K=5 baseline and seven holdout cases remain untouched.

`evaluation/full_development.json` contains 60 draft cases: 24 direct, 24 cross-application workflow, six clarification and six unsupported cases. Associated excerpts are source-backed review aids selected by lexical overlap. A human must supply/accept expected answer points and evidence groups; empty gold fields are intentionally not treated as accepted labels. The six workflow families are website ordering, POS sales/returns, delivery/invoicing, partial payments, returns/credits and purchasing/replenishment.

Once a candidate is actually indexed and funded, preview it on port 8010 with a separate store/cookie:

```bash
PILOT_RELEASE_FILE="$PWD/../data/expansion/candidate-release.json" \
PILOT_CANDIDATE_PREVIEW=true PILOT_PUBLIC_ORIGIN=http://localhost:8010 \
PILOT_BUDGET_FILE="$PWD/../data/expansion/budget.sqlite3" \
uv run python -m app.pilot --port 8010
```

The server rejects an unindexed descriptor, a candidate without preview mode, or preview on the main origin. Sessions/requests record their release ID. Existing SQLite stores receive an additive migration; switching release invalidates old cookies while retaining history and feedback for export. `/api/session` supplies the release, topics, page classifications and accepted workflow-family labels; the UI always uses Odoo 19 and does not imply that indexing a page validates its workflow.

For approval, create a private review JSON with `reviewer`, the evaluation file's `evaluation_sha256`, explicit true values for `parser_coverage_accepted`, `access_checks_accepted`, and `no_confidently_wrong_actions`, plus `workflow_cases`. That object must contain all six family names; each value contains its `case_id` and explicit `correct`, `complete`, `supported` verdicts. The approval command checks that each selected case belongs to its family and actually returned an answer. Abstentions cannot satisfy these workflow gates.

```bash
uv run python -m app.expansion.approve \
  --release ../data/expansion/candidate-release.json \
  --evaluation ../data/expansion/evaluations/<run>.json \
  --review ../data/expansion/human-review.json \
  --output ../data/expansion/approved-release.json
```

Approval creates a descriptor only. Activation requires explicitly setting `PILOT_RELEASE_FILE` to that approved descriptor and restarting the pilot. Rollback removes the override and restarts the original profile. Keep separate budget/settings and backup the SQLite store first. No external deployment is part of this release switch.
