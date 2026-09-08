from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from app.config import Settings
from app.db.models import SessionRecord
from app.llm.redaction import redact, safe_error
from app.intake.catalog import IntakeCatalog
from app.schemas.api import AssertionObject, ExtractionOperation, ExtractionResult
from app.services.cards import create_card_session
from app.services.resources import create_resources


@pytest.mark.asyncio
async def test_ontology_snapshot_catalog_and_allow_list(app_client):
    _client, app = app_client
    ontology = app.state.resources.ontology
    catalog = app.state.resources.catalog
    assert ontology.snapshot["id"] == "15ae2eaf5e674114"
    assert ontology.snapshot["integrated_triples"] == 1962
    assert len(ontology.constraints) == 71
    assert len(catalog.fields) == 50
    assert all(field.question and field.predicate_uri for field in catalog.fields)
    assert all(
        field.predicate_uri in ontology.shacl_path_uris
        for field in catalog.fields
        if field.source == "shacl"
    )
    with pytest.raises(ValueError, match="Unknown ontology URI"):
        ontology.assert_allowed(["https://example.invalid/not-in-agent-o"])


@pytest.mark.asyncio
async def test_catalog_uses_ontology_and_question_fallbacks(app_client, tmp_path: Path):
    _client, app = app_client
    catalog_path = tmp_path / "catalog.yaml"
    catalog_path.write_text(
        yaml.safe_dump(
            {
                "fields": [
                    {
                        "id": "fallback_name",
                        "section": "identity",
                        "subject": "agent",
                        "predicate_uri": "https://w3id.org/agent-o/core#hasName",
                        "object_kind": "literal",
                        "datatype_uri": "http://www.w3.org/2001/XMLSchema#string",
                        "required": True,
                        "source": "shacl",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    overrides_path = tmp_path / "overrides.yaml"
    overrides_path.write_text(
        yaml.safe_dump(
            {
                "questions": {
                    "https://w3id.org/agent-o/core#hasName": {
                        "prompt": "What is the agent called?",
                        "help": "Use the documented system name.",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    catalog = IntakeCatalog(catalog_path, app.state.resources.ontology, overrides_path)
    field = catalog.fields[0]
    assert field.label == "Name"
    assert field.question == "What is the agent called?"
    assert field.help == "Use the documented system name."


def test_strict_extraction_schema_rejects_invalid_operations():
    with pytest.raises(ValidationError):
        ExtractionOperation(
            op="invent",
            field_id="agent_name",
            subject_ref="agent",
            predicate_uri="https://example.invalid/predicate",
            object=AssertionObject(kind="literal", value="Example"),
            source_evidence="Example",
            confidence=2.0,
        )


def test_remote_bind_requires_access_token(tmp_path: Path):
    with pytest.raises(ValidationError, match="APP_ACCESS_TOKEN"):
        Settings(app_host="0.0.0.0", app_data_dir=tmp_path)
    settings = Settings(
        app_host="0.0.0.0",
        app_access_token="configured",
        app_data_dir=tmp_path,
    )
    assert settings.is_remote_bind is True


def test_secret_redaction():
    secret = "never-show-this-value"
    text = (
        f"Authorization: Bearer {secret} client_secret={secret} "
        f"access_token={secret} api_key={secret}"
    )
    cleaned = redact(text)
    assert secret not in cleaned
    assert cleaned.count("[REDACTED]") == 4
    assert secret not in safe_error(RuntimeError(text))


@pytest.mark.asyncio
async def test_access_token_protects_private_api(protected_client):
    health = await protected_client.get("/api/health")
    assert health.status_code == 200
    public = await protected_client.get("/api/config/public")
    assert public.status_code == 200
    assert public.json()["access_token_required"] is True

    unauthorized = await protected_client.get("/api/sessions")
    assert unauthorized.status_code == 401
    authorized = await protected_client.get(
        "/api/sessions", headers={"Authorization": "Bearer test-access-token"}
    )
    assert authorized.status_code == 200


@pytest.mark.asyncio
async def test_import_limits_and_types(app_client):
    client, _app = app_client
    created = await client.post(
        "/api/sessions", json={"name": "Import checks", "intake_mode": "import"}
    )
    session_id = created.json()["id"]
    unsupported = await client.post(
        f"/api/sessions/{session_id}/imports",
        json={"filename": "unsafe.exe", "content": "not executable"},
    )
    assert unsupported.status_code == 415

    oversized = await client.post(
        f"/api/sessions/{session_id}/imports",
        json={"filename": "large.txt", "content": "x" * 2_000_001},
    )
    assert oversized.status_code == 413


@pytest.mark.asyncio
async def test_invalid_llm_patch_is_rolled_back_but_message_is_saved(app_client):
    client, app = app_client

    class InvalidPatchLLM:
        async def complete_structured_chat(self, **_kwargs):
            return ExtractionResult(
                operations=[
                    ExtractionOperation(
                        field_id="not_in_catalog",
                        subject_ref="agent",
                        predicate_uri="https://example.invalid/predicate",
                        object=AssertionObject(kind="literal", value="Unsafe candidate"),
                        source_evidence="Anything",
                        confidence=0.9,
                    )
                ]
            )

    app.state.resources.llm = InvalidPatchLLM()
    created = await client.post(
        "/api/sessions", json={"name": "Rejected patch", "intake_mode": "existing"}
    )
    session_id = created.json()["id"]
    response = await client.post(
        f"/api/sessions/{session_id}/messages?stream=false",
        json={"content": "Anything"},
    )
    assert response.status_code == 200
    assert response.json()["patch"] == {"added": 0, "rejected": True}
    assert response.json()["assistant"]["status"] == "error"
    assert response.json()["session"]["assertions"] == []
    assert [item["role"] for item in response.json()["session"]["messages"]] == [
        "assistant",
        "user",
        "assistant",
    ]


@pytest.mark.asyncio
async def test_gateway_outage_preserves_user_message_and_draft(app_client):
    client, app = app_client

    class UnavailableLLM:
        async def complete_structured_chat(self, **_kwargs):
            raise TimeoutError("synthetic gateway timeout")

    app.state.resources.llm = UnavailableLLM()
    created = await client.post(
        "/api/sessions", json={"name": "Outage preservation", "intake_mode": "existing"}
    )
    session_id = created.json()["id"]
    response = await client.post(
        f"/api/sessions/{session_id}/messages?stream=false",
        json={"content": "The agent is named Durable Draft."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["patch"] == {"added": 0}
    assert body["assistant"]["status"] == "error"
    assert body["session"]["assertions"] == []
    assert body["session"]["messages"][-2]["content"] == "The agent is named Durable Draft."
    assert "synthetic gateway timeout" not in json.dumps(body)


def test_session_retention_removes_expired_records(tmp_path: Path):
    settings = Settings(
        app_host="127.0.0.1",
        app_data_dir=tmp_path / "retention",
        session_retention_days=30,
        llm_provider="mock",
    )
    resources = create_resources(settings)
    with resources.session_factory() as db:
        record = create_card_session(db, resources, "Expired", "existing")
        expired_id = record.id
        record.updated_at = datetime.now(timezone.utc) - timedelta(days=31)
        db.commit()

    refreshed = create_resources(settings)
    with refreshed.session_factory() as db:
        assert db.get(SessionRecord, expired_id) is None
