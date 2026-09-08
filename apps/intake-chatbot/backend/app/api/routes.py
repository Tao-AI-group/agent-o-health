from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import __version__
from app.db.models import ExportRecord, PatchEventRecord, SessionRecord
from app.intake.patch_engine import mark_not_applicable, skip_field, undo_last_patch
from app.schemas.api import (
    ApplicabilityRequest,
    CardPatchRequest,
    CreateSessionRequest,
    ExportRequest,
    ImportRequest,
    MessageRequest,
    UpdateSessionRequest,
)
from app.services.cards import (
    apply_human_updates,
    canonical_card,
    completeness_for,
    create_card_session,
    delete_session,
    export_card,
    get_session,
    migrate_ontology_snapshot,
    process_user_message,
    run_validation,
    serialize_session,
)
from app.services.resources import AppResources


router = APIRouter(prefix="/api")


async def resources(request: Request) -> AppResources:
    return request.app.state.resources


async def database(request: Request) -> AsyncIterator[Session]:
    value: AppResources = request.app.state.resources
    db = value.session_factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def session_or_404(db: Session, session_id: str) -> SessionRecord:
    try:
        return get_session(db, session_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Session not found") from exc


@router.get("/health")
async def health(app: AppResources = Depends(resources), db: Session = Depends(database)) -> dict:
    db.execute(text("SELECT 1"))
    return {
        "status": "ok",
        "database": "ok",
        "ontology": "loaded",
        "profile": "loaded",
        "llm_configuration": "configured" if app.settings.llm_provider != "mock" else "mock",
        "version": __version__,
    }


@router.get("/config/public")
async def public_config(app: AppResources = Depends(resources)) -> dict:
    return {
        "application_name": "AGENT-O Agent Card Intake",
        "version": __version__,
        "access_token_required": bool(app.settings.app_access_token),
        "profile_id": app.ontology.manifest["profile"]["id"],
        "profile_version": app.ontology.manifest["profile"]["version"],
        "research_mode": app.settings.research_mode,
        "max_import_bytes": app.settings.max_import_bytes,
        "allowed_import_extensions": list(app.settings.allowed_import_extensions),
        "notice": (
            "This tool assesses reporting completeness and ontology conformance. "
            "It does not determine agent quality, safety, clinical utility, compliance, "
            "or deployment readiness."
        ),
    }


@router.get("/ontology/status")
async def ontology_status(app: AppResources = Depends(resources)) -> dict:
    return app.ontology.status()


@router.get("/profiles")
async def profiles(app: AppResources = Depends(resources)) -> list[dict]:
    profile = app.ontology.manifest["profile"]
    return [
        {
            "id": profile["id"],
            "uri": profile["uri"],
            "version": profile["version"],
            "root_report_class": profile["root_report_class"],
            "root_system_class": profile["root_system_class"],
            "sections": app.ontology.manifest["sections"],
            "fields": app.catalog.public(),
        }
    ]


@router.post("/sessions", status_code=201)
async def create_session(
    payload: CreateSessionRequest,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = create_card_session(db, app, payload.name, payload.intake_mode)
    db.flush()
    return serialize_session(db, app, record)


@router.get("/sessions")
async def list_sessions(app: AppResources = Depends(resources), db: Session = Depends(database)) -> list[dict]:
    records = list(db.scalars(select(SessionRecord).order_by(SessionRecord.updated_at.desc())))
    return [serialize_session(db, app, item, full=False) for item in records]


@router.get("/sessions/{session_id}")
async def read_session(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    return serialize_session(db, app, session_or_404(db, session_id))


@router.patch("/sessions/{session_id}")
async def update_session(
    session_id: str,
    payload: UpdateSessionRequest,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    if payload.name is not None:
        record.name = payload.name
    if payload.status is not None:
        record.status = payload.status
    return serialize_session(db, app, record)


@router.delete("/sessions/{session_id}", status_code=204, response_class=Response)
async def remove_session(session_id: str, db: Session = Depends(database)) -> Response:
    delete_session(db, session_or_404(db, session_id))
    return Response(status_code=204)


def sse_payload(event: str, data: dict | str) -> str:
    encoded = data if isinstance(data, str) else json.dumps(data, ensure_ascii=True)
    return f"event: {event}\ndata: {encoded}\n\n"


@router.post("/sessions/{session_id}/messages")
async def send_message(
    session_id: str,
    payload: MessageRequest,
    stream: bool = Query(default=True),
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
):
    if len(payload.content) > app.settings.max_message_chars:
        raise HTTPException(status_code=413, detail="Message exceeds the configured size limit")
    record = session_or_404(db, session_id)
    result = await process_user_message(db, app, record, payload.content)
    db.commit()
    if not stream:
        return result

    async def emit():
        yield sse_payload("patch", result["patch"])
        words = result["assistant"]["content"].split(" ")
        for index, word in enumerate(words):
            yield sse_payload("token", word + (" " if index < len(words) - 1 else ""))
            await asyncio.sleep(0.006)
        yield sse_payload("done", {"session": result["session"], "assistant": result["assistant"]})

    return StreamingResponse(
        emit(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-store", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions/{session_id}/events")
async def session_events(session_id: str, db: Session = Depends(database)) -> StreamingResponse:
    session_or_404(db, session_id)
    events = list(
        db.scalars(
            select(PatchEventRecord)
            .where(PatchEventRecord.session_id == session_id)
            .order_by(PatchEventRecord.created_at)
        )
    )

    async def emit():
        for event in events:
            yield sse_payload(
                event.event_type,
                {"id": event.id, "created_at": event.created_at.isoformat(), "undone": event.undone},
            )
        yield sse_payload("done", {"count": len(events)})

    return StreamingResponse(emit(), media_type="text/event-stream")


@router.post("/sessions/{session_id}/actions/undo")
async def undo(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    if not undo_last_patch(db, session_id):
        raise HTTPException(status_code=409, detail="There is no applied update to undo")
    db.flush()
    return serialize_session(db, app, record)


@router.post("/sessions/{session_id}/actions/skip")
async def skip(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    if not record.current_field_id:
        raise HTTPException(status_code=409, detail="There is no current requirement to skip")
    skip_field(db, record, record.current_field_id)
    db.flush()
    return serialize_session(db, app, record)


@router.post("/sessions/{session_id}/actions/not-applicable")
async def not_applicable(
    session_id: str,
    payload: ApplicabilityRequest,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    if payload.field_id not in app.catalog.by_id:
        raise HTTPException(status_code=422, detail="Unknown requirement")
    mark_not_applicable(db, record, payload.field_id, payload.reason, None)
    db.flush()
    return serialize_session(db, app, record)


@router.post("/sessions/{session_id}/actions/validate")
async def validate_session(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    if record.ontology_snapshot_id != app.ontology.snapshot["id"]:
        raise HTTPException(
            status_code=409,
            detail="Migrate this session to the active ontology snapshot before validation",
        )
    return run_validation(db, app, record)


@router.post("/sessions/{session_id}/actions/migrate")
async def migrate_snapshot(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    try:
        migrate_ontology_snapshot(db, app, record)
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail="The draft contains ontology terms that require curator review before migration",
        ) from exc
    return serialize_session(db, app, record)


@router.get("/sessions/{session_id}/completeness")
async def completeness(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    session_or_404(db, session_id)
    return completeness_for(db, app, session_id)


@router.get("/sessions/{session_id}/card")
async def card(
    session_id: str,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    return canonical_card(db, record, completeness_for(db, app, session_id), None)


@router.patch("/sessions/{session_id}/card")
async def patch_card(
    session_id: str,
    payload: CardPatchRequest,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    unknown = [item.field_id for item in payload.updates if item.field_id not in app.catalog.by_id]
    if unknown:
        raise HTTPException(status_code=422, detail=f"Unknown requirement: {unknown[0]}")
    try:
        return apply_human_updates(db, app, session_or_404(db, session_id), payload.updates)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/imports")
async def import_content(
    session_id: str,
    payload: ImportRequest,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    suffix = Path(payload.filename).suffix.lower()
    if suffix not in app.settings.allowed_import_extensions:
        raise HTTPException(status_code=415, detail="This file type is not supported")
    if len(payload.content.encode("utf-8")) > app.settings.max_import_bytes:
        raise HTTPException(status_code=413, detail="Imported content exceeds the configured size limit")
    record = session_or_404(db, session_id)
    untrusted = f"Imported file: {payload.filename}\n\n{payload.content}"
    return await process_user_message(db, app, record, untrusted, force_confirmation=True)


@router.post("/sessions/{session_id}/exports", status_code=201)
async def create_export(
    session_id: str,
    _payload: ExportRequest,
    app: AppResources = Depends(resources),
    db: Session = Depends(database),
) -> dict:
    record = session_or_404(db, session_id)
    if record.ontology_snapshot_id != app.ontology.snapshot["id"]:
        raise HTTPException(
            status_code=409,
            detail="Migrate this session to the active ontology snapshot before export",
        )
    try:
        return export_card(db, app, record, include_draft=_payload.include_draft)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/sessions/{session_id}/exports/{export_id}")
async def download_export(session_id: str, export_id: str, db: Session = Depends(database)) -> Response:
    session_or_404(db, session_id)
    record = db.get(ExportRecord, export_id)
    if not record or record.session_id != session_id:
        raise HTTPException(status_code=404, detail="Export not found")
    path = Path(record.bundle_path)
    if not path.is_file():
        raise HTTPException(status_code=410, detail="Export file is no longer available")
    return Response(
        content=path.read_bytes(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="agent-card-{session_id}.zip"'
        },
    )
