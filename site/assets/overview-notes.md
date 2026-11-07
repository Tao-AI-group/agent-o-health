# AGENT-O engineering-review overview

Prepared 2026-11-05 from the six authoritative ontology modules.

- [Vector PDF](agent-o_engineer_overview.pdf)
- [Editable SVG](agent-o_engineer_overview.svg)
- [Source hashes and checked relationships](overview-source-manifest.json)
- [Complete term reference](../terms.html)

## Caption

**Selected AGENT-O relationships for engineering review.** (A) A configured
system contains acting participants and functional components; model resources,
component roles, model specifications and deployments have separate identities.
(B) Evaluation studies select targets and produce metric results. (C) Policies
specify escalation plans and override capabilities. (D) Reporting-assessment
activities use publications and generate reporting-completeness assessments.
(E) Intended clinical use connects a system to its clinical context and population
specification. Solid arrows summarize object-property links between instances;
dashed arrows with hollow heads show subclass-to-parent relationships. Boxes
denote classes, and repeated boxes refer to the same class.

## Interpretation

The diagram shows 23 distinct classes and 20 checked relationships. It is a
selected schema view. Panels are explanatory groups, not additional classes
or containment axioms. Namespace prefixes are printed on every node. The
original handout's box fills provide visual emphasis; the website's module
cards and interactive explorer use consistent namespace colors.

Object-property arrows do not themselves impose existence or cardinality
requirements. The ontology separately requires an AgentSystem to have some
Agent member, possibly unnamed under the open-world assumption. A configured
system need not have past runs. Model specifications are Documents; model
resources are Models. Prospective controls remain distinct from actual events.
Clinical-context links concern intended use. Reporting completeness concerns
publication coverage.

The canvas is 400 × 320 mm for review and zoomable reading. Detailed workflow
steps, tools, evidence, human review, reporting profiles, constraints and external
alignments are available in the full ontology rather than this selected figure.

For feedback, give a concrete system example and identify the distinction,
relationship or missing concept that prevents an accurate representation.
