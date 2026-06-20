"""Template listing endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.generation import TemplateInfo
from app.services.template_service import TemplateService

router = APIRouter(tags=["templates"])
_svc = TemplateService()


@router.get("/templates", response_model=list[TemplateInfo], summary="List all pre-built templates")
async def list_templates() -> list[TemplateInfo]:
    """Returns metadata for all available pre-built dataset templates."""
    return _svc.list_templates()
