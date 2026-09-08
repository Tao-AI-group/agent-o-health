# Implementation and Acceptance Report

**Report date:** 2026-09-04
**Application version:** 0.1.0
**Status:** Verified functional MVP; internal pilot and deployment-owner
configuration remain.

## Implemented

- Real AGENT-O discovery and immutable snapshot fingerprinting.
- English-only React intake interface with desktop and mobile layouts.
- Session create, list, restore, rename, archive status, delete, and retention.
- Conversational mock and institutional-gateway LLM adapters.
- Strict extraction schema, evidence checks, URI allow-list, datatype checks,
  conflict handling, correction, N/A, skip, undo, and transactional rollback.
- Requirement, section, and five-dimension reporting completeness.
- Separate SHACL conformance and review readiness.
- Explicit stale-snapshot migration before validation/export.
- Deterministic RDF graph and all required export formats.
- Draft versus conformant export enforcement and per-file checksums.
- Access-token gate, remote-bind guard, CSP, sanitized Markdown, import limits,
  secret redaction, and safe defaults.
- README, architecture, security, deployment, user, testing, discovery, and
  handoff documentation.

## Verification Evidence

At the time of this report:

| Verification | Result |
| --- | --- |
| AGENT-O discovery | Passed: snapshot `15ae2eaf5e674114`, 1,962 triples, 71 constraints, 555 URIs |
| Backend pytest | Passed: 22 default tests; 1 live test excluded by default |
| Frontend Vitest | Passed: 2 tests |
| TypeScript/Vite production build | Passed: 1,746 modules |
| npm audit | Passed: 0 vulnerabilities |
| Source-tree secret scan | Passed: 80 candidate files; values never displayed |
| English visible-source scan | Passed: no Han characters in frontend source |
| Complete synthetic Agent Card | Passed SHACL with no findings |
| Sparse synthetic Agent Card | Correctly rejected as conformant export |
| Playwright test implementation | Complete for desktop and mobile |
| Playwright execution | Passed: 6/6 desktop/mobile primary, keyboard, and stop workflows, including rename and reload persistence |
| Live institutional LLM smoke | Passed: 1 synthetic, non-PHI structured-extraction test |
| Single-port HTTP smoke | Passed: health, SPA, create, SSE message, assertion, and delete |
| Authenticated remote-bind smoke | Passed: health 200, private API 401 without token and 200 with token |
| Manual screenshot review | Passed: desktop and mobile nonblank, framed, and without incoherent overlap; desktop session actions remain visible at 1440 x 900 |

The single pytest warning is an upstream RDFLib JSON-LD parser deprecation
warning and does not indicate invalid output.

## Acceptance Boundary

The code implements the requested vertical slice and its deterministic
contracts. Browser E2E, manual screenshot review, and the live LLM path have
been verified. Mock mode remains the safe default and is used by the normal
test suite. Deployment approval, pilot-user configuration, and any PHI-capable
use remain operational decisions outside this software verification.

## Remaining Actions

1. Configure the internal service, TLS/authentication, retention, and pilot users.
2. Conduct 3-5 deidentified user pilots and record usability feedback before a
   broader internal rollout using `docs/PILOT_PROTOCOL.md` and
   `docs/PILOT_RESULTS_TEMPLATE.md`.
