# Test Plan

## Test Principles

Tests use the deterministic mock LLM and synthetic, non-PHI content by default.
Ontology source files are read-only. Live gateway tests require explicit opt-in
and must never transmit a real Card, paper, patient data, or credential value.

## Automated Commands

```bash
make ontology-check
make secret-scan
make test
npm --prefix frontend run test
npm --prefix frontend run build
npm --prefix frontend run e2e
npm --prefix frontend audit
```

## Backend Coverage

The current pytest suite covers:

- Real ontology/profile/shape load, fingerprint, and field catalog.
- SHACL-backed catalog provenance and ontology/question fallback generation.
- Health, profile, SPA, and security headers through the ASGI application.
- Session creation, persistence, message extraction, evidence, and next question.
- Conflicting values, explicit correction, and undo.
- N/A reason, skip history, unknown field, and datatype rejection.
- Strict extraction schema and ontology URI allow-list.
- LLM patch rollback while preserving the user's message.
- Imported candidate confirmation and prompt-like imported instructions.
- Sparse-card conformant-export rejection.
- Complete 50-field card, OWL-RL/SHACL conformance, and seven-file ZIP export.
- JSON-LD and Turtle parsing plus manifest checksum verification.
- Access-token protection, remote-bind guard, import type/size limits, and redaction.
- Explicit ontology snapshot migration and stale-snapshot export/validation block.
- Startup session retention.
- One-time LLM schema repair and failure after an invalid repair.
- SSE patch/token/done protocol, gateway outage persistence, and finite retry.

## Frontend Unit Coverage

Vitest/testing-library verifies the reporting-quality boundary and all three
first-run modes. Additional interaction behavior is covered by the Playwright
scenario rather than duplicating the browser workflow in jsdom.

## Playwright Scenario

`frontend/tests/intake.spec.ts` runs at desktop `1440x900` and mobile `390x844`.
It covers session creation and rename, SSE chat, Inspector edit, sparse
validation, draft download, reload/resume, horizontal-overflow check,
screenshot capture, session deletion, and keyboard-only session
creation/message submission. A controlled delayed-response scenario verifies
that `Stop response` aborts an active browser request without losing the user
message already persisted by the backend. The suite uses
one worker because both viewport projects share one isolated test database.

The institutional VPC rejected the Playwright CDN browser download, so the test
configuration uses the test-only `@sparticuz/chromium` package. On 2026-09-04,
all six project/test combinations passed: the primary, keyboard, and stop
workflows at both desktop and mobile viewports.

## Manual Browser Review

For desktop and mobile, verify:

1. No clipped or overlapping text, buttons, drawers, modals, or Inspector content.
2. Keyboard tab order, visible focus, Enter-to-send, Shift+Enter, and Escape/close behavior.
3. English-only visible content and no OpenAI branding.
4. CSP console has no blocked application style/script errors.
5. Stop and retry preserve the session after simulated failure.
6. Long names, evidence, and ontology labels wrap without shifting fixed controls.
7. Imported candidate review is understandable.
8. Draft and conformant export choices produce the expected result.

The saved successful desktop and mobile screenshots were manually inspected on
2026-09-04. Both were nonblank, correctly framed, and free of incoherent
overlap or horizontal page overflow. The mobile screenshot correctly showed
the Inspector as a full-height drawer over a scrim.

## Optional Live Test

Run only after gateway settings and authorization are confirmed:

```bash
RUN_LIVE_LLM_TESTS=1 make live-llm-smoke
```

`backend/tests/test_live_llm.py` sends one short synthetic agent name and checks
for schema-valid output, exact source evidence, and ontology allow-list
membership. It passed against an approved institutional gateway on 2026-09-04. Normal
`make test` excludes this test and makes no network request.
