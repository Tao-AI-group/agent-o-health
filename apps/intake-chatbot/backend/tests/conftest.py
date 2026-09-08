from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import httpx
import pytest_asyncio

from app.config import Settings, default_agent_o_root
from app.main import create_app


AGENT_O_ROOT = default_agent_o_root()


@pytest_asyncio.fixture
async def app_client(tmp_path: Path) -> AsyncIterator[tuple[httpx.AsyncClient, object]]:
    settings = Settings(
        app_host="127.0.0.1",
        app_data_dir=tmp_path / "data",
        agent_o_root=AGENT_O_ROOT,
        llm_provider="mock",
    )
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, app


@pytest_asyncio.fixture
async def protected_client(tmp_path: Path) -> AsyncIterator[httpx.AsyncClient]:
    settings = Settings(
        app_host="0.0.0.0",
        app_access_token="test-access-token",
        app_data_dir=tmp_path / "protected-data",
        agent_o_root=AGENT_O_ROOT,
        llm_provider="mock",
    )
    app = create_app(settings)
    async with app.router.lifespan_context(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
