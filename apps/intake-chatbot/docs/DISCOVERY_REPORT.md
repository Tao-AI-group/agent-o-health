# AGENT-O Intake Discovery Report

**Generated from the current read-only AGENT-O source.**

## Source State

- AGENT-O root: repository root
- Public release branch/status: `## main...origin/main`
- Public release commit: `2cde5dbcd0f73d6c056b4d270fd8c139cd7cd20b`
- Integrated ontology: `ontology/agento.ttl`
- Integrated triples: `1962`
- Snapshot ID: `15ae2eaf5e674114`
- Combined snapshot SHA-256: `15ae2eaf5e6741140f80dcfd13481b5dde9cbdc081bf569648ad1ee21f650e3f`

The six module files are authoritative. The integrated ontology is a generated read-only input for this application. Historical ACRO files and figure-only reduced TTL files are excluded.

## Authoritative Modules

| Module | SHA-256 |
| --- | --- |
| `ontology/modules/agento-core.ttl` | `d2665173d1942483dda59cb995e310335e5fb8b9845d58bd35e36517c01855c3` |
| `ontology/modules/agento-doc.ttl` | `2da89d9a90c164b2c51c11a374ad14d61e55f3b14e7a5324695a95a9b4147cc7` |
| `ontology/modules/agento-eval.ttl` | `e73ff2788fcbf731a3f2f91cbf89cbade6a71c634aa27afd8596365b4d88650b` |
| `ontology/modules/agento-gov.ttl` | `114b9c4970d20aac1eefc930c1c28b09c11792ea26978fe141ffabb357077d22` |
| `ontology/modules/agento-health.ttl` | `1c58878e8ae5e103d4852a3f4ad8e07fece058535b9b19e680804fa347764628` |
| `ontology/modules/agento-report.ttl` | `c7fe66aaa6d05be88ed54ceeab3926eaccd67988d83f68618e22befb4865eb7d` |

## Profile Contract

- Profile ID: `agento-agent-card`
- Profile URI: `https://w3id.org/agent-o/profiles/reporting`
- Profile version: `2026-08-31`
- Root report class: `https://w3id.org/agent-o/reporting#AgentCard`
- Root described-system class: `https://w3id.org/agent-o/health#HealthAgent`
- Report-to-system property: `https://w3id.org/agent-o/reporting#documentsAgentSystem`

### Required reporting sections

- `https://w3id.org/agent-o/reporting#AgentIdentityScopeSection`
- `https://w3id.org/agent-o/reporting#ClinicalContextSection`
- `https://w3id.org/agent-o/reporting#DatasetsMetricsSection`
- `https://w3id.org/agent-o/reporting#DeploymentMonitoringSection`
- `https://w3id.org/agent-o/reporting#EvaluationReportingSection`
- `https://w3id.org/agent-o/reporting#FailureFallbackSection`
- `https://w3id.org/agent-o/reporting#HumanReviewSection`
- `https://w3id.org/agent-o/reporting#InputOutputDataSection`
- `https://w3id.org/agent-o/reporting#IntendedUseSection`
- `https://w3id.org/agent-o/reporting#ModelComponentsSection`
- `https://w3id.org/agent-o/reporting#ModelSpecificationSection`
- `https://w3id.org/agent-o/reporting#PlanningReasoningSection`
- `https://w3id.org/agent-o/reporting#PrivacySecurityComplianceSection`
- `https://w3id.org/agent-o/reporting#ReproducibilitySection`
- `https://w3id.org/agent-o/reporting#RiskUncertaintySection`
- `https://w3id.org/agent-o/reporting#RuntimeArchitectureSection`
- `https://w3id.org/agent-o/reporting#ToolUseSection`
- `https://w3id.org/agent-o/reporting#WorkflowSection`

### Recommended reporting sections

- `https://w3id.org/agent-o/reporting#AssessmentMethodsSection`
- `https://w3id.org/agent-o/reporting#DataUseSection`
- `https://w3id.org/agent-o/reporting#GovernanceReportingSection`
- `https://w3id.org/agent-o/reporting#SubgroupEquityEvaluationSection`

## SHACL Requirement Catalog

| Shape | Target class | Path | Min | Max | Value constraint | Severity | Message | Source |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `https://w3id.org/agent-o/health#FHIRResourceInputArchitectureShape` | `https://w3id.org/agent-o/health#FHIRResourceInput` | `https://w3id.org/agent-o/health#hasDataFormat` | 1 |  | `https://w3id.org/agent-o/health#DataFormat` | Violation | FHIR-aligned inputs must identify their serialization format. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#FHIRResourceInputArchitectureShape` | `https://w3id.org/agent-o/health#FHIRResourceInput` | `https://w3id.org/agent-o/health#usesTerminologySystem` | 1 |  | `https://w3id.org/agent-o/health#TerminologySystem` | Violation | FHIR-aligned inputs must identify terminology systems used to encode clinical content. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#FHIRResourceInputArchitectureShape` | `https://w3id.org/agent-o/health#FHIRResourceInput` | `https://w3id.org/agent-o/health#usesFHIRProfile` | 1 |  | `https://w3id.org/agent-o/health#FHIRProfile` | Violation | FHIR-aligned inputs must identify the FHIR profile or StructureDefinition used. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#ModelDeploymentArchitectureShape` | `https://w3id.org/agent-o/core#ModelDeployment` | `https://w3id.org/agent-o/core#deploysModelSpecification` | 1 |  | `https://w3id.org/agent-o/core#AIModelSpecification` | Violation | Model deployments must identify the model specification they deploy. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#ModelDeploymentArchitectureShape` | `https://w3id.org/agent-o/core#ModelDeployment` | `https://w3id.org/agent-o/core#hasProvider` | 1 |  | `https://w3id.org/agent-o/core#Agent` | Violation | Model deployments must identify their provider or operator. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasTargetPopulation` | 1 |  | `https://w3id.org/agent-o/health#PatientPopulation` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasIntendedAction` | 1 |  | `https://w3id.org/agent-o/health#IntendedClinicalAction` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasIntendedUser` | 1 |  | `https://w3id.org/agent-o/health#IntendedUserRole` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasCareSetting` | 1 |  | `https://w3id.org/agent-o/health#ClinicalSetting` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasDeploymentMode` | 1 |  | `https://w3id.org/agent-o/health#DeploymentMode` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasDecisionRole` | 1 |  | `https://w3id.org/agent-o/health#ClinicalDecisionRole` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#ClinicalUseCaseArchitectureShape` | `https://w3id.org/agent-o/health#ClinicalUseCase` | `https://w3id.org/agent-o/health#hasClinicalTask` | 1 |  | `https://w3id.org/agent-o/health#ClinicalTask` | Violation | Clinical use cases must identify intended users, target population, care setting, clinical task, decision role, intended clinical action, and deployment mode. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/health#HealthAgentIntendedUseShape` | `https://w3id.org/agent-o/health#HealthAgent` | `https://w3id.org/agent-o/health#hasIntendedClinicalUse` | 1 |  | `https://w3id.org/agent-o/health#ClinicalUseCase` | Violation | Health-oriented agent systems must identify an intended clinical use context. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#modelVersion` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | AI model specifications must provide a checkpoint, snapshot, or version. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasName` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | AI model specifications must provide a model name. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasModelOutputSpecification` | 1 |  | `https://w3id.org/agent-o/core#ModelOutputSpecification` | Violation | AI model specifications must distinguish model output from downstream agent output. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasDeveloper` | 1 |  | `https://w3id.org/agent-o/core#Agent` | Violation | AI model specifications must identify their developer. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#supportsInputModality` | 1 |  | `https://w3id.org/agent-o/core#InputModality` | Violation | AI model specifications must identify supported input modalities. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#modelIdentifier` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | AI model specifications must provide a model identifier. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasModelCapability` | 1 |  | `https://w3id.org/agent-o/core#ModelCapability` | Violation | AI model specifications must identify relevant model capabilities. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasModelLimitation` | 1 |  | `https://w3id.org/agent-o/core#ModelLimitation` | Violation | AI model specifications must state model-level limitations. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#modelArchitectureType` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | AI model specifications must identify their architecture or model type. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasModelInputSpecification` | 1 |  | `https://w3id.org/agent-o/core#ModelInputSpecification` | Violation | AI model specifications must distinguish their model-level input representation. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#hasModelIntendedUse` | 1 |  | `https://w3id.org/agent-o/core#ModelIntendedUse` | Violation | AI model specifications must state model-level intended use. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/core#modelReleaseDate` | 1 |  | `http://www.w3.org/2001/XMLSchema#date` | Violation | AI model specifications must provide a release or snapshot date. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AIModelSpecificationArchitectureShape` | `https://w3id.org/agent-o/core#AIModelSpecification` | `https://w3id.org/agent-o/doc#hasLicense` | 1 |  | `https://w3id.org/agent-o/doc#License` | Violation | AI model specifications must identify their license or access terms. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AgentSystemArchitectureShape` | `https://w3id.org/agent-o/core#AgentSystem` | `https://w3id.org/agent-o/core#hasComponent` | 1 |  | `https://w3id.org/agent-o/core#AgentComponent` | Violation | Agent systems must identify at least one functional component. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#AgentSystemArchitectureShape` | `https://w3id.org/agent-o/core#AgentSystem` | `https://w3id.org/agent-o/core#hasSystemExecution` | 1 |  | `https://w3id.org/agent-o/core#ExecutionRun` | Violation | Agent systems must identify at least one execution run. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#ModelComponentArchitectureShape` | `https://w3id.org/agent-o/core#ModelComponent` | `https://w3id.org/agent-o/core#hasModelComponentRole` | 1 |  | `https://w3id.org/agent-o/core#ModelComponentRole` | Violation | Model components must identify their function in the agent workflow. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/core#ModelComponentArchitectureShape` | `https://w3id.org/agent-o/core#ModelComponent` | `https://w3id.org/agent-o/core#realizesModelSpecification` | 1 |  | `https://w3id.org/agent-o/core#AIModelSpecification` | Violation | Model components must identify the AI model specification they realize. | `agento-architecture-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#PatientFacingGovernanceShape` | `https://w3id.org/agent-o/health#PatientFacingAgent` | `https://w3id.org/agent-o/health#hasIntendedClinicalUse / https://w3id.org/agent-o/health#hasIntendedUser` | 1 |  | `` | Warning | Patient-facing agents should declare intended users through their clinical use case. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#GovernanceProfileShape` | `https://w3id.org/agent-o/reporting#GovernanceProfile` | `https://w3id.org/agent-o/gov#hasEthicalPrinciple` | 3 |  | `` | Warning | Governance profiles should include multiple ethical or governance principles. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#GovernanceProfileShape` | `https://w3id.org/agent-o/reporting#GovernanceProfile` | `https://w3id.org/agent-o/reporting#alignsWithGuideline` | 1 |  | `` | Warning | Governance profiles should identify their external guideline references. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ClinicalDecisionSupportGovernanceShape` | `https://w3id.org/agent-o/health#ClinicalDecisionSupportAgent` | `https://w3id.org/agent-o/gov#hasAutomationLevel` | 1 |  | `` | Warning | Clinical decision-support agents should declare the allowed automation level. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ClinicalDecisionSupportGovernanceShape` | `https://w3id.org/agent-o/health#ClinicalDecisionSupportAgent` | `https://w3id.org/agent-o/gov#hasRisk` | 1 |  | `` | Warning | Clinical decision-support agents should identify at least one governance risk. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ClinicalDecisionSupportGovernanceShape` | `https://w3id.org/agent-o/health#ClinicalDecisionSupportAgent` | `https://w3id.org/agent-o/gov#hasAccountabilityRole` | 1 |  | `` | Warning | Clinical decision-support agents should declare an accountability role. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ClinicalDecisionSupportGovernanceShape` | `https://w3id.org/agent-o/health#ClinicalDecisionSupportAgent` | `https://w3id.org/agent-o/gov#monitoredBy` | 1 |  | `` | Warning | Clinical decision-support agents should declare a post-deployment monitoring rule. | `agento-governance-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#hasHumanVerificationStatus` | 1 |  | `https://w3id.org/agent-o/reporting#HumanVerificationStatus` | Violation | Completeness assessments must record whether a human has verified the result. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#assessmentConfidence` | 1 |  | `http://www.w3.org/2001/XMLSchema#decimal` | Violation | Automated or hybrid completeness assessments must record a confidence value from 0 to 1. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#hasEvidenceQuote` | 1 |  | `` | Warning | Completeness assessments should include a short source evidence quote. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#hasCompletenessLabel` | 1 |  | `` | Violation | Completeness assessments must use a present, partial, missing, or not-applicable label. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#generatedByAssessmentActivity` | 1 |  | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | Violation | Completeness assessments must link to the activity that generated them. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#hasSupportingEvidence` | 1 |  | `https://w3id.org/agent-o/reporting#EvidenceStatement` | Violation | Completeness assessments must link to structured supporting evidence. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#assessesReport` | 1 |  | `` | Violation | Completeness assessments must identify the report being assessed. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#assessesSection` | 1 |  | `` | Violation | Completeness assessments must identify the reporting section being assessed. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessmentShape` | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | `https://w3id.org/agent-o/reporting#assessesDimension` | 1 |  | `https://w3id.org/agent-o/reporting#CompletenessDimension` | Violation | Completeness assessments must identify the rubric dimension being assessed. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ModelCardReportShape` | `https://w3id.org/agent-o/reporting#ModelCardReport` | `https://w3id.org/agent-o/reporting#describesModelSpecification` | 1 |  | `` | Violation | A model card must identify the AI model specification it describes. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#usedReport` | 1 |  | `https://w3id.org/agent-o/reporting#AssessableReport` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#promptVersion` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#usedReportingProfile` | 1 |  | `https://w3id.org/agent-o/reporting#ReportingProfile` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#rubricVersion` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#assessmentTimestamp` | 1 |  | `http://www.w3.org/2001/XMLSchema#dateTime` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#generatedAssessment` | 1 |  | `https://w3id.org/agent-o/reporting#ReportingCompletenessAssessment` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingAssessmentActivityShape` | `https://w3id.org/agent-o/reporting#ReportingAssessmentActivity` | `https://w3id.org/agent-o/reporting#associatedWithAssessor` | 1 |  | `https://w3id.org/agent-o/reporting#AssessmentAgent` | Violation | Reporting-assessment activities must identify their input report and profile, assessor, outputs, rubric and prompt versions, and timestamp. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingProfileShape` | `https://w3id.org/agent-o/reporting#ReportingProfile` | `https://w3id.org/agent-o/reporting#requiresReportingSection` | 1 |  | `` | Violation | Reporting profiles must declare at least one required reporting section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#ReportingProfileShape` | `https://w3id.org/agent-o/reporting#ReportingProfile` | `https://w3id.org/agent-o/reporting#alignsWithGuideline` | 1 |  | `` | Warning | Reporting profiles should cite external guideline references. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#EvidenceStatementShape` | `https://w3id.org/agent-o/reporting#EvidenceStatement` | `https://w3id.org/agent-o/reporting#evidenceQuote` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | Evidence statements must preserve a quote, source section, and source locator. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#EvidenceStatementShape` | `https://w3id.org/agent-o/reporting#EvidenceStatement` | `https://w3id.org/agent-o/reporting#evidenceLocator` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | Evidence statements must preserve a quote, source section, and source locator. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#EvidenceStatementShape` | `https://w3id.org/agent-o/reporting#EvidenceStatement` | `https://w3id.org/agent-o/reporting#evidenceSourceSection` | 1 |  | `http://www.w3.org/2001/XMLSchema#string` | Violation | Evidence statements must preserve a quote, source section, and source locator. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AssessableReportShape` | `https://w3id.org/agent-o/reporting#AssessableReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` | 1 |  | `` | Violation | Assessable reports must include at least one typed reporting section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include an intended-use section that distinguishes model use from system-level clinical use. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include an evaluation reporting section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include a reproducibility section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` | 1 |  | `` | Violation | Agent-system reports must include at least one reporting section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#containsStatement` |  |  | `` | Warning | Reports should contain an intended-use statement linked to the represented use entity. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#documentsAgentSystem` | 1 |  | `` | Violation | Agent-system reports must identify the agent system they document. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include a governance reporting section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include a runtime architecture section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include a risk and uncertainty section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include a human-review section. | `agento-reporting-shapes.ttl` |
| `https://w3id.org/agent-o/reporting#AgentSystemReportShape` | `https://w3id.org/agent-o/reporting#AgentSystemReport` | `https://w3id.org/agent-o/reporting#hasReportingSection` |  |  | `` | Warning | Reports should include a model specification section with identity, role, interface, and deployment evidence. | `agento-reporting-shapes.ttl` |

No current property shape declares `sh:group`, `sh:order`, `sh:in`, or `sh:pattern`; the loader nevertheless preserves these fields when future snapshots add them. Composite `sh:or` and SPARQL constraints remain available to pySHACL and are not reduced to property rows above.

## Conversational Section Map

The UI groups ontology requirements into the following conversational sections. These groups are navigation aids and do not replace ontology classes or SHACL paths.

| Order | Section | Description |
| ---: | --- | --- |
| 10 | Card metadata | Card identity, version, authorship, and review state. |
| 20 | Agent identity and scope | What the agent is, why it exists, and its operating boundaries. |
| 30 | Intended use and context | Users, population, setting, task, decision role, and prohibited uses. |
| 40 | Agent architecture | Components, roles, orchestration, and system structure. |
| 50 | Models and deployments | Model roles, versioned specifications, interfaces, and runtime deployments. |
| 60 | Workflow and execution | Steps, planning, reasoning, memory, tools, and runtime environment. |
| 70 | Inputs, outputs, and actions | Data sources, artifacts, model outputs, and downstream actions. |
| 80 | Evaluation | Datasets, tasks, baselines, metrics, results, and failure analysis. |
| 90 | Provenance and reproducibility | Sources, traces, artifacts, versions, environment, and rerun instructions. |
| 100 | Governance and safety | Accountability, review, fallback, risk, privacy, security, and compliance. |
| 110 | Limitations and evidence | Known gaps, supporting evidence, confidence, and human verification. |

## Applicability and N/A

The Agent Card profile is intended for a concrete existing or planned agent system. Required SHACL paths are applicable whenever their target entity is instantiated. A user may mark an intake requirement not applicable only with a recorded reason; that workflow decision is stored separately from RDF completeness labels. No profile rule silently assigns N/A. Optional five-dimension scoring excludes confirmed N/A requirements from its denominator.

## Golden Fixtures

- `data/examples/converted_test_agent_annotations.ttl`: broad architecture/reporting fixture.
- `data/examples/governance_reporting_profile_example.ttl`: governance and reporting fixture.
- `data/examples/health_interoperability_example.ttl`: clinical/FHIR fixture.
- `data/examples/prov_decision_trace_example.ttl`: provenance trace fixture.

The chatbot uses synthetic data derived from these patterns. It does not modify or redistribute source-paper content.

## LLM and Credential Integration

The existing `agent-o/scripts/run_llm_reverse_validation.py` provides a reusable credential-record loader, OAuth client-credentials token refresh pattern, retry behavior, and OpenAI-compatible chat payload. This application reimplements those behaviors behind an `LLMClient` protocol and redacts all errors. Credential values are loaded only at runtime and are never included in this report, the database, logs, frontend responses, or exports.

Streaming, JSON-schema response format, and tool-calling support are gateway/deployment capabilities that still require an explicitly enabled synthetic live smoke test. The default provider is the deterministic mock and health checks never call the gateway.

## Expert Confirmation Items

- Confirm whether every one of the 18 reporting-profile sections should block a conformant export or whether some should remain reporting-completeness requirements only.
- Confirm organization/person modeling for model developers and deployment providers, because the current range is `core:Agent`.
- Confirm institution-specific retention, authentication, PHI handling, and gateway model/deployment settings before a real internal pilot.
- Confirm whether reporting assessments should be embedded in every exported Agent Card or remain in the separate validation report for the MVP.
