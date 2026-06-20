"""SQL DDL and DML statement generator supporting multiple dialects."""

from __future__ import annotations

from typing import Any

from app.constants.distributions import SQLDialect
from app.constants.field_types import FieldType
from app.schemas.generation import FieldDefinition, RelationshipDefinition, TableSchema


# ── Type mappings per dialect ─────────────────────────────────────────────────

_PG_TYPES: dict[FieldType, str] = {
    FieldType.UUID: "UUID",
    FieldType.FIRST_NAME: "VARCHAR(100)",
    FieldType.LAST_NAME: "VARCHAR(100)",
    FieldType.FULL_NAME: "VARCHAR(200)",
    FieldType.EMAIL: "VARCHAR(320)",
    FieldType.PHONE: "VARCHAR(30)",
    FieldType.ADDRESS: "TEXT",
    FieldType.CITY: "VARCHAR(100)",
    FieldType.STATE: "VARCHAR(100)",
    FieldType.COUNTRY: "VARCHAR(100)",
    FieldType.ZIPCODE: "VARCHAR(20)",
    FieldType.LATITUDE: "NUMERIC(10,6)",
    FieldType.LONGITUDE: "NUMERIC(10,6)",
    FieldType.COMPANY: "VARCHAR(200)",
    FieldType.JOB_TITLE: "VARCHAR(200)",
    FieldType.DEPARTMENT: "VARCHAR(100)",
    FieldType.PRODUCT_NAME: "VARCHAR(200)",
    FieldType.CATEGORY: "VARCHAR(100)",
    FieldType.CURRENCY: "CHAR(3)",
    FieldType.SALARY: "NUMERIC(15,2)",
    FieldType.REVENUE: "NUMERIC(18,2)",
    FieldType.INTEGER: "INTEGER",
    FieldType.FLOAT: "DOUBLE PRECISION",
    FieldType.PERCENTAGE: "NUMERIC(6,2)",
    FieldType.BOOLEAN: "BOOLEAN",
    FieldType.DATE: "DATE",
    FieldType.DATETIME: "TIMESTAMP",
    FieldType.AGE: "SMALLINT",
    FieldType.GENDER: "VARCHAR(50)",
    FieldType.USERNAME: "VARCHAR(150)",
    FieldType.PASSWORD: "VARCHAR(256)",
    FieldType.URL: "TEXT",
    FieldType.IP_ADDRESS: "INET",
    FieldType.MAC_ADDRESS: "MACADDR",
    FieldType.TEXT: "VARCHAR(500)",
    FieldType.PARAGRAPH: "TEXT",
    FieldType.JSON: "JSONB",
    FieldType.CUSTOM_STRING: "VARCHAR(255)",
}

_MYSQL_OVERRIDES: dict[FieldType, str] = {
    FieldType.UUID: "VARCHAR(36)",
    FieldType.BOOLEAN: "TINYINT(1)",
    FieldType.DATETIME: "DATETIME",
    FieldType.LATITUDE: "DECIMAL(10,6)",
    FieldType.LONGITUDE: "DECIMAL(10,6)",
    FieldType.SALARY: "DECIMAL(15,2)",
    FieldType.REVENUE: "DECIMAL(18,2)",
    FieldType.PERCENTAGE: "DECIMAL(6,2)",
    FieldType.IP_ADDRESS: "VARCHAR(45)",
    FieldType.MAC_ADDRESS: "VARCHAR(17)",
    FieldType.JSON: "JSON",
    FieldType.FLOAT: "DOUBLE",
}

_SQLITE_OVERRIDES: dict[FieldType, str] = {
    FieldType.UUID: "TEXT",
    FieldType.BOOLEAN: "INTEGER",
    FieldType.DATE: "TEXT",
    FieldType.DATETIME: "TEXT",
    FieldType.LATITUDE: "REAL",
    FieldType.LONGITUDE: "REAL",
    FieldType.SALARY: "REAL",
    FieldType.REVENUE: "REAL",
    FieldType.PERCENTAGE: "REAL",
    FieldType.IP_ADDRESS: "TEXT",
    FieldType.MAC_ADDRESS: "TEXT",
    FieldType.JSON: "TEXT",
    FieldType.FLOAT: "REAL",
    FieldType.INTEGER: "INTEGER",
    FieldType.AGE: "INTEGER",
    FieldType.CURRENCY: "TEXT",
}

_SQLSERVER_OVERRIDES: dict[FieldType, str] = {
    FieldType.UUID: "UNIQUEIDENTIFIER",
    FieldType.BOOLEAN: "BIT",
    FieldType.DATETIME: "DATETIME2",
    FieldType.LATITUDE: "DECIMAL(10,6)",
    FieldType.LONGITUDE: "DECIMAL(10,6)",
    FieldType.SALARY: "DECIMAL(15,2)",
    FieldType.REVENUE: "DECIMAL(18,2)",
    FieldType.PERCENTAGE: "DECIMAL(6,2)",
    FieldType.IP_ADDRESS: "VARCHAR(45)",
    FieldType.MAC_ADDRESS: "VARCHAR(17)",
    FieldType.JSON: "NVARCHAR(MAX)",
    FieldType.FLOAT: "FLOAT",
    FieldType.PARAGRAPH: "NVARCHAR(MAX)",
    FieldType.URL: "NVARCHAR(MAX)",
    FieldType.ADDRESS: "NVARCHAR(MAX)",
}


class SQLGenerator:
    """Generates CREATE TABLE, ALTER TABLE (FK), INDEX, and INSERT INTO statements."""

    def get_type(self, field_type: FieldType, dialect: SQLDialect) -> str:
        base = _PG_TYPES.get(field_type, "VARCHAR(255)")
        if dialect == SQLDialect.MYSQL:
            return _MYSQL_OVERRIDES.get(field_type, base)
        if dialect == SQLDialect.SQLITE:
            return _SQLITE_OVERRIDES.get(field_type, base)
        if dialect == SQLDialect.SQLSERVER:
            return _SQLSERVER_OVERRIDES.get(field_type, base)
        return base  # PostgreSQL

    def quote(self, name: str, dialect: SQLDialect) -> str:
        if dialect == SQLDialect.MYSQL:
            return f"`{name}`"
        if dialect == SQLDialect.SQLSERVER:
            return f"[{name}]"
        return f'"{name}"'

    def generate_create_table(
        self,
        table: TableSchema,
        dialect: SQLDialect,
        relationships: list[RelationshipDefinition] | None = None,
    ) -> str:
        q = lambda n: self.quote(n, dialect)  # noqa: E731
        lines: list[str] = [f"CREATE TABLE {q(table.name)} ("]
        col_parts: list[str] = []

        for field in table.fields:
            sql_type = self.get_type(field.field_type, dialect)
            col = f"    {q(field.name)} {sql_type}"

            # UUID primary key detection
            if field.field_type == FieldType.UUID and field.unique:
                col += " PRIMARY KEY"
            elif not field.nullable:
                col += " NOT NULL"

            if field.unique and field.field_type != FieldType.UUID:
                col += " UNIQUE"

            if field.default is not None:
                col += f" DEFAULT {self._format_default(field.default, field.field_type, dialect)}"

            col_parts.append(col)

        lines.append(",\n".join(col_parts))
        lines.append(");")
        return "\n".join(lines)

    def generate_indexes(
        self,
        table: TableSchema,
        dialect: SQLDialect,
        relationships: list[RelationshipDefinition] | None = None,
    ) -> str:
        q = lambda n: self.quote(n, dialect)  # noqa: E731
        stmts: list[str] = []

        # Index on FK fields
        if relationships:
            for rel in relationships:
                if rel.child_table == table.name:
                    idx_name = f"idx_{table.name}_{rel.child_field}"
                    if dialect == SQLDialect.SQLSERVER:
                        stmts.append(
                            f"CREATE INDEX {q(idx_name)} ON {q(table.name)} ({q(rel.child_field)});"
                        )
                    else:
                        stmts.append(
                            f"CREATE INDEX {q(idx_name)} ON {q(table.name)} ({q(rel.child_field)});"
                        )

        return "\n".join(stmts)

    def generate_foreign_keys(
        self,
        relationships: list[RelationshipDefinition],
        dialect: SQLDialect,
    ) -> str:
        q = lambda n: self.quote(n, dialect)  # noqa: E731
        stmts: list[str] = []

        for rel in relationships:
            fk_name = f"fk_{rel.child_table}_{rel.child_field}"
            stmt = (
                f"ALTER TABLE {q(rel.child_table)}\n"
                f"    ADD CONSTRAINT {q(fk_name)}\n"
                f"    FOREIGN KEY ({q(rel.child_field)})\n"
                f"    REFERENCES {q(rel.parent_table)} ({q(rel.parent_field)});"
            )
            stmts.append(stmt)

        return "\n\n".join(stmts)

    def generate_inserts(
        self,
        table_name: str,
        rows: list[dict[str, Any]],
        dialect: SQLDialect,
        batch_size: int = 50,
    ) -> str:
        if not rows:
            return ""

        q = lambda n: self.quote(n, dialect)  # noqa: E731
        columns = list(rows[0].keys())
        header = f"INSERT INTO {q(table_name)} ({', '.join(q(c) for c in columns)}) VALUES"

        stmts: list[str] = []
        for start in range(0, len(rows), batch_size):
            batch = rows[start : start + batch_size]
            value_rows = []
            for row in batch:
                vals = ", ".join(self._format_value(row[c]) for c in columns)
                value_rows.append(f"    ({vals})")
            stmts.append(f"{header}\n" + ",\n".join(value_rows) + ";")

        return "\n\n".join(stmts)

    @staticmethod
    def _format_value(val: Any) -> str:
        if val is None:
            return "NULL"
        if isinstance(val, bool):
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return str(val)
        # Escape single quotes
        escaped = str(val).replace("'", "''")
        return f"'{escaped}'"

    @staticmethod
    def _format_default(val: Any, field_type: FieldType, dialect: SQLDialect) -> str:
        if val is None:
            return "NULL"
        if isinstance(val, bool):
            if dialect == SQLDialect.SQLITE:
                return "1" if val else "0"
            return "TRUE" if val else "FALSE"
        if isinstance(val, (int, float)):
            return str(val)
        escaped = str(val).replace("'", "''")
        return f"'{escaped}'"
