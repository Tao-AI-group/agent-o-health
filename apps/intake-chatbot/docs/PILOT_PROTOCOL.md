# Deidentified Internal Pilot Protocol

## Purpose

This pilot evaluates whether an internal user without ontology expertise can
independently create, review, validate, and export an AGENT-O Agent Card. It
evaluates usability and reporting workflow fit. It does not evaluate the
clinical quality, safety, effectiveness, compliance, or deployment readiness
of the described agent.

## Entry Criteria

Run the pilot only after all of the following are true:

- `make ontology-check`, `make test`, `make build`, and `make e2e` pass.
- The deployment uses TLS and an access-control mechanism approved by the
  deployment owner.
- Session retention, access, backup, and deletion policies are documented.
- Pilot participants have been told not to enter patient identifiers or PHI.
- Each use-case owner has reviewed the intake brief and confirmed that it is
  deidentified.

## Participants

Recruit 3-5 participants across the intended roles when feasible:

| Role | Target | Primary perspective |
| --- | ---: | --- |
| Agent developer or technical lead | 1-2 | Architecture, models, tools, and runtime |
| Evaluator or researcher | 1 | Datasets, metrics, failures, and reproducibility |
| Governance or clinical reviewer | 1 | Oversight, escalation, privacy, and intended use |
| Ontology curator | 0-1 | Term fit, entity boundaries, and validation findings |

A participant should not receive step-by-step assistance during the primary
task. Assistance may be given afterward and must be recorded.

## Use-Case Sampling

Select 3-5 real internal agent projects, using only deidentified system-level
information. Aim to cover the following categories:

| Case ID | Required category | Selected project | Owner | Deidentification confirmed |
| --- | --- | --- | --- | --- |
| P01 | Single-agent tool use | To be assigned | To be assigned | Pending |
| P02 | Multi-agent workflow | To be assigned | To be assigned | Pending |
| P03 | Clinical intended use | To be assigned | To be assigned | Pending |
| P04 | Non-deployed research prototype | To be assigned | To be assigned | Pending |
| P05 | Governance-heavy system | To be assigned | To be assigned | Pending |

One project may satisfy more than one category. Do not use patient examples,
clinical notes, screenshots containing identifiers, credentials, private
endpoints, or proprietary source text that is not approved for the pilot.

## Standard Task

Give each participant the deployment URL and the following neutral instruction:

> Create an AGENT-O Agent Card for the assigned agent. Describe the system in
> your own words, review the extracted facts, resolve or defer fields as
> appropriate, run validation, and export the draft. Stop when you believe the
> Card accurately represents what is currently known.

The observer may answer questions about access or a software failure but should
not explain ontology terms or tell the participant which values to enter during
the primary task.

## Procedure

1. Record participant role, case ID, browser, deployment version, AGENT-O
   snapshot, and start time in `PILOT_RESULTS_TEMPLATE.md`.
2. Confirm that the participant understands the no-PHI/no-credentials rule.
3. Ask the participant to create a session and complete the standard task.
4. Record completion time, assistance, errors, abandoned steps, and whether an
   export bundle was produced.
5. Ask the participant to explain the difference among reporting completeness,
   SHACL conformance, and review readiness.
6. Collect the post-task ratings and open feedback.
7. Delete or retain the session according to the approved pilot retention rule.
8. Review findings after all participants finish; do not alter earlier records.

## Measures

Required measures:

- Task completion without step-by-step assistance: yes/no.
- Session created, restored, renamed, validated, and exported: yes/no per step.
- Time to first structured assertion and time to completed export.
- Number of software errors, blocked tasks, and requests for ontology help.
- Participant understanding of the three independent status concepts.
- Five-point ratings for ease of use, question clarity, extracted-fact review,
  validation clarity, export usefulness, and overall confidence in the Card.
- Free-text observations, confusing terms, missing fields, and recommended fixes.

Optional research metrics must remain disabled unless the study owner has
approved their collection. Do not collect raw keystrokes, hidden prompts, or
unnecessary message content.

## Pilot Exit Criteria

The MVP pilot passes when:

- At least three deidentified real use cases are completed.
- Every participant can produce an export bundle.
- At least one participant without ontology expertise completes the task
  independently.
- No credential, PHI, or restricted endpoint information appears in the UI,
  logs, database export, screenshots, or Git.
- No blocker prevents session creation, conversation, review, validation, or
  draft export.
- Observed terminology or workflow issues are triaged as fixed, accepted for
  the MVP, or assigned with an owner and rationale.

Passing the pilot does not certify the represented agents. It only supports the
usability and operational readiness of the reporting-intake workflow.
