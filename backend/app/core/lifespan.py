"""FastAPI lifespan handler — startup/shutdown hooks."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from faker import Faker

from app.core.config import settings
from app.core.logging import setup_logging

logger = logging.getLogger(__name__)

# Application-wide shared state
_app_state: dict = {}


def get_faker() -> Faker:
    """Return the pre-warmed application Faker instance."""
    return _app_state["faker"]


@asynccontextmanager
async def lifespan(app: object) -> AsyncGenerator[None, None]:  # type: ignore[type-arg]
    """Manage application startup and shutdown lifecycle."""
    # ── Startup ───────────────────────────────────────────────────────────────
    setup_logging(level=settings.log_level, json_logs=settings.log_json)
    logger.info(
        "DataForge starting",
        extra={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "max_rows": settings.max_rows,
        },
    )

    # Warm up Faker — instantiation is expensive due to provider loading
    fake = Faker()
    fake.seed_instance(None)  # true random
    _app_state["faker"] = fake
    logger.info("Faker provider warmed up")

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    _app_state.clear()
    logger.info("DataForge shutdown complete")
