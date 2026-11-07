# Pilot implementation verification — 6–7 November 2026

The browser-to-answer pilot is implemented and runnable locally. **Ready for internal operations review; client exposure remains pending.** This is not a production-readiness or generated-answer-accuracy claim.

UI update, 7 November 2026: removed the version selector following the confirmed Odoo 19-only scope. Questions automatically use 19.0 and the composer shows a fixed Odoo 19 label. `npm run build` and both updated browser tests pass; the first question no longer requires version selection. The running local server was checked to serve the updated assets. This UI check used synthetic retrieval/generation and made no live provider calls.

## Repository and baseline

- Isolated branch: `pilot/grounded-browser`, based on `0095126`. Preexisting changes were backed up to `/tmp/odoo-pilot-preexisting.tar.gz` and `.patch`. Checksums confirm the four modified ingestion/indexing files plus the existing untracked source loader/include reader remain byte-identical. Handoff/roadmap additions are deliberate documentation updates. No user changes were committed or discarded.
- All three accepted normalized/chunk/embedding snapshot fingerprints match their directory identities. All 30 source hashes match Git blobs at `c9202e68ae702daec981b47d0b6055191084ffa2`; all 205 saved chunk/vector associations validate.
- The stopped existing `odoo-functional-rag-db-1` container was started with its original volume. The active published index is still `e8f661333130c61d51f1a68908ef2038c9a5d24575369bbaa3bccf0bb2b97818`, with 205 chunks. The deployment bootstrap also passed its real existing-index reuse/verification path. A fresh-database bootstrap was not exercised in this session.
- Frozen benchmark checksum remains `e1d893f01c13c23f1f3014f65d5045ff1c4015534b9b57edb76226b290fd8425`. The native baseline file remains unchanged; the context report records/checks its SHA-256. Holdout questions were not selected, printed, generated against or tuned on.
- No corpus embedding regeneration, new corpus publication, external deployment or client messages occurred. Live smoke queries reused cached question vectors.

## Repeatable checks actually run

| Check | Result and boundary |
|---|---|
| Existing unittest suite before changes | 38 passed |
| Final backend suite | **72 passed**: 38 existing + 34 pilot tests |
| TypeScript and production Vite build | Passed; about 73 KiB gzipped JS, 3 KiB CSS |
| Playwright Chromium | **2 passed** on final UI: sign-in, unknown-version clarification, answer/evidence links, feedback, refresh persistence, logout/isolation, mobile overflow and recoverable API error |
| Real pgvector connectivity and snapshot check | Passed on the original project database |
| Real existing-index bootstrap | Passed using saved 205 vectors; no embedding calls |
| Live browser → API → provider | Passed: development invoicing question, three cited steps/two source passages, cached embedding, draft/review usage recorded, 7.717 s; signed out afterward |
| Operator HTTP export CLI | Passed with the real local key; exported private JSONL without printing credentials |
| Candidate systemd unit | `systemd-analyze --user verify deploy/odoo-pilot.service` passed; unit not installed or started |
| Visual inspection | Desktop real-answer screenshot and mobile error screenshot inspected; spacing issue fixed before final browser run |
| Git whitespace/preservation checks | Passed; original backend edits remain byte-identical |

Mocks: normal backend/browser tests use synthetic provider and retrieval fixtures. Their passing states validate the pipeline/control behavior, not model answer quality. The real browser check uses the configured OpenAI `gpt-6-luna`, actual query cache, actual pgvector retrieval and actual generation/support review.

Relevant commands are in the README. Opt-in `npm run test:live` from `frontend` repeats the metered localhost-only browser check. It is separate from `npm test`. Live results/screenshots are under `data/pilot/browser/`; they are engineering checks, not operations feedback.

## Evidence assembly measurement

Dense retrieval is unchanged at K=5. The separate `pilot-support-passages-0.1` policy supplies the existing customer-credit-note prerequisites and backorder-policy passage when relevant retrieved pages/question terms justify them. It uses immutable IDs from the reviewed corpus, reads the same database snapshot, preserves all dense results and makes no new embedding requests. Context construction caps candidates at eight and fits whole passages into 3,500 tokens.

Replaying **all 23 frozen development results** through the actual builder produced:

| Evidence measurement, 15 answerable cases | Frozen dense result | Pilot assembled context |
|---|---:|---:|
| Complete required groups | 9/15 (60.0%) | 11/15 (73.3%) |
| Mean required group coverage | 74.4% | 80.6% |

These compare evidence available in the packet; they are not new dense Hit@5/MRR measurements and not answer accuracy. The packet size varies with dependencies/budget. The existing paragraph alignment remains `m3-paragraph-evidence-0.1`. The two targeted cases 004 and 010 now have all benchmark-required groups in their packets, but generation still does not reliably complete them.

Separate replay artifact: `data/pilot/context-evaluation/4fcb3397-4946-4cc5-a74d-a3b525fd86ac.json`.

## Live behavior and manual review

Five development scenarios were exercised with small metered runs and targeted repeats. Reports preserve failed attempts as well as later behavior. No answer-accuracy percentage is inferred from this small, tuned sample.

| Development case | Observed behavior and review |
|---|---|
| 001 — existing product invoicing policy | Answered. The final real browser answer correctly says existing products need manual updates, names Sales → Products → Products and General Information → Invoicing Policy, with exact supporting quotes and pinned links. Three final claims were checked against their displayed excerpts. |
| 004 — partial delivery/backorder/invoice | Initial provider timeout retained. An earlier model-reviewed answer included an ambiguous return-to-delivery screen transition, caught during inspection. Prompts now require precise action/screen order. Later checks safely rejected the draft or asked whether the shipment uses one/multiple packages. **This task is not accepted as reliably solved.** |
| 010 — physical return and partial credit | Initially missing credit-note evidence; the support policy repairs the measured group gap. Subsequent runs rejected a quote or abstained; the latest run returns insufficient evidence. **Still an unresolved generation/usefulness problem despite complete benchmark groups.** |
| 007 — ambiguous return | Asked whether the customer invoice was validated/sent and whether a refund is sought. Useful clarification observed before the final diagnostic-only additions. |
| 027 — actual stock availability | Returned insufficient evidence rather than inventing live warehouse data. Observed before the final diagnostic-only additions. |

Reports: initial direct check `66e2b5d3-8db2-4bf6-8263-5d207caeaa9e.json`; timeout `9d076c54-9ae5-4bc5-960a-be5e374430b9.json`; first low-reasoning four-case run `29ba2177-4930-4697-923b-6e45fc8927e2.json`; dependency/strict-review run `d618ebb6-2d68-4f97-bcad-287cfc42a34e.json`; latest workflow diagnostic run `232e7609-7e5a-4d94-81ce-f52a8d86e48c.json`, all under `data/pilot/smoke/`.

The model support reviewer missed an earlier screen-order issue. Citation existence and a second model pass cannot replace semantic review. The latest return and partial-delivery behavior shows a substantial false-abstention/clarification risk. Keep the pilot internal, inspect rejected drafts through operator export, and collect the actual operations task set before deciding on client use.

## Remaining work

Aarib confirmed Odoo 19-only coverage on 7 November 2026. Collect the real Odoo 19 task observations in `PILOT_PROTOCOL.md`. Diagnose the hard workflow false abstentions and review clarification follow-ups without weakening support/citation gates. Four of fifteen answerable development packets still lack a required group. No customer impact or time saving has been measured.

The broader M3 include-aware rebuild/publication, cross-file alignment/scoring, lifecycle reporting, window comparison and consolidated M3.1 acceptance remain unfinished. M4/M5 ranking research, cross-version support and broad M6/M9/M10 completion gates remain open. The pilot has no Odoo writes, uploads, enterprise identity administration, automatic data retention or distributed quotas/concurrency controls. The runbook/systemd candidate is prepared; no concrete external target has been reviewed or deployed.
