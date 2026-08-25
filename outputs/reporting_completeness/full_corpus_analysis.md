# Full-Corpus Reporting-Completeness Analysis

## Run Status

| Item | Value |
| --- | --- |
| Papers prepared | 279 |
| Papers assessed | 279 |
| Failures | 0 |
| Model | `gpt-5.1` |
| Rubric | `agento-reporting-completeness-2.2.3` |
| Prompt/workflow | `blinded-multi-evidence-2.2.3` |
| Assessment design | Label-blinded, section-aware, multi-evidence LLM assessment with targeted repair |
| Human calibration | Pending |

## Score Summary

| Metric | Value |
| --- | ---: |
| Mean | 63.7 |
| Median | 67.5 |
| Minimum | 0.0 |
| Maximum | 100.0 |

## Score Bands

| Score band | Count | Percent |
| --- | ---: | ---: |
| 0-49.9 | 39 | 14.0% |
| 50-64.9 | 72 | 25.8% |
| 65-79.9 | 130 | 46.6% |
| 80-89.9 | 23 | 8.2% |
| 90-100 | 15 | 5.4% |

## Dimension Labels

| Dimension | Present | Partial | Missing | Not applicable | Incomplete among applicable |
| --- | ---: | ---: | ---: | ---: | ---: |
| Runtime/architecture | 40 | 188 | 32 | 19 | 84.6% |
| Evaluation | 204 | 62 | 9 | 4 | 25.8% |
| Provenance/reproducibility | 61 | 189 | 28 | 1 | 78.1% |
| Governance/safety | 48 | 176 | 55 | 0 | 82.8% |
| Benchmark-process alignment | 191 | 68 | 13 | 7 | 29.8% |

## Paper-Type Summary

| Paper type | Count | Mean | Median | Minimum | Maximum |
| --- | ---: | ---: | ---: | ---: | ---: |
| Agent system | 148 | 62.37 | 67.5 | 0 | 95 |
| Benchmark/evaluation framework | 39 | 71.86 | 77.5 | 35 | 90 |
| Conceptual/commentary | 5 | 81 | 80 | 70 | 100 |
| Governance/policy | 2 | 58.34 | 58.34 | 46.67 | 70 |
| Method/model | 73 | 61.06 | 65 | 22.5 | 90 |
| Survey/review | 12 | 63.16 | 70 | 0 | 93.33 |

## Evidence QA

| Check | Count |
| --- | ---: |
| Evidence items retained | 4692 |
| Retained items source-verified | 4692 |
| Invalid items dropped | 111 |
| Exact-subspan repairs | 1367 |
| Word-limit truncations | 348 |
| Evidence lists truncated | 574 |
| Deterministically derived locators | 4688 |
| Papers routed to human-review queue | 190 |

## Interpretation Boundary

These scores estimate publication-level reporting completeness under the AGENT-O rubric. They do not measure agent performance, clinical utility, correctness, fairness, safety, or deployment readiness. Prior score or label assignments were hidden from the LLM judge; the source-paper evidence itself was not blinded. All paper-level results have `human_verification_status=not_human_verified`, and the stratified human-calibration study remains pending. The files in this directory should therefore be interpreted as reproducible LLM-assisted estimates rather than a human-validated reference standard.

The public package excludes copyrighted full text, evidence quotations, raw prompts and responses, credentials, endpoint configuration, and local filesystem paths. `human_review_queue.csv` records cases selected by the workflow for subsequent manual review.
