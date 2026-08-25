# AGENT-O Health

AGENT-O is a modular OWL/RDF ontology framework for health-oriented AI agent reporting and ontology-guided reporting-completeness assessment.

This public package contains the ontology, SHACL shapes, SPARQL competency queries, validation scripts, example RDF graphs, a sanitized corpus manifest, and evaluation outputs used to support the AGENT-O manuscript. The current corpus outputs correspond to the completed v2.2.3 assessment of 279 papers (mean, 63.7/100; median, 67.5/100).

## Repository Contents

- `ontology/`: integrated AGENT-O ontology, module files, application profiles, and external alignment files.
- `shapes/`: SHACL shapes for agent/model architecture, governance, and reporting-assessment profiles.
- `queries/competency/`: SPARQL competency queries.
- `scripts/`: reproducibility scripts for ontology validation, SHACL validation, competency queries, alignment summaries, and reporting-completeness scoring.
- `data/examples/`: small RDF examples for provenance traces, health interoperability, and governance/reporting profiles.
- `data/manifest/paper_manifest_public.csv`: sanitized 279-paper manifest with paper identifiers, titles, paper types, and completeness scores.
- `outputs/`: validation, alignment, SHACL, SPARQL, and reporting-completeness results, including sanitized paper-level labels and run metadata.
- `tables/`: manuscript-ready supplementary tables, corpus reference material, and the model/clinical/reporting architecture crosswalk.
- `docs/design/`: design notes and crosswalks to external resources.
- `tests/`: unit tests for ontology architecture, competency-result serialization, and the deterministic baseline scorer.

## Quick Start

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run formal ontology checks:

```bash
python3 scripts/validate_ontology.py
```

Rebuild the integrated ontology from the six authoritative modules:

```bash
python3 scripts/build_integrated_ontology.py
```

Run SHACL profile validation:

```bash
python3 scripts/run_shacl_validation.py
```

Run competency queries:

```bash
python3 scripts/run_sparql_cqs.py
```

Run the deterministic keyword baseline on a local machine-readable paper corpus:

```bash
python3 scripts/run_corpus_reporting_completeness.py \
  --project-root /path/to/local-corpus-root \
  --output-root /path/to/output-directory \
  --limit 0
```

The local corpus root must follow the extraction-tree layout documented in `docs/design/corpus_collection_protocol.md`. This command runs the baseline scorer used during workflow development; it does not recreate the released v2.2.3 LLM-assisted scores. The released scores were produced with `gpt-5.1` using rubric `agento-reporting-completeness-2.2.3` and prompt/workflow `blinded-multi-evidence-2.2.3`. See `docs/design/reporting_completeness_v2_2_3.md`, `outputs/reporting_completeness/run_metadata.json`, and Supplementary Table S8 for the scoring specification and interpretation boundary.

## Public-Release Scope

This package intentionally does not include full-text paper markdown files, raw LLM prompts, raw LLM responses, API credentials, institution-specific API endpoints, or third-party ontology source files. The released corpus manifest is sanitized and does not include local filesystem paths.

Sanitized paper-level labels and aggregate reporting-completeness outputs are included to support verification of the manuscript tables without redistributing copyrighted source text. All released paper-level labels are marked `not_human_verified`; the planned stratified human-calibration study remains pending. The values are therefore LLM-assisted reporting-completeness estimates, not a human-validated reference standard.

The corpus was derived from the literature inventories accompanying two reviews of medical and healthcare AI agents, plus a prespecified AgentArena benchmark-alignment case. It is not presented as an independent systematic bibliographic-database search. See `docs/design/corpus_collection_protocol.md` for collection details and provenance limitations.

## License

This repository uses a dual-license structure:

- Code under `scripts/`, `tests/`, and `pyproject.toml` is released under the MIT License.
- Ontology files, SHACL shapes, SPARQL queries, documentation, examples, manifests, tables, and aggregate outputs are released under CC BY 4.0.

See `LICENSE`, `LICENSE-CODE-MIT`, and `LICENSE-CONTENT-CC-BY-4.0`.

## Suggested Citation

Please cite the accompanying AGENT-O manuscript. A formal `CITATION.cff` file can be added after the manuscript title, author list, DOI, and version are finalized.
