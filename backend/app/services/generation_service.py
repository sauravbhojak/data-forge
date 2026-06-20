"""Generation service — orchestrates schema validation, generation, and metrics."""

from __future__ import annotations

import time
from collections.abc import Iterator
from typing import Any

from faker import Faker

from app.core.config import settings
from app.exceptions.custom import GenerationError, RowLimitExceededError
from app.generators.table_generator import TableGenerator
from app.schemas.generation import (
    GenerationMetrics,
    GenerationResponse,
    PreviewResponse,
    TableSchema,
)
from app.utils.memory import MemorySnapshot


class GenerationService:
    """Thin orchestration layer between API routes and the table generator."""

    def __init__(self, fake: Faker) -> None:
        self._table_gen = TableGenerator(fake)

    def validate_schema(self, schema: TableSchema) -> None:
        """Enforce server-side limits beyond Pydantic validation."""
        if schema.row_count > settings.max_rows:
            raise RowLimitExceededError(schema.row_count, settings.max_rows)
        if len(schema.fields) > settings.max_fields:
            raise GenerationError(
                f"Field count {len(schema.fields)} exceeds limit {settings.max_fields}"
            )

    def preview(self, schema: TableSchema) -> PreviewResponse:
        """Generate and return the first preview_rows rows in full."""
        self.validate_schema(schema)

        preview_schema = schema.model_copy(update={"row_count": settings.preview_rows})

        start = time.perf_counter()
        with MemorySnapshot() as mem:
            rows = list(self._table_gen.generate(preview_schema))
        elapsed_ms = (time.perf_counter() - start) * 1000

        columns = list(rows[0].keys()) if rows else []

        return PreviewResponse(
            table_name=schema.name,
            columns=columns,
            rows=rows,
            total_count=schema.row_count,
            preview_count=len(rows),
            metrics=GenerationMetrics(
                row_count=len(rows),
                field_count=len(schema.fields),
                generation_time_ms=round(elapsed_ms, 2),
                memory_delta_mb=mem.delta_mb,
            ),
        )

    def generate_iter(self, schema: TableSchema) -> tuple[Iterator[dict[str, Any]], GenerationMetrics]:
        """
        Return an iterator over all generated rows plus pre-calculated metrics stub.

        The iterator is lazy — actual generation happens as the caller consumes it.
        Metrics are estimated; use the actual timing wrapper in the calling context.
        """
        self.validate_schema(schema)
        it = self._table_gen.generate(schema)
        metrics = GenerationMetrics(
            row_count=schema.row_count,
            field_count=len(schema.fields),
            generation_time_ms=0.0,
            memory_delta_mb=0.0,
        )
        return it, metrics

    def generate_response(self, schema: TableSchema) -> GenerationResponse:
        """Generate all rows and return a summary response (no data returned)."""
        self.validate_schema(schema)

        start = time.perf_counter()
        with MemorySnapshot() as mem:
            # Consume the iterator to force generation (for timing)
            count = sum(1 for _ in self._table_gen.generate(schema))
        elapsed_ms = (time.perf_counter() - start) * 1000

        return GenerationResponse(
            table_name=schema.name,
            row_count=count,
            metrics=GenerationMetrics(
                row_count=count,
                field_count=len(schema.fields),
                generation_time_ms=round(elapsed_ms, 2),
                memory_delta_mb=mem.delta_mb,
            ),
        )
