from __future__ import annotations

import json
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import PROJECT_ROOT
from app.db.models import (
    ApplicabilityRecord,
    AssertionRecord,
    EntityRecord,
    ExportRecord,
    MessageRecord,
    PatchEventRecord,
    SessionRecord,
    ValidationRunRecord,
)
from app.intake.completeness import compute_completeness
from app.intake.patch_engine import (
    active_assertions,
    apply_operations,
    bootstrap_session_entities,
    current_values,
    mark_not_applicable,
    skip_field,
    undo_last_patch,
)
from app.intake.planner import choose_next
from app.ontology.exporter import build_graph, canonical_card, write_export_bundle
from app.ontology.validator import validate_graph
from app.schemas.api import CardFieldUpdate, ExtractionOperation
from app.services.resources import AppResources


WELCOME = (
    "This intake creates a structured AGENT-O Agent Card. It assesses reporting "
    "completeness and ontology conformance; it does not judge agent quality, safety, "
    "clinical effectiveness, compliance, or deployment readiness. Do not enter patient "
    "identifiers or PHI unless this deployment has been institutionally approved."
)

OPENING_QUESTION = (
    "Please describe the agent, its purpose, intended users, main workflow, models, "
    "tools, and current deployment status. It is okay if some details are unknown."
)


def new_id() -> str:
    return str(uuid.uuid4())


def get_session(db: Session, session_id: str) -> SessionRecord:
    record = db.get(SessionRecord, session_id)
    if not record:
        raise LookupError("Session not found")
    return record


def add_message(db: Session, session_id: str, role: str, content: str, status: str = "complete") -> MessageRecord:
    record = MessageRecord(
        id=new_id(), session_id=session_id, role=role, content=content, status=status
    )
    db.add(record)
    db.flush()
    return record


def create_card_session(db: Session, resources: AppResources, name: str, intake_mode: str) -> SessionRecord:
    manifest = resources.ontology.manifest["profile"]
    record = SessionRecord(
        id=new_id(),
        name=name,
        intake_mode=intake_mode,
        profile_id=manifest["id"],
        profile_uri=manifest["uri"],
        profile_version=manifest["version"],
        ontology_snapshot_id=resources.ontology.snapshot["id"],
    )
    db.add(record)
    db.flush()
    bootstrap_session_entities(db, record.id)
    add_message(db, record.id, "assistant", f"{WELCOME}\n\n{OPENING_QUESTION}")
    return record


def completeness_for(db: Session, resources: AppResources, session_id: str) -> dict[str, Any]:
    return compute_completeness(
        db,
        session_id,
        resources.catalog,
        resources.ontology.manifest,
        PROJECT_ROOT / "config" / "dimension_mapping.yaml",
    )


def message_dict(item: MessageRecord) -> dict[str, Any]:
    return {
        "id": item.id,
        "role": item.role,
        "content": item.content,
        "status": item.status,
        "created_at": item.created_at.isoformat(),
    }


def assertion_dict(db: Session, item: AssertionRecord) -> dict[str, Any]:
    subject = db.get(EntityRecord, item.subject_entity_id)
    obj = db.get(EntityRecord, item.object_entity_id) if item.object_entity_id else None
    return {
        "id": item.id,
        "field_id": item.field_id,
        "subject": {"id": subject.id, "label": subject.label, "type_uri": subject.rdf_type_uri} if subject else None,
        "predicate_uri": item.predicate_uri,
        "object_kind": item.object_kind,
        "value": item.object_value,
        "object_entity": {"id": obj.id, "label": obj.label, "type_uri": obj.rdf_type_uri} if obj else None,
        "source_message_id": item.source_message_id,
        "source_evidence": item.source_evidence,
        "confidence": item.extraction_confidence,
        "explicitness": item.explicitness,
        "review_state": item.review_state,
        "user_confirmed": item.user_confirmed,
        "created_at": item.created_at.isoformat(),
    }


def serialize_session(db: Session, resources: AppResources, record: SessionRecord, full: bool = True) -> dict[str, Any]:
    completeness = completeness_for(db, resources, record.id)
    record.review_readiness = completeness["review_readiness"]
    data = {
        "id": record.id,
        "name": record.name,
        "intake_mode": record.intake_mode,
        "status": record.status,
        "profile": {"id": record.profile_id, "uri": record.profile_uri, "version": record.profile_version},
        "ontology_snapshot_id": record.ontology_snapshot_id,
        "ontology_snapshot_current": record.ontology_snapshot_id == resources.ontology.snapshot["id"],
        "review_readiness": completeness["review_readiness"],
        "created_at": record.created_at.isoformat(),
        "updated_at": record.updated_at.isoformat(),
        "current_question": None,
        "completeness_summary": {
            "score": completeness["reporting_completeness_score"],
            "unresolved_required_count": completeness["unresolved_required_count"],
            "shacl_conformance": completeness["shacl_conformance"],
        },
    }
    if full:
        messages = list(
            db.scalars(
                select(MessageRecord)
                .where(MessageRecord.session_id == record.id)
                .order_by(MessageRecord.created_at)
            )
        )
        assertions = active_assertions(db, record.id)
        data["messages"] = [message_dict(item) for item in messages]
        data["assertions"] = [
            assertion_dict(db, item) for item in assertions if not item.field_id.startswith("_system_")
        ]
        data["completeness"] = completeness
        next_question = choose_next(completeness, db, record.id)
        data["current_question"] = next_question
        record.current_field_id = next_question["id"] if next_question and next_question["id"] != "validation_issue" else None
    return data


def field_context(resources: AppResources) -> list[dict[str, object]]:
    return [asdict(item) for item in resources.catalog.fields]


async def process_user_message(
    db: Session,
    resources: AppResources,
    record: SessionRecord,
    content: str,
    force_confirmation: bool = False,
) -> dict[str, Any]:
    user_message = add_message(db, record.id, "user", content)
    values = current_values(db, record.id)
    try:
        extraction = await resources.llm.complete_structured_chat(
            message=content,
            current_field_id=record.current_field_id,
            field_context=field_context(resources),
            current_values=values,
        )
    except Exception:
        assistant = add_message(
            db,
            record.id,
            "assistant",
            "I saved your message, but the language service is temporarily unavailable. Your draft was not changed. Please retry this message later.",
            status="error",
        )
        return {"assistant": message_dict(assistant), "patch": {"added": 0}, "session": serialize_session(db, resources, record)}

    if force_confirmation:
        for operation in extraction.operations:
            operation.requires_confirmation = True
    try:
        with db.begin_nested():
            if extraction.user_intent == "skip" and record.current_field_id:
                skip_field(db, record, record.current_field_id)
                patch_result: dict[str, Any] = {"added": 0, "skipped": record.current_field_id}
            else:
                patch_result = apply_operations(
                    db,
                    record,
                    extraction.operations,
                    resources.catalog,
                    resources.ontology,
                    user_message.id,
                    content,
                    allow_replace=extraction.user_intent == "correction",
                )
    except (TypeError, ValueError):
        assistant = add_message(
            db,
            record.id,
            "assistant",
            "I saved your message, but the extracted update did not match the active ontology profile. Your Card was not changed. Please rephrase the answer or edit the field in the Card Inspector.",
            status="error",
        )
        return {
            "assistant": message_dict(assistant),
            "patch": {"added": 0, "rejected": True},
            "session": serialize_session(db, resources, record),
        }
    db.flush()
    completeness = completeness_for(db, resources, record.id)
    next_question = choose_next(completeness, db, record.id)
    captured = int(patch_result.get("added", 0))
    parts = []
    if extraction.assistant_text:
        parts.append(extraction.assistant_text)
    elif captured:
        parts.append(f"Updated {captured} Card field{'s' if captured != 1 else ''}.")
    elif extraction.user_intent == "skip":
        parts.append("Skipped for now. The item remains incomplete and can be revisited.")
    else:
        parts.append("I saved your response but did not extract a new Card fact.")
    if patch_result.get("conflicts"):
        parts.append("I found a conflicting value. Please review it in the Card Inspector.")
    if force_confirmation and captured:
        parts.append(
            "Imported facts are candidate assertions. Review and confirm them in the Card Inspector before they count as present."
        )
    if next_question:
        parts.append(next_question["question"])
        record.current_field_id = next_question["id"] if next_question["id"] != "validation_issue" else None
    else:
        parts.append("All intake requirements have a status. Review the extracted facts, validate the draft, and export when ready.")
        record.current_field_id = None
    assistant = add_message(db, record.id, "assistant", "\n\n".join(parts))
    record.updated_at = datetime.now(timezone.utc)
    db.flush()
    return {
        "assistant": message_dict(assistant),
        "patch": patch_result,
        "session": serialize_session(db, resources, record),
    }


def apply_human_updates(
    db: Session,
    resources: AppResources,
    record: SessionRecord,
    updates: list[CardFieldUpdate],
) -> dict[str, Any]:
    evidence = "\n".join(f"{resources.catalog.by_id[item.field_id].label}: {item.value}" for item in updates)
    message = add_message(db, record.id, "user", evidence)
    operations = []
    for update in updates:
        field = resources.catalog.by_id.get(update.field_id)
        if not field:
            raise ValueError(f"Unknown field ID: {update.field_id}")
        span = f"{field.label}: {update.value}"
        operations.append(
            ExtractionOperation.model_validate(
                {
                    "op": "replace" if update.replace else "add",
                    "field_id": field.id,
                    "subject_ref": field.subject,
                    "predicate_uri": field.predicate_uri,
                    "object": {"kind": field.object_kind, "value": update.value, "datatype": field.datatype_uri},
                    "source_evidence": span,
                    "confidence": 1.0,
                    "explicitness": "explicit",
                    "requires_confirmation": False,
                }
            )
        )
    result = apply_operations(
        db, record, operations, resources.catalog, resources.ontology,
        message.id, evidence, allow_replace=True,
    )
    db.flush()
    return {"patch": result, "session": serialize_session(db, resources, record)}


def run_validation(db: Session, resources: AppResources, record: SessionRecord) -> dict[str, Any]:
    completeness = completeness_for(db, resources, record.id)
    graph = build_graph(db, record, completeness)
    result = validate_graph(graph, resources.ontology)
    run = ValidationRunRecord(
        id=new_id(), session_id=record.id, ontology_snapshot_id=record.ontology_snapshot_id,
        shape_manifest_version=record.profile_version, conforms=result["conforms"],
        result_json=json.dumps(result, ensure_ascii=True), completed_at=datetime.now(timezone.utc),
    )
    db.add(run)
    db.flush()
    result["id"] = run.id
    result["data_triples"] = len(graph)
    return result


def migrate_ontology_snapshot(
    db: Session, resources: AppResources, record: SessionRecord
) -> SessionRecord:
    previous = record.ontology_snapshot_id
    current = resources.ontology.snapshot["id"]
    if previous == current:
        return record
    resources.ontology.assert_allowed(
        item.predicate_uri for item in active_assertions(db, record.id)
    )
    record.ontology_snapshot_id = current
    db.add(
        PatchEventRecord(
            id=new_id(),
            session_id=record.id,
            event_type="ontology_migration",
            payload_json=json.dumps({"from": previous, "to": current}),
            inverse_json="{}",
        )
    )
    db.flush()
    return record


def export_card(
    db: Session,
    resources: AppResources,
    record: SessionRecord,
    include_draft: bool = True,
) -> dict[str, Any]:
    validation = run_validation(db, resources, record)
    completeness = completeness_for(db, resources, record.id)
    if not include_draft and (
        not validation["conforms"] or completeness["unresolved_required_count"]
    ):
        raise ValueError(
            "A conformant export requires no SHACL violations and no unresolved required requirements"
        )
    graph = build_graph(db, record, completeness)
    export_id = new_id()
    export_root = resources.settings.app_data_dir / "exports"
    export_root.mkdir(parents=True, exist_ok=True)
    zip_path, manifest = write_export_bundle(
        export_root, db, record, completeness, validation, graph,
        resources.ontology.snapshot, export_id, resources.settings.app_commit,
    )
    db.add(
        ExportRecord(
            id=export_id, session_id=record.id, bundle_path=str(zip_path),
            manifest_json=json.dumps(manifest, ensure_ascii=True),
        )
    )
    return {
        "id": export_id,
        "filename": f"agent-card-{record.id}.zip",
        "download_url": f"/api/sessions/{record.id}/exports/{export_id}",
        "manifest": manifest,
    }


def delete_session(db: Session, record: SessionRecord) -> None:
    db.delete(record)
