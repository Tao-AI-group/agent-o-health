# Canonical AGENT-O Modeling Pattern

## Scope

AGENT-O separates four questions that were previously easy to conflate:

1. What functional role does a model play inside an agent system?
2. Which identifiable and versioned model resource realizes that role?
3. Which endpoint, service, or loaded checkpoint was used in a particular run?
4. Which publication or card states the evidence needed to reconstruct those facts?

## Canonical Pattern

```text
AgentSystem
  -> hasComponent ModelComponent
       -> hasModelComponentRole ModelComponentRole
       -> realizesModelSpecification AIModelSpecification
            -> modelIdentifier / modelVersion / modelArchitectureType / modelReleaseDate
            -> hasDeveloper OrganizationAgent / hasLicense License
            -> hasModelInputSpecification ModelInputSpecification
            -> hasModelOutputSpecification ModelOutputSpecification
            -> supportsInputModality / hasModelCapability
            -> hasModelIntendedUse / hasModelLimitation
            <- describesModelSpecification ModelCardReport
  -> hasSystemExecution ExecutionRun
       -> usesModelDeployment ModelDeployment
            -> deploysModelSpecification AIModelSpecification
            -> hasProvider OrganizationAgent
       -> usesModelInputArtifact Artifact
       -> generatedModelOutput GeneratedModelOutput
  -> hasIntendedClinicalUse ClinicalUseCase
       -> hasIntendedUser IntendedUserRole
       -> hasTargetPopulation PatientPopulation
       -> hasCareSetting ClinicalSetting
       -> hasClinicalTask ClinicalTask
       -> hasIntendedAction IntendedClinicalAction
       -> hasDecisionRole ClinicalDecisionRole
       -> hasDeploymentMode DeploymentMode
       -> hasOutOfScopeUse / hasProhibitedUse UseConstraint
```

`ModelComponent` is system-relative: the same model specification may be a
planner in one agent and a verifier in another. `AIModelSpecification` is a
versioned resource independent of any one system. `ModelDeployment` identifies
the runtime access point or loaded checkpoint and its provider. A model card is
a document about a model specification, not the model itself.

## Clinical Data Layers

The health and core modules distinguish:

- a `HealthDataSource`, such as an EHR dataset;
- an agent-level `FHIRResourceInput`, `StructuredHealthDataArtifact`, or
  `UnstructuredHealthDataArtifact`;
- a `ModelInputSpecification` describing the representation accepted by a model;
- a runtime input artifact supplied during an `ExecutionRun`;
- a `GeneratedModelOutput`; and
- a downstream `ProposedAction`, clinical recommendation, or patient-facing output.

This separation prevents a FHIR resource, prompt representation, model token
output, and clinical recommendation from being treated as interchangeable.

## Reporting Assessment

AGENT-O represents the inputs, activity, evidence, and outputs of reporting
assessment; it does not claim that the ontology itself executes an LLM judge.

```text
ReportingAssessmentActivity
  -> usedReport AssessableReport
  -> usedReportingProfile ReportingCompletenessProfile
  -> associatedWithAssessor HumanAssessor | SoftwareAssessor | LLMAssessor
  -> generatedAssessment ReportingCompletenessAssessment
       -> assessesDimension CompletenessDimension
       -> hasSupportingEvidence EvidenceStatement
       -> hasHumanVerificationStatus HumanVerificationStatus
```

An external application performs extraction and scoring. SHACL profiles provide
machine-checkable constraints between the ontology and that application.

## Paper-Type Scope

`AssessableReport` has separate subclasses for concrete agent-system reports,
benchmark reports, surveys/reviews, governance or policy reports, method/model
reports, and conceptual/commentary reports. These paper-type classes are
mutually disjoint. Only `AgentSystemReport` uses
`documentsAgentSystem`; other report types use `documentsEvaluatedEntity`.
This supports paper-type-specific applicability without asserting that every
paper describes a runnable agent system.
