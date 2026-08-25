# AGENT-O Reporting-Completeness Assessment v2.2.3

## Purpose

The workflow estimates whether a publication reports enough information to
instantiate AGENT-O concepts. It assesses publication-level reporting
completeness, not agent performance, clinical utility, correctness, fairness,
safety, or deployment readiness.

## Run Configuration

| Item | Value |
| --- | --- |
| Papers assessed | 279 |
| Model | `gpt-5.1` |
| Rubric | `agento-reporting-completeness-2.2.3` |
| Prompt/workflow | `blinded-multi-evidence-2.2.3` |
| Assessment design | Label-blinded, section-aware, multi-evidence LLM assessment with targeted repair |
| Temperature | 0.0 |
| Reasoning effort | `none` |
| Maximum completion tokens | 4,800 |
| Maximum request attempts | 3 |
| Concurrent workers | 3 |
| Human calibration | Pending |

Label-blinded means that prior deterministic scores, prior dimension labels,
and prior paper-type labels were not shown to the judge. The paper evidence
itself was not blinded.

## Dimensions And Subelements

| Dimension | Weight | Controlled subelements |
| --- | ---: | --- |
| Runtime and architecture | 25% | Agent identity and scope; components and roles; workflow, planning, and reasoning; memory and context; tools and execution environment; model identity, version, and provider; model interfaces, capabilities, and outputs; model deployment; clinical intended use and boundaries |
| Evaluation | 25% | Datasets and tasks; baselines and comparators; metrics; quantitative or qualitative results; uncertainty or variability; error or failure analysis |
| Provenance and reproducibility | 20% | Source data and provenance; execution trace or lineage; code, data, and artifacts; versions and configurations; environment and dependencies; access, license, and reproduction instructions |
| Governance and safety | 20% | Governance policy and accountability; human review and override; escalation and fallback; uncertainty, refusal, or abstention; risk and safety; privacy and data protection; security; compliance, ethics, bias, or fairness |
| Benchmark-process alignment | 10% | Runtime/evaluation separation; stepwise or intermediate verification; validity and refusal handling; reliability; stability; cost or resource reporting; task taxonomy and extensibility |

## Labels And Score

Each applicable dimension receives `present` (1.0), `partial` (0.5), or
`missing` (0.0). `not_applicable` dimensions are removed from the denominator.
The total is:

`100 * sum(weight * label_fraction) / sum(applicable_weights)`

A `present` or `partial` label requires source-verified evidence linked to one
or more controlled subelements. Evidence quotations were limited to 25 words
and no more than four items per dimension. Deterministic post-processing
removed unsupported evidence, normalized subelement coverage, downgraded labels
when evidence did not support the claimed coverage, and never increased a
paper's score.

## Paper-Type Applicability

| Paper type | Runtime | Evaluation | Provenance | Governance | Benchmark process |
| --- | --- | --- | --- | --- | --- |
| Agent system | Required | Required | Required | Required | Conditional |
| Benchmark/evaluation framework | Conditional | Required | Required | Required | Required |
| Survey/review | Not applicable | Required | Required | Conditional | Conditional |
| Governance/policy | Not applicable | Conditional | Required | Required | Conditional |
| Method/model | Required | Required | Required | Conditional | Conditional |
| Conceptual/commentary | Not applicable | Conditional | Conditional | Conditional | Conditional |

Conditional dimensions are applicable only when the publication makes a
substantive contribution or claim in that dimension. This stratification
prevents non-system papers from being automatically penalized for not reporting
a concrete agent runtime.

## Quality Controls And Remaining Calibration

All 279 requests were assessed without failures. The technical gate confirmed
that no prior score, prior label, prior paper type, or reference-manifest entry
was present in the judge requests and that all retained evidence was verified
against the source text. The workflow routed 190 papers to a human-review queue
because of low confidence, paper-type uncertainty, evidence repair, or another
prespecified review trigger.

All public paper-level rows remain marked `not_human_verified`. Human review is
therefore a pending calibration study, not a completed validation result.
