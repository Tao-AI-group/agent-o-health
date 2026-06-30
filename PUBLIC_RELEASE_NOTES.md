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
- Tests: `tests/test_corpus_reporting_completeness.py`.
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

## Pre-Submission Cleanup

Before creating the final public repository, consider renaming legacy file and class names that still use `reporting-completeness` to `reporting-completeness` for consistency with the manuscript terminology.

Recommended examples:

- `agento-reporting-completeness-profile.ttl` to `agento-reporting-completeness-profile.ttl`.
- `report:ReportingCompletenessProfile` to `report:ReportingCompletenessProfile`.
- Script/report labels that say `reporting completeness assessment` to `reporting completeness assessment`.

These renames should be done carefully because ontology URIs, SHACL profiles, scripts, and tests may need synchronized updates.
