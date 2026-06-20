"""Pydantic v2 request and response schemas for data generation."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.constants.distributions import (
    AnalyticsDatasetType,
    Distribution,
    RelationshipType,
    SQLDialect,
)
from app.constants.field_types import FieldType


# ── Field Definition ──────────────────────────────────────────────────────────

class FieldDefinition(BaseModel):
    """Complete definition of a single table column."""

    name: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    field_type: FieldType
    nullable: bool = False
    unique: bool = False
    default: Any | None = None
    min_value: float | None = None
    max_value: float | None = None
    prefix: str | None = Field(default=None, max_length=32)
    suffix: str | None = Field(default=None, max_length=32)
    length: int | None = Field(default=None, ge=1, le=10_000)
    regex: str | None = Field(default=None, max_length=256)
    sequential: bool = False
    enum_values: list[Any] | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=512)
    distribution: Distribution | None = None

    @field_validator("enum_values")
    @classmethod
    def validate_enum_not_empty(cls, v: list[Any] | None) -> list[Any] | None:
        if v is not None and len(v) == 0:
            raise ValueError("enum_values must not be an empty list")
        return v

    @model_validator(mode="after")
    def validate_min_max(self) -> "FieldDefinition":
        if self.min_value is not None and self.max_value is not None:
            if self.min_value > self.max_value:
                raise ValueError("min_value must be less than or equal to max_value")
        return self


# ── Table Schema ──────────────────────────────────────────────────────────────

class DataQualityConfig(BaseModel):
    """Data quality controls for a generated table."""

    null_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Fraction of nullable fields to set NULL")
    duplicate_rate: float = Field(default=0.0, ge=0.0, le=0.5, description="Fraction of rows to duplicate")
    outlier_rate: float = Field(default=0.0, ge=0.0, le=0.2, description="Fraction of numeric rows that become outliers")
    distribution: Distribution | None = None


class TableSchema(BaseModel):
    """Schema definition for a single table to be generated."""

    name: str = Field(..., min_length=1, max_length=64, pattern=r"^[a-zA-Z_][a-zA-Z0-9_]*$")
    fields: list[FieldDefinition] = Field(..., min_length=1, max_length=100)
    row_count: int = Field(default=100, ge=1, le=1_000_000)
    quality: DataQualityConfig = Field(default_factory=DataQualityConfig)

    @field_validator("fields")
    @classmethod
    def validate_unique_field_names(cls, v: list[FieldDefinition]) -> list[FieldDefinition]:
        names = [f.name for f in v]
        if len(names) != len(set(names)):
            raise ValueError("Field names must be unique within a table")
        return v


# ── Relationship ─────────────────────────────────────────────────────────────

class RelationshipDefinition(BaseModel):
    """Defines a foreign key relationship between two tables."""

    parent_table: str = Field(..., min_length=1, max_length=64)
    parent_field: str = Field(..., min_length=1, max_length=64)
    child_table: str = Field(..., min_length=1, max_length=64)
    child_field: str = Field(..., min_length=1, max_length=64)
    relationship_type: RelationshipType = RelationshipType.ONE_TO_MANY

    @model_validator(mode="after")
    def validate_different_tables(self) -> "RelationshipDefinition":
        if self.parent_table == self.child_table:
            raise ValueError("parent_table and child_table must be different")
        return self


# ── Generation Requests ───────────────────────────────────────────────────────

class PreviewRequest(BaseModel):
    """Request to preview the first N rows of a single table."""

    table: TableSchema


class GenerationRequest(BaseModel):
    """Request to generate a single table (non-streaming metadata response)."""

    table: TableSchema


class RelationalSchemaRequest(BaseModel):
    """Request to generate multiple related tables."""

    tables: list[TableSchema] = Field(..., min_length=1, max_length=20)
    relationships: list[RelationshipDefinition] = Field(default_factory=list, max_length=50)

    @field_validator("tables")
    @classmethod
    def validate_unique_table_names(cls, v: list[TableSchema]) -> list[TableSchema]:
        names = [t.name for t in v]
        if len(names) != len(set(names)):
            raise ValueError("Table names must be unique in the schema")
        return v


class SQLSchemaRequest(BaseModel):
    """Request to generate a SQL DDL script."""

    tables: list[TableSchema] = Field(..., min_length=1, max_length=20)
    relationships: list[RelationshipDefinition] = Field(default_factory=list)
    dialect: SQLDialect = SQLDialect.POSTGRESQL
    include_inserts: bool = False
    sample_rows: int = Field(default=10, ge=0, le=100)


class ERDRequest(BaseModel):
    """Request to generate a Mermaid ER diagram."""

    tables: list[TableSchema] = Field(..., min_length=1, max_length=20)
    relationships: list[RelationshipDefinition] = Field(default_factory=list)


class AnalyticsRequest(BaseModel):
    """Request to generate a correlated analytics dataset."""

    dataset_type: AnalyticsDatasetType
    row_count: int = Field(default=365, ge=1, le=1_000_000)
    start_date: str | None = Field(default=None, description="ISO date string YYYY-MM-DD")
    trend_strength: float = Field(default=1.0, ge=0.0, le=5.0)
    noise_level: float = Field(default=0.1, ge=0.0, le=1.0)


# ── Export Requests ───────────────────────────────────────────────────────────

class ExportRequest(BaseModel):
    """Generic export request for single table → file."""

    table: TableSchema


class AnalyticsExportRequest(BaseModel):
    """Export request for analytics datasets."""

    analytics: AnalyticsRequest


class RelationalExportRequest(BaseModel):
    """Export request for relational multi-table → ZIP of files."""

    tables: list[TableSchema] = Field(..., min_length=1, max_length=20)
    relationships: list[RelationshipDefinition] = Field(default_factory=list)


# ── Response Models ───────────────────────────────────────────────────────────

class GenerationMetrics(BaseModel):
    """Performance metrics returned after generation."""

    row_count: int
    field_count: int
    generation_time_ms: float
    memory_delta_mb: float


class PreviewResponse(BaseModel):
    """Response containing preview rows and metadata."""

    table_name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total_count: int
    preview_count: int
    metrics: GenerationMetrics


class GenerationResponse(BaseModel):
    """Response after successful generation (no data — triggers download)."""

    table_name: str
    row_count: int
    metrics: GenerationMetrics
    message: str = "Generation complete"


class SQLResponse(BaseModel):
    """Response containing generated SQL DDL."""

    dialect: SQLDialect
    ddl: str
    insert_statements: str | None = None


class ERDResponse(BaseModel):
    """Response containing Mermaid ER diagram source."""

    mermaid: str
    table_count: int
    relationship_count: int


class TemplateInfo(BaseModel):
    """Metadata for a pre-built template."""

    id: str
    name: str
    description: str
    icon: str
    tags: list[str]
    template_type: str = "single"
    field_count: int | None = None
    field_names: list[str] | None = None
    fields: list[FieldDefinition] | None = None
    table_count: int | None = None
    relationship_count: int | None = None
    tables: list[TableSchema] | None = None
    relationships: list[RelationshipDefinition] | None = None
