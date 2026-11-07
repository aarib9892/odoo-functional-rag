# Restricted pilot runbook

## Current launch boundary

Run on one host, one Uvicorn worker, behind a single origin. The backend serves the built UI and keeps provider keys server-side. The current runnable target is **localhost:8000 for internal review**. No external host/domain has been selected or deployed. The existing PostgreSQL container and its volume are reused; the pilot adds no ingestion jobs or Odoo connections.

Runtime data lives in `data/pilot/pilot.sqlite3` (sessions, request results, operator-only draft/review audits, feedback, persistent quotas) and the existing `data/embeddings/query-cache/`. SQLite is intentional for this small single-host pilot. Do not scale to multiple app processes/hosts: the two-request concurrency bound is process-local. Export contains questions and feedback; keep it private.

## Prepare a deployment for review

1. Identify the actual internal host, HTTPS origin, operator and named pilot cohort. Odoo 19.0 is the confirmed product scope; use the pilot with compatible Odoo 19 tasks and keep corpus expansion within that version. Agree on retention and the task observation protocol before collecting real client information.
2. Copy/build this repository with `uv sync --frozen --no-dev`, `npm ci` and `npm run build`. Restore the accepted snapshots and the existing pgvector database backup, or initialize only this project's empty database with `python -m app.pilot.bootstrap` using the saved chunk/embedding snapshots. That command refuses to replace another active index and never calls an embedding provider.
3. Keep `.env` and `.env.pilot` readable only by the service account. Generate unique access keys for each person and a separate operator key. `python -m app.pilot.configure` safely creates a local example with random keys. Set `PILOT_PUBLIC_ORIGIN=https://<reviewed-host>` and `PILOT_SECURE_COOKIE=true` for remote access. Settings reject remote HTTP or non-secure cookies.
4. Run the app on loopback behind the approved TLS reverse proxy. Preserve the Host and Origin headers; do not enable wildcard CORS. A candidate systemd user unit is in `deploy/odoo-pilot.service`; review paths/account first. The backend ignores forwarded headers, binds locally by default and accepts only the configured host. Restrict access at the proxy/network to the pilot cohort. A proxy should bound request bodies to 16 KiB and its upstream timeout to at least the configured 60-second application limit.
5. Verify `/health` (liveness only), then sign in and call `/api/ready` (database snapshot/chunk count and configured provider presence). Readiness does not make a billable provider request or guarantee provider availability. Run one small live smoke question, confirm its citations and export, and repeat unauthorized/cross-session tests on the reviewed target.
6. Complete the internal task review before deciding on a limited client cohort. External publication is a separate action requiring review of the concrete target; nothing here publishes or messages clients.

## Controls and operations

Access uses high-entropy named invitation keys exchanged for random HttpOnly, SameSite=Strict session cookies (eight-hour expiry). Only hashes of browser session tokens and access keys are stored in the database. No provider/admin key goes into the frontend. POST endpoints require the exact configured Origin, even for scripts; the operator export is a separate bearer-authenticated GET endpoint. API docs are disabled. There is no public registration or upload route.

Limits: 1,800 question characters, 16 KiB body, five answers per person/minute, 100/person/day and 500/day across the pilot by default, 30 feedback writes/person/minute, bounded login attempts, two concurrent answers, 45-second provider timeout and 60-second total answer timeout. Daily quotas count admitted attempts, including abstentions/failures; they are request limits rather than exact currency caps. Use provider account spending limits as well. Each answered request uses a draft plus support review; automatic provider retries are disabled. Timeouts/cancellation may still incur provider cost. Completed-stage usage is retained; unavailable provider usage is recorded as incomplete rather than guessed.

The fixed `pilot-support-passages-0.1` context policy adds up to three reviewed chunks from the **same published snapshot** for return/credit and backorder questions when relevant pages were retrieved. At most eight candidates fit into a 3,500-token evidence budget; passages are kept whole. It adds no provider embedding requests. The expected database/source snapshot is locked in settings. A different active index fails closed until the corpus, citations, support-policy IDs and evaluation are reviewed together.

To revoke a person, remove or rotate their key in `.env.pilot` and restart the app; their existing cookies then fail authentication. Rotate the operator key independently. Logs contain request IDs, outcome, duration and exception class, not exception messages or provider credentials. Use the operator export for structured usage, full evidence and rejected draft/review diagnostics; rejected drafts do not appear in ordinary history/API results.

## Backup, retention and rollback

Use SQLite's online backup API for a consistent running-store copy (copying the main file alone can miss WAL data). For example, from the repository root:

```bash
python3 - <<'PY'
from pathlib import Path
import os, sqlite3
os.umask(0o077)
source = Path('data/pilot/pilot.sqlite3')
target = Path('data/pilot/backups/pilot-before-release.sqlite3')
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists():
    raise SystemExit('Backup exists; choose a new name')
with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
    src.backup(dst)
PY
```

Back up the existing PostgreSQL volume through the project's normal database procedure. Keep accepted corpus artifacts, frozen benchmark/baseline and the release's code/build hashes. Do not include real `.env` files in a release artifact. Agree on retention before external use; the pilot does not yet auto-delete question/feedback history. Session expiry revokes access but does not erase operator review records.

Rollback: stop the pilot app/user service, preserve the SQLite backup and exports, restore the previous reviewed app/UI build, and start one worker with matching settings. If the first pilot release is unacceptable, leave the app stopped; ingestion/retrieval CLIs and the accepted index remain available. This implementation does not change the dense schema, published snapshot or original ingestion files. Never use `docker compose down -v`, reset the database, or discard the user's uncommitted ingestion work as a rollback step.

Store schema changes in a later release need an explicit migration before replacing the binary. This first pilot has its own new SQLite schema; do not point it at unrelated SQLite files.
