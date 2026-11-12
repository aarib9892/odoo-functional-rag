# Odoo Fieldguide — internal RAG pilot

A restricted browser assistant for the selected **Odoo 19 English Sales and Inventory documentation**: 30 pages and 205 indexed chunks. One Accounting page supports customer returns/refunds. Odoo 19 is the confirmed product version scope; other versions are deferred. The external hosting target still needs selection.

The pilot reuses the existing query embedding cache and exact pgvector K=5 retriever. It adds bounded support passages for two observed workflow gaps, structured answers, server-validated citation IDs and verbatim quotes, a separate model support/completeness review, session isolation and task feedback. A model review does not establish factual correctness; internal operations review is still required.

**Full-application expansion is prepared separately:** all 944 pages have passed offline normalization and chunk preparation, producing 11,926 chunks. The current 30-page release remains active. New embeddings and live candidate evaluation await a user-chosen spending cap; candidate activation also requires human review. See [full-corpus preparation, estimate and release steps](docs/FULL_CORPUS.md).

## Run locally

Requirements: Python 3.12+, uv, Node 18.19+ (Node 22 recommended for a new machine), npm, and the existing project PostgreSQL/pgvector database. Existing provider/database secrets remain in `backend/.env`.

From the repository root, start the existing database if stopped:

```bash
docker compose --env-file backend/.env -f compose.db.yaml start db
cd frontend
npm ci
npm run build
cd ../backend
uv sync --frozen --group parser-spike --group pilot-test
uv run python -m app.pilot.configure
uv run python -m app.pilot
```

Open **http://localhost:8000**. Sign in with the `operations` key in `backend/.env.pilot`. All browser questions automatically use Odoo 19; the interface shows a fixed version label with no version selector. `configure` creates private random access/operator keys only if that file is absent, and never overwrites existing secrets. It was run during this implementation. No keys are embedded in browser assets or stored in localStorage.

`backend/.env.example` describes configuration without secrets. The model uses `PILOT_GENERATION_MODEL`, then the existing `OPENAI_MODEL`, then `gpt-4.1-mini`. The checked environment uses `gpt-6-luna`, with low reasoning for the pilot; `PILOT_REASONING_EFFORT` can override it for a model that supports the setting. The API uses [structured Responses output](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses); [Luna supports low reasoning](https://developers.openai.com/api/docs/models/gpt-6-luna).

On a fresh project database, run `uv run python -m app.pilot.bootstrap` after starting the Compose database with `up -d db`. This applies the existing migration and imports **saved vectors**, without embedding calls. It refuses to replace another active snapshot. The `data/` artifacts and source checkout are ignored by Git: a new machine needs the accepted snapshot bundle or a verified copy/backup from this machine.

For frontend development, set `PILOT_PUBLIC_ORIGIN=http://localhost:5173` in `.env.pilot`, run the backend, then run `npm run dev` from `frontend`. Restore the origin to port 8000 when serving the built UI. Use one consistent hostname; origin and cookie boundaries deliberately reject other origins.

## Verify

```bash
cd backend
uv run --group parser-spike --group pilot-test python -m unittest discover -s tests -v
uv run --group parser-spike python -m app.pilot.evaluate_context
cd ../frontend
npm run build
npx playwright install chromium
npm test
```

Backend tests use synthetic retrieval/provider responses. Browser tests use the real UI, access/session store and endpoints with synthetic retrieval/generation; they do not call OpenAI or read holdout questions. The context evaluation replays all 23 frozen **development** retrieval results through the actual context builder without provider calls. It writes a separate report in `data/pilot/context-evaluation/` and does not alter the baseline or benchmark.

Optional **metered live check**, from `backend`: `uv run python -m app.pilot.smoke --limit 1`. Maximum five fixed development cases; two bounded generation calls per answered case, one for an abstention, and cached query embeddings where available. Reports go to `data/pilot/smoke/`. This is a smoke check, not an answer-accuracy evaluation. See [verified checks and known limitations](docs/PILOT_VERIFICATION.md).

## Use and review

Ask a task, expand its cited passages, and check the versioned documentation or commit-pinned source. The source link preserves the indexed text; rendered documentation can change. Unsupported versions, missing conditions and insufficient evidence produce an explicit non-answer. Conversation questions clarify intent and never become trusted source evidence. The assistant has no live Odoo connection or actions.

Each response accepts **solved / partially solved / unresolved**, an optional correction, and optional task duration. History survives refresh within the same browser session. Signing out and signing back in creates a new isolated session; old activity stays available only to the operator export. Removing or rotating a person's access key revokes their existing sessions on the next request.

Run `uv run python -m app.pilot.export --output ../data/pilot/review.jsonl` from `backend` to review request-linked answers, evidence, feedback, latency and model/token usage. The export CLI calls the operator-authenticated HTTP endpoint without placing the key in shell arguments. See the [deployment and rollback runbook](docs/PILOT_RUNBOOK.md) and the [internal observation protocol](docs/PILOT_PROTOCOL.md).
