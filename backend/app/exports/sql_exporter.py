"""Streaming SQL INSERT exporter with batched statements."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from app.constants.distributions import SQLDialect
from app.generators.sql_generator import SQLGenerator


class SQLExporter:
    """
    Streams INSERT INTO statements in configurable batches.

    Memory: O(batch_size) — only one batch of rows is held at a time.
    """

    def __init__(self, batch_size: int = 500) -> None:
        self._batch_size = batch_size
        self._sql_gen = SQLGenerator()

    def export(
        self,
        table_name: str,
        data: Iterator[dict[str, Any]],
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
    ) -> Iterator[bytes]:
        """Yield UTF-8 encoded SQL INSERT statements in batches."""
        batch: list[dict[str, Any]] = []

        for row in data:
            batch.append(row)
            if len(batch) >= self._batch_size:
                sql = self._sql_gen.generate_inserts(table_name, batch, dialect, self._batch_size)
                yield (sql + "\n\n").encode("utf-8")
                batch.clear()

        # Flush remaining rows
        if batch:
            sql = self._sql_gen.generate_inserts(table_name, batch, dialect, self._batch_size)
            yield (sql + "\n").encode("utf-8")
