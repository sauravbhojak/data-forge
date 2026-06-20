"""Table-level generator — produces rows as an iterator (never full dataset in memory)."""

from __future__ import annotations

import random
from collections.abc import Iterator
from typing import Any

from faker import Faker

from app.generators.field_generator import FieldGenerator
from app.schemas.generation import DataQualityConfig, FieldDefinition, TableSchema


class TableGenerator:
    """
    Generates table rows one at a time using a stateful FieldGenerator.

    Memory characteristics:
    - Only one row dict is live at a time.
    - Unique tracking sets grow with unique field cardinality (bounded by row_count).
    - Outlier buffer is O(1) per row.
    """

    def __init__(self, fake: Faker) -> None:
        self._field_gen = FieldGenerator(fake)

    def generate(self, schema: TableSchema) -> Iterator[dict[str, Any]]:
        """
        Yield rows for the given table schema.

        Applies data quality controls:
        - null_rate: probability a nullable field is NULL
        - duplicate_rate: some rows are repeats of previous rows
        - outlier_rate: some numeric values become extreme
        """
        self._field_gen.reset()

        quality = schema.quality
        fields = schema.fields
        row_count = schema.row_count

        # Pre-build field keys for fast access
        field_keys = [f"{schema.name}.{f.name}" for f in fields]

        # Small circular buffer for duplicates (bounded size regardless of row_count)
        dup_buffer: list[dict[str, Any]] = []
        dup_buffer_size = min(20, max(1, row_count // 100))

        for _ in range(row_count):
            # ── Duplicate injection ───────────────────────────────────────────
            if quality.duplicate_rate > 0 and dup_buffer and random.random() < quality.duplicate_rate:
                yield random.choice(dup_buffer).copy()
                continue

            row = self._generate_row(fields, field_keys, quality)

            # ── Outlier injection ─────────────────────────────────────────────
            if quality.outlier_rate > 0 and random.random() < quality.outlier_rate:
                row = self._inject_outliers(row, fields)

            # Feed duplicate buffer (circular, constant memory)
            if quality.duplicate_rate > 0:
                if len(dup_buffer) < dup_buffer_size:
                    dup_buffer.append(row.copy())
                else:
                    dup_buffer[random.randint(0, dup_buffer_size - 1)] = row.copy()

            yield row

    def _generate_row(
        self,
        fields: list[FieldDefinition],
        field_keys: list[str],
        quality: DataQualityConfig,
    ) -> dict[str, Any]:
        row: dict[str, Any] = {}
        for field, key in zip(fields, field_keys, strict=True):
            row[field.name] = self._field_gen.generate_value(
                field, key, null_rate=quality.null_rate
            )
        return row

    @staticmethod
    def _inject_outliers(row: dict[str, Any], fields: list[FieldDefinition]) -> dict[str, Any]:
        """Replace a random numeric field value with an extreme outlier."""
        numeric_fields = [f for f in fields if isinstance(row.get(f.name), (int, float))]
        if not numeric_fields:
            return row

        target = random.choice(numeric_fields)
        current = row[target.name]
        if isinstance(current, int):
            row[target.name] = current * random.randint(10, 100)
        else:
            row[target.name] = round(current * random.uniform(10.0, 100.0), 2)
        return row
