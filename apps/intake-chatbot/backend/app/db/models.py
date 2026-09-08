from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="Untitled Agent Card")
    intake_mode: Mapped[str] = mapped_column(String, default="existing")
    profile_id: Mapped[str] = mapped_column(String)
    profile_uri: Mapped[str] = mapped_column(String)
    profile_version: Mapped[str] = mapped_column(String)
    ontology_snapshot_id: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active")
    review_readiness: Mapped[str] = mapped_column(String, default="draft")
    current_field_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)

    messages: Mapped[list[MessageRecord]] = relationship(cascade="all, delete-orphan")
    entities: Mapped[list[EntityRecord]] = relationship(cascade="all, delete-orphan")
    assertions: Mapped[list[AssertionRecord]] = relationship(cascade="all, delete-orphan")


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="complete")
    request_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


class EntityRecord(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    entity_key: Mapped[str] = mapped_column(String, index=True)
    rdf_type_uri: Mapped[str] = mapped_column(String)
    stable_uri: Mapped[str] = mapped_column(String, unique=True)
    label: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)


class AssertionRecord(Base):
    __tablename__ = "assertions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    field_id: Mapped[str] = mapped_column(String, index=True)
    subject_entity_id: Mapped[str] = mapped_column(ForeignKey("entities.id"))
    predicate_uri: Mapped[str] = mapped_column(String)
    object_kind: Mapped[str] = mapped_column(String)
    object_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    object_entity_id: Mapped[str | None] = mapped_column(ForeignKey("entities.id"), nullable=True)
    datatype_uri: Mapped[str | None] = mapped_column(String, nullable=True)
    source_message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    source_evidence: Mapped[str] = mapped_column(Text, default="")
    extraction_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    explicitness: Mapped[str] = mapped_column(String, default="explicit")
    review_state: Mapped[str] = mapped_column(String, default="confirmed")
    user_confirmed: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
    superseded_at: Mapped[datetime | None] = mapped_column(nullable=True)


class ApplicabilityRecord(Base):
    __tablename__ = "applicability_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    requirement_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String)
    source_message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    confirmed_at: Mapped[datetime] = mapped_column(default=utc_now)


class PatchEventRecord(Base):
    __tablename__ = "patch_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    event_type: Mapped[str] = mapped_column(String)
    payload_json: Mapped[str] = mapped_column(Text)
    inverse_json: Mapped[str] = mapped_column(Text)
    undone: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


class ValidationRunRecord(Base):
    __tablename__ = "validation_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    ontology_snapshot_id: Mapped[str] = mapped_column(String)
    shape_manifest_version: Mapped[str] = mapped_column(String)
    conforms: Mapped[bool] = mapped_column(Boolean)
    result_json: Mapped[str] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(default=utc_now)
    completed_at: Mapped[datetime] = mapped_column(default=utc_now)


class ExportRecord(Base):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), index=True)
    bundle_path: Mapped[str] = mapped_column(Text)
    manifest_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


class OntologySnapshotRecord(Base):
    __tablename__ = "ontology_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    catalog_version: Mapped[str] = mapped_column(String)
    metadata_json: Mapped[str] = mapped_column(Text)
    loaded_at: Mapped[datetime] = mapped_column(default=utc_now)
