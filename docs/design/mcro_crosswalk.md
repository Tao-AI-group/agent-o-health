# MCRO Crosswalk

AGENT-O uses MCRO as the model-card reporting alignment target. MCRO should not replace AGENT-O's agent-system reporting layer because AGENT-O describes the full lifecycle of an agentic system, including tools, workflows, memory, reasoning, provenance, evaluation, human oversight, and governance.

The initial mapping uses real MCRO IRIs extracted from `data/external/mcro.ttl`.

| AGENT-O concept | MCRO target | Mapping type | Notes |
| --- | --- | --- | --- |
| `report:AgentSystemReport` | `obo:MCRO_0000001` Model Card Report | `skos:relatedMatch` | Agent-system reports are broader than model card reports. |
| `report:AgentCard` | `obo:MCRO_0000001` Model Card Report | `skos:relatedMatch` | Agent cards can contain or reference model card content. |
| `report:ModelCardReference` | `obo:MCRO_0000001` Model Card Report | `skos:closeMatch` | AGENT-O references MCRO model card reports. |
| `core:ModelComponent` | `obo:MCRO_0000021` Model Detail Section; `obo:MCRO_0000019` Model Architecture Information Section | `skos:relatedMatch` | MCRO represents model details as report sections; AGENT-O represents model components used by agents. |
| `report:EvaluationReportingSection` | `obo:MCRO_0000027` Performance Metric Information Section | `skos:closeMatch` | AGENT-O evaluation can include model, workflow, tool, and agent-level metrics. |
| `eval:Dataset` | `obo:MCRO_0000006`, `obo:MCRO_0000008`, `obo:MCRO_0000037` | `skos:relatedMatch` | MCRO distinguishes dataset, evaluation data, and training data sections. |
| `doc:License` | `obo:MCRO_0000016` License Information Section | `skos:closeMatch` | AGENT-O license metadata can be reported through MCRO-like sections. |
| `gov:Risk` | `obo:MCRO_0000033` Risk Information Section | `skos:closeMatch` | AGENT-O risks can include model, workflow, tool, data, and deployment risks. |
| `gov:PrivacyConstraint` | `obo:MCRO_0000028`, `obo:MCRO_0000034` | `skos:relatedMatch` | AGENT-O privacy constraints include PII/PHI and sensitive data use. |
| `report:IntendedUse` | `obo:MCRO_0000029`, `obo:MCRO_0000038` | `skos:closeMatch` | AGENT-O extends intended use with agent task and deployment context. |
| `report:IntendedUser` | `obo:MCRO_0000030`, `obo:MCRO_0000039` | `skos:closeMatch` | AGENT-O intended users can include patients, clinicians, researchers, and administrators. |

## Design Decision

No `owl:equivalentClass` mappings are used in the initial MCRO alignment. MCRO's scope is model-card reporting, while AGENT-O's reporting layer is agent-system reporting. The relationship is alignment and reuse, not semantic identity.

