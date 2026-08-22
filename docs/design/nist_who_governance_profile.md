# AGENT-O NIST and WHO Governance Profile

Milestone 4 represents governance frameworks as profiles, SKOS concept schemes, competency queries, and SHACL constraints. The intent is not to import NIST AI RMF or WHO health AI guidance as strict ontologies, but to make their expectations operational for agent-paper annotation and ontology-guided reporting assessment.

## NIST AI RMF Alignment

`ontology/alignments/agento-align-nist-rmf.ttl` represents the four NIST AI RMF functions as AGENT-O governance concepts:

| NIST function | AGENT-O coverage |
| --- | --- |
| Govern | `gov:Policy`, `gov:AccountabilityRole`, `gov:AuditEvent`, `gov:HumanReviewRequirement`, `gov:AutomationLevel` |
| Map | `health:ClinicalUseCase`, `health:ClinicalSetting`, `health:PatientPopulation`, `health:HealthDataSource`, `gov:Risk` |
| Measure | `eval:EvaluationStudy`, `eval:Metric`, `eval:MetricResult`, `eval:SafetyMetric`, `eval:FailureCase`, `eval:BiasAssessment` |
| Manage | `gov:EscalationEvent`, `gov:FallbackStrategy`, `gov:MonitoringRule`, `gov:Incident`, `gov:OverrideAction` |

This supports checklist-style questions such as who is accountable, what automation level is allowed, which policy constrains the agent, what risks are identified, what metrics measure those risks, what triggers escalation, what fallback exists, and what monitoring applies after deployment.

## WHO Health AI Profile

`ontology/alignments/agento-align-who-health-ai.ttl` represents WHO health AI governance expectations as governance requirement classes:

| WHO-inspired requirement | AGENT-O term |
| --- | --- |
| Human autonomy | `gov:HumanAutonomyRequirement` |
| Transparency | `gov:TransparencyRequirement` |
| Explainability | `gov:ExplainabilityRequirement` |
| Equity | `gov:EquityRequirement` |
| Accountability | `gov:AccountabilityRequirement` |
| Safety | `gov:SafetyRequirement` |
| Privacy | `gov:PrivacyRequirement` |

The governance SHACL profile checks health-agent conditions that matter for biomedical use: intended audience, patient-facing output category, human review or override, PHI/privacy/compliance coverage, and fallback/escalation for high-risk agents.

## Validation Artifacts

- `ontology/profiles/agento-governance-profile.ttl` defines the governance profile.
- `shapes/agento-governance-shapes.ttl` turns the profile into executable warnings.
- `queries/competency/cq_governance_profile_checklist.rq` produces an agent-level governance checklist.
- `data/examples/governance_reporting_profile_example.ttl` demonstrates a governed clinical decision-support agent and an ontology-guided reporting-assessment POC case.
