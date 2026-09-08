from __future__ import annotations

import re

from app.schemas.api import AssertionObject, ExtractionOperation, ExtractionResult


class MockLLMClient:
    provider_name = "mock"

    @staticmethod
    def _operation(field: dict[str, object], value: str, evidence: str, confidence: float = 0.96) -> ExtractionOperation:
        return ExtractionOperation(
            field_id=str(field["id"]),
            subject_ref=str(field["subject"]),
            predicate_uri=str(field["predicate_uri"]),
            object=AssertionObject(
                kind=str(field["object_kind"]),  # type: ignore[arg-type]
                value=value.strip(" ."),
                datatype=str(field.get("datatype_uri") or "") or None,
            ),
            source_evidence=evidence,
            confidence=confidence,
            explicitness="explicit",
            requires_confirmation=False,
        )

    async def complete_structured_chat(
        self,
        *,
        message: str,
        current_field_id: str | None,
        field_context: list[dict[str, object]],
        current_values: dict[str, str],
    ) -> ExtractionResult:
        stripped = message.strip()
        lower = stripped.lower()
        if lower in {"/skip", "skip", "skip for now", "i don't know", "i do not know"}:
            return ExtractionResult(user_intent="skip")
        if lower in {"/status", "status"}:
            return ExtractionResult(user_intent="status")
        if lower in {"/validate", "validate"}:
            return ExtractionResult(user_intent="validate")
        if lower in {"/export", "export"}:
            return ExtractionResult(user_intent="export")

        by_id = {str(field["id"]): field for field in field_context}
        operations: list[ExtractionOperation] = []

        # Explicit field-id or label lines make the mock useful for deterministic demos.
        for line in stripped.splitlines():
            if ":" not in line:
                continue
            key, value = (part.strip() for part in line.split(":", 1))
            normalized = re.sub(r"[^a-z0-9]+", "_", key.lower()).strip("_")
            field = by_id.get(normalized)
            if field is None:
                field = next(
                    (item for item in field_context if str(item["label"]).lower() == key.lower()),
                    None,
                )
            if field and value:
                operations.append(self._operation(field, value, line))

        patterns = {
            "agent_name": r"(?:called|named)\s+([A-Z][\w .-]{1,80}?)(?=\s+(?:is|uses|supports|for)\b|[.,;]|$)",
            "model_name": r"\b(?:uses?|powered by|based on)\s+([A-Z][A-Za-z0-9._ -]{1,50}?)(?=\s+(?:model|through|via|for|to)\b|[.,;]|$)",
            "model_version": r"\b(?:version|checkpoint|snapshot)\s+([A-Za-z0-9._-]+)",
            "intended_user": r"\bfor\s+(clinicians?|physicians?|patients?|researchers?|nurses?|care teams?)\b",
        }
        existing_ids = {operation.field_id for operation in operations}
        for field_id, pattern in patterns.items():
            if field_id in existing_ids or field_id not in by_id:
                continue
            match = re.search(pattern, stripped, re.IGNORECASE)
            if match:
                operations.append(self._operation(by_id[field_id], match.group(1), match.group(0), 0.9))

        correction = bool(re.search(r"\b(?:actually|correction|replace|instead)\b", lower))
        if not operations and current_field_id and current_field_id in by_id:
            operations.append(self._operation(by_id[current_field_id], stripped, stripped))

        captured = ", ".join(str(by_id[item.field_id]["label"]) for item in operations)
        return ExtractionResult(
            assistant_text=f"Captured: {captured}." if captured else "I could not map that response to the current Card field.",
            operations=operations,
            user_intent="correction" if correction else "answer",
        )

    async def stream_structured_chat(self, **kwargs) -> ExtractionResult:  # type: ignore[no-untyped-def]
        return await self.complete_structured_chat(**kwargs)

    async def healthcheck(self) -> str:
        return "available"
