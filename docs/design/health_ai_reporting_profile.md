# AGENT-O Health AI Reporting and Reporting-Completeness Profile

Milestone 4 makes reporting guidelines usable as paper-completeness profiles. The profile distinguishes ontology coverage from paper-description completeness: AGENT-O may contain the terms needed to represent an agent, while a paper may still fail to describe some required dimensions.

## Reporting Profile

`ontology/profiles/agento-reporting-profile.ttl` defines the expected sections for an agent-system report:

| Reporting dimension | AGENT-O section |
| --- | --- |
| Agent identity and scope | `report:AgentIdentityScopeSection` |
| Runtime architecture | `report:RuntimeArchitectureSection` |
| Model components | `report:ModelComponentsSection` |
| Tool use and workflow | `report:ToolUseSection`, `report:WorkflowSection` |
| Planning and reasoning | `report:PlanningReasoningSection` |
| Input and output data | `report:InputOutputDataSection` |
| Clinical context | `report:ClinicalContextSection` |
| Evaluation datasets and metrics | `report:EvaluationReportingSection`, `report:DatasetsMetricsSection` |
| Equity and subgroup evaluation | `report:SubgroupEquityEvaluationSection` |
| Governance and human review | `report:GovernanceReportingSection`, `report:HumanReviewSection` |
| Risk, privacy, security, compliance | `report:RiskUncertaintySection`, `report:PrivacySecurityComplianceSection` |
| Deployment, monitoring, fallback | `report:DeploymentMonitoringSection`, `report:FailureFallbackSection` |
| Reproducibility | `report:ReproducibilitySection` |

The reporting profile cites MCRO, PROV-O, DUO, FHIR RDF, NIST AI RMF, and WHO health AI guidance as external guideline references.

## Reporting Completeness Assessment

`ontology/profiles/agento-reporting-completeness-profile.ttl` defines a smaller profile for checking whether papers describe their agents comprehensively enough for AGENT-O annotation. It uses `report:ReportingCompletenessAssessment` with controlled labels:

| Label | Meaning |
| --- | --- |
| `report:Present` | The paper provides enough information for the section. |
| `report:Partial` | The paper provides some information but leaves gaps. |
| `report:Missing` | The paper does not provide usable information for the section. |
| `report:NotApplicable` | The section is not applicable for the agent or paper. |

`shapes/agento-reporting-shapes.ttl` validates report structure and completeness-assessment records. `queries/competency/cq_reporting_gaps.rq` extracts partial and missing sections so they can be turned into a paper-facing gap report in Milestone 5.
