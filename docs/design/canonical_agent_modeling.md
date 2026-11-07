# Canonical AGENT-O Modeling Pattern

Updated 2026-10-29 after the comprehensive semantic review. The six module files
are authoritative; rebuild the integrated ontology after changing a module.
The historical ACRO migration script is not the current ontology builder.

## System and acting participant

`AgentSystem` identifies a configured software system. `Agent` identifies an
acting participant bearing responsibility, including people, organizations and
software actors. Containing agents does not make every system an Agent.

```text
AgentSystem
  -> hasMemberAgent Agent
  -> hasComponent ModelComponent
       -> hasModelComponentRole ModelComponentRole
       -> usesModelResource AIModelResource
  -> hasWorkflow Workflow
  -> hasSystemExecution ExecutionRun
```

Shared capability, workflow and governance properties explicitly allow both
agents and systems where appropriate. Their domains do not silently turn a
system into an Agent. The two classes are not declared disjoint: collective
agency may be asserted independently when justified.

The existing definition that a system contains an acting participant is now
formalized as `AgentSystem` subclass of `hasMemberAgent some Agent`. This
requires a member to exist without requiring it to be named in an incomplete
graph, and does not classify the system itself as an Agent. Configured systems
need not have a past execution run. Clinical-use requirements apply to clinical
systems, rather than every biomedical research system.

`HealthAgent` and its existing specializations represent acting participants.
Use `HealthAgentSystem`, `ClinicalAgentSystem`,
`ClinicalDecisionSupportAgentSystem`, or `PatientFacingAgentSystem` for the
corresponding configured systems.

## Model resource, document, component role and deployment

```text
ModelComponent
  -> usesModelResource AIModelResource
       -> modelIdentifier / modelVersion / modelArchitectureType / modelReleaseDate
       -> hasDeveloper Agent
       -> hasModelInputSpecification ModelInputSpecification
       -> hasModelOutputSpecification ModelOutputSpecification
       -> supportsInputModality / hasModelCapability
       -> hasModelIntendedUse / hasModelLimitation
       -> doc:hasLicense License
       <- specifiesModel AIModelSpecification
       <- describesModelResource ModelCardReport

ExecutionRun
  -> usesModelDeployment ModelDeployment
       -> deploysModelResource AIModelResource
       -> hasProvider Agent
  -> usesModelInputArtifact Artifact
  -> generatedModelOutput GeneratedModelOutput
```

`AIModelResource` is a versioned computational model, checkpoint or API snapshot
and is a subclass of `Model`. `AIModelSpecification` is a document specifying
that resource and is a subclass of `doc:Document`, not `Model`. A model card is
also a document about a model resource; it need not describe any agent system.

`ModelComponent` is a system-relative component binding. Its functional role is
a separate `ModelComponentRole` instance. The same model resource can support
different roles in different systems. A `ModelDeployment` identifies runtime
access or hosting configuration rather than the model or its document.

ModelComponent and ModelComponentRole are disjoint; a component cannot be its
own model-role assignment. General system outputs use `generates` and are
Artifacts. `producesProposedAction` specializes it for recommendations or
suggested actions; an educational output need not be a ProposedAction.

Metadata such as a license does not imply agency. String model versions do not
inherit SWO's object-valued version property, and model developers do not force
every parameter resource to become a SWO software individual.

## Clinical context and health-data layers

`ClinicalUseCase` describes intended clinical use through users, target
population, setting, task, specialty, condition, workflow stage, intended
action, decision role and deployment mode. These contextual descriptions are
distinct from real patients, diseases and action occurrences.

EHR origin does not imply FHIR representation. `EHRInput` is an Artifact;
`FHIRResourceInput` requires explicit FHIR representation or mapping. A source
may be a dataset, repository or service endpoint, so `HealthDataSource` does
not universally inherit Dataset. One record may contain both structured data
and unstructured text. A clinically contraindicated-use constraint becomes an
explicit prohibition only where the applicable policy says so.

## Implementation and execution

`ExecutionUnit` is a reusable implementation, `WorkflowPattern` a reusable
control-flow template, `Workflow` a configured enactment, and `WorkflowStep` a
prospective or actual step occurrence in one execution run. Share a pattern
across runs; use separate step-occurrence instances. SHACL rejects assigning
one step occurrence to two execution runs.

## Governance

`GovernanceRequirement` represents a concrete obligation; `EthicalPrinciple`
represents its guiding principle; `Policy` organizes rules and obligations.
Requirements do not inherit principles merely because they address the same
topic. Use `hasGovernanceRequirement` and `basedOnPrinciple` to connect the
separate instances.

Policies specify prospective controls through `hasEscalationPlan` and
`hasOverrideCapability`. An EscalationPlan uses `hasTriggerCondition` and
`plannedRecipient`; an OverrideCapability uses `canOverrideAction`. Actual
escalation and override occurrences retain EscalationEvent and OverrideAction.
`triggeredBy` specializes `hasTriggerCondition` in one direction, so a plan's
condition does not silently turn the plan into an event.

System-level review obligations use `hasGovernanceRequirement` with a
HumanReviewRequirement. `requiresReview` applies to a ProposedAction and must
not be used on a system merely to record its review policy.

High-risk fallback and escalation checks apply to both `Agent` and
`AgentSystem`. The clinical decision-support, PHI and patient-facing checks
target the corresponding system classes. Their Warning findings remain
warnings even when implemented as SPARQL constraints.

## Reporting profiles and assessment

Profiles reference section classes and schema elements using annotation
properties: `requiresReportingSection`, `recommendedReportingSection`,
`requirementTargetsSection`, and `requiresInformationElement`. These schema
references do not assert document-part instances. Reports use
`hasReportingSection` to link actual section instances. When a report declares
`hasReportingProfile`, SHACL checks that its actual sections satisfy the
profile's required section types.

```text
ReportingAssessmentActivity
  -> usedReport AssessableReport
  -> usedReportingProfile ReportingCompletenessProfile
  -> associatedWithAssessor AssessmentAgent
  -> generatedAssessment ReportingCompletenessAssessment
       -> assessesDimension CompletenessDimension
       -> hasSupportingEvidence EvidenceStatement
       -> hasHumanVerificationStatus HumanVerificationStatus
```

Assessment is performed by an external application. Its activity, responsible
actor and result are separate identities. Completeness labels and human
verification status are controlled individuals checked with SHACL `sh:in`.

Every assessment identifies its report and rubric dimension. An
`assessesSection` link identifies an actual section belonging to that report;
an unrelated section is rejected. Present and Partial assessments require
such a section. Missing and NotApplicable assessments may omit the link when
no section exists, while retaining the assessed dimension and evidence.
Missing may also describe absent information within an existing section.
The reporting-gap query includes assessments without section links.

Missing gap explanations are warnings. Required assessment fields and invalid
section ownership remain violations; the two severities use separate shapes.

The assessed report must be an input of the generating assessment activity.
SHACL accepts either direction of the inverse generation relation, so a valid
representation does not have to duplicate both triples. Evaluation targets
receive EvaluableEntity identity without becoming a particular technical kind
of entity. Specific data-use permissions and restrictions also entail the
general `hasDataUseCondition` relation.

All active named classes and properties have definitions. Current review
evidence and remaining datatype limits are in the
[October 29 review](deep_review_2026-10-29/REVIEW_ZH.md).

Agent-system, benchmark, review, policy, method/model and commentary reports
remain subclasses of `AssessableReport` and may overlap. An assessment's
primary paper-type label is a classification choice, not proof that every
publication belongs to exactly one mutually exclusive document class.

The October revision changes RDF resource identifiers and the former meaning
of `AIModelSpecification`. See [the semantic revision and migration notes](semantic_revision_2026-10-28.md)
before reusing graphs or application sessions created with the earlier model.
