# AGENT-O Architecture Revision and Manuscript Alignment

## Executive Decision

**Paper argument:** AGENT-O provides a modular semantic layer that jointly
represents health-oriented agent-system architecture, versioned AI model
resources and runtime deployments, clinical intended use, governance, and
provenance-aware reporting-completeness assessment.

The revised architecture resolves the review comments without treating AGENT-O
as a universal ontology for every health AI system. It preserves the paper's
scope as an ontology for health-oriented **agent systems**, while broadening the
clinical framing beyond conventional prediction models.

The manuscript DOCX was not edited during this revision. The recommendations
below are a change map for the next writing pass.

## Review-Comment Resolution

| Review concern | Architecture response | Executable evidence |
| --- | --- | --- |
| Why report triples rather than axioms? | Validation now reports RDF triples, active/deprecated entity declarations, and transparently defined RDF-level schema-axiom statements separately. | `scripts/validate_ontology.py`; `outputs/validation/formal_quality_results.json` |
| The competency queries were not explained. | Six architecture-focused CQs were added to the existing six, with plain-language questions documented. | `queries/competency/README.md`; 12/12 answered |
| The 279-paper analysis was unclear. | Reporting assessment is now a provenance-aware activity with report, profile, assessor, evidence, confidence, prompt/rubric versions, and human-verification status. | Reporting module, reporting SHACL, assessment-provenance CQ |
| The health-AI framing was too narrow. | The ontology retains an agent-system scope, while the clinical layer now represents use case, users, population, care setting, task, specialty, condition, workflow stage, intended action, decision role, deployment mode, and out-of-scope or prohibited use. | `health:ClinicalUseCase` and related properties |
| Paper collection/search should be disclosed. | The two curated GitHub source lists, extraction pipeline, eligibility rule, and limitations are documented. | `docs/design/corpus_collection_protocol.md` |
| AI model features had no clear home. | Model role, model resource, and runtime deployment are distinct: `ModelComponent`, `AIModelSpecification`, and `ModelDeployment`. | Architecture SHACL and model-specification/deployment CQ |
| The health module covers more than interoperability. | The module is now labeled **Clinical Context, Intended Use, and Health Data Interoperability**. | `ontology/modules/agento-health.ttl` |
| Is reporting assessment part of the ontology or a separate agent? | The ontology represents assessment entities and provenance. An external human/software/LLM/hybrid application performs extraction and scoring. | `ReportingAssessmentActivity`, `AssessmentAgent`, PROV-O alignment |
| LLM extraction may be imperfect. | The new workflow uses section-aware evidence selection, source locators, confidence thresholds, explicit `not_human_verified` status, and a stratified manual-calibration workflow. | LLM script tests and manual-calibration scripts |

## Canonical Architecture

### Agent, Model, and Runtime

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
```

This resolves three different identities:

- `ModelComponent`: the function of a model in one agent system, such as
  planner, reasoner, retriever, critic, verifier, or router;
- `AIModelSpecification`: an identifiable and versioned model, checkpoint,
  fine-tuned derivative, or API snapshot; and
- `ModelDeployment`: the endpoint, service, or loaded checkpoint used at
  runtime, including provider, version/access time, serving framework, and
  deployment configuration.

`LanguageModel`, `VisionModel`, `MultimodalModel`, `FoundationModel`, and related
model types are now subclasses of `AIModelSpecification`, not
`ModelComponent`. The three principal classes are pairwise separated by
disjointness axioms where appropriate.

### Clinical Context and Intended Use

```text
AgentSystem
  -> hasIntendedClinicalUse ClinicalUseCase
       -> hasIntendedUser IntendedUserRole
       -> hasTargetPopulation PatientPopulation
       -> hasCareSetting ClinicalSetting
       -> hasClinicalTask ClinicalTask
       -> hasClinicalSpecialty ClinicalSpecialty
       -> hasTargetCondition TargetCondition
       -> hasWorkflowStage ClinicalWorkflowStage
       -> hasIntendedAction IntendedClinicalAction
       -> hasDecisionRole ClinicalDecisionRole
       -> hasDeploymentMode DeploymentMode
       -> hasOutOfScopeUse / hasProhibitedUse UseConstraint
```

Model-level intended use (`core:ModelIntendedUse`) remains distinct from the
clinical intended use of the complete agent system (`health:ClinicalUseCase`)
and from the statement in a report (`report:IntendedUseStatement`). Deprecated
reporting-layer `IntendedUse` and `IntendedUser` terms remain only as explicit
compatibility mappings.

### Data and Output Layers

AGENT-O now distinguishes a health-data source, structured or unstructured
agent-level health-data artifacts, a FHIR-aligned input and profile, a model
input specification, the runtime input artifact, generated model output, and
the final agent action or clinical recommendation. The examples demonstrate
that a source record, model input representation, model score or rationale, and
reviewable clinical recommendation are not interchangeable.

### Reporting and Assessment

`AgentSystemReport`, `BenchmarkReport`, `SurveyReviewReport`,
`GovernancePolicyReport`, `MethodModelReport`, and
`ConceptualCommentaryReport` are mutually disjoint subclasses of `AssessableReport`.
Only a concrete agent-system report uses `documentsAgentSystem`; other paper
types use `documentsEvaluatedEntity`. This prevents AgentArena from being
inferred to be a concrete agent merely because its paper is assessed.

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

The assessment application remains outside the ontology. AGENT-O represents the
activity, inputs, methods, provenance, evidence, and outputs so the process is
auditable and queryable.

## External Reuse Boundary

| Resource | Reused for | AGENT-O contribution beyond it |
| --- | --- | --- |
| PROV-O | Agents, activities, entities, use, generation, attribution, and derivation | Agent workflow roles, model deployments, governance, clinical use, and reporting profiles |
| SWO | Software, implementation, version, developer, interface, and execution-environment semantics | Agent-specific tools, component roles, model use during runs, and clinical context |
| MCRO | Model-card document and section semantics | Distinction among model component role, model specification, deployment, agent card, and agent-system report |
| FHIR RDF | Clinical resources, StructureDefinitions, CodeSystems/ValueSets, and endpoints | Agent input artifacts, transformations, clinical use cases, and downstream agent outputs |
| DUO | Data-use permissions and restrictions | Dataset-use context connected to agent evaluation, privacy, governance, and compliance |
| IAO | Documents, document parts, and information artifacts | Typed agent/benchmark/policy reports, evidence statements, and completeness assessments |
| NIST AI RMF and WHO guidance | Governance concept schemes and profile expectations | Executable agent-level governance properties, SHACL checks, escalation, fallback, and human review |

MCRO is reused selectively. A model card is a document describing an
`AIModelSpecification`; it is not the model, deployment, or agent system.

## Validation Results For This Revision

### Ontology Inventory

The integrated serialization contains **1,962 RDF triples**. It declares **252
active classes**, **198 active object properties**, and **51 active datatype
properties**. Four deprecated classes and two deprecated object properties are
retained for compatibility and excluded from active counts. The validation
script reports **679 RDF-level schema-axiom statements** using a documented
predicate-based counting rule; this value is not presented as an OWLAPI logical
axiom count.

| Module | RDF triples | Active classes | Active object properties | Active datatype properties |
| --- | ---: | ---: | ---: | ---: |
| Core agent/model/runtime | 635 | 80 | 77 | 18 |
| Documentation/provenance | 90 | 9 | 10 | 7 |
| Evaluation | 174 | 22 | 23 | 4 |
| Governance/safety | 293 | 39 | 34 | 8 |
| Clinical context/health interoperability | 301 | 48 | 23 | 3 |
| Reporting/assessment representation | 466 | 54 | 31 | 11 |

### Formal, SHACL, Reasoning, and Query Checks

- Source package: 26 TTL files parsed; 0 parse failures.
- Public package: 25 TTL files parsed; 0 parse failures.
- Integrated ontology equals the semantic union of the six authoritative modules.
- 0 active classes or properties missing labels.
- 0 active object or datatype properties missing domain/range declarations.
- 0 undefined AGENT-O terms in alignment files.
- 183 external mapping statements across PROV-O, SWO, MCRO, FHIR RDF, DUO,
  IAO, NIST AI RMF, and WHO guidance.
- Architecture, governance, and reporting SHACL: all conform; 0 findings.
- OWL-RL query graph: 3,644 input triples and 6,364 additional inferred triples.
- Competency queries: 12/12 answered.
- Automated tests: 24/24 passed in the development package and 12/12 passed in
  the synchronized public release package.

The six new architecture CQs retrieve model role/specification/deployment,
model-interface layering, clinical intended use, report evidence for model
version and intended use, assessment provenance, and paper-type scope.

### Corpus-Assessment Rerun Status

All 279 papers were successfully converted into section-aware version-2.1 judge
requests. The new request format retains source sections and character locators
and no longer discards the middle of long papers. A five-paper API pilot could
not be completed because the institutional OAuth endpoint rejected the current
session credentials with HTTP 401. No version-2 scores were fabricated or mixed
with the earlier results.

The published corpus statistics from the earlier rubric should therefore remain
labeled as version 1 until the 279 papers are rescored with
`agento-reporting-completeness-2.1` and manually calibrated.

## Manuscript Revision Map

### Title

Recommended:

> **AGENT-O: A Modular Ontology for Reporting, Interoperability, and Governance of Health-Oriented AI Agent Systems**

This is more accurate than making “agent card” the whole ontology, because the
ontology also represents runtime executions, model deployments, clinical use,
evaluation, provenance, and assessment records.

### Abstract

- **Objective:** state that AGENT-O represents health-oriented agent systems and
  supports ontology-guided assessment of reporting completeness.
- **Methods:** name the three model layers, first-class clinical use case,
  paper-type-specific reports, and provenance-aware assessment activity.
- **Results:** replace the old 1,355/190/141/33 inventory after a release is
  frozen; report RDF triples and active entities separately from schema axioms.
- **Conclusion:** retain the boundary that reporting completeness is not agent
  performance, clinical utility, or deployment readiness.

Suggested result sentence after release freeze:

> The integrated release contained 1,962 RDF triples and declared 252 active
> classes, 198 active object properties, and 51 active datatype properties.
> All three SHACL suites conformed without findings, and 12 of 12 competency
> queries returned the expected evidence types.

### Introduction

Broaden the opening from “clinical prediction models” to **health AI systems**,
including predictive and generative models, clinical decision support,
conversational systems, workflow automation, multimodal interpretation,
research agents, and patient-facing services. Then narrow explicitly to the
agentic subset addressed by AGENT-O. This answers the breadth concern without
claiming that AGENT-O models every health AI system.

### Materials and Methods: Ontology Design

Add a short subsection titled **Agent-system, model, and deployment
separation**. Explain that `ModelComponent` is system-relative,
`AIModelSpecification` is versioned and identifiable, and `ModelDeployment` is
the runtime resource used by an `ExecutionRun`. State that MCRO informs
model-card document semantics, while SWO and PROV-O support software/version and
provenance semantics.

Rename the health subsection to **Clinical context, intended use, and health
data interoperability**. Describe clinical use as more than a FHIR mapping:
user, population, setting, specialty, condition, workflow stage, task, intended
clinical action, decision role, deployment mode, and excluded or prohibited uses
are represented explicitly.

Rename the reporting subsection to **Reporting and assessment representation**.
State directly that an external application executes extraction and scoring;
the ontology represents the report, profile, assessor, evidence, activity, and
assessment output.

### Materials and Methods: Corpus and Assessment

Describe the 279-paper dataset as a **curated-source corpus**, not a systematic
database search. Name both public lists, explain URL extraction/deduplication,
PDF resolution, Markdown conversion, inclusion based on readable extraction,
and addition of AgentArena as a prespecified case. Add the missing retrieval
date and repository commit SHAs before submission.

Replace head/tail truncation language with section-aware evidence retrieval.
Report the rubric version, prompt version, model deployment, evidence locators,
confidence, human-verification status, and paper-type applicability rules.
Prespecify a stratified manual calibration sample and report agreement rather
than treating the LLM labels as reference truth.

### Evaluation Methods

Separate four evidence streams:

1. formal RDF/OWL parsing and active-entity quality checks;
2. architecture, governance, and reporting SHACL validation;
3. 12 executable competency queries with expected evidence types; and
4. case/corpus coverage assessment with human calibration.

Do not describe warning-tolerant conformance for this release; the current
three SHACL suites have zero findings.

### Results

Update the module inventory and external alignment count. Add results for the
three-way model separation and clinical intended-use CQ. Explicitly report that
AgentArena is represented as a `BenchmarkReport` about a `BenchmarkFramework`,
not as a concrete `AgentSystem`.

Do not combine version-1 corpus scores with the revised runtime/architecture
rubric. Either rerun all 279 papers and replace the corpus tables, or label the
earlier analysis as exploratory and move it to the supplement.

### Discussion and Limitations

Emphasize that AGENT-O integrates existing resources rather than replacing
them. Add the limitations that the corpus came from curated lists, section-aware
retrieval can still omit relevant evidence, LLM labels require human
calibration, and SHACL conformance tests example/profile requirements rather
than clinical safety or scientific correctness.

### Figures and Supplement

Revise the ontology architecture figure so its panels show:

- **Panel A:** `AgentSystem`, agent components, workflow, tools, memory, and
  multi-agent interaction;
- **Panel B:** `ModelComponent`, model roles, `AIModelSpecification`, model
  interfaces, `ModelDeployment`, `ExecutionRun`, and generated model output;
- **Panel C:** `ClinicalUseCase`, intended users/population/setting/task/intended
  action/decision role, health-data sources, FHIR inputs/profiles, and clinical
  outputs; and
- **Panel D:** governance plus `AssessableReport` paper types,
  `ReportingAssessmentActivity`, evidence, completeness labels, confidence, and
  human-verification status.

Update Supplementary Tables S1-S4 for the new inventory, 183 mappings, three
SHACL suites, 12 CQs, and new reasoning counts. Update the rubric table only
after the version-2 corpus rerun and calibration are complete.

## Terminology Ledger

| Use consistently | Avoid in active prose | Reason |
| --- | --- | --- |
| ontology-guided reporting-completeness assessment | reverse validation | Avoids implying an undefined opposite of “forward” validation |
| `AIModelSpecification` | model component when referring to a model/checkpoint | Separates resource identity from system role |
| `ModelDeployment` | model when referring to an endpoint or loaded checkpoint | Preserves runtime identity and provenance |
| clinical intended use / `ClinicalUseCase` | intended use as a reporting section only | Intended use is a system/context entity; reports contain statements about it |
| `ModelCardReport` | model card reference as if it were the model | A model card is a document |
| reporting and assessment representation | automated ontology evaluation agent | The ontology represents assessment; an external application executes it |
| curated-source corpus | systematic literature search | Matches the actual collection method |

## Claim-Evidence Boundaries

| Defensible claim | Evidence | Required boundary |
| --- | --- | --- |
| AGENT-O represents model roles, specifications, and deployments separately. | OWL classes/properties, disjointness, SHACL, examples, CQs | Does not validate that a reported model is scientifically appropriate. |
| AGENT-O represents clinical intended use and FHIR-aligned inputs. | Health module, FHIR alignment, examples, CQs | Does not certify FHIR conformance or clinical deployment readiness. |
| Assessment outputs are auditable and provenance-aware. | Assessment activity, evidence statements, PROV-O mappings, SHACL | An external application performs extraction/scoring; LLM outputs are not truth. |
| The revised example/profile graphs conform to SHACL. | 0 findings across three suites | Conformance is limited to encoded shapes and supplied graphs. |
| The ontology answers 12 implemented competency questions. | 12/12 query results | Query coverage is not proof of completeness or universality. |

## Remaining Actions Before Manuscript Update

1. Restore valid institutional API credentials and rerun all 279 papers with
   rubric version 2.1 into a new output directory.
2. Complete a paper-type- and score-stratified manual calibration worksheet;
   report exact agreement, Cohen's kappa, and score mean absolute error.
3. Add immutable source-list commit SHAs, retrieval date, identifiers,
   checksums, extraction version, and deduplication/exclusion fields to the
   corpus release manifest.
4. Freeze and tag the ontology release, then update all manuscript and
   supplementary counts from that tag.
5. Revise the DOCX section by section using this map and regenerate the class
   architecture figure from the revised ontology.
