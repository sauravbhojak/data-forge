"""DataForge FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api import analytics, erd, export, generate, health, preview, relations, schema, templates
from app.core.config import settings
from app.core.lifespan import lifespan
from app.exceptions.custom import DataForgeError
from app.exceptions.handlers import (
    dataforge_error_handler,
    generic_error_handler,
    pydantic_error_handler,
    validation_error_handler,
)
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.payload_guard import PayloadGuardMiddleware


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "DataForge — Smart Test Data Generation Platform. "
            "Generate realistic datasets for testing, development, analytics, and more."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept", "X-Request-ID"],
    )

    # ── Custom Middleware (executed last-registered → first) ───────────────────
    app.add_middleware(ObservabilityMiddleware)
    app.add_middleware(PayloadGuardMiddleware)

    # ── Exception Handlers ────────────────────────────────────────────────────
    app.add_exception_handler(DataForgeError, dataforge_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ValidationError, pydantic_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_error_handler)

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health.router)
    app.include_router(templates.router)
    app.include_router(preview.router)
    app.include_router(generate.router)
    app.include_router(schema.router)
    app.include_router(relations.router)
    app.include_router(erd.router)
    app.include_router(export.router)
    app.include_router(analytics.router)

    return app


app = create_app()
