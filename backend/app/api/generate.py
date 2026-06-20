"""Generate endpoint — returns generation metrics without data payload."""

from __future__ import annotations

from fastapi import APIRouter

from app.dependencies.faker_provider import FakerDep
from app.schemas.generation import GenerationRequest, GenerationResponse
from app.services.generation_service import GenerationService

router = APIRouter(tags=["generation"])


@router.post("/generate", response_model=GenerationResponse, summary="Generate data and return metrics")
async def generate(body: GenerationRequest, fake: FakerDep) -> GenerationResponse:
    """
    Generates the full dataset server-side and returns timing/memory metrics.
    Use the /export/* endpoints to receive the actual data as a downloadable file.
    """
    svc = GenerationService(fake)
    return svc.generate_response(body.table)
