# PROV-O Crosswalk

AGENT-O uses PROV-O for provenance-compatible traces while keeping agent-specific runtime, reasoning, governance, and evaluation semantics in AGENT-O.

| AGENT-O concept | PROV-O target | Mapping | Notes |
| --- | --- | --- | --- |
| `core:Agent` | `prov:Agent` | `rdfs:subClassOf` | Agentic systems can be provenance agents. |
| `core:AgentSystem` | `prov:Agent` | `rdfs:subClassOf` | A concrete agent system can be associated with execution activities. |
| `core:HumanAgent` | `prov:Agent` | `rdfs:subClassOf` | Human reviewers are also provenance agents. |
| `core:ExecutionRun` | `prov:Activity` | `rdfs:subClassOf` | Runs are execution activities. |
| `core:WorkflowStep` | `prov:Activity` | `rdfs:subClassOf` | Steps can contribute to provenance traces. |
| `core:ToolInvocation` | `prov:Activity` | `rdfs:subClassOf` | Tool invocations are execution activities. |
| `report:ReportingAssessmentActivity` | `prov:Activity` | `rdfs:subClassOf` | Reporting assessment is represented as a provenance-aware activity executed by a human, software, LLM, or hybrid assessor. |
| `core:Artifact` | `prov:Entity` | `rdfs:subClassOf` | Runtime artifacts can be provenance entities. |
| `core:Observation` | `prov:Entity` | `rdfs:subClassOf` | Observations can be provenance entities. |
| `core:ProposedAction` | `prov:Entity` | `rdfs:subClassOf` | Proposed actions are outputs that can be traced. |
| `core:AIModelSpecification`, `core:ModelDeployment`, `core:GeneratedModelOutput` | `prov:Entity` | `rdfs:subClassOf` | Versioned model resources, deployments, and generated model-level outputs can participate in provenance traces. |
| `report:EvidenceStatement`, `report:ReportingCompletenessAssessment` | `prov:Entity` | `rdfs:subClassOf` | Evidence and assessment results retain provenance links to the generating activity. |
| `doc:LineageTrace` | `prov:Entity` | `rdfs:subClassOf` | Lineage traces are represented as provenance entities in the initial alignment. |
| `doc:derivedFrom` | `prov:wasDerivedFrom` | `rdfs:subPropertyOf` | Safe derivation mapping. |
| `core:usesTool` | `prov:used` | `skos:relatedMatch` | Not a subproperty because the AGENT-O domain/range are agent/tool, not activity/entity. |
| `core:produces` | `prov:generated` | `skos:relatedMatch` | Direction and domain/range are not identical. |
| `core:producesArtifact` | `prov:generated` | `skos:relatedMatch` | Direction and domain/range are not identical. |
| `core:executedInRun` | `prov:wasInformedBy` | `skos:relatedMatch` | Kept as an AGENT-O relation because step/run semantics are agent-specific. |
| `core:performedBy` | `prov:wasAssociatedWith` | `skos:relatedMatch` | Review-event semantics are more specific than PROV association. |
| `eval:derivedFromRun` | `prov:wasGeneratedBy` | `skos:relatedMatch` | Metric results can be connected to runs without replacing AGENT-O evaluation semantics. |
| `core:usesModelDeployment`, `core:usesModelInputArtifact` | `prov:used` | `rdfs:subPropertyOf` | Runtime executions explicitly identify model deployments and model-interface input artifacts. |
| `report:usedReport`, `report:usedReportingProfile` | `prov:used` | `rdfs:subPropertyOf` | Assessment activities identify the report and profile used. |
| `report:generatedAssessment`, `report:generatedByAssessmentActivity` | `prov:generated`, `prov:wasGeneratedBy` | `rdfs:subPropertyOf` | Assessment outputs are linked bidirectionally to their generating activity. |

## Design Decision

PROV-O is used for interoperability and provenance-style querying. It does not replace AGENT-O concepts such as review requirements, automation levels, confidence scores, planners, reasoners, memory modules, or governance policies.
