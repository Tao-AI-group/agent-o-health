from __future__ import annotations

from collections import Counter
from typing import Any

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import ApplicabilityRecord, AssertionRecord, ValidationRunRecord
from app.intake.catalog import IntakeCatalog


LABEL_FRACTIONS = {
    "present": 1.0,
    "partial": 0.5,
    "missing": 0.0,
    "not_applicable": 0.0,
}


def compute_completeness(
    db: Session,
    session_id: str,
    catalog: IntakeCatalog,
    manifest: dict[str, Any],
    dimension_mapping_path,
) -> dict[str, Any]:
    active = list(
        db.scalars(
            select(AssertionRecord).where(
                AssertionRecord.session_id == session_id,
                AssertionRecord.superseded_at.is_(None),
                ~AssertionRecord.field_id.startswith("_system_"),
            )
        )
    )
    by_field: dict[str, list[AssertionRecord]] = {}
    for assertion in active:
        by_field.setdefault(assertion.field_id, []).append(assertion)
    applicability = {
        item.requirement_id: item
        for item in db.scalars(
            select(ApplicabilityRecord).where(ApplicabilityRecord.session_id == session_id)
        )
    }

    requirements = []
    for field in catalog.fields:
        decision = applicability.get(field.id)
        assertions = by_field.get(field.id, [])
        if decision and decision.status == "not_applicable":
            label = "not_applicable"
        elif not assertions:
            label = "missing"
        elif any(
            item.review_state in {"conflict", "needs_confirmation"} or not item.user_confirmed
            for item in assertions
        ):
            label = "partial"
        else:
            label = "present"
        requirements.append(
            {
                "id": field.id,
                "section": field.section,
                "label": field.label,
                "status": label,
                "required": field.required,
                "source": field.source,
                "question": field.question,
                "ontology_term": field.predicate_uri,
                "value": assertions[-1].object_value if assertions else None,
                "confidence": assertions[-1].extraction_confidence if assertions else None,
                "review_state": assertions[-1].review_state if assertions else None,
                "applicability_reason": decision.reason if decision else None,
            }
        )

    sections = []
    for section in sorted(manifest["sections"], key=lambda value: value["order"]):
        items = [item for item in requirements if item["section"] == section["id"]]
        counts = Counter(item["status"] for item in items)
        applicable = [item for item in items if item["status"] != "not_applicable"]
        if applicable and all(item["status"] == "present" for item in applicable):
            status = "present"
        elif applicable and all(item["status"] == "missing" for item in applicable):
            status = "missing"
        elif not applicable:
            status = "not_applicable"
        else:
            status = "partial"
        sections.append(
            {
                "id": section["id"],
                "label": section["label"],
                "description": section["description"],
                "order": section["order"],
                "status": status,
                "counts": dict(counts),
                "total": len(items),
            }
        )

    dimensions_config = yaml.safe_load(dimension_mapping_path.read_text(encoding="utf-8"))["dimensions"]
    section_by_id = {item["id"]: item for item in sections}
    dimensions = []
    numerator = 0.0
    denominator = 0.0
    for dimension_id, config in dimensions_config.items():
        statuses = [
            section_by_id[section_id]["status"]
            for section_id in config["sections"]
            if section_id in section_by_id
        ]
        applicable = [status for status in statuses if status != "not_applicable"]
        fraction = (
            sum(LABEL_FRACTIONS[status] for status in applicable) / len(applicable)
            if applicable
            else None
        )
        weight = float(config["weight"])
        if fraction is not None:
            numerator += weight * fraction
            denominator += weight
        dimensions.append(
            {
                "id": dimension_id,
                "label": config["label"],
                "weight": weight,
                "fraction": fraction,
                "score": round(weight * fraction, 2) if fraction is not None else None,
            }
        )

    latest_validation = db.scalar(
        select(ValidationRunRecord)
        .where(ValidationRunRecord.session_id == session_id)
        .order_by(ValidationRunRecord.completed_at.desc())
    )
    unresolved = [
        item
        for item in requirements
        if item["required"] and item["status"] in {"missing", "partial"}
    ]
    conflicts = [item for item in requirements if item["review_state"] == "conflict"]
    needs_confirmation = [
        item for item in requirements if item["review_state"] == "needs_confirmation"
    ]
    if conflicts or needs_confirmation:
        readiness = "needs_user_confirmation"
    elif not unresolved:
        readiness = "ready_for_human_review"
    else:
        readiness = "draft"
    return {
        "requirements": requirements,
        "sections": sections,
        "dimensions": dimensions,
        "reporting_completeness_score": round(100 * numerator / denominator, 1)
        if denominator
        else None,
        "score_interpretation": (
            "Publication-level reporting coverage only; this is not an agent quality, "
            "safety, clinical utility, or deployment readiness score."
        ),
        "shacl_conformance": (
            "conformant"
            if latest_validation and latest_validation.conforms
            else "non_conformant"
            if latest_validation
            else "not_yet_validated"
        ),
        "review_readiness": readiness,
        "unresolved_required_count": len(unresolved),
        "conflict_count": len(conflicts),
    }
