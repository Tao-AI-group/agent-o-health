# Public Release Notes

## Current Public Snapshot

The repository contains the active six-module AGENT-O ontology and the completed v2.2.3 reporting-completeness outputs for 279 papers. The final automated run assessed all 279 records without request failures and produced a mean score of 63.7/100 and median score of 67.5/100.

The v2.2.3 workflow used `gpt-5.1`, rubric `agento-reporting-completeness-2.2.3`, and prompt/workflow `blinded-multi-evidence-2.2.3`. Prior paper scores and labels were hidden from the judge, while section-aware source-paper evidence was supplied. The released values are therefore described as label-blinded, LLM-assisted reporting-completeness estimates.

Human calibration is pending. All released paper-level records retain `human_verification_status=not_human_verified`, and 190 cases selected by the workflow are listed in `outputs/reporting_completeness/human_review_queue.csv`.

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

## Evaluation Artifacts

- All three SHACL suites conform with zero findings over the released example graphs.
- All 12 executable competency queries return their prespecified evidence types. Supplementary Tables S4A and S4B report the summary and per-query results.
- Supplementary Tables S6 and S7 report the final v2.2.3 score distribution and paper-type-stratified statistics.
- Supplementary Table S8 defines the weighted rubric, controlled labels, score calculation, and paper-type applicability rules.
- `outputs/reporting_completeness/run_metadata.json` records the sanitized model and workflow configuration.

## Architecture Revision

The architecture revision separates model roles within an agent system from identifiable model specifications and runtime deployments. It also promotes clinical intended use to a first-class health concept, distinguishes model-interface output from final agent output, represents reporting assessment as a provenance-aware activity, and separates concrete agent-system reports from benchmark, review, policy, method/model, and conceptual reports.

The included application profiles now check model identity, version, architecture, developer, license, input/output interfaces, modality, capability, model-level intended use, limitations, deployment provenance, clinical intended action, and FHIR profile/format/terminology evidence. All architecture, governance, and reporting SHACL suites conform with zero findings over the released example graphs.

Deprecated compatibility entities remain labeled with `owl:deprecated true`; active entity counts exclude them. The integrated ontology is generated from the six authoritative modules and checked for graph equivalence during formal validation.
