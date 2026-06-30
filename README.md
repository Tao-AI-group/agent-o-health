# AGENT-O Health

AGENT-O is a modular OWL/RDF ontology framework for health-oriented AI agent reporting and ontology-guided reporting-completeness assessment.

This public release package contains the ontology, SHACL shapes, SPARQL competency queries, validation scripts, example RDF graphs, sanitized corpus manifest, and aggregate evaluation outputs used to support the AGENT-O manuscript.

## Repository Contents

- `ontology/`: integrated AGENT-O ontology, module files, application profiles, and external alignment files.
- `shapes/`: SHACL shapes for governance and reporting profiles.
- `queries/competency/`: SPARQL competency queries.
- `scripts/`: reproducibility scripts for ontology validation, SHACL validation, competency queries, alignment summaries, and reporting-completeness scoring.
- `data/examples/`: small RDF examples for provenance traces, health interoperability, and governance/reporting profiles.
- `data/manifest/paper_manifest_public.csv`: sanitized 279-paper manifest with paper identifiers, titles, paper types, and completeness scores.
- `outputs/`: aggregate validation, alignment, SHACL, SPARQL, and reporting-completeness results.
- `tables/`: manuscript-ready supplementary tables and corpus reference material.
- `docs/design/`: design notes and crosswalks to external resources.
- `tests/`: lightweight unit tests for deterministic corpus scoring.

## Quick Start

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run formal ontology checks:

```bash
python3 scripts/validate_ontology.py
```

Run SHACL profile validation:

```bash
python3 scripts/run_shacl_validation.py
```

Run competency queries:

```bash
python3 scripts/run_sparql_cqs.py
```

Run deterministic paper-level reporting-completeness scoring on a local markdown corpus:

```bash
python3 scripts/run_corpus_reporting_completeness.py --limit 0
```

## Public-Release Scope

This package intentionally does not include full-text paper markdown files, raw LLM prompts, raw LLM responses, API credentials, institution-specific API endpoints, or third-party ontology source files. The released corpus manifest is sanitized and does not include local filesystem paths.

Parsed and aggregate reporting-completeness outputs are included to support reproducibility of the manuscript tables without redistributing copyrighted source text.

## License

This repository uses a dual-license structure:

- Code under `scripts/`, `tests/`, and `pyproject.toml` is released under the MIT License.
- Ontology files, SHACL shapes, SPARQL queries, documentation, examples, manifests, tables, and aggregate outputs are released under CC BY 4.0.

See `LICENSE`, `LICENSE-CODE-MIT`, and `LICENSE-CONTENT-CC-BY-4.0`.

## Suggested Citation

Please cite the accompanying AGENT-O manuscript. A formal `CITATION.cff` file can be added after the manuscript title, author list, DOI, and version are finalized.
