# AGENT-O Semantic Design Revision

The 2026-10-28 revision separates system composition, acting participants,
computational model resources, specification documents, roles and execution
occurrences. It addresses the 18 findings from the preceding design review.
This is a development revision, not an archived release.

Independent reviews prompted follow-up corrections to governance coverage,
assessment-section ownership and SHACL result severity. The October 29 review
also added the migration rules below. Current executable validation results
are published under `outputs/validation/`, `outputs/shacl/` and `outputs/sparql/`;
the regression tests are included in this repository.

## Modeling decisions

- A system contains agents through `hasMemberAgent`; it does not universally
  inherit `Agent`. Shared properties explicitly allow their intended subjects.
  Independently justified collective agency remains possible.
- `AIModelResource` inherits `Model`. `AIModelSpecification` is a document
  linked to that resource by `specifiesModel`. Model types classify resources.
- Components, their roles, resources, deployments and documents have separate
  identities. A model card does not universally inherit system documentation.
- EHR origin, FHIR representation, source identity and data structure are
  independent axes. Mixed structured and unstructured artifacts are allowed.
- Governance requirements reference principles rather than inheriting them.
  Evaluation activities produce separate result records.
- Report types can overlap. Profiles refer to schema terms through annotations;
  actual reports contain section instances. Declared profiles have an explicit
  SHACL section-presence check.
- Controlled completeness and verification labels have enumerated SHACL
  constraints. A step occurrence cannot belong to two execution runs.
- High-risk governance checks cover both actors and systems. Assessments link
  only to sections belonging to their assessed report; Missing and
  NotApplicable may omit a nonexistent section while retaining the dimension.
  Present and Partial require an actual section. Reporting-gap queries retain
  missing-section assessments, and advisory SPARQL checks produce Warnings.

The canonical patterns and the definitions in the six module files specify the
scope of these choices. Every active named class now has a textual definition.

## RDF migration

This revision deliberately changes the earlier interpretation of
`AIModelSpecification`. Earlier graphs used that class for checkpoints and
versioned computational models. Those **resource instances** must be migrated
to `AIModelResource`; use the retained `AIModelSpecification` class only for
actual specification documents. There is no equivalence axiom between them.

| Earlier term or assertion | Revised representation |
| --- | --- |
| Resource typed `AIModelSpecification` | Type the computational resource as `AIModelResource` |
| `realizesModelSpecification` | `usesModelResource` |
| `realizedByModelComponent` | `usedByModelComponent` |
| `deploysModelSpecification` | `deploysModelResource` |
| `hasBaseModelSpecification` | `hasBaseModelResource` |
| `describesModelSpecification` | `describesModelResource` |
| System typed `HealthAgent` or a clinical/patient-facing agent subtype | Use the corresponding `*AgentSystem` class; keep actual acting participants as agents |
| EHR-derived input assumed to be FHIR | Assert `FHIRResourceInput` only when represented by or mapped to FHIR |
| Requirement instance reused as an ethical principle | Use a requirement and a separate principle connected by `basedOnPrinciple` |
| A profile's section class treated as an actual section | Keep the class reference as metadata; create a report-section instance separately |
| General `generates` assumed to imply ProposedAction | Use `producesProposedAction` or an explicit action type when a recommendation is intended |
| Configured policy control represented as `triggersEscalation` / EscalationEvent | Use `hasEscalationPlan` / EscalationPlan; retain events for actual occurrences |
| Configured override represented as `enablesOverride` / OverrideAction | Use `hasOverrideCapability` / OverrideCapability |
| Prospective plan using `triggeredBy` or `escalatesTo` | Use `hasTriggerCondition` and `plannedRecipient` |
| Override capability using `overridesAction` | Use `canOverrideAction`; retain the former for actual override occurrences |
| System-level review requirement linked with `requiresReview` | Use `hasGovernanceRequirement` and a HumanReviewRequirement; `requiresReview` belongs on a ProposedAction |

An assessment's report must also be an input of its generating activity.
Previously stored RDF graphs require migration before claiming conformance
to this revision; publishing the revised ontology does not rewrite those graphs.

The 279-paper v2.2.3 reporting-completeness scores and human-calibration status
are historical assessment outputs. This ontology revision does not rerun or
revalidate those scientific results, and current schema counts must not be
presented as counts from that earlier frozen ontology.

## Validation and future edits

Run from the repository root with its requirements and test dependencies:

```bash
python3 scripts/build_integrated_ontology.py
python3 scripts/validate_ontology.py
python3 scripts/run_shacl_validation.py
python3 scripts/run_sparql_cqs.py
python3 scripts/generate_alignment_matrix.py
python3 -m pytest -q
```

`tests/test_semantic_design.py` exercises the counterexamples and necessary
identity separations. The tests include forbidden type inferences, overlapping
reports, mixed health artifacts, required-section presence and controlled-value
rejection.

Inventory counts now report named entities separately from anonymous class
expressions. See `outputs/validation/formal_quality_results.json` for current
metrics and `outputs/shacl/` and `outputs/sparql/` for executable evidence.

For each future subclass change, state why every child instance is a parent
instance and test a nearby counterexample. For each property change, inspect
the types inferred for both ends, including external superproperties. Formal
validation and OWL-RL tests do not establish a complete OWL 2 DL consistency
proof over all external imports or replace expert domain-content review.
