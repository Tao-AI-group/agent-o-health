# Supplementary Table. Model, Clinical-Use, and Reporting-Assessment Crosswalk

This table identifies the canonical AGENT-O home for information elements raised
during architecture review. External resources are reused selectively; the
mapping does not assert that the external term is identical unless an exact
mapping is explicitly declared in an alignment file.

| Information element | Canonical AGENT-O representation | External reuse or alignment | Validation evidence |
| --- | --- | --- | --- |
| Agent system | `core:AgentSystem` | PROV-O `prov:Agent` | Architecture SHACL; model/runtime CQs |
| Model's role in one system | `core:ModelComponent` plus `core:hasModelComponentRole` | Agent-specific extension | Architecture SHACL; model specification/deployment CQ |
| Versioned model or checkpoint | `core:AIModelSpecification`; `core:modelIdentifier`; `core:modelVersion` | PROV-O entity; SWO software/version; MCRO model-detail sections | Architecture SHACL; model and reporting-evidence CQs |
| Model name, architecture, developer, release date, and license | `core:hasName`; `core:modelArchitectureType`; `core:hasDeveloper`; `core:modelReleaseDate`; `doc:hasLicense` | PROV-O attribution; SWO developer/version/license; MCRO sections | Architecture SHACL; reporting-completeness profile |
| Model inputs, outputs, and modalities | `core:ModelInputSpecification`; `core:ModelOutputSpecification`; `core:InputModality` | MCRO input/output and model-detail sections | Architecture SHACL; model-interface CQ |
| Model capabilities, intended use, and limitations | `core:ModelCapability`; `core:ModelIntendedUse`; `core:ModelLimitation` | MCRO intended-use and limitation sections | Architecture SHACL; reporting-completeness profile |
| Runtime model endpoint or loaded checkpoint | `core:ModelDeployment`; `core:deploysModelSpecification`; provider, endpoint, version, access date, serving framework, quantization, region, and runtime configuration properties | PROV-O entity/use; SWO implementation and execution-environment semantics | Architecture SHACL; model specification/deployment CQ |
| Model card document | `report:ModelCardReport`; `report:describesModelSpecification` | MCRO model-card report; IAO document | Reporting SHACL; model-card alignment CQ |
| Agent-system clinical intended use | `health:ClinicalUseCase` | Related to MCRO intended-use sections and NIST AI RMF Map concepts | Architecture SHACL; clinical intended-use CQ |
| Intended user, population, and care setting | `health:IntendedUserRole`; `health:PatientPopulation`; `health:ClinicalSetting` | FHIR/clinical-context and governance mappings | Architecture SHACL; clinical intended-use CQ |
| Specialty, condition, workflow stage, and task | `health:ClinicalSpecialty`; `health:TargetCondition`; `health:ClinicalWorkflowStage`; `health:ClinicalTask` | FHIR RDF and biomedical context mappings where available | Reporting profile; clinical intended-use CQ |
| Intended clinical action and decision role | `health:IntendedClinicalAction`; `health:ClinicalDecisionRole` | Agent-specific clinical context extension | Architecture SHACL; clinical intended-use CQ |
| Deployment mode and excluded use | `health:DeploymentMode`; `health:OutOfScopeUse`; `health:ProhibitedUse`; `health:ContraindicatedUse` | Governance guidance | Reporting profile; clinical intended-use CQ |
| Health-data source and modality | `health:HealthDataSource`; `health:DataModality` | DUO for data-use constraints; FHIR for clinical resources | Data-use and FHIR CQs |
| Structured or unstructured agent input | `health:StructuredHealthDataArtifact`; `health:UnstructuredHealthDataArtifact`; FHIR input subclasses | FHIR RDF resources and profiles | Architecture SHACL; FHIR-input CQ |
| Model-level generated output | `core:GeneratedModelOutput` | PROV-O entity/generated relation | Model-interface and provenance CQs |
| Final agent action or clinical recommendation | `core:ProposedAction` and health recommendation subclasses | PROV-O entity/derivation | Model-interface and provenance CQs |
| Paper/report type | Mutually disjoint subclasses of `report:AssessableReport` | IAO document semantics | Paper-type-scope CQ |
| Reporting assessment process | `report:ReportingAssessmentActivity`; `report:AssessmentAgent` | PROV-O activity and agent | Reporting SHACL; assessment-provenance CQ |
| Evidence-grounded assessment output | `report:ReportingCompletenessAssessment`; `report:EvidenceStatement`; confidence and human-verification properties | PROV-O entity/provenance | Reporting SHACL; assessment-provenance and reporting-gap CQs |

The assessment application is outside the ontology. AGENT-O represents its
inputs, profile, assessor, evidence, provenance, and outputs so that automated
or human judgments remain inspectable and can be calibrated.
