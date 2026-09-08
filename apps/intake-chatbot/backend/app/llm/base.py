from __future__ import annotations

from typing import Protocol

from app.schemas.api import ExtractionResult


class LLMClient(Protocol):
    provider_name: str

    async def complete_structured_chat(
        self,
        *,
        message: str,
        current_field_id: str | None,
        field_context: list[dict[str, object]],
        current_values: dict[str, str],
    ) -> ExtractionResult: ...

    async def stream_structured_chat(
        self,
        *,
        message: str,
        current_field_id: str | None,
        field_context: list[dict[str, object]],
        current_values: dict[str, str],
    ) -> ExtractionResult: ...

    async def healthcheck(self) -> str: ...
