from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rdflib import Graph, Literal, Namespace, RDF, RDFS, URIRef
from rdflib.namespace import XSD
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import __version__
from app.db.models import AssertionRecord, EntityRecord, SessionRecord


CORE = Namespace("https://w3id.org/agent-o/core#")
DOC = Namespace("https://w3id.org/agent-o/doc#")
EVAL = Namespace("https://w3id.org/agent-o/eval#")
GOV = Namespace("https://w3id.org/agent-o/gov#")
HEALTH = Namespace("https://w3id.org/agent-o/health#")
REPORT = Namespace("https://w3id.org/agent-o/reporting#")


SECTION_TYPES = {
    "metadata": [REPORT.AgentIdentityScopeSection],
    "identity": [REPORT.AgentIdentityScopeSection],
    "intended_use": [REPORT.ClinicalContextSection, REPORT.IntendedUseSection],
    "architecture": [REPORT.RuntimeArchitectureSection, REPORT.ModelComponentsSection],
    "models": [REPORT.ModelSpecificationSection],
    "workflow": [REPORT.ToolUseSection, REPORT.WorkflowSection, REPORT.PlanningReasoningSection],
    "inputs_outputs": [REPORT.InputOutputDataSection],
    "evaluation": [REPORT.EvaluationReportingSection, REPORT.DatasetsMetricsSection, REPORT.AssessmentMethodsSection],
    "provenance": [REPORT.ReproducibilitySection, REPORT.DataUseSection],
    "governance": [
        REPORT.GovernanceReportingSection,
        REPORT.HumanReviewSection,
        REPORT.RiskUncertaintySection,
        REPORT.PrivacySecurityComplianceSection,
        REPORT.DeploymentMonitoringSection,
        REPORT.FailureFallbackSection,
        REPORT.SubgroupEquityEvaluationSection,
    ],
}


def _literal(value: str, datatype_uri: str | None) -> Literal:
    if not datatype_uri:
        return Literal(value)
    return Literal(value, datatype=URIRef(datatype_uri))


def build_graph(db: Session, session: SessionRecord, completeness: dict[str, Any]) -> Graph:
    graph = Graph()
    for prefix, namespace in (
        ("core", CORE), ("doc", DOC), ("eval", EVAL), ("gov", GOV),
        ("health", HEALTH), ("report", REPORT),
    ):
        graph.bind(prefix, namespace)

    entities = list(db.scalars(select(EntityRecord).where(EntityRecord.session_id == session.id)))
    by_id = {item.id: item for item in entities}
    for entity in sorted(entities, key=lambda item: item.stable_uri):
        subject = URIRef(entity.stable_uri)
        graph.add((subject, RDF.type, URIRef(entity.rdf_type_uri)))
        graph.add((subject, RDFS.label, Literal(entity.label, lang="en")))
        if entity.entity_key == "agent":
            graph.add((subject, RDF.type, CORE.AgentSystem))

    assertions = list(
        db.scalars(
            select(AssertionRecord).where(
                AssertionRecord.session_id == session.id,
                AssertionRecord.superseded_at.is_(None),
                AssertionRecord.review_state != "conflict",
            )
        )
    )
    for assertion in assertions:
        subject_entity = by_id.get(assertion.subject_entity_id)
        if not subject_entity:
            continue
        subject = URIRef(subject_entity.stable_uri)
        predicate = URIRef(assertion.predicate_uri)
        if assertion.object_kind == "entity_ref" and assertion.object_entity_id in by_id:
            obj = URIRef(by_id[assertion.object_entity_id].stable_uri)
        elif assertion.object_kind == "iri":
            obj = URIRef(assertion.object_value or "")
        else:
            obj = _literal(assertion.object_value or "", assertion.datatype_uri)
        graph.add((subject, predicate, obj))

    report = next((item for item in entities if item.entity_key == "report"), None)
    use_case = next((item for item in entities if item.entity_key == "use_case"), None)
    if report:
        report_uri = URIRef(report.stable_uri)
        section_status = {item["id"]: item["status"] for item in completeness["sections"]}
        emitted: set[URIRef] = set()
        for section_id, classes in SECTION_TYPES.items():
            if section_status.get(section_id) in {None, "missing", "not_applicable"}:
                continue
            for section_class in classes:
                if section_class in emitted:
                    continue
                emitted.add(section_class)
                section_uri = URIRef(f"{report.stable_uri}:section:{str(section_class).rsplit('#', 1)[-1]}")
                graph.add((report_uri, REPORT.hasReportingSection, section_uri))
                graph.add((section_uri, RDF.type, section_class))
                graph.add((section_uri, RDFS.label, Literal(str(section_class).rsplit("#", 1)[-1], lang="en")))
        if section_status.get("intended_use") not in {None, "missing", "not_applicable"}:
            statement = URIRef(f"{report.stable_uri}:statement:intended-use")
            graph.add((report_uri, REPORT.containsStatement, statement))
            graph.add((statement, RDF.type, REPORT.IntendedUseStatement))
            if use_case:
                graph.add((statement, REPORT.representsInformationElement, URIRef(use_case.stable_uri)))
    return graph


def canonical_card(
    db: Session,
    session: SessionRecord,
    completeness: dict[str, Any],
    validation: dict[str, Any] | None,
) -> dict[str, Any]:
    entities = list(db.scalars(select(EntityRecord).where(EntityRecord.session_id == session.id)))
    assertions = list(
        db.scalars(
            select(AssertionRecord).where(
                AssertionRecord.session_id == session.id,
                AssertionRecord.superseded_at.is_(None),
            )
        )
    )
    return {
        "card_id": session.id,
        "name": session.name,
        "intake_mode": session.intake_mode,
        "profile": {
            "id": session.profile_id,
            "uri": session.profile_uri,
            "version": session.profile_version,
        },
        "ontology_snapshot_id": session.ontology_snapshot_id,
        "review_readiness": completeness["review_readiness"],
        "shacl_conformance": completeness["shacl_conformance"],
        "reporting_completeness": completeness,
        "entities": [
            {
                "id": item.id,
                "key": item.entity_key,
                "uri": item.stable_uri,
                "type_uri": item.rdf_type_uri,
                "label": item.label,
            }
            for item in sorted(entities, key=lambda value: value.stable_uri)
        ],
        "assertions": [
            {
                "id": item.id,
                "field_id": item.field_id,
                "subject_entity_id": item.subject_entity_id,
                "predicate_uri": item.predicate_uri,
                "object_kind": item.object_kind,
                "object_value": item.object_value,
                "object_entity_id": item.object_entity_id,
                "datatype_uri": item.datatype_uri,
                "source_message_id": item.source_message_id,
                "source_evidence": item.source_evidence,
                "confidence": item.extraction_confidence,
                "explicitness": item.explicitness,
                "review_state": item.review_state,
                "user_confirmed": item.user_confirmed,
            }
            for item in sorted(assertions, key=lambda value: (value.field_id, value.created_at))
        ],
        "validation": validation,
    }


def render_markdown(card: dict[str, Any]) -> str:
    lines = [
        f"# {card['name']}",
        "",
        "> This Agent Card documents reported system information. It does not certify agent quality, safety, clinical utility, compliance, or deployment readiness.",
        "",
        "## Status",
        "",
        f"- SHACL conformance: **{card['shacl_conformance'].replace('_', ' ').title()}**",
        f"- Reporting completeness: **{card['reporting_completeness']['reporting_completeness_score']} / 100**",
        f"- Review readiness: **{card['review_readiness'].replace('_', ' ').title()}**",
        "",
    ]
    requirements = card["reporting_completeness"]["requirements"]
    for section in card["reporting_completeness"]["sections"]:
        lines.extend([f"## {section['label']}", ""])
        items = [item for item in requirements if item["section"] == section["id"]]
        for item in items:
            value = item["value"] or "Not reported"
            lines.append(f"- **{item['label']}** ({item['status'].replace('_', ' ').title()}): {value}")
        lines.append("")
    return "\n".join(lines)


def render_validation_markdown(validation: dict[str, Any]) -> str:
    lines = [
        "# Validation Report",
        "",
        f"- Conforms: **{validation['conforms']}**",
        f"- Findings: **{len(validation['results'])}**",
        "",
        "Conformance is a structural validation result. It is not evidence that the agent is safe, clinically effective, compliant, or ready to deploy.",
        "",
    ]
    if validation["results"]:
        lines.extend(["## Findings", ""])
        for item in validation["results"]:
            lines.append(f"- **{item['severity']}** `{item.get('path') or 'node'}`: {item['message']}")
    return "\n".join(lines) + "\n"


def write_export_bundle(
    output_root: Path,
    db: Session,
    session: SessionRecord,
    completeness: dict[str, Any],
    validation: dict[str, Any],
    graph: Graph,
    snapshot: dict[str, Any],
    export_id: str,
    application_commit: str,
) -> tuple[Path, dict[str, Any]]:
    output_dir = output_root / export_id
    output_dir.mkdir(parents=True, exist_ok=False)
    card = canonical_card(db, session, completeness, validation)
    generated_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "card_id": session.id,
        "card_version": next(
            (item["object_value"] for item in card["assertions"] if item["field_id"] == "card_version"),
            "draft",
        ),
        "profile_uri": session.profile_uri,
        "profile_version": session.profile_version,
        "ontology_snapshot_id": session.ontology_snapshot_id,
        "ontology_hashes": snapshot["hashes"],
        "generated_at": generated_at,
        "validation_status": "conformant" if validation["conforms"] else "non_conformant",
        "human_verification_status": "not_human_verified",
        "unresolved_issues_count": completeness["unresolved_required_count"] + len(validation["results"]),
        "application_version": __version__,
        "application_commit": application_commit,
        "prompt_version": "intake-0.1.0",
    }
    files: dict[str, str] = {
        "agent-card.md": render_markdown(card),
        "agent-card.json": json.dumps(card, indent=2, ensure_ascii=True),
        "agent-card.jsonld": graph.serialize(format="json-ld", indent=2),
        "agent-card.ttl": graph.serialize(format="longturtle"),
        "validation-report.json": json.dumps(validation, indent=2, ensure_ascii=True),
        "validation-report.md": render_validation_markdown(validation),
    }
    manifest["files"] = {
        name: {
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "bytes": len(content.encode("utf-8")),
        }
        for name, content in sorted(files.items())
    }
    files["manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=True)
    for name, content in files.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    zip_path = output_root / f"{export_id}.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.write(output_dir / name, arcname=name)
    return zip_path, manifest
