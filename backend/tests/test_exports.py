"""Unit tests for all export formats."""

from __future__ import annotations

import csv
import io
import json

import pytest

from app.constants.distributions import SQLDialect
from app.exports.csv_exporter import CSVExporter
from app.exports.excel_exporter import ExcelExporter
from app.exports.json_exporter import JSONExporter
from app.exports.sql_exporter import SQLExporter


def make_rows(n: int = 10) -> list[dict]:
    return [
        {"id": i, "name": f"User {i}", "active": i % 2 == 0, "score": round(i * 1.5, 2)}
        for i in range(1, n + 1)
    ]


class TestCSVExporter:
    def test_produces_valid_csv(self) -> None:
        exporter = CSVExporter()
        rows = make_rows(5)
        chunks = list(exporter.export(iter(rows)))
        content = b"".join(chunks).decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))
        parsed = list(reader)
        assert len(parsed) == 5
        assert parsed[0]["name"] == "User 1"

    def test_has_header_row(self) -> None:
        exporter = CSVExporter()
        chunks = b"".join(exporter.export(iter(make_rows(3))))
        lines = chunks.decode("utf-8-sig").strip().split("\r\n")
        assert "id" in lines[0]
        assert "name" in lines[0]

    def test_empty_iterator_yields_nothing(self) -> None:
        exporter = CSVExporter()
        chunks = list(exporter.export(iter([])))
        assert chunks == []

    def test_large_row_count_is_memory_efficient(self) -> None:
        """Generator should not OOM — just verify it runs."""
        exporter = CSVExporter()
        large = ({"id": i, "val": "x" * 100} for i in range(10_000))
        byte_count = sum(len(chunk) for chunk in exporter.export(large))
        assert byte_count > 0


class TestJSONExporter:
    def test_produces_valid_json_array(self) -> None:
        exporter = JSONExporter()
        rows = make_rows(5)
        raw = b"".join(exporter.export(iter(rows))).decode("utf-8")
        parsed = json.loads(raw)
        assert isinstance(parsed, list)
        assert len(parsed) == 5

    def test_preserves_field_values(self) -> None:
        exporter = JSONExporter()
        rows = [{"name": "Alice", "age": 30}]
        raw = b"".join(exporter.export(iter(rows))).decode("utf-8")
        parsed = json.loads(raw)
        assert parsed[0]["name"] == "Alice"
        assert parsed[0]["age"] == 30

    def test_empty_iterator_yields_valid_empty_array(self) -> None:
        exporter = JSONExporter()
        raw = b"".join(exporter.export(iter([]))).decode("utf-8")
        parsed = json.loads(raw)
        assert parsed == []


class TestSQLExporter:
    def test_produces_insert_statements(self) -> None:
        exporter = SQLExporter(batch_size=5)
        rows = make_rows(5)
        sql = b"".join(exporter.export("users", iter(rows), SQLDialect.POSTGRESQL)).decode("utf-8")
        assert "INSERT INTO" in sql
        assert '"users"' in sql

    def test_mysql_uses_backticks(self) -> None:
        exporter = SQLExporter(batch_size=5)
        rows = make_rows(3)
        sql = b"".join(exporter.export("users", iter(rows), SQLDialect.MYSQL)).decode("utf-8")
        assert "`users`" in sql

    def test_batches_correctly(self) -> None:
        exporter = SQLExporter(batch_size=3)
        rows = make_rows(10)
        chunks = list(exporter.export("t", iter(rows), SQLDialect.POSTGRESQL))
        # Expect ceil(10/3) = 4 chunks
        assert len(chunks) == 4

    def test_handles_none_values(self) -> None:
        exporter = SQLExporter(batch_size=5)
        rows = [{"id": 1, "name": None}]
        sql = b"".join(exporter.export("t", iter(rows))).decode("utf-8")
        assert "NULL" in sql


class TestExcelExporter:
    def test_returns_bytes(self) -> None:
        exporter = ExcelExporter()
        rows = make_rows(5)
        result = exporter.export(iter(rows))
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_valid_xlsx_magic_bytes(self) -> None:
        """XLSX files start with PK (zip archive magic bytes)."""
        exporter = ExcelExporter()
        rows = make_rows(3)
        result = exporter.export(iter(rows))
        assert result[:2] == b"PK"

    def test_empty_iterator(self) -> None:
        exporter = ExcelExporter()
        result = exporter.export(iter([]))
        assert isinstance(result, bytes)
