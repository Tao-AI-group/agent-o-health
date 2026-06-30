# Full-Corpus LLM Reporting-Completeness Analysis

## Run Status

| Item | Value |
| --- | --- |
| Papers prepared | 279 |
| Papers judged | 279 |
| Failures | 0 |
| Provider | apigee_azure_openai |
| Model | gpt-5.1 |

## Score Distribution

| Metric | Value |
| --- | --- |
| Mean | 78.66 |
| Median | 85.00 |
| Minimum | 22.5 |
| Maximum | 100.0 |
| Perfect-score papers | 34 |

## Score Bands

| Band | Count | Percent |
| --- | --- | --- |
| 0-49.9 | 15 | 5.4% |
| 50-64.9 | 50 | 17.9% |
| 65-79.9 | 51 | 18.3% |
| 80-89.9 | 67 | 24.0% |
| 90-100 | 96 | 34.4% |

## Dimension Labels

| Dimension | Present | Partial | Missing | N/A | Partial+Missing |
| --- | --- | --- | --- | --- | --- |
| Runtime/architecture | 187 | 80 | 3 | 9 | 29.7% |
| Evaluation | 240 | 33 | 6 | 0 | 14.0% |
| Provenance/reproducibility | 161 | 112 | 6 | 0 | 42.3% |
| Governance/safety | 95 | 164 | 20 | 0 | 65.9% |
| Benchmark-process alignment | 77 | 179 | 14 | 9 | 69.2% |

## Paper-Type Summary

| Paper type | Count | Mean | Median | Min | Max |
| --- | --- | --- | --- | --- | --- |
| agent_system | 216 | 77.65 | 85.00 | 22.5 | 100.0 |
| benchmark | 48 | 78.07 | 78.75 | 47.5 | 100.0 |
| governance_policy | 3 | 88.33 | 85.00 | 85.0 | 95.0 |
| survey_review | 11 | 97.95 | 100.00 | 82.5 | 100.0 |
| method_model | 1 | 85.00 | 85.00 | 85.0 | 85.0 |

## Lowest-Scoring Papers

| Score | Type | Paper | Labels |
| --- | --- | --- | --- |
| 22.5 | agent_system | Agentic AI Medical Morality and the Transformation of the Patient-Physician Relationship | partial/missing/missing/partial/missing |
| 22.5 | agent_system | Coordinated AI agents for advancing healthcare | partial/missing/missing/partial/missing |
| 32.5 | agent_system | MedBuild AI An Agent-Based Hybrid Intelligence Framework for Reshaping Agency in Healthcare Infr | partial/missing/partial/partial/missing |
| 35.0 | agent_system | AI-VAXGUIDE AN AGENTIC RAG-BASED LLM FOR VACCINATION DECISIONS | partial/partial/partial/missing/missing |
| 35.0 | agent_system | Agent AI with LangGraph A Modular Framework for Enhancing Machine Translation Using Large Langua | partial/partial/partial/missing/missing |
| 35.0 | agent_system | AgentMRI A Vison Language Model-Powered AI System for Self-regulating MRI Reconstruction with Mu | partial/partial/partial/missing/missing |
| 37.5 | agent_system | AI agent in healthcare applications evaluations and future directions | missing/partial/missing/present/partial |
| 40.0 | agent_system | Rx Strategist Prescription Verification using LLM Agents System | partial/partial/partial/missing/partial |
| 40.0 | agent_system | SynthAgent A Multi-Agent LLM Framework for Realistic Patient Simulation - A Case Study in Obesit | partial/partial/partial/missing/partial |
| 40.0 | agent_system | TOWARDS NEXT-GENERATION MEDICAL AGENT HOW 01 IS RESHAPING DECISION-MAKING IN MEDICAL SCENARIOS | partial/partial/missing/partial/partial |
| 42.5 | agent_system | AGENTIC AI GOVERNANCE AND LIFECYCLE MANAGEMENT IN HEALTHCARE | partial/missing/partial/present/missing |
| 42.5 | agent_system | Engineering AI Agents for Clinical Workflows A Case Study in Architecture MLOps and Governance | partial/missing/partial/present/missing |
| 45.0 | agent_system | An Agentic AI Framework for Training General Practitioner Student Skills | partial/partial/partial/partial/missing |
| 45.0 | agent_system | Many-to-One Adversarial Consensus Exposing Multi-Agent Collusion Risks in AI-Based Healthcare | partial/partial/partial/partial/missing |
| 47.5 | benchmark | Medical Malice A Dataset for Context-Aware Safety in Healthcare LLMs | partial/missing/partial/present/partial |
| 50.0 | agent_system | Agentic Reasoning for Large Language Models | partial/partial/partial/partial/partial |
| 50.0 | agent_system | Application of MATEC Multi-AI Agent Team Care Framework in Sepsis Care | partial/partial/partial/partial/partial |
| 50.0 | agent_system | From Chatbots to Agentic Workflows Ensuring Responsible Deployment of Large Language Models in R | partial/partial/missing/present/partial |
| 50.0 | agent_system | HEAL-KGGen A Hierarchical Multi-Agent LLM Framework with Knowledge Graph Enhancement for Genetic | partial/partial/partial/partial/partial |
| 50.0 | agent_system | LLM-based agentic systems in medicine and healthcare | partial/partial/missing/present/partial |

## Main Interpretation

- The full run succeeded technically: every paper was judged and every raw response was retained for audit.
- Evaluation reporting is comparatively strong: 240/279 papers are `present` on the evaluation dimension.
- Governance/safety is the largest substantive reporting gap: only 95/279 are `present`, while 164 are `partial` and 20 are `missing`.
- Benchmark-process alignment is the second major gap: only 77/279 are `present`; most papers do not fully separate runtime from evaluation or report validity/refusal, reliability, stability, and cost.
- Provenance/reproducibility is mixed: 161/279 are `present`, but 112 are `partial`, usually because code, model/data versions, lineage, or artifact release details are incomplete.
- Survey/review papers score high because runtime and benchmark-process dimensions are often not applicable; low-scoring papers are usually conceptual agent papers or papers that describe a system idea without empirical evaluation or reproducibility details.

## Recommended Next Steps

1. Manually audit 10-15 low-scoring papers to calibrate whether the LLM judge is too strict or correctly identifying incomplete descriptions.
2. Add a calibration layer comparing deterministic labels against LLM labels; use LLM judgments as the main score and deterministic scores as a cheap triage baseline.
3. Convert recurring gaps into an AGENT-O reporting checklist for paper annotation: governance, provenance, benchmark separation, refusal/validity handling, reliability/stability, and cost.
4. Use the full-corpus output to propose ontology refinements only after repeated gaps indicate missing AGENT-O terms rather than missing paper descriptions.
