from __future__ import annotations

import os

import pytest

from app.config import Settings
from app.services.cards import field_context
from app.services.resources import create_resources


pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("RUN_LIVE_LLM_TESTS") != "1",
        reason="Set RUN_LIVE_LLM_TESTS=1 to call the institutional gateway",
    ),
]


@pytest.mark.asyncio
async def test_synthetic_agent_name_extraction_through_live_gateway(tmp_path):
    settings = Settings(app_host="127.0.0.1", app_data_dir=tmp_path)
    assert settings.llm_provider != "mock"
    resources = create_resources(settings)
    result = await resources.llm.complete_structured_chat(
        message="The agent is called Synthetic Intake Smoke Test.",
        current_field_id="agent_name",
        field_context=field_context(resources),
        current_values={},
    )
    assert result.assistant_text or result.operations
    assert all(operation.predicate_uri in resources.ontology.allowed_uris for operation in result.operations)
    assert all(
        operation.source_evidence in "The agent is called Synthetic Intake Smoke Test."
        for operation in result.operations
    )
