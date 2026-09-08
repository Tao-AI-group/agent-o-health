from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session, sessionmaker

from app.config import PROJECT_ROOT, Settings
from app.db.database import create_database, session_scope
from app.db.models import OntologySnapshotRecord, SessionRecord
from app.intake.catalog import IntakeCatalog
from app.llm.agigee import AgigeeOpenAICompatibleClient
from app.llm.base import LLMClient
from app.llm.mock import MockLLMClient
from app.ontology.loader import OntologyBundle


@dataclass
class AppResources:
    settings: Settings
    ontology: OntologyBundle
    catalog: IntakeCatalog
    session_factory: sessionmaker[Session]
    llm: LLMClient


def create_resources(settings: Settings) -> AppResources:
    ontology = OntologyBundle(PROJECT_ROOT, settings.agent_o_root)
    catalog = IntakeCatalog(
        PROJECT_ROOT / "config" / "intake_fields.yaml",
        ontology,
        PROJECT_ROOT / "config" / "question_overrides.yaml",
    )
    _engine, factory = create_database(settings)
    with session_scope(factory) as db:
        retention_cutoff = datetime.now(timezone.utc) - timedelta(
            days=settings.session_retention_days
        )
        db.execute(delete(SessionRecord).where(SessionRecord.updated_at < retention_cutoff))
        if db.get(OntologySnapshotRecord, ontology.snapshot["id"]) is None:
            db.add(
                OntologySnapshotRecord(
                    id=ontology.snapshot["id"],
                    catalog_version=ontology.snapshot["catalog_version"],
                    metadata_json=json.dumps(ontology.snapshot, sort_keys=True),
                )
            )
    if settings.llm_provider.lower() == "mock":
        llm: LLMClient = MockLLMClient()
    elif settings.llm_provider.lower() in {
        "agigee",
        "agigee_openai_compatible",
        "apigee_azure_openai",
    }:
        llm = AgigeeOpenAICompatibleClient(
            settings,
            (PROJECT_ROOT / "prompts" / "system.md").read_text(encoding="utf-8"),
            (PROJECT_ROOT / "prompts" / "extract_and_plan.md").read_text(encoding="utf-8"),
        )
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {settings.llm_provider}")
    return AppResources(settings, ontology, catalog, factory, llm)
