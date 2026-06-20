"""Request observability middleware — logs timing, status, and memory for every request."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import new_request_id
from app.utils.memory import current_process_memory_mb

logger = logging.getLogger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Attaches a request-ID to every request and logs structured metrics on completion."""

    async def dispatch(self, request: Request, call_next: object) -> Response:
        rid = new_request_id()
        request.state.request_id = rid

        mem_before = current_process_memory_mb()
        start = time.perf_counter()

        response: Response = await call_next(request)  # type: ignore[operator]

        elapsed_ms = (time.perf_counter() - start) * 1000
        mem_delta = round(current_process_memory_mb() - mem_before, 3)

        logger.info(
            "Request completed",
            extra={
                "request_id": rid,
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(elapsed_ms, 2),
                "memory_delta_mb": mem_delta,
            },
        )

        response.headers["X-Request-ID"] = rid
        response.headers["X-Response-Time-Ms"] = str(round(elapsed_ms, 2))
        return response
