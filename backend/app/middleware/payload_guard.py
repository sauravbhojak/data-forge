"""Payload guard middleware — blocks oversized or abusive requests before processing."""

from __future__ import annotations

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

logger = logging.getLogger(__name__)

# Maximum raw request body size in bytes (10 MB)
MAX_BODY_BYTES = 10 * 1024 * 1024

_GUARDED_PATHS = {"/preview", "/generate", "/export/csv", "/export/json", "/export/sql", "/export/excel",
                  "/generate-schema", "/generate-relations", "/generate-erd"}


class PayloadGuardMiddleware(BaseHTTPMiddleware):
    """Rejects requests with bodies exceeding MAX_BODY_BYTES."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        if request.method in ("POST", "PUT", "PATCH") and request.url.path in _GUARDED_PATHS:
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_BODY_BYTES:
                logger.warning(
                    "Payload too large",
                    extra={"path": request.url.path, "content_length": content_length},
                )
                return JSONResponse(
                    status_code=413,
                    content={
                        "error": {
                            "code": "PayloadTooLarge",
                            "message": f"Request body exceeds {MAX_BODY_BYTES // 1024 // 1024} MB limit",
                        }
                    },
                )
        return await call_next(request)  # type: ignore[operator]
