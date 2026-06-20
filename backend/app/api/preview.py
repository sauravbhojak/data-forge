"""Preview endpoint — returns first 50 rows as JSON."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from faker import Faker

from app.dependencies.faker_provider import FakerDep
from app.schemas.generation import PreviewRequest, PreviewResponse
from app.services.generation_service import GenerationService

router = APIRouter(tags=["generation"])


@router.post("/preview", response_model=PreviewResponse, summary="Preview first 50 rows")
async def preview(body: PreviewRequest, fake: FakerDep) -> PreviewResponse:
    """
    Generates and returns the first 50 rows for a given table schema.
    Never streams — response is small by design.
    """
    svc = GenerationService(fake)
    return svc.preview(body.table)
