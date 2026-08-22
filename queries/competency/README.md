# AGENT-O Competency Queries

The executable SPARQL queries test whether the ontology and example graphs can
answer representation questions rather than merely declare the relevant terms.

| Query | Competency question |
| --- | --- |
| `cq_model_specification_deployment.rq` | Which versioned model specification realizes each model component, what role does it play, what model/reporting fields describe it, and which deployment was used at runtime? |
| `cq_model_interface_layers.rq` | Can agent inputs, model-interface inputs and outputs, deployments, and final agent actions be distinguished? |
| `cq_clinical_intended_use.rq` | What are the intended user, population, setting, specialty, condition, workflow stage, task, intended action, decision role, deployment mode, and excluded or prohibited uses of a clinical agent use case? |
| `cq_report_model_and_intended_use_evidence.rq` | Does an agent-system report provide model identity/version evidence and an intended-use statement? |
| `cq_reporting_assessment_provenance.rq` | Which assessor, report, profile, rubric/prompt versions, evidence, and human-verification status produced an assessment? |
| `cq_report_type_scope.rq` | Can benchmark and other non-system papers be assessed without classifying their subject as a concrete agent system? |

The directory also retains the earlier queries for PROV traces, FHIR inputs,
data-use permissions, governance profile coverage, model-card alignment, and
reporting gaps.
