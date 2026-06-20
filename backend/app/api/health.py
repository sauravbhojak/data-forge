"""Health and readiness check endpoints."""

from __future__ import annotations

import platform
import sys

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness check")
async def health() -> dict:
    """Returns 200 if the application process is running."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }


@router.get("/ready", summary="Readiness check")
async def ready() -> dict:
    """Returns 200 if the application is ready to serve traffic."""
    return {
        "status": "ready",
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "max_rows": settings.max_rows,
    }
