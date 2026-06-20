"""Centralized application settings using Pydantic BaseSettings."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration — driven by environment variables or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "DataForge"
    app_version: str = "1.0.0"
    debug: bool = False

    # ── Server ───────────────────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ── Generation Limits ────────────────────────────────────────────────────
    max_rows: Annotated[int, Field(ge=1)] = 1_000_000
    preview_rows: Annotated[int, Field(ge=1, le=500)] = 50
    max_fields: Annotated[int, Field(ge=1)] = 100
    max_tables: Annotated[int, Field(ge=1)] = 20
    chunk_size: Annotated[int, Field(ge=100)] = 1_000

    # ── Rate Limiting ────────────────────────────────────────────────────────
    rate_limit_generate: str = "30/minute"
    rate_limit_export: str = "10/minute"
    rate_limit_preview: str = "60/minute"

    # ── Logging ──────────────────────────────────────────────────────────────
    log_level: str = "INFO"
    log_json: bool = True


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached Settings singleton."""
    return Settings()


# Module-level singleton for convenience imports.
settings: Settings = get_settings()
