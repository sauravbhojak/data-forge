"""Pre-built template generator — instantiates TableSchema from template definitions."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from faker import Faker

from app.constants.templates import TEMPLATES
from app.exceptions.custom import TemplateNotFoundError
from app.generators.table_generator import TableGenerator
from app.schemas.generation import DataQualityConfig, FieldDefinition, TableSchema


class TemplateGenerator:
    """Resolves a template ID into a full TableSchema and generates rows."""

    def __init__(self, fake: Faker) -> None:
        self._table_gen = TableGenerator(fake)

    def get_schema(
        self,
        template_id: str,
        row_count: int,
        quality: DataQualityConfig | None = None,
    ) -> TableSchema:
        """Return a TableSchema built from a pre-built template definition."""
        tmpl = TEMPLATES.get(template_id)
        if not tmpl:
            raise TemplateNotFoundError(template_id)

        fields = [FieldDefinition(**f) for f in tmpl["fields"]]
        return TableSchema(
            name=template_id,
            fields=fields,
            row_count=row_count,
            quality=quality or DataQualityConfig(),
        )

    def generate(
        self,
        template_id: str,
        row_count: int,
        quality: DataQualityConfig | None = None,
    ) -> Iterator[dict[str, Any]]:
        """Yield rows for the specified pre-built template."""
        schema = self.get_schema(template_id, row_count, quality)
        yield from self._table_gen.generate(schema)
