from __future__ import annotations

import json

import pytest

from app.config import Settings
from app.llm import agigee
from app.llm.agigee import AgigeeOpenAICompatibleClient


class FakeResponse:
    def __init__(self, content: str):
        self.content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"choices": [{"message": {"content": self.content}}]}


@pytest.mark.asyncio
async def test_agigee_client_repairs_invalid_schema_once(tmp_path, monkeypatch):
    credentials = tmp_path / "credentials.jsonl"
    credentials.write_text(
        json.dumps({"alias": "test", "client_id": "synthetic-id", "client_secret": "synthetic-secret"}),
        encoding="utf-8",
    )
    settings = Settings(
        app_host="127.0.0.1",
        agigee_credentials_path=credentials,
        llm_provider="agigee_openai_compatible",
        llm_model="synthetic-model",
        llm_credential_alias="test",
        llm_base_url="https://gateway.invalid",
        llm_token_url="https://token.invalid",
        llm_api_version="test-version",
        llm_max_retries=0,
    )
    client = AgigeeOpenAICompatibleClient(settings, "system", "extract")

    async def fake_token() -> str:
        return "synthetic-token"

    client._access_token = fake_token  # type: ignore[method-assign]
    responses = [
        FakeResponse('{"operations": "not-a-list"}'),
        FakeResponse('{"assistant_text": "Repaired", "operations": [], "user_intent": "answer"}'),
    ]
    payloads: list[dict] = []

    class FakeAsyncClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, _url, *, json, headers):
            assert headers["Authorization"] == "Bearer synthetic-token"
            payloads.append(json.copy())
            return responses.pop(0)

    monkeypatch.setattr(agigee.httpx, "AsyncClient", FakeAsyncClient)
    result = await client.complete_structured_chat(
        message="Synthetic input",
        current_field_id=None,
        field_context=[],
        current_values={},
    )
    assert result.assistant_text == "Repaired"
    assert len(payloads) == 2
    assert "did not match the required JSON schema" in payloads[1]["messages"][-1]["content"]


@pytest.mark.asyncio
async def test_agigee_client_stops_after_one_failed_repair(tmp_path, monkeypatch):
    credentials = tmp_path / "credentials.jsonl"
    credentials.write_text(
        json.dumps({"alias": "test", "client_id": "synthetic-id", "client_secret": "synthetic-secret"}),
        encoding="utf-8",
    )
    settings = Settings(
        app_host="127.0.0.1",
        agigee_credentials_path=credentials,
        llm_provider="agigee_openai_compatible",
        llm_model="synthetic-model",
        llm_credential_alias="test",
        llm_base_url="https://gateway.invalid",
        llm_token_url="https://token.invalid",
        llm_api_version="test-version",
        llm_max_retries=0,
    )
    client = AgigeeOpenAICompatibleClient(settings, "system", "extract")

    async def fake_token() -> str:
        return "synthetic-token"

    client._access_token = fake_token  # type: ignore[method-assign]

    class InvalidAsyncClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, _url, **_kwargs):
            return FakeResponse('{"operations": "still-invalid"}')

    monkeypatch.setattr(agigee.httpx, "AsyncClient", InvalidAsyncClient)
    with pytest.raises(RuntimeError, match="schema repair returned invalid"):
        await client.complete_structured_chat(
            message="Synthetic input",
            current_field_id=None,
            field_context=[],
            current_values={},
        )


@pytest.mark.asyncio
async def test_agigee_client_retries_one_transient_network_failure(tmp_path, monkeypatch):
    credentials = tmp_path / "credentials.jsonl"
    credentials.write_text(
        json.dumps({"alias": "test", "client_id": "synthetic-id", "client_secret": "synthetic-secret"}),
        encoding="utf-8",
    )
    settings = Settings(
        app_host="127.0.0.1",
        agigee_credentials_path=credentials,
        llm_provider="agigee_openai_compatible",
        llm_model="synthetic-model",
        llm_credential_alias="test",
        llm_base_url="https://gateway.invalid",
        llm_token_url="https://token.invalid",
        llm_api_version="test-version",
        llm_max_retries=1,
    )
    client = AgigeeOpenAICompatibleClient(settings, "system", "extract")

    async def fake_token() -> str:
        return "synthetic-token"

    client._access_token = fake_token  # type: ignore[method-assign]
    attempts = 0

    class RetryingAsyncClient:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, _url, **_kwargs):
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise agigee.httpx.ConnectError("synthetic connection failure")
            return FakeResponse(
                '{"assistant_text":"Recovered","operations":[],"user_intent":"answer"}'
            )

    async def no_wait(_seconds):
        return None

    monkeypatch.setattr(agigee.httpx, "AsyncClient", RetryingAsyncClient)
    monkeypatch.setattr(agigee.asyncio, "sleep", no_wait)
    result = await client.complete_structured_chat(
        message="Synthetic input",
        current_field_id=None,
        field_context=[],
        current_values={},
    )
    assert attempts == 2
    assert result.assistant_text == "Recovered"
