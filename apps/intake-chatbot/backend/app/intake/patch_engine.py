from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    ApplicabilityRecord,
    AssertionRecord,
    EntityRecord,
    PatchEventRecord,
    SessionRecord,
)
from app.intake.catalog import FieldDefinition, IntakeCatalog
from app.ontology.loader import OntologyBundle
from app.schemas.api import ExtractionOperation


CORE = "https://w3id.org/agent-o/core#"
HEALTH = "https://w3id.org/agent-o/health#"
REPORT = "https://w3id.org/agent-o/reporting#"
EVAL = "https://w3id.org/agent-o/eval#"
GOV = "https://w3id.org/agent-o/gov#"

SUBJECT_TYPES = {
    "report": REPORT + "AgentCard",
    "agent": HEALTH + "HealthAgent",
    "use_case": HEALTH + "ClinicalUseCase",
    "component": CORE + "ModelComponent",
    "model_spec": CORE + "AIModelSpecification",
    "model_deployment": CORE + "ModelDeployment",
    "execution": CORE + "ExecutionRun",
    "evaluation": EVAL + "EvaluationStudy",
    "metric_result": EVAL + "MetricResult",
    "policy": GOV + "Policy",
}

SYSTEM_LINKS = {
    "agent": ("report", "agent", REPORT + "documentsAgentSystem"),
    "use_case": ("agent", "use_case", HEALTH + "hasIntendedClinicalUse"),
    "component": ("agent", "component", CORE + "hasComponent"),
    "model_spec": ("component", "model_spec", CORE + "realizesModelSpecification"),
    "execution": ("agent", "execution", CORE + "hasSystemExecution"),
    "model_deployment": ("execution", "model_deployment", CORE + "usesModelDeployment"),
    "evaluation": ("evaluation", "agent", EVAL + "evaluates"),
    "metric_result": ("evaluation", "metric_result", EVAL + "producesResult"),
    "policy": ("policy", "agent", GOV + "constrains"),
}


def _id() -> str:
    return str(uuid.uuid4())


def _entity(db: Session, session_id: str, key: str) -> EntityRecord | None:
    return db.scalar(
        select(EntityRecord).where(
            EntityRecord.session_id == session_id, EntityRecord.entity_key == key
        )
    )


def ensure_entity(db: Session, session_id: str, key: str) -> EntityRecord:
    existing = _entity(db, session_id, key)
    if existing:
        return existing
    if key not in SUBJECT_TYPES:
        raise ValueError(f"Unknown subject reference: {key}")
    entity = EntityRecord(
        id=_id(),
        session_id=session_id,
        entity_key=key,
        rdf_type_uri=SUBJECT_TYPES[key],
        stable_uri=f"urn:uuid:{_id()}",
        label=key.replace("_", " ").title(),
    )
    db.add(entity)
    db.flush()
    if key in SYSTEM_LINKS:
        subject_key, object_key, predicate = SYSTEM_LINKS[key]
        subject = entity if subject_key == key else ensure_entity(db, session_id, subject_key)
        object_entity = entity if object_key == key else ensure_entity(db, session_id, object_key)
        link_id = f"_system_{subject_key}_{object_key}"
        already = db.scalar(
            select(AssertionRecord).where(
                AssertionRecord.session_id == session_id,
                AssertionRecord.field_id == link_id,
                AssertionRecord.superseded_at.is_(None),
            )
        )
        if not already:
            db.add(
                AssertionRecord(
                    id=_id(),
                    session_id=session_id,
                    field_id=link_id,
                    subject_entity_id=subject.id,
                    predicate_uri=predicate,
                    object_kind="entity_ref",
                    object_value=object_entity.label,
                    object_entity_id=object_entity.id,
                    source_evidence="Created by deterministic entity linkage.",
                    review_state="system",
                    user_confirmed=True,
                )
            )
    if key == "model_deployment":
        spec = ensure_entity(db, session_id, "model_spec")
        db.add(
            AssertionRecord(
                id=_id(), session_id=session_id, field_id="_system_deployment_spec",
                subject_entity_id=entity.id, predicate_uri=CORE + "deploysModelSpecification",
                object_kind="entity_ref", object_value=spec.label, object_entity_id=spec.id,
                source_evidence="Created by deterministic entity linkage.", review_state="system",
                user_confirmed=True,
            )
        )
    return entity


def bootstrap_session_entities(db: Session, session_id: str) -> None:
    ensure_entity(db, session_id, "report")
    ensure_entity(db, session_id, "agent")


def active_assertions(db: Session, session_id: str, field_id: str | None = None) -> list[AssertionRecord]:
    query = select(AssertionRecord).where(
        AssertionRecord.session_id == session_id,
        AssertionRecord.superseded_at.is_(None),
    )
    if field_id is not None:
        query = query.where(AssertionRecord.field_id == field_id)
    return list(db.scalars(query.order_by(AssertionRecord.created_at)))


def current_values(db: Session, session_id: str) -> dict[str, str]:
    return {
        item.field_id: item.object_value or ""
        for item in active_assertions(db, session_id)
        if not item.field_id.startswith("_system_")
    }


def validate_operation(
    operation: ExtractionOperation,
    field: FieldDefinition,
    ontology: OntologyBundle,
    source_message: str,
) -> None:
    if operation.subject_ref != field.subject:
        raise ValueError(f"Subject mismatch for {field.id}")
    if operation.predicate_uri != field.predicate_uri:
        raise ValueError(f"Predicate mismatch for {field.id}")
    if operation.object.kind != field.object_kind:
        raise ValueError(f"Object kind mismatch for {field.id}")
    if operation.object.datatype and operation.object.datatype != field.datatype_uri:
        raise ValueError(f"Datatype mismatch for {field.id}")
    ontology.assert_allowed([operation.predicate_uri])
    if operation.source_evidence not in source_message:
        raise ValueError(f"Evidence for {field.id} is not an exact span of the current message")
    value = operation.object.value.strip()
    if not value:
        raise ValueError(f"Empty value for {field.id}")
    if field.datatype_uri:
        _validate_lexical_form(field.id, value, field.datatype_uri)


def _validate_lexical_form(field_id: str, value: str, datatype_uri: str) -> None:
    local_name = datatype_uri.rsplit("#", 1)[-1]
    try:
        if local_name == "date":
            date.fromisoformat(value)
        elif local_name == "dateTime":
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        elif local_name in {"decimal", "double", "float"}:
            Decimal(value)
        elif local_name in {"integer", "int", "long", "nonNegativeInteger"}:
            number = int(value)
            if local_name == "nonNegativeInteger" and number < 0:
                raise ValueError
        elif local_name == "boolean" and value.lower() not in {"true", "false", "1", "0"}:
            raise ValueError
    except (ValueError, InvalidOperation) as exc:
        raise ValueError(f"Invalid {local_name} value for {field_id}") from exc


def apply_operations(
    db: Session,
    session: SessionRecord,
    operations: Iterable[ExtractionOperation],
    catalog: IntakeCatalog,
    ontology: OntologyBundle,
    source_message_id: str,
    source_message: str,
    allow_replace: bool,
) -> dict[str, object]:
    added: list[str] = []
    superseded: list[str] = []
    conflicts: list[str] = []
    for operation in operations:
        if operation.field_id not in catalog.by_id:
            raise ValueError(f"Unknown field ID: {operation.field_id}")
        field = catalog.by_id[operation.field_id]
        validate_operation(operation, field, ontology, source_message)
        existing = active_assertions(db, session.id, field.id)
        existing_value = existing[-1].object_value if existing else None
        value = operation.object.value.strip()
        resolving_review = allow_replace and any(
            item.review_state in {"conflict", "needs_confirmation"} or not item.user_confirmed
            for item in existing
        )
        if existing_value == value and not resolving_review:
            continue
        if existing and not allow_replace:
            review_state = "conflict"
            conflicts.append(field.id)
        else:
            review_state = "needs_confirmation" if operation.requires_confirmation else "confirmed"
            for item in existing:
                item.superseded_at = datetime.now(timezone.utc)
                superseded.append(item.id)

        subject = ensure_entity(db, session.id, field.subject)
        object_entity_id = None
        if field.object_kind == "entity_ref":
            object_entity = EntityRecord(
                id=_id(),
                session_id=session.id,
                entity_key=f"value:{field.id}:{_id()}",
                rdf_type_uri=field.object_type_uri or "",
                stable_uri=f"urn:uuid:{_id()}",
                label=value,
            )
            db.add(object_entity)
            db.flush()
            object_entity_id = object_entity.id
        assertion = AssertionRecord(
            id=_id(),
            session_id=session.id,
            field_id=field.id,
            subject_entity_id=subject.id,
            predicate_uri=field.predicate_uri,
            object_kind=field.object_kind,
            object_value=value,
            object_entity_id=object_entity_id,
            datatype_uri=field.datatype_uri,
            source_message_id=source_message_id,
            source_evidence=operation.source_evidence,
            extraction_confidence=operation.confidence,
            explicitness=operation.explicitness,
            review_state=review_state,
            user_confirmed=not operation.requires_confirmation,
        )
        db.add(assertion)
        db.flush()
        added.append(assertion.id)

    if added or superseded:
        db.add(
            PatchEventRecord(
                id=_id(),
                session_id=session.id,
                event_type="patch",
                payload_json=json.dumps({"added": added, "superseded": superseded, "conflicts": conflicts}),
                inverse_json=json.dumps({"supersede": added, "restore": superseded}),
            )
        )
    return {"added": len(added), "superseded": len(superseded), "conflicts": conflicts}


def mark_not_applicable(
    db: Session,
    session: SessionRecord,
    field_id: str,
    reason: str,
    source_message_id: str | None,
) -> None:
    existing = db.scalar(
        select(ApplicabilityRecord).where(
            ApplicabilityRecord.session_id == session.id,
            ApplicabilityRecord.requirement_id == field_id,
        )
    )
    if existing:
        existing.status = "not_applicable"
        existing.reason = reason
        existing.source = "user"
        existing.source_message_id = source_message_id
    else:
        db.add(
            ApplicabilityRecord(
                id=_id(), session_id=session.id, requirement_id=field_id,
                status="not_applicable", reason=reason, source="user",
                source_message_id=source_message_id,
            )
        )
    db.add(
        PatchEventRecord(
            id=_id(), session_id=session.id, event_type="not_applicable",
            payload_json=json.dumps({"field_id": field_id, "reason": reason}), inverse_json="{}",
        )
    )


def skip_field(db: Session, session: SessionRecord, field_id: str) -> None:
    db.add(
        PatchEventRecord(
            id=_id(), session_id=session.id, event_type="skip",
            payload_json=json.dumps({"field_id": field_id}), inverse_json="{}",
        )
    )


def undo_last_patch(db: Session, session_id: str) -> bool:
    event = db.scalar(
        select(PatchEventRecord)
        .where(
            PatchEventRecord.session_id == session_id,
            PatchEventRecord.event_type == "patch",
            PatchEventRecord.undone.is_(False),
        )
        .order_by(PatchEventRecord.created_at.desc())
    )
    if not event:
        return False
    inverse = json.loads(event.inverse_json)
    now = datetime.now(timezone.utc)
    for assertion_id in inverse.get("supersede", []):
        assertion = db.get(AssertionRecord, assertion_id)
        if assertion:
            assertion.superseded_at = now
    for assertion_id in inverse.get("restore", []):
        assertion = db.get(AssertionRecord, assertion_id)
        if assertion:
            assertion.superseded_at = None
    event.undone = True
    db.add(
        PatchEventRecord(
            id=_id(), session_id=session_id, event_type="undo",
            payload_json=json.dumps({"undid_event": event.id}), inverse_json="{}",
        )
    )
    return True
