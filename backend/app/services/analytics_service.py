"""Analytics service — orchestrates analytics dataset generation."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

from app.core.config import settings
from app.exceptions.custom import RowLimitExceededError
from app.generators.analytics_generator import AnalyticsGenerator
from app.schemas.generation import AnalyticsRequest


class AnalyticsService:
    """Thin service for analytics dataset generation."""

    def __init__(self) -> None:
        self._gen = AnalyticsGenerator()

    def validate(self, request: AnalyticsRequest) -> None:
        if request.row_count > settings.max_rows:
            raise RowLimitExceededError(request.row_count, settings.max_rows)

    def generate_iter(self, request: AnalyticsRequest) -> Iterator[dict[str, Any]]:
        """Return a lazy iterator over analytics rows."""
        self.validate(request)
        return self._gen.generate(request)

    def preview(self, request: AnalyticsRequest) -> list[dict[str, Any]]:
        """Generate preview rows (first preview_rows rows)."""
        self.validate(request)
        preview_req = request.model_copy(update={"row_count": settings.preview_rows})
        return list(self._gen.generate(preview_req))
