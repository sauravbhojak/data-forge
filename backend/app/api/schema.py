"""SQL DDL schema generation endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.dependencies.faker_provider import FakerDep
from app.generators.relational_generator import RelationalGenerator
from app.generators.sql_generator import SQLGenerator
from app.schemas.generation import SQLResponse, SQLSchemaRequest
from app.services.generation_service import GenerationService

router = APIRouter(tags=["schema"])
_sql_gen = SQLGenerator()


@router.post("/generate-schema", response_model=SQLResponse, summary="Generate SQL DDL")
async def generate_schema(body: SQLSchemaRequest, fake: FakerDep) -> SQLResponse:
    """
    Generates CREATE TABLE, FOREIGN KEY, and INDEX statements for the given schema.
    Optionally generates sample INSERT INTO statements.
    """
    dialect = body.dialect
    ddl_parts: list[str] = []

    # CREATE TABLE for each table (sorted by name for deterministic output)
    for table in body.tables:
        ddl_parts.append(_sql_gen.generate_create_table(table, dialect, body.relationships))
        index_sql = _sql_gen.generate_indexes(table, dialect, body.relationships)
        if index_sql:
            ddl_parts.append(index_sql)

    # FOREIGN KEY constraints (after all tables exist)
    if body.relationships:
        fk_sql = _sql_gen.generate_foreign_keys(body.relationships, dialect)
        if fk_sql:
            ddl_parts.append(fk_sql)

    ddl = "\n\n".join(ddl_parts)

    # Optional sample INSERT INTO
    insert_sql: str | None = None
    if body.include_inserts and body.sample_rows > 0:
        gen_svc = GenerationService(fake)
        insert_parts: list[str] = []
        for table in body.tables:
            sample_schema = table.model_copy(update={"row_count": body.sample_rows})
            it, _ = gen_svc.generate_iter(sample_schema)
            rows = list(it)
            insert_parts.append(_sql_gen.generate_inserts(table.name, rows, dialect))
        insert_sql = "\n\n".join(insert_parts)

    return SQLResponse(dialect=dialect, ddl=ddl, insert_statements=insert_sql)
