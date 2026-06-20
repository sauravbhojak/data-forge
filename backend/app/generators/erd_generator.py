"""Mermaid ER diagram generator."""

from __future__ import annotations

from app.constants.distributions import RelationshipType
from app.constants.field_types import FieldType
from app.schemas.generation import ERDRequest, RelationshipDefinition, TableSchema

# Map FieldType → Mermaid entity attribute type
_MERMAID_TYPES: dict[FieldType, str] = {
    FieldType.UUID: "string",
    FieldType.FIRST_NAME: "string",
    FieldType.LAST_NAME: "string",
    FieldType.FULL_NAME: "string",
    FieldType.EMAIL: "string",
    FieldType.PHONE: "string",
    FieldType.ADDRESS: "string",
    FieldType.CITY: "string",
    FieldType.STATE: "string",
    FieldType.COUNTRY: "string",
    FieldType.ZIPCODE: "string",
    FieldType.LATITUDE: "float",
    FieldType.LONGITUDE: "float",
    FieldType.COMPANY: "string",
    FieldType.JOB_TITLE: "string",
    FieldType.DEPARTMENT: "string",
    FieldType.PRODUCT_NAME: "string",
    FieldType.CATEGORY: "string",
    FieldType.CURRENCY: "string",
    FieldType.SALARY: "decimal",
    FieldType.REVENUE: "decimal",
    FieldType.INTEGER: "int",
    FieldType.FLOAT: "float",
    FieldType.PERCENTAGE: "float",
    FieldType.BOOLEAN: "boolean",
    FieldType.DATE: "date",
    FieldType.DATETIME: "datetime",
    FieldType.AGE: "int",
    FieldType.GENDER: "string",
    FieldType.USERNAME: "string",
    FieldType.PASSWORD: "string",
    FieldType.URL: "string",
    FieldType.IP_ADDRESS: "string",
    FieldType.MAC_ADDRESS: "string",
    FieldType.TEXT: "string",
    FieldType.PARAGRAPH: "string",
    FieldType.JSON: "object",
    FieldType.CUSTOM_STRING: "string",
}

# Mermaid relationship cardinality notation
_CARDINALITY: dict[RelationshipType, str] = {
    RelationshipType.ONE_TO_ONE: "||--||",
    RelationshipType.ONE_TO_MANY: "||--o{",
    RelationshipType.MANY_TO_ONE: "}o--||",
}


class ERDGenerator:
    """Generates Mermaid erDiagram syntax from table schemas and relationships."""

    def generate(self, request: ERDRequest) -> str:
        lines: list[str] = ["erDiagram"]

        # ── Entity definitions ────────────────────────────────────────────────
        for table in request.tables:
            lines.append(f"    {table.name} {{")
            for field in table.fields:
                mtype = _MERMAID_TYPES.get(field.field_type, "string")
                pk_marker = " PK" if (field.unique and field.field_type == FieldType.UUID) else ""
                fk_marker = self._fk_marker(field.name, table.name, request)
                marker = pk_marker or fk_marker
                lines.append(f"        {mtype} {field.name}{marker}")
            lines.append("    }")

        # ── Relationships ─────────────────────────────────────────────────────
        for rel in request.relationships:
            cardinality = _CARDINALITY.get(rel.relationship_type, "||--o{")
            label = f"{rel.parent_field} to {rel.child_field}"
            lines.append(f'    {rel.parent_table} {cardinality} {rel.child_table} : "{label}"')

        return "\n".join(lines)

    @staticmethod
    def _fk_marker(
        field_name: str,
        table_name: str,
        request: ERDRequest,
    ) -> str:
        for rel in request.relationships:
            if rel.child_table == table_name and rel.child_field == field_name:
                return " FK"
        return ""
