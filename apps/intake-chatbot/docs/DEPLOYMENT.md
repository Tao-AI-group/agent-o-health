# Deployment Guide

## Prerequisites

- Linux host with Python 3.11+ and Node.js/npm.
- Read-only access to a validated AGENT-O checkout.
- A writable application data directory.
- An approved internal port and TLS reverse proxy for shared use.
- An access token or stronger upstream authentication for any remote bind.

## Install and Verify

```bash
cd /path/to/agent-card-intake-chatbot
make bootstrap
make ontology-check
make test
make build
```

The E2E suite uses a packaged test-only Chromium runtime:

```bash
make e2e
```

No browser binary is included in the production frontend bundle or required by
the running application.

## Local Run

```bash
make run
```

Open `http://127.0.0.1:7860`. Runtime data is written to `./var` unless
`APP_DATA_DIR` is changed.

## Internal Server Configuration

Place a protected environment file outside the repository, mode `0600`:

```bash
APP_HOST=0.0.0.0
APP_PORT=7860
APP_ENV=production
APP_COMMIT=<deployed-git-commit>
APP_DATA_DIR=/var/lib/agent-card-intake
APP_ACCESS_TOKEN=<strong-random-token>
ALLOW_INSECURE_BIND=false
SESSION_RETENTION_DAYS=90
AGENT_O_ROOT=/opt/agent-o
LLM_PROVIDER=mock
LOG_MESSAGE_CONTENT=false
RESEARCH_MODE=false
```

For an approved live gateway, add the values listed in `docs/SECURITY.md`. Do
not include credentials directly in a systemd unit or shell history.

Start the production bundle with:

```bash
scripts/start_server.sh
```

The script rejects an unauthenticated remote bind and runs the ontology check
before Uvicorn starts.

## systemd Example

`deploy/agent-card-intake.service.example` provides a hardened baseline. Adapt
the service user, installation path, environment-file path, and writable data
directory. Build the frontend before enabling the service.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now agent-card-intake.service
sudo systemctl status agent-card-intake.service
```

Use an institutional reverse proxy for TLS, request-size limits, access logs
without body capture, and stronger identity management. Do not expose Uvicorn
directly to the public internet.

## Health and Operations

```bash
curl -fsS http://127.0.0.1:7860/api/health
```

The endpoint checks the database and reports loaded ontology/profile state. It
does not call the live LLM or return endpoint/credential data.

Back up the SQLite database only under the approved data policy. WAL mode may
create `-wal` and `-shm` files; use a SQLite-aware backup procedure. Session
delete removes local records, and startup retention removes sessions older than
`SESSION_RETENTION_DAYS`. Review export-directory retention separately.

## Upgrade Procedure

1. Stop intake traffic and back up approved local state.
2. Install the new application revision and dependencies.
3. Run ontology check, backend tests, frontend tests, build, and E2E where a
   browser is available.
4. Set `APP_COMMIT` to the deployed revision.
5. Restart and inspect `/api/health`.
6. Existing sessions with an earlier ontology fingerprint will show a migration
   banner and cannot validate/export until a user explicitly migrates them.

## Rollback

Restore the prior application revision and its compatible ontology checkout.
Do not rewrite session snapshot IDs manually. Preserve the database before any
schema migration; the MVP currently creates tables directly and does not yet
include Alembic migrations.
