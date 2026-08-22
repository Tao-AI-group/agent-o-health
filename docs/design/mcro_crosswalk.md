# MCRO Crosswalk

AGENT-O uses MCRO as the model-card reporting alignment target. MCRO should not replace AGENT-O's agent-system reporting layer because AGENT-O describes the full lifecycle of an agentic system, including tools, workflows, memory, reasoning, provenance, evaluation, human oversight, and governance.

The initial mapping uses real MCRO IRIs extracted from `data/external/mcro.ttl`.

| AGENT-O concept | MCRO target | Mapping type | Notes |
| --- | --- | --- | --- |
| `report:AgentSystemReport` | `obo:MCRO_0000001` Model Card Report | `skos:relatedMatch` | Agent-system reports are broader than model card reports. |
| `report:AgentCard` | `obo:MCRO_0000001` Model Card Report | `skos:relatedMatch` | Agent cards can contain or reference model card content. |
| `report:ModelCardReport` | `obo:MCRO_0000001` Model Card Report | `skos:closeMatch` | A model card is a document about a model specification, not the model resource itself. |
| `core:AIModelSpecification` | `obo:MCRO_0000021` Model Detail Section; `obo:MCRO_0000019` Model Architecture Information Section | `skos:relatedMatch` | AGENT-O represents the identifiable and versioned model resource; MCRO represents document sections describing it. |
| `core:ModelComponent` | MCRO model-role information | `skos:relatedMatch` | A model component represents a role within one agent system and remains distinct from model-card content. |
| `core:ModelInputSpecification`, `core:ModelOutputSpecification` | MCRO input/output information sections | `skos:closeMatch` | AGENT-O distinguishes model interfaces from agent-level health inputs and final outputs. |
| `report:EvaluationReportingSection` | `obo:MCRO_0000027` Performance Metric Information Section | `skos:closeMatch` | AGENT-O evaluation can include model, workflow, tool, and agent-level metrics. |
| `eval:Dataset` | `obo:MCRO_0000006`, `obo:MCRO_0000008`, `obo:MCRO_0000037` | `skos:relatedMatch` | MCRO distinguishes dataset, evaluation data, and training data sections. |
| `doc:License` | `obo:MCRO_0000016` License Information Section | `skos:closeMatch` | AGENT-O license metadata can be reported through MCRO-like sections. |
| `gov:Risk` | `obo:MCRO_0000033` Risk Information Section | `skos:closeMatch` | AGENT-O risks can include model, workflow, tool, data, and deployment risks. |
| `gov:PrivacyConstraint` | `obo:MCRO_0000028`, `obo:MCRO_0000034` | `skos:relatedMatch` | AGENT-O privacy constraints include PII/PHI and sensitive data use. |
| `core:ModelIntendedUse` | `obo:MCRO_0000029`, `obo:MCRO_0000038` | `skos:closeMatch` | Model-level intended use remains distinct from the clinical use of an entire agent system. |
| `health:ClinicalUseCase` | MCRO intended-use sections | `skos:relatedMatch` | Clinical use adds user, population, setting, specialty, condition, workflow stage, task, intended action, decision role, deployment mode, and excluded or prohibited use. |
| `health:IntendedUserRole` | `obo:MCRO_0000030`, `obo:MCRO_0000039` | `skos:closeMatch` | Intended users can include patients, clinicians, researchers, and administrators. |

## Design Decision

No `owl:equivalentClass` mappings are used in the initial MCRO alignment. MCRO's scope is model-card reporting, while AGENT-O's reporting layer is agent-system reporting. The relationship is alignment and reuse, not semantic identity.
