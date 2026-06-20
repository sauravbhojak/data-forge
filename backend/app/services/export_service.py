"""Export service — routes data iterators to the appropriate exporter."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any
import os
import tempfile
import zipfile

from app.constants.distributions import ExportFormat, SQLDialect
from app.exceptions.custom import ExportError
from app.exports.csv_exporter import CSVExporter
from app.exports.excel_exporter import ExcelExporter
from app.exports.json_exporter import JSONExporter
from app.exports.sql_exporter import SQLExporter


class ExportService:
    """Thin service that dispatches to the correct exporter."""

    def __init__(self) -> None:
        self._csv = CSVExporter()
        self._json = JSONExporter()
        self._sql = SQLExporter()
        self._excel = ExcelExporter()

    def stream_csv(self, data: Iterator[dict[str, Any]]) -> Iterator[bytes]:
        """Stream CSV bytes."""
        try:
            yield from self._csv.export(data)
        except Exception as e:
            raise ExportError(f"CSV export failed: {e}", str(e)) from e

    def stream_json(self, data: Iterator[dict[str, Any]]) -> Iterator[bytes]:
        """Stream JSON bytes."""
        try:
            yield from self._json.export(data)
        except Exception as e:
            raise ExportError(f"JSON export failed: {e}", str(e)) from e

    def stream_sql(
        self,
        table_name: str,
        data: Iterator[dict[str, Any]],
        dialect: SQLDialect = SQLDialect.POSTGRESQL,
    ) -> Iterator[bytes]:
        """Stream SQL INSERT bytes."""
        try:
            yield from self._sql.export(table_name, data, dialect)
        except Exception as e:
            raise ExportError(f"SQL export failed: {e}", str(e)) from e

    def export_excel(self, data: Iterator[dict[str, Any]], sheet_name: str = "DataForge") -> bytes:
        """Return complete Excel file bytes."""
        try:
            return self._excel.export(data, sheet_name=sheet_name)
        except Exception as e:
            raise ExportError(f"Excel export failed: {e}", str(e)) from e

    def export_relational_csv_zip(self, datasets: dict[str, Iterator[dict[str, Any]]]) -> str:
        """Writes CSVs into a zip file on disk and returns the filepath."""
        fd, filepath = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        try:
            with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                for table_name, data_iter in datasets.items():
                    with zf.open(f"{table_name}.csv", "w") as f:
                        for chunk in self._csv.export(data_iter):
                            f.write(chunk)
            return filepath
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ExportError(f"Relational CSV export failed: {e}", str(e)) from e

    def export_relational_json_zip(self, datasets: dict[str, Iterator[dict[str, Any]]]) -> str:
        """Writes JSONs into a zip file on disk and returns the filepath."""
        fd, filepath = tempfile.mkstemp(suffix=".zip")
        os.close(fd)
        try:
            with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as zf:
                for table_name, data_iter in datasets.items():
                    with zf.open(f"{table_name}.json", "w") as f:
                        for chunk in self._json.export(data_iter):
                            f.write(chunk)
            return filepath
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ExportError(f"Relational JSON export failed: {e}", str(e)) from e

    def export_relational_excel(self, datasets: dict[str, Iterator[dict[str, Any]]]) -> str:
        """Writes a multi-sheet Excel file to disk and returns the filepath."""
        fd, filepath = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)
        try:
            self._excel.export_relational(datasets, filepath)
            return filepath
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ExportError(f"Relational Excel export failed: {e}", str(e)) from e

    def export_relational_sql(
        self, datasets: dict[str, Iterator[dict[str, Any]]], dialect: SQLDialect = SQLDialect.POSTGRESQL
    ) -> str:
        """Writes SQL INSERTS for all tables into a single SQL file on disk and returns the filepath."""
        fd, filepath = tempfile.mkstemp(suffix=".sql")
        os.close(fd)
        try:
            with open(filepath, "wb") as f:
                for table_name, data_iter in datasets.items():
                    for chunk in self._sql.export(table_name, data_iter, dialect):
                        f.write(chunk)
            return filepath
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            raise ExportError(f"Relational SQL export failed: {e}", str(e)) from e
