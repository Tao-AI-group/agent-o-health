# Product-Spec Completion Audit

**Audit date:** 2026-09-05
**Audit introduced:** `76d7c2e`; record the current HEAD at formal acceptance
**AGENT-O snapshot:** `15ae2eaf5e674114`

This audit maps the application's implementation requirements to current
authoritative evidence. A passing software check is not used to claim that a
human review or pilot has occurred.

## Acceptance Requirements

| Requirement | Status | Evidence |
| --- | --- | --- |
| Browser service can bind to `0.0.0.0:${APP_PORT}` | Verified | Authenticated runtime smoke on `0.0.0.0:7861`: health 200, private API 401 without token and 200 with token; bind guard test in `backend/tests/test_contracts.py` |
| Create, restore, rename, and delete sessions | Verified | Desktop/mobile primary Playwright workflow in `frontend/tests/intake.spec.ts` |
| Streaming conversation | Verified | SSE protocol backend test and desktop/mobile Playwright message workflow |
| Stop an active response | Verified | Controlled delayed-response Playwright scenario verifies abort, no error alert, and persisted input after reload |
| Load ontology, profile, and shapes from real AGENT-O | Verified | `scripts/inspect_ontology.py --check`, discovery report, and loader/catalog tests |
| Pin each session to an ontology snapshot/hash | Verified | Snapshot model, API tests, and stale-snapshot migration test |
| Drive requirements primarily from profile/SHACL | Verified | SHACL-backed catalog contract and fallback tests; 24 direct SHACL-backed and 26 profile-backed fields |
| Preserve key ontology entity boundaries | Verified | Separate entities in database/exporter and complete-card RDF assertions in backend tests |
| Preserve assertion source, evidence, confidence, and review state | Verified | Assertion model plus message, import, and complete-card tests |
| Enforce strict LLM schema and URI allow-list | Verified | Schema/allow-list tests, malformed-response repair tests, and synthetic live smoke |
| Display Present, Partial, Missing, and N/A | Verified | Deterministic completeness engine, API tests, and Inspector UI |
| Require an N/A reason and source | Verified | Applicability endpoint and `test_not_applicable_skip_history_and_unknown_field` |
| Separate completeness from SHACL conformance | Verified | Service contracts, UI status panel, and complete/sparse tests |
| Do not display agent quality, safety, or readiness scores | Verified | English source scan, UI boundary tests, and visible boundary notices |
| Run full SHACL validation | Verified | Three loaded shape suites and complete/sparse validation tests |
| Export Markdown, JSON, JSON-LD, Turtle, and validation reports | Verified | Seven-file ZIP export test with parsing and checksum verification |
| Complete golden example conforms | Verified | `test_complete_card_validates_and_exports_all_formats` |
| Sparse example produces the correct next question | Verified | Sparse message/planner API test and primary browser workflow |
| Keep credentials out of code, logs, frontend, fixtures, and Git | Verified for current tree/history | Non-disclosing source-tree scan, `.gitignore`, runtime-only adapter, redaction tests, and reviewed local history |
| Do not log raw prompts/responses by default | Verified | `LOG_MESSAGE_CONTENT=false`, logging/redaction design, and security documentation |
| Backend, frontend, and Playwright tests pass | Verified | 22 default backend tests, 2 frontend tests, and 6/6 desktop/mobile E2E tests |
| README, architecture, security, deployment, and user guide complete | Verified | Files under `docs/` and README documentation index |
| Bootstrap, test, build, and run are reproducible | Verified | Clean `make bootstrap`; repeated `make test` and `make e2e`; current `make run` health and SPA GET smoke |

## Milestone Exit Conditions

| Exit condition | Status | Required next evidence |
| --- | --- | --- |
| Ontology expert or project owner reviews the discovered profile map | Pending external review | Complete and sign `ONTOLOGY_PROFILE_REVIEW_CHECKLIST.md` against the recorded snapshot |
| Sparse, ambiguous, governance-gap, N/A, conflict, injection, outage, and migration scenarios pass | Verified | Backend tests and E2E suite |
| Complete card produces a conformant export and incomplete card reports issues | Verified | Backend complete/sparse export tests and browser validation workflow |
| Three to five real, deidentified pilot use cases are completed | Pending external pilot | Execute `PILOT_PROTOCOL.md` and freeze `PILOT_RESULTS_TEMPLATE.md` |
| An internal user without ontology expertise independently completes a Card | Pending external pilot | Participant-level completion record with no step-by-step assistance |
| No secret leakage or blocker bug appears during pilot | Pending external pilot | Pilot privacy checklist and triaged findings |

## Current Decision

The software implementation is a verified functional MVP and is running in
safe local mock mode. Formal project completion remains unproven until the
profile-map review and deidentified internal pilot exit conditions are met.
