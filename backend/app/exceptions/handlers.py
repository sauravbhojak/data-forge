"""Centralized exception handlers registered on the FastAPI application."""

from __future__ import annotations

import logging

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.exceptions.custom import (
    DataForgeError,
    ExportError,
    GenerationError,
    PayloadTooLargeError,
    RateLimitError,
    RowLimitExceededError,
    SchemaValidationError,
    TemplateNotFoundError,
)

logger = logging.getLogger(__name__)


def _error_body(code: str, message: str, detail: str | None = None) -> dict:
    return {"error": {"code": code, "message": message, "detail": detail or message}}


async def dataforge_error_handler(request: Request, exc: DataForgeError) -> JSONResponse:
    """Handle all DataForge-specific errors."""
    status_map: dict[type, int] = {
        RowLimitExceededError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        TemplateNotFoundError: status.HTTP_404_NOT_FOUND,
        SchemaValidationError: status.HTTP_422_UNPROCESSABLE_ENTITY,
        GenerationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ExportError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
        PayloadTooLargeError: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
    }
    http_status = status_map.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.warning(
        "DataForge error",
        extra={
            "error_type": type(exc).__name__,
            "message": exc.message,
            "path": str(request.url.path),
        },
    )
    return JSONResponse(
        status_code=http_status,
        content=_error_body(type(exc).__name__, exc.message, exc.detail),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic/FastAPI request validation errors."""
    errors = exc.errors()
    logger.info(
        "Request validation error",
        extra={"path": str(request.url.path), "error_count": len(errors)},
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "ValidationError",
                "message": "Request validation failed",
                "detail": errors,
            }
        },
    )


async def pydantic_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle direct Pydantic ValidationError (e.g. from service layer)."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body("ValidationError", "Schema validation failed", str(exc)),
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler for unexpected errors."""
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body(
            "InternalServerError",
            "An unexpected error occurred",
            "Please try again or contact support.",
        ),
    )
