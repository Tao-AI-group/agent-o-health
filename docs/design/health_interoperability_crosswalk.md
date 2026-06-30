# Health Interoperability Crosswalk

Milestone 3 adds optional health interoperability alignments for IAO, SWO, DUO, and FHIR RDF. These alignments keep AGENT-O core portable while letting health examples answer cross-standard questions about information artifacts, software tools, data use conditions, and clinical data inputs.

## IAO

| AGENT-O concept | IAO target | Mapping | Rationale |
| --- | --- | --- | --- |
| `doc:Reference` | `obo:IAO_0000030` information content entity | `rdfs:subClassOf` | References are information artifacts. |
| `doc:Citation` | `obo:IAO_0000030` information content entity | `rdfs:subClassOf` | Citations are information artifacts. |
| `report:AgentSystemReport` | `obo:IAO_0000310` document | `rdfs:subClassOf` | Agent system reports are documents. |
| `report:ReportingSection` | `obo:IAO_0000314` document part | `rdfs:subClassOf` | Reporting sections are document parts. |
| `core:Artifact` | `obo:IAO_0000030` information content entity | `skos:relatedMatch` | Only some runtime artifacts are information artifacts. |

## SWO

| AGENT-O concept | SWO target | Mapping | Rationale |
| --- | --- | --- | --- |
| `core:Tool` | `swo:SWO_0000001` software | `rdfs:subClassOf` | Many AGENT-O tools are software tools. |
| `core:Script` | `swo:SWO_0000001` software | `rdfs:subClassOf` | Scripts are software artifacts. |
| `core:ExecutionUnit` | `swo:SWO_0000001` software | `skos:relatedMatch` | Some execution units are workflows or APIs, not only software. |
| `doc:License` | `swo:SWO_0000002` licence | `skos:closeMatch` | License metadata aligns with SWO licence. |
| `core:hasVersion` | `swo:SWO_0004000` has version | `skos:relatedMatch` | Version metadata is represented in AGENT-O as a lightweight datatype property. |

## DUO

| AGENT-O concept | DUO target | Mapping | Rationale |
| --- | --- | --- | --- |
| `gov:DataUsePermission` | `obo:DUO_0000001` data use permission | `skos:closeMatch` | AGENT-O permissions align with DUO data use permissions. |
| `gov:DataUseRestriction` | `obo:DUO_0000017` data use modifier | `skos:closeMatch` | Restrictions align with DUO modifiers. |
| `gov:ConsentConstraint` | `obo:DUO_0000027` project specific restriction | `skos:relatedMatch` | Consent constraints can imply project-specific restrictions. |
| `eval:DatasetUseContext` | `obo:DUO_0000001` data use permission | `skos:relatedMatch` | AGENT-O keeps the dataset-use context separate from DUO terms. |

## FHIR RDF

| AGENT-O concept | FHIR RDF target | Mapping | Rationale |
| --- | --- | --- | --- |
| `health:PatientRecordInput` | `fhir:Patient` | `skos:closeMatch` | Patient record inputs can map to FHIR Patient resources. |
| `health:ObservationInput` | `fhir:Observation` | `skos:closeMatch` | Observation inputs can map to FHIR Observation resources. |
| `health:MedicationInput` | `fhir:Medication`, `fhir:MedicationRequest` | `skos:relatedMatch` | Medication-related inputs may map to multiple FHIR resource types. |
| `health:ConditionInput` | `fhir:Condition` | `skos:closeMatch` | Condition inputs can map to FHIR Condition resources. |
| `health:DiagnosticReportInput` | `fhir:DiagnosticReport` | `skos:closeMatch` | Diagnostic report inputs can map to FHIR DiagnosticReport resources. |

## Acceptance Tests

The health interoperability demo supports two competency queries:

- `cq_data_use_permissions.rq`: lists datasets with data use conditions, permissions, restrictions, and constraining policies.
- `cq_fhir_inputs.rq`: lists FHIR-derived input artifacts, resource types, resource IRIs, connected agents, and downstream recommendations.

