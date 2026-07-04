from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    app_name: str = "Ollama File Organizer"
    database_url: str = "sqlite:///./data/ollama_file_organizer.db"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_model: str = "qwen3:8b"
    ollama_timeout: float = 120.0
    dry_run: bool = True
    auto_processing: bool = False
    auto_confidence_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    review_confidence_threshold: float = Field(default=0.80, ge=0.0, le=1.0)
    max_file_size_mb: int = 100
    max_extracted_text_length: int = 30_000
    scan_batch_size: int = 200
    mattermost_enabled: bool = False
    mattermost_webhook_url: str = ""
    log_level: str = "INFO"
    allowed_extensions: str = ".txt,.md,.csv,.json,.pdf,.docx,.xlsx"
    default_exclude_patterns: str = "~$*,*.tmp,*.temp,*.part,*.crdownload,*.download,.DS_Store,Thumbs.db,desktop.ini"

    @property
    def allowed_extension_set(self) -> set[str]:
        return {item.strip().lower() if item.strip().startswith(".") else f".{item.strip().lower()}" for item in self.allowed_extensions.split(",") if item.strip()}

    @property
    def exclude_pattern_list(self) -> list[str]:
        return [item.strip() for item in self.default_exclude_patterns.split(",") if item.strip()]

    @property
    def data_dir(self) -> Path:
        return Path("./data")


@lru_cache
def get_settings() -> Settings:
    return Settings()
