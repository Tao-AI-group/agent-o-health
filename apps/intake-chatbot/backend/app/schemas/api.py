from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CreateSessionRequest(BaseModel):
    name: str = Field(default="Untitled Agent Card", min_length=1, max_length=160)
    intake_mode: Literal["existing", "planned", "import"] = "existing"


class UpdateSessionRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    status: Literal["active", "archived"] | None = None


class MessageRequest(BaseModel):
    content: str = Field(min_length=1)


class CardFieldUpdate(BaseModel):
    field_id: str
    value: str = Field(min_length=1, max_length=10_000)
    replace: bool = True


class CardPatchRequest(BaseModel):
    updates: list[CardFieldUpdate] = Field(min_length=1, max_length=50)


class ApplicabilityRequest(BaseModel):
    field_id: str
    reason: str = Field(min_length=3, max_length=1_000)


class ImportRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)

    @field_validator("filename")
    @classmethod
    def filename_only(cls, value: str) -> str:
        if value != value.replace("\\", "/").rsplit("/", 1)[-1]:
            raise ValueError("filename must not contain a path")
        return value


class ExportRequest(BaseModel):
    include_draft: bool = True


class AssertionObject(BaseModel):
    kind: Literal["literal", "iri", "entity_ref"]
    value: str
    datatype: str | None = None


class ExtractionOperation(BaseModel):
    op: Literal["add", "replace", "remove", "mark_not_applicable"] = "add"
    field_id: str
    subject_ref: str
    predicate_uri: str
    object: AssertionObject
    source_evidence: str
    confidence: float = Field(ge=0, le=1)
    explicitness: Literal["explicit", "inferred"] = "explicit"
    requires_confirmation: bool = False


class ExtractionResult(BaseModel):
    assistant_text: str = ""
    operations: list[ExtractionOperation] = Field(default_factory=list, max_length=50)
    clarifications: list[str] = Field(default_factory=list, max_length=5)
    possible_conflicts: list[str] = Field(default_factory=list, max_length=5)
    user_intent: Literal[
        "answer", "correction", "skip", "status", "validate", "export", "other"
    ] = "answer"
