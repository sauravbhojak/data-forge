"""Template service — resolves template metadata and schemas."""

from __future__ import annotations

from app.constants.templates import TEMPLATES
from app.exceptions.custom import TemplateNotFoundError
from app.schemas.generation import FieldDefinition, TableSchema, TemplateInfo


class TemplateService:
    """Provides template metadata and schema resolution."""

    def list_templates(self) -> list[TemplateInfo]:
        """Return metadata for all available pre-built templates."""
        from app.schemas.generation import TableSchema, RelationshipDefinition
        result: list[TemplateInfo] = []
        for tmpl in TEMPLATES.values():
            template_type = tmpl.get("template_type", "single")
            if template_type == "single":
                field_names = [f["name"] for f in tmpl.get("fields", [])]
                result.append(
                    TemplateInfo(
                        id=tmpl["id"],
                        name=tmpl["name"],
                        description=tmpl["description"],
                        icon=tmpl["icon"],
                        tags=tmpl["tags"],
                        template_type=template_type,
                        field_count=len(tmpl.get("fields", [])),
                        field_names=field_names,
                        fields=[FieldDefinition(**f) for f in tmpl.get("fields", [])],
                    )
                )
            else:
                tables = tmpl.get("tables", [])
                relationships = tmpl.get("relationships", [])
                result.append(
                    TemplateInfo(
                        id=tmpl["id"],
                        name=tmpl["name"],
                        description=tmpl["description"],
                        icon=tmpl["icon"],
                        tags=tmpl["tags"],
                        template_type=template_type,
                        table_count=len(tables),
                        relationship_count=len(relationships),
                        tables=[TableSchema(**t) for t in tables],
                        relationships=[RelationshipDefinition(**r) for r in relationships],
                    )
                )
        return result

    def get_schema(self, template_id: str, row_count: int) -> TableSchema:
        """Build a TableSchema from a template ID."""
        tmpl = TEMPLATES.get(template_id)
        if not tmpl:
            raise TemplateNotFoundError(template_id)
        fields = [FieldDefinition(**f) for f in tmpl["fields"]]
        return TableSchema(name=template_id, fields=fields, row_count=row_count)
