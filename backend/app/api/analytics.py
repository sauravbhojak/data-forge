"""Analytics preview endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.generation import AnalyticsRequest
from app.services.analytics_service import AnalyticsService

router = APIRouter(tags=["analytics"])


@router.post("/analytics/preview", summary="Preview analytics dataset")
async def analytics_preview(body: AnalyticsRequest) -> dict:
    """Returns first 50 rows of the requested analytics dataset."""
    svc = AnalyticsService()
    rows = svc.preview(body)
    columns = list(rows[0].keys()) if rows else []
    return {
        "dataset_type": body.dataset_type,
        "columns": columns,
        "rows": rows,
        "preview_count": len(rows),
    }
