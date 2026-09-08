from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def default_agent_o_root() -> Path:
    candidates = (
        PROJECT_ROOT.parent / "agent-o",
        PROJECT_ROOT.parents[1],
    )
    for candidate in candidates:
        if (candidate / "ontology" / "agento.ttl").is_file() and (
            candidate / "shapes"
        ).is_dir():
            return candidate
    return candidates[0]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_host: str = "127.0.0.1"
    app_port: int = 7860
    app_env: str = "development"
    app_commit: str = "uncommitted"
    app_data_dir: Path = PROJECT_ROOT / "var"
    app_access_token: str = ""
    allow_insecure_bind: bool = False
    session_retention_days: int = Field(default=90, ge=1, le=3650)

    agent_o_root: Path = Field(default_factory=default_agent_o_root)
    agigee_credentials_path: Path = PROJECT_ROOT / "credentials.jsonl"

    llm_provider: str = "mock"
    llm_model: str = ""
    llm_credential_alias: str = "key1"
    llm_base_url: str = ""
    llm_token_url: str = ""
    llm_api_version: str = ""
    llm_timeout_seconds: int = 90
    llm_max_retries: int = 2
    llm_temperature: float = 0.0
    llm_max_completion_tokens: int = Field(default=2_000, ge=256, le=32_000)
    llm_reasoning_effort: str = "none"

    log_level: str = "INFO"
    log_message_content: bool = False
    research_mode: bool = False
    max_message_chars: int = 30_000
    max_import_bytes: int = 2_000_000
    allowed_import_extensions: tuple[str, ...] = (
        ".txt",
        ".md",
        ".json",
        ".jsonld",
        ".yaml",
        ".yml",
        ".ttl",
    )

    @property
    def database_url(self) -> str:
        return f"sqlite:///{(self.app_data_dir / 'agent_cards.sqlite3').resolve()}"

    @property
    def is_remote_bind(self) -> bool:
        return self.app_host in {"0.0.0.0", "::"}

    @model_validator(mode="after")
    def validate_runtime_security(self) -> "Settings":
        if self.is_remote_bind and not self.app_access_token and not self.allow_insecure_bind:
            raise ValueError(
                "APP_ACCESS_TOKEN is required for a remote bind unless "
                "ALLOW_INSECURE_BIND=true is explicitly set"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.app_data_dir.mkdir(parents=True, exist_ok=True)
    return settings
