# AGENT-O Competency Queries

The executable SPARQL queries test whether the ontology and example graphs can
answer representation questions rather than merely declare the relevant terms.

| CQ ID | Query file | Competency question |
| --- | --- | --- |
| CQ1 | `cq_model_specification_deployment.rq` | Which versioned model specification realizes each model component, what role does it play, what descriptive fields characterize it, and which deployment was used at runtime? |
| CQ2 | `cq_model_interface_layers.rq` | Can agent-level inputs, model deployments, generated model outputs, and final agent actions be distinguished? |
| CQ3 | `cq_clinical_intended_use.rq` | What are the intended user, population, setting, specialty, condition, workflow stage, task, intended action, decision role, deployment mode, and excluded or prohibited uses of a clinical agent use case? |
| CQ4 | `cq_fhir_inputs.rq` | Which inputs are aligned with FHIR resources, profiles, formats, and terminology systems, and how are they connected to agents or recommendations? |
| CQ5 | `cq_data_use_permissions.rq` | Which datasets have data-use conditions, permissions, restrictions, or governing policies? |
| CQ6 | `cq_governance_profile_checklist.rq` | Which automation, accountability, policy, risk, review, fallback, escalation, monitoring, and compliance elements are represented for clinical agents? |
| CQ7 | `cq_model_card_alignment.rq` | Which model-card document describes the versioned model specification used by each model component, and which agent-system report cites it? |
| CQ8 | `cq_report_model_and_intended_use_evidence.rq` | Does an agent-system report provide model identity/version evidence and an intended-use statement about the same clinical use case? |
| CQ9 | `cq_prov_trace.rq` | Which source entities support a proposed action, which activity generated each source, who was associated with it, and which metric result came from the same run? |
| CQ10 | `cq_reporting_assessment_provenance.rq` | Which assessor, report, profile, rubric/prompt versions, evidence, and human-verification status produced a reporting assessment? |
| CQ11 | `cq_reporting_gaps.rq` | Which report sections are partial or missing, what evidence supports the assessment, and what correction is recommended? |
| CQ12 | `cq_report_type_scope.rq` | Can benchmark and other non-system papers be assessed without classifying their subject as a concrete agent system? |

The stable CQ identifiers above are used in the manuscript supplementary table.
An executable query is considered answered when it returns at least one row
containing the prespecified evidence type from the reasoned example graph.
