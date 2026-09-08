from __future__ import annotations

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Any

import httpx
from pydantic import ValidationError

from app.config import Settings
from app.llm.redaction import safe_error
from app.schemas.api import ExtractionResult


def load_credentials(path: Path, alias: str | None) -> tuple[str, str]:
    if not path.is_file():
        raise FileNotFoundError("Configured credential file is unavailable")
    selected: dict[str, Any] | None = None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Credential record {line_number} is invalid JSON") from exc
        if not isinstance(record, dict):
            raise ValueError(f"Credential record {line_number} is not an object")
        if alias is None or str(record.get("alias", "")) == alias:
            selected = record
            break
    if selected is None:
        raise ValueError("Configured credential alias was not found")
    client_id = str(selected.get("client_id") or "")
    client_secret = str(selected.get("client_secret") or "")
    if not client_id or not client_secret:
        raise ValueError("Credential record is missing required fields")
    return client_id, client_secret


class AgigeeOpenAICompatibleClient:
    provider_name = "agigee_openai_compatible"

    def __init__(self, settings: Settings, system_prompt: str, extraction_prompt: str):
        if not all(
            (
                settings.llm_model,
                settings.llm_base_url,
                settings.llm_token_url,
                settings.llm_api_version,
            )
        ):
            raise ValueError(
                "Live LLM configuration requires model, base URL, token URL, and API version"
            )
        self.settings = settings
        self.system_prompt = system_prompt
        self.extraction_prompt = extraction_prompt
        self.client_id, self.client_secret = load_credentials(
            settings.agigee_credentials_path, settings.llm_credential_alias
        )
        self._token = ""
        self._token_expiry = 0.0
        self._lock = asyncio.Lock()

    async def _access_token(self) -> str:
        async with self._lock:
            if self._token and time.time() < self._token_expiry - 60:
                return self._token
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    self.settings.llm_token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                payload = response.json()
            token = str(payload.get("access_token") or "")
            if not token:
                raise RuntimeError("Gateway authentication returned no access token")
            self._token = token
            self._token_expiry = time.time() + int(payload.get("expires_in") or 3600)
            return token

    def _chat_url(self) -> str:
        base = self.settings.llm_base_url.rstrip("/")
        return (
            f"{base}/llm-azure-openai/openai/deployments/{self.settings.llm_model}"
            f"/chat/completions?api-version={self.settings.llm_api_version}"
        )

    async def complete_structured_chat(
        self,
        *,
        message: str,
        current_field_id: str | None,
        field_context: list[dict[str, object]],
        current_values: dict[str, str],
    ) -> ExtractionResult:
        context = {
            "current_field_id": current_field_id,
            "allowed_fields": field_context,
            "current_values": current_values,
            "untrusted_user_message": message,
            "response_json_schema": ExtractionResult.model_json_schema(),
        }
        request_id = str(uuid.uuid4())
        payload = {
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": self.extraction_prompt
                    + "\n\n<UNTRUSTED_INPUT>\n"
                    + json.dumps(context, ensure_ascii=True)
                    + "\n</UNTRUSTED_INPUT>",
                },
            ],
            "temperature": self.settings.llm_temperature,
            "max_completion_tokens": self.settings.llm_max_completion_tokens,
            "reasoning_effort": self.settings.llm_reasoning_effort,
            "response_format": {"type": "json_object"},
        }
        last_error: Exception | None = None
        network_failures = 0
        repair_used = False
        while True:
            try:
                token = await self._access_token()
                async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
                    response = await client.post(
                        self._chat_url(),
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Content-Type": "application/json",
                            "X-Request-ID": request_id,
                        },
                    )
                response.raise_for_status()
                content = response.json()["choices"][0]["message"]["content"]
                try:
                    return ExtractionResult.model_validate_json(content)
                except ValidationError as exc:
                    if repair_used:
                        raise RuntimeError("LLM schema repair returned invalid structured output") from exc
                    repair_used = True
                    payload["messages"].extend(
                        [
                            {"role": "assistant", "content": content},
                            {
                                "role": "user",
                                "content": (
                                    "The previous response did not match the required JSON schema. "
                                    "Return one corrected JSON object only. Preserve only facts and "
                                    "evidence from the untrusted input; do not invent ontology terms."
                                ),
                            },
                        ]
                    )
                    continue
            except Exception as exc:
                last_error = exc
                if isinstance(exc, RuntimeError) and "schema repair" in str(exc):
                    break
                if network_failures < self.settings.llm_max_retries:
                    await asyncio.sleep(min(2**network_failures, 4))
                    network_failures += 1
                    continue
                break
        raise RuntimeError(f"LLM request failed: {safe_error(last_error or RuntimeError())}")

    async def stream_structured_chat(self, **kwargs) -> ExtractionResult:  # type: ignore[no-untyped-def]
        return await self.complete_structured_chat(**kwargs)

    async def healthcheck(self) -> str:
        await self._access_token()
        return "available"
