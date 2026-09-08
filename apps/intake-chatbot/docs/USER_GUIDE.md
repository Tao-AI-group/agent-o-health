# User Guide

## What the Tool Does

AGENT-O Agent Card Intake helps document a health-oriented AI agent in a
structured, traceable format. It identifies what has been reported, what still
needs clarification, and whether the generated RDF conforms to selected
AGENT-O SHACL constraints.

It does not decide whether an agent is accurate, safe, clinically useful,
compliant, or ready to deploy.

## Start a Card

Choose one mode:

- **Describe an existing agent** for an implemented or currently used system.
- **Document a planned agent** for a proposed architecture or governance plan.
- **Import structured information** to start from text, Markdown, JSON, JSON-LD,
  YAML, or Turtle.

The first answer can describe several topics at once: purpose, intended users,
workflow, models, tools, deployment, evaluation, and governance. Unknown details
can be left for later.

## Conversation Actions

- **Send message** submits the current answer.
- **Stop response** stops the active browser stream; saved server state is not lost.
- **I don't know** prepares that answer for the current question.
- **Not applicable** requires a reason and records an applicability decision.
- **Skip for now** leaves the requirement unresolved and records the skip event.
- **Review extracted facts** opens the reporting-section view.
- **Undo last update** reverses the latest applied patch.
- **Retry last message** appears after a language/extraction error.

The assistant usually asks one topic with one to three related details. A single
answer may populate several fields.

## Card Inspector

- **Overview** separates SHACL conformance, reporting completeness, and review readiness.
- **Sections** shows Present, Partial, Missing, and Not applicable requirements.
- **Issues** runs or displays SHACL validation findings.
- **Preview** shows the human-readable Card draft.
- **History** shows value, evidence, confidence, review state, and ontology property.

Click a requirement in Sections to confirm or edit its value. A direct edit is
stored as a confirmed human assertion with provenance.

## Imports

Imported material is untrusted source content. The application extracts only
candidate facts and ignores instructions embedded in the document. Candidate
assertions are Partial and `needs_confirmation` until reviewed in the Card
Inspector. Unsupported extensions, paths in filenames, and oversized files are
rejected. PDF and DOCX are not supported in the MVP.

## Conflicts

If a new answer contradicts a confirmed value, the new assertion is marked as a
conflict rather than silently replacing the prior value. State the correction
explicitly or edit the field in the Inspector. The correction becomes confirmed
and the previous values remain in audit history.

## Validate

Select **Validate** to build the RDF graph and run all active architecture,
governance, and reporting SHACL suites. Findings show severity, message, and
ontology path. Conformance is structural only and is not a safety certification.

If an ontology snapshot has changed, migrate the session explicitly before
validation. Migration verifies that existing predicates still belong to the
active ontology catalog.

## Export

Select **Export** and choose:

- **Download draft** to export the current state with missing fields and findings.
- **Download conformant bundle** to require no unresolved required fields and a
  conformant SHACL result.

The ZIP contains the Agent Card in Markdown, JSON, JSON-LD, and Turtle, plus
machine- and human-readable validation reports and a manifest with versions,
ontology hashes, file checksums, and unresolved-issue count.

## Privacy

Do not enter patient identifiers or PHI unless the deployment has been approved
for that use. Delete a session from the Inspector when its local record is no
longer needed. Ask the deployment owner about access, retention, and backups.
