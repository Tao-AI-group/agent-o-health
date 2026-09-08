# Architecture

## Purpose

The application is an ontology-driven conversational state machine with an LLM
semantic parser and deterministic validator/exporter. The LLM proposes
candidate facts; it never owns the Card state or RDF graph.

## Runtime Flow

```text
Browser message or import
  -> size and file-type checks
  -> persist user message
  -> LLM candidate extraction (mock by default)
  -> strict Pydantic response validation
  -> field, subject, predicate, datatype, evidence-span, and URI checks
  -> transactional patch or complete candidate rollback
  -> recompute requirement, section, and dimension completeness
  -> deterministic next-question planner
  -> REST/SSE response
```

Validation and export follow a separate deterministic path:

```text
Persistent entities and active assertions
  -> RDFLib graph builder
  -> OWL-RL plus three AGENT-O SHACL shape suites
  -> structured validation result
  -> Markdown/JSON/JSON-LD/Turtle reports
  -> SHA-256 file manifest
  -> ZIP bundle
```

## Components

The backend is a FastAPI application under `backend/app`. SQLAlchemy stores
state in SQLite with WAL and foreign-key enforcement. RDFLib builds graphs;
pySHACL performs validation. The frontend is a React/TypeScript/Vite single-page
application under `frontend/src`.

`OntologyBundle` loads the integrated ontology, three profiles, and three shape
suites from the injected read-only AGENT-O root. It verifies required files,
creates a 555-URI allow-list, extracts 71 property constraints, hashes every
authoritative asset, and creates a snapshot ID. `IntakeCatalog` validates its 50
field mappings against that snapshot at startup.

## Semantic Boundaries

The deterministic entity registry preserves these distinct resources:

| Internal key | AGENT-O role |
| --- | --- |
| `report` | Agent Card/report that documents a system |
| `agent` | Health agent and agent system |
| `use_case` | System-level clinical intended use |
| `component` | Model component role in the workflow |
| `model_spec` | Identified and versioned AI model specification |
| `model_deployment` | Runtime endpoint, service, or checkpoint deployment |
| `execution` | A system execution run |
| `evaluation` | An evaluation study |
| `metric_result` | A metric result produced by an evaluation |
| `policy` | A governance policy that constrains the system |

System links among these entities are created deterministically. User or LLM
text cannot change their predicates or substitute an unknown ontology URI.

## Persistent State

- `SessionRecord`: profile, snapshot, workflow status, and current question.
- `MessageRecord`: user/assistant content and request status.
- `EntityRecord`: stable `urn:uuid` resource and AGENT-O type.
- `AssertionRecord`: value plus message/evidence/confidence/review provenance.
- `ApplicabilityRecord`: explicit N/A reason, source, and timestamp.
- `PatchEventRecord`: patch inverse, skip, N/A, undo, and migration history.
- `ValidationRunRecord`: immutable validation result for a snapshot.
- `ExportRecord`: local bundle path and manifest.
- `OntologySnapshotRecord`: hashes and profile catalog version.

Sessions are deleted on startup when their last update exceeds
`SESSION_RETENTION_DAYS`. Deletion cascades through local session data.

## Completeness, Conformance, and Readiness

These are intentionally independent:

1. Reporting completeness uses Present, Partial, Missing, and Not applicable at
   requirement and section level. The five weighted dimensions are secondary.
2. SHACL conformance is Not yet validated, Conformant, or Non-conformant and is
   based only on the latest validation run.
3. Review readiness is Draft, Needs user confirmation, or Ready for human review.

No result is an agent quality, safety, clinical utility, compliance, or
deployment-readiness score.

## Snapshot Lifecycle

Each new session stores the current ontology fingerprint. A session whose
fingerprint differs from the active snapshot displays a migration warning and
cannot validate or export. Explicit migration checks every active predicate
against the new allow-list, records a migration event, and then updates the
session fingerprint. Unknown terms require ontology-curator review.

## Concurrency Note

The MVP uses synchronous SQLAlchemy and pySHACL operations inside async route
handlers. This avoids the problematic worker-thread path observed in the test
cluster and is appropriate for a low-volume internal pilot. Full SHACL runs can
block the single process for several seconds. A production scale-out should
move validation/export to a bounded job worker and adopt an async or pooled
database architecture without changing the deterministic contracts.
