# AGENT-O Intake Profile Expert Review Checklist

**Review status:** Pending
**Ontology snapshot:** `15ae2eaf5e674114`
**Combined SHA-256:** `15ae2eaf5e6741140f80dcfd13481b5dde9cbdc081bf569648ad1ee21f650e3f`
**Public AGENT-O source commit:** `2cde5dbcd0f73d6c056b4d270fd8c139cd7cd20b`

## Review Record

| Item | Value |
| --- | --- |
| Reviewer | To be completed |
| Role/expertise | To be completed |
| Review date | To be completed |
| Decision | `Approved` / `Approved with changes` / `Revision required` / `Pending` |
| Reviewed application commit | To be completed |

This review confirms whether the chatbot's intake profile is a defensible
application of the frozen AGENT-O snapshot. It does not certify any agent
described with the application.

## Source Contract

Confirm each statement and record exceptions in the findings table.

- [ ] The six files under `ontology/modules/` are the authoritative ontology
  modules; historical ACRO and Figure-only reduced TTLs are excluded.
- [ ] `ontology/agento.ttl` is treated as a generated read-only dependency.
- [ ] The selected reporting profile is
  `https://w3id.org/agent-o/profiles/reporting`, version `2026-08-31`.
- [ ] The root report class is `reporting:AgentCard`.
- [ ] The described system class is `health:HealthAgent`.
- [ ] `reporting:documentsAgentSystem` is the correct report-to-system relation.
- [ ] All three SHACL suites are appropriate for full validation of exported
  Agent Cards.

Run before review:

```bash
cd apps/intake-chatbot
.venv/bin/python scripts/inspect_ontology.py --check --write-report
make test
```

## Semantic Boundaries

- [ ] `AgentCard` and the represented `AgentSystem` remain different entities.
- [ ] `ModelComponent`, `AIModelSpecification`, and `ModelDeployment` remain
  different entities with the expected linking properties.
- [ ] System-level clinical intended use, model intended use, and report-level
  intended-use statements remain distinguishable.
- [ ] Health data sources, input artifacts, FHIR profiles, model inputs and
  outputs, generated outputs, and proposed actions are not collapsed.
- [ ] Evaluation, provenance, governance policy, and reporting assessment are
  represented independently.
- [ ] Present, Partial, Missing, and NotApplicable are treated as controlled
  labels rather than OWL classes.
- [ ] The Agent Card workflow is restricted to concrete existing or planned
  agent systems and does not silently treat other report types as Agent Cards.

## Requirement Catalog

The current catalog contains 50 fields grouped into 11 conversational sections:

| Section | Fields | Review question |
| --- | ---: | --- |
| Card metadata | 2 | Are identity, version, authorship, and review state represented at the correct report level? |
| Agent identity and scope | 3 | Are system identity, purpose, and boundaries sufficient? |
| Intended use and context | 7 | Are users, population, setting, task, decision role, action, and prohibited use separated correctly? |
| Agent architecture | 2 | Are component structure and orchestration represented without flattening? |
| Models and deployments | 15 | Do role, specification, interface, version, provider, and deployment fields preserve model boundaries? |
| Workflow and execution | 4 | Are planning, reasoning, memory, tools, runtime, and execution represented at appropriate levels? |
| Inputs, outputs, and actions | 2 | Are source data, artifacts, outputs, and proposed actions kept distinct? |
| Evaluation | 4 | Are datasets/tasks, comparators, metrics/results, and failure analysis represented? |
| Provenance and reproducibility | 2 | Are evidence, lineage, versions, artifacts, and rerun information sufficient? |
| Governance and safety | 8 | Are accountability, review, escalation, fallback, risk, privacy, security, and compliance covered? |
| Limitations and evidence | 1 | Are limitations and human verification represented without implying certification? |

- [ ] Every SHACL-backed field uses the same `sh:path`, datatype/value class,
  and requiredness as the loaded shape.
- [ ] Profile-backed fields have a defensible ontology property and subject role.
- [ ] Conversational labels and help text preserve ontology meaning.
- [ ] No required field should be downgraded merely to improve completion rates.
- [ ] N/A is allowed only through an explicit user decision and reason.

Machine-readable files to inspect:

```text
config/profile_manifest.yaml
config/intake_fields.yaml
config/dimension_mapping.yaml
config/question_overrides.yaml
docs/DISCOVERY_REPORT.md
```

## Decisions Requiring Explicit Confirmation

Record one decision for each item:

| Question | Decision | Rationale |
| --- | --- | --- |
| Should all 18 profile-required reporting sections block a conformant export, or should some affect completeness only? | Pending |  |
| Is `core:Agent` the intended range for both model developers and deployment providers/operators? | Pending |  |
| Should reporting assessments be embedded in every exported Agent Card or remain in the validation report for the MVP? | Pending |  |
| Are current N/A rules adequate for planned versus deployed systems? | Pending |  |
| Are any institution-specific health-data, governance, or reporting requirements missing from the pilot profile? | Pending |  |

## Findings and Disposition

| Finding ID | Term/field/shape | Finding | Severity | Required change | Owner | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| R01 |  |  |  |  |  |  |

## Sign-Off

By recording an approval decision, the reviewer confirms that the profile map
was reviewed against the identified AGENT-O snapshot and that all findings have
a documented disposition.

**Reviewer:**
**Decision:**
**Date:**
**Notes:**
