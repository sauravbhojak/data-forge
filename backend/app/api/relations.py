"""Relational data generation endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.dependencies.faker_provider import FakerDep
from app.generators.relational_generator import RelationalGenerator
from app.schemas.generation import RelationalSchemaRequest

router = APIRouter(tags=["generation"])


@router.post("/generate-relations", summary="Preview relational multi-table data")
async def generate_relations(body: RelationalSchemaRequest, fake: FakerDep) -> dict:
    """
    Generates relational multi-table data with referential integrity.
    Returns first 50 rows per table as preview.
    For full export use /export/* endpoints with the same schema.
    """
    gen = RelationalGenerator(fake)
    full_data = gen.generate(body)

    # Return only first 50 rows per table for preview
    preview: dict[str, list] = {}
    for table_name, rows in full_data.items():
        preview[table_name] = rows[:50]

    return {
        "tables": list(preview.keys()),
        "preview": preview,
        "row_counts": {name: len(rows) for name, rows in full_data.items()},
    }
