"""Streaming export endpoints for CSV, JSON, SQL, and Excel."""

from __future__ import annotations

import logging
import os

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse, Response, StreamingResponse

from app.constants.distributions import SQLDialect
from app.dependencies.faker_provider import FakerDep
from app.generators.analytics_generator import AnalyticsGenerator
from app.schemas.generation import (
    AnalyticsExportRequest,
    AnalyticsRequest,
    ExportRequest,
    RelationalExportRequest,
)
from app.services.analytics_service import AnalyticsService
from app.services.export_service import ExportService
from app.services.generation_service import GenerationService
from app.utils.sanitize import sanitize_filename

router = APIRouter(tags=["export"])
logger = logging.getLogger(__name__)

_export_svc = ExportService()


# ── Helper ────────────────────────────────────────────────────────────────────

def _cd(filename: str, inline: bool = False) -> str:
    disposition = "inline" if inline else "attachment"
    return f'{disposition}; filename="{filename}"'


def _remove_file(path: str) -> None:
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            logger.error(f"Failed to remove temp file {path}: {e}")


# ── CSV ───────────────────────────────────────────────────────────────────────

@router.post("/export/csv", summary="Stream CSV export")
async def export_csv(body: ExportRequest, fake: FakerDep) -> StreamingResponse:
    """Streams a CSV file for the given table schema. Uses chunked transfer encoding."""
    svc = GenerationService(fake)
    it, _ = svc.generate_iter(body.table)
    filename = sanitize_filename(body.table.name, "csv")

    logger.info("CSV export started", extra={"table": body.table.name, "rows": body.table.row_count})

    return StreamingResponse(
        _export_svc.stream_csv(it),
        media_type="text/csv",
        headers={"Content-Disposition": _cd(filename)},
    )


# ── JSON ──────────────────────────────────────────────────────────────────────

@router.post("/export/json", summary="Stream JSON export")
async def export_json(body: ExportRequest, fake: FakerDep) -> StreamingResponse:
    """Streams a JSON array file for the given table schema."""
    svc = GenerationService(fake)
    it, _ = svc.generate_iter(body.table)
    filename = sanitize_filename(body.table.name, "json")

    return StreamingResponse(
        _export_svc.stream_json(it),
        media_type="application/json",
        headers={"Content-Disposition": _cd(filename)},
    )


# ── SQL ───────────────────────────────────────────────────────────────────────

@router.post("/export/sql", summary="Stream SQL INSERT export")
async def export_sql(
    body: ExportRequest,
    fake: FakerDep,
    dialect: SQLDialect = SQLDialect.POSTGRESQL,
) -> StreamingResponse:
    """Streams SQL INSERT INTO statements for the given table schema."""
    svc = GenerationService(fake)
    it, _ = svc.generate_iter(body.table)
    filename = sanitize_filename(body.table.name, "sql")

    return StreamingResponse(
        _export_svc.stream_sql(body.table.name, it, dialect),
        media_type="application/sql",
        headers={"Content-Disposition": _cd(filename)},
    )


# ── Excel ─────────────────────────────────────────────────────────────────────

@router.post("/export/excel", summary="Export Excel file")
async def export_excel(body: ExportRequest, fake: FakerDep) -> Response:
    """
    Returns an Excel (.xlsx) file for the given table schema.
    Note: Excel is not streaming — the full file is generated in memory before sending.
    For datasets > 100k rows, prefer CSV or JSON.
    """
    svc = GenerationService(fake)
    it, _ = svc.generate_iter(body.table)
    filename = sanitize_filename(body.table.name, "xlsx")

    xlsx_bytes = _export_svc.export_excel(it, sheet_name=body.table.name[:31])

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": _cd(filename)},
    )


# ── Analytics Exports ─────────────────────────────────────────────────────────

@router.post("/export/analytics/csv", summary="Stream analytics dataset as CSV")
async def export_analytics_csv(body: AnalyticsRequest) -> StreamingResponse:
    """Streams an analytics dataset as CSV."""
    svc = AnalyticsService()
    it = svc.generate_iter(body)
    filename = sanitize_filename(f"{body.dataset_type}_analytics", "csv")

    return StreamingResponse(
        _export_svc.stream_csv(it),
        media_type="text/csv",
        headers={"Content-Disposition": _cd(filename)},
    )


@router.post("/export/analytics/json", summary="Stream analytics dataset as JSON")
async def export_analytics_json(body: AnalyticsRequest) -> StreamingResponse:
    """Streams an analytics dataset as JSON."""
    svc = AnalyticsService()
    it = svc.generate_iter(body)
    filename = sanitize_filename(f"{body.dataset_type}_analytics", "json")

    return StreamingResponse(
        _export_svc.stream_json(it),
        media_type="application/json",
        headers={"Content-Disposition": _cd(filename)},
    )


# ── Relational Exports ────────────────────────────────────────────────────────

@router.post("/export/relational/csv", summary="Export relational schema as CSV ZIP")
async def export_relational_csv(body: RelationalExportRequest, fake: FakerDep, background_tasks: BackgroundTasks) -> FileResponse:
    """Generates all tables and returns a single ZIP file containing CSVs."""
    svc = GenerationService(fake)
    datasets = {table.name: svc.generate_iter(table)[0] for table in body.tables}
    filepath = _export_svc.export_relational_csv_zip(datasets)
    background_tasks.add_task(_remove_file, filepath)
    filename = "relational_dataset_csv.zip"
    return FileResponse(filepath, media_type="application/zip", headers={"Content-Disposition": _cd(filename)})


@router.post("/export/relational/json", summary="Export relational schema as JSON ZIP")
async def export_relational_json(body: RelationalExportRequest, fake: FakerDep, background_tasks: BackgroundTasks) -> FileResponse:
    """Generates all tables and returns a single ZIP file containing JSONs."""
    svc = GenerationService(fake)
    datasets = {table.name: svc.generate_iter(table)[0] for table in body.tables}
    filepath = _export_svc.export_relational_json_zip(datasets)
    background_tasks.add_task(_remove_file, filepath)
    filename = "relational_dataset_json.zip"
    return FileResponse(filepath, media_type="application/zip", headers={"Content-Disposition": _cd(filename)})


@router.post("/export/relational/excel", summary="Export relational schema as multi-sheet Excel")
async def export_relational_excel(body: RelationalExportRequest, fake: FakerDep, background_tasks: BackgroundTasks) -> FileResponse:
    """Generates all tables and returns a single Excel file with multiple sheets."""
    svc = GenerationService(fake)
    datasets = {table.name: svc.generate_iter(table)[0] for table in body.tables}
    filepath = _export_svc.export_relational_excel(datasets)
    background_tasks.add_task(_remove_file, filepath)
    filename = "relational_dataset.xlsx"
    return FileResponse(filepath, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": _cd(filename)})


@router.post("/export/relational/sql", summary="Export relational schema as SQL")
async def export_relational_sql(
    body: RelationalExportRequest, 
    fake: FakerDep, 
    background_tasks: BackgroundTasks,
    dialect: SQLDialect = SQLDialect.POSTGRESQL
) -> FileResponse:
    """Generates all tables and returns a single SQL file containing inserts."""
    svc = GenerationService(fake)
    datasets = {table.name: svc.generate_iter(table)[0] for table in body.tables}
    filepath = _export_svc.export_relational_sql(datasets, dialect)
    background_tasks.add_task(_remove_file, filepath)
    filename = "relational_dataset.sql"
    return FileResponse(filepath, media_type="application/sql", headers={"Content-Disposition": _cd(filename)})
