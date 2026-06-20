"""ERD generation endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.generators.erd_generator import ERDGenerator
from app.schemas.generation import ERDRequest, ERDResponse

router = APIRouter(tags=["schema"])
_erd_gen = ERDGenerator()


@router.post("/generate-erd", response_model=ERDResponse, summary="Generate Mermaid ER diagram")
async def generate_erd(body: ERDRequest) -> ERDResponse:
    """
    Generates a Mermaid erDiagram definition from table schemas and relationships.
    The frontend renders this using mermaid.js.
    """
    mermaid = _erd_gen.generate(body)
    return ERDResponse(
        mermaid=mermaid,
        table_count=len(body.tables),
        relationship_count=len(body.relationships),
    )
