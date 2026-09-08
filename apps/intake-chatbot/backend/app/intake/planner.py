from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PatchEventRecord, ValidationRunRecord


def skipped_field_ids(db: Session, session_id: str) -> set[str]:
    skipped: set[str] = set()
    events = db.scalars(
        select(PatchEventRecord)
        .where(PatchEventRecord.session_id == session_id, PatchEventRecord.event_type == "skip")
        .order_by(PatchEventRecord.created_at)
    )
    for event in events:
        payload = json.loads(event.payload_json)
        if event.undone:
            skipped.discard(payload["field_id"])
        else:
            skipped.add(payload["field_id"])
    return skipped


def choose_next(completeness: dict, db: Session, session_id: str) -> dict[str, str] | None:
    latest = db.scalar(
        select(ValidationRunRecord)
        .where(ValidationRunRecord.session_id == session_id)
        .order_by(ValidationRunRecord.completed_at.desc())
    )
    if latest and not latest.conforms:
        result = json.loads(latest.result_json)
        violations = [item for item in result.get("results", []) if item.get("severity") == "Violation"]
        if violations:
            return {
                "id": "validation_issue",
                "label": "Validation issue",
                "question": violations[0].get("message", "Please resolve the current SHACL violation."),
            }
    for item in completeness["requirements"]:
        if item["review_state"] == "conflict":
            return {"id": item["id"], "label": item["label"], "question": f"Two values conflict for {item['label']}. Which value should the Card retain?"}
    skipped = skipped_field_ids(db, session_id)
    for desired in ("missing", "partial"):
        for item in completeness["requirements"]:
            if item["required"] and item["status"] == desired and item["id"] not in skipped:
                return {"id": item["id"], "label": item["label"], "question": item["question"]}
    for item in completeness["requirements"]:
        if item["status"] == "missing" and item["id"] not in skipped:
            return {"id": item["id"], "label": item["label"], "question": item["question"]}
    return None
