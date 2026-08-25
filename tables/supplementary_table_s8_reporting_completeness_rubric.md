# Supplementary Table S8. AGENT-O rubric for paper-description completeness

## S8A. Weighted dimensions

| Dimension | Weight | Main reporting elements assessed |
| --- | ---: | --- |
| Runtime and architecture | 25% | Agent identity and scope; components and roles; workflow, planning, reasoning, memory, context, tools, execution environment; model identity, interfaces, capabilities, deployment; clinical intended use and boundaries |
| Evaluation | 25% | Datasets and tasks; baselines and comparators; metrics; results; uncertainty or variability; error or failure analysis |
| Provenance and reproducibility | 20% | Source data and provenance; execution trace or lineage; code, data, and artifacts; versions and configurations; environment and dependencies; access, license, and reproduction instructions |
| Governance and safety | 20% | Policy and accountability; human review and override; escalation and fallback; uncertainty, refusal, or abstention; risk and safety; privacy, security, compliance, ethics, bias, and fairness |
| Benchmark-process alignment | 10% | Runtime/evaluation separation; stepwise verification; validity and refusal handling; reliability; stability; cost or resources; task taxonomy and extensibility |

## S8B. Controlled labels and scoring

| Label | Fraction | Interpretation |
| --- | ---: | --- |
| Present | 1.0 | Most applicable subelements are reported with source-verified evidence and no major reporting gap. |
| Partial | 0.5 | Usable evidence is present, but one or more major applicable subelements remain insufficiently reported. |
| Missing | 0.0 | No sufficient source-verified evidence supports the applicable dimension. |
| Not applicable | Excluded | The dimension is outside the scope of the paper type or the paper's substantive contribution and is excluded from the denominator. |

`Total score = 100 * sum(weight * label fraction) / sum(weights of applicable dimensions)`.

## S8C. Applicability by paper type

| Paper type | Runtime | Evaluation | Provenance | Governance | Benchmark process |
| --- | --- | --- | --- | --- | --- |
| Agent system | Required | Required | Required | Required | Conditional |
| Benchmark/evaluation framework | Conditional | Required | Required | Required | Required |
| Survey/review | Not applicable | Required | Required | Conditional | Conditional |
| Governance/policy | Not applicable | Conditional | Required | Required | Conditional |
| Method/model | Required | Required | Required | Conditional | Conditional |
| Conceptual/commentary | Not applicable | Conditional | Conditional | Conditional | Conditional |

Conditional dimensions were scored only when the publication made a substantive contribution or claim in that area. Scores estimate publication-level reporting completeness and do not measure agent performance, clinical validity, safety, or deployment readiness. The v2.2.3 paper-level outputs have not yet completed human calibration.
