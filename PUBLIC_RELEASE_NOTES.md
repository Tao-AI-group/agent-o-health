# Public Release Notes

## Recommended GitHub Repository Name

Recommended name: `agent-o-health`

Rationale: the name is short, searchable, and clearly communicates that AGENT-O is scoped to health-oriented AI agent reporting rather than a universal ontology of all agents.

Alternative names:

- `agent-o`
- `agent-o-ontology`
- `agent-o-health-ai`
- `agento-health`

## Include In GitHub

- Ontology TTL files: `ontology/agento.ttl`, `ontology/modules/`, `ontology/profiles/`, and `ontology/alignments/`.
- Validation assets: `shapes/`, `queries/competency/`, and validation scripts under `scripts/`.
- Example RDF graphs: `data/examples/`.
- Sanitized corpus manifest: `data/manifest/paper_manifest_public.csv`.
- Aggregate outputs: `outputs/alignment/`, `outputs/validation/`, `outputs/shacl/`, `outputs/sparql/`, and selected `outputs/reporting_completeness/`.
- Manuscript support tables: `tables/`.
- Design documentation: `docs/design/`.
- Tests: deterministic corpus tests and ontology architecture contract tests under `tests/`.
- Project metadata: `README.md`, `pyproject.toml`, `requirements.txt`, `.gitignore`.
- License files: `LICENSE`, `LICENSE-CODE-MIT`, and `LICENSE-CONTENT-CC-BY-4.0`.

## Do Not Include In GitHub

- Full paper markdown files or extracted paper full text.
- Raw LLM prompts or raw LLM responses.
- Institution-specific API endpoints, credentials, or token logic.
- Local absolute file paths.
- Third-party ontology source downloads under `data/external/`, unless their licenses are checked and redistribution is explicitly allowed.
- Python cache directories such as `__pycache__/`.
- Dummy Protege screenshot TTL files, unless they are explicitly released as figure-generation utilities.

## Architecture Revision

The architecture revision separates model roles within an agent system from identifiable model specifications and runtime deployments. It also promotes clinical intended use to a first-class health concept, distinguishes model-interface output from final agent output, represents reporting assessment as a provenance-aware activity, and separates concrete agent-system reports from benchmark, review, policy, method/model, and conceptual reports.

The included application profiles now check model identity, version, architecture, developer, license, input/output interfaces, modality, capability, model-level intended use, limitations, deployment provenance, clinical intended action, and FHIR profile/format/terminology evidence. All architecture, governance, and reporting SHACL suites conform with zero findings over the released example graphs.

Deprecated compatibility entities remain labeled with `owl:deprecated true`; active entity counts exclude them. The integrated ontology is generated from the six authoritative modules and checked for graph equivalence during formal validation.
