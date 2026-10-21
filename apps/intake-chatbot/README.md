# AGENT-O Agent Card Intake Chatbot

An English-language, ontology-driven conversational intake application for
creating AGENT-O Agent Cards. It turns user-reported information into a
traceable structured draft, reports missing information, validates generated
RDF against AGENT-O SHACL profiles, and exports a review bundle.

The application assesses **reporting completeness and structural conformance**.
It does not assess agent quality, safety, clinical utility, regulatory
compliance, or deployment readiness.

## Features

- Conversational intake for existing, planned, or imported agent descriptions.
- Deterministic URI allow-list, patch, conflict, N/A, undo, and completeness logic.
- Separate Agent Card, agent system, clinical use, model component, model
  specification, model deployment, execution, evaluation, and policy entities.
- Per-assertion source message, evidence span, confidence, and review state.
- SQLite session persistence and explicit ontology-snapshot migration.
- Full AGENT-O SHACL validation with structured findings.
- Markdown, canonical JSON, JSON-LD, Turtle, validation report, and checksummed
  manifest export.
- Responsive React interface with session management and Card Inspector.
- Deterministic mock LLM by default and an opt-in institutional gateway adapter.

## Repository Layout

```text
Application: apps/intake-chatbot/
Read-only AGENT-O dependency: repository root
```

Ontology discovery and the application architecture are documented in
`docs/DISCOVERY_REPORT.md` and `docs/ARCHITECTURE.md`.

## Quick Start

Requirements: Python 3.11 or later and Node.js/npm.

```bash
cd apps/intake-chatbot
make bootstrap
make ontology-check
make test
make build
make run
```

The secure local default is `http://127.0.0.1:7860`. The default provider is
`mock`; no credential or network call is needed.

For an internal remote bind, create a non-committed `.env` and configure at
least:

```bash
APP_HOST=0.0.0.0
APP_PORT=7860
APP_ACCESS_TOKEN=<strong-random-token>
APP_DATA_DIR=/var/lib/agent-card-intake
AGENT_O_ROOT=/path/to/agent-o-health
```

Then run `make run APP_HOST=0.0.0.0`. A remote bind without an access token is
rejected unless `ALLOW_INSECURE_BIND=true` is explicitly set.

For the local Mayo credential store, the convenience launcher configures the
gateway, obtains and refreshes OAuth tokens automatically, and prints a one-click
browser sign-in link:

```bash
./scripts/run_mayo_server.sh
```

It defaults to `/home/m327768/my-codex/apis.jsonl`, credential alias `key1`,
model `gpt-5.6-luna`, and `0.0.0.0:7860`. Set `APP_PUBLIC_URL` to the URL clients
use (for example, `http://192.0.2.10:7860`) so the printed sign-in link is ready
to open. The URL fragment is removed from the address bar immediately and is
not sent in HTTP requests. Override any corresponding environment variable when
needed; credential values are never copied into the repository.

## Development

```bash
make dev
```

This starts FastAPI at `127.0.0.1:7860` and Vite at `127.0.0.1:5173`; Vite
proxies `/api` to the backend.

Useful checks:

```bash
make ontology-check
.venv/bin/python -m pytest
npm --prefix frontend run test
npm --prefix frontend run build
npm --prefix frontend run e2e
npm --prefix frontend audit
```

The institutional adapter has an opt-in synthetic smoke test. Configure the
approved gateway variables without committing them, then run:

```bash
RUN_LIVE_LLM_TESTS=1 make live-llm-smoke
```

Normal `make test` uses the mock provider and makes no network request.

Playwright uses the test-only `@sparticuz/chromium` package, so `make e2e` does
not depend on downloading a browser from the Playwright CDN. The packaged
browser is a development dependency and is not included in the production
frontend bundle.

## Documentation

- `docs/ARCHITECTURE.md`: components, data flow, and semantic boundaries.
- `docs/SECURITY.md`: trust boundaries, credential handling, and deployment controls.
- `docs/DEPLOYMENT.md`: local and internal-server deployment.
- `docs/USER_GUIDE.md`: intake, review, validation, and export workflows.
- `docs/TEST_PLAN.md`: automated and manual verification matrix.
- `docs/COMPLETION_AUDIT.md`: requirement-by-requirement evidence and pending human gates.
- `docs/ONTOLOGY_PROFILE_REVIEW_CHECKLIST.md`: frozen-snapshot expert review packet.
- `docs/PILOT_PROTOCOL.md`: deidentified internal pilot procedure and exit criteria.
- `docs/PILOT_RESULTS_TEMPLATE.md`: participant, task, rating, and finding record.
- `docs/FINAL_IMPLEMENTATION_REPORT.md`: current acceptance status.

## Important Data Rules

- Do not enter patient identifiers or PHI unless the deployment has received
  institutional approval for that use.
- Do not commit `.env`, credentials, `var/`, exports, logs, source papers, or
  message databases.
- Imported facts are untrusted candidates and remain Partial until a user
  confirms or edits them.
- Do not edit AGENT-O ontology files from this application repository.
