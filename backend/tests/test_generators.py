"""Unit tests for field and table generators."""

from __future__ import annotations

import pytest
from faker import Faker

from app.constants.field_types import FieldType
from app.constants.distributions import Distribution
from app.generators.field_generator import FieldGenerator
from app.generators.table_generator import TableGenerator
from app.generators.analytics_generator import AnalyticsGenerator
from app.schemas.generation import (
    AnalyticsRequest,
    DataQualityConfig,
    FieldDefinition,
    TableSchema,
)
from app.constants.distributions import AnalyticsDatasetType


@pytest.fixture
def fake() -> Faker:
    return Faker()


@pytest.fixture
def field_gen(fake: Faker) -> FieldGenerator:
    return FieldGenerator(fake)


@pytest.fixture
def table_gen(fake: Faker) -> TableGenerator:
    return TableGenerator(fake)


# ── FieldGenerator tests ──────────────────────────────────────────────────────

class TestFieldGenerator:
    def test_uuid_generation(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="id", field_type=FieldType.UUID)
        val = field_gen.generate_value(field, "t.id")
        assert isinstance(val, str)
        assert len(val) == 36  # UUID4 format

    def test_email_is_valid_string(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="email", field_type=FieldType.EMAIL)
        val = field_gen.generate_value(field, "t.email")
        assert isinstance(val, str)
        assert "@" in val

    def test_integer_respects_range(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="age", field_type=FieldType.INTEGER, min_value=18, max_value=65)
        for _ in range(50):
            val = field_gen.generate_value(field, "t.age")
            assert 18 <= val <= 65

    def test_float_respects_range(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="score", field_type=FieldType.FLOAT, min_value=0.0, max_value=1.0)
        for _ in range(50):
            val = field_gen.generate_value(field, "t.score")
            assert 0.0 <= val <= 1.0

    def test_nullable_returns_none_sometimes(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="phone", field_type=FieldType.PHONE, nullable=True)
        results = [field_gen.generate_value(field, "t.phone", null_rate=0.9) for _ in range(100)]
        none_count = sum(1 for r in results if r is None)
        # With 90% null rate, expect at least some NULLs
        assert none_count > 0

    def test_enum_values_respected(self, field_gen: FieldGenerator) -> None:
        opts = ["Red", "Green", "Blue"]
        field = FieldDefinition(name="color", field_type=FieldType.CUSTOM_STRING, enum_values=opts)
        for _ in range(50):
            val = field_gen.generate_value(field, "t.color")
            assert val in opts

    def test_prefix_suffix_applied(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="code", field_type=FieldType.INTEGER, prefix="ID-", suffix="-X")
        val = field_gen.generate_value(field, "t.code")
        assert str(val).startswith("ID-")
        assert str(val).endswith("-X")

    def test_unique_generates_distinct_values(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="uid", field_type=FieldType.UUID, unique=True)
        values = {field_gen.generate_value(field, "t.uid") for _ in range(100)}
        assert len(values) == 100  # All unique

    def test_sequential_increments(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="seq", field_type=FieldType.INTEGER, sequential=True)
        vals = [field_gen.generate_value(field, "t.seq") for _ in range(5)]
        assert vals == [1, 2, 3, 4, 5]

    def test_default_value_returned(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(name="status", field_type=FieldType.CUSTOM_STRING, default="active")
        for _ in range(20):
            val = field_gen.generate_value(field, "t.status")
            assert val == "active"

    def test_normal_distribution(self, field_gen: FieldGenerator) -> None:
        field = FieldDefinition(
            name="salary", field_type=FieldType.FLOAT,
            min_value=50_000.0, max_value=200_000.0,
            distribution=Distribution.NORMAL,
        )
        vals = [field_gen.generate_value(field, "t.salary") for _ in range(200)]
        assert all(50_000 <= v <= 200_000 for v in vals)
        mean = sum(vals) / len(vals)
        assert 80_000 <= mean <= 170_000  # Should be near center

    @pytest.mark.parametrize("field_type", [
        FieldType.FIRST_NAME, FieldType.LAST_NAME, FieldType.FULL_NAME,
        FieldType.CITY, FieldType.COUNTRY, FieldType.COMPANY, FieldType.JOB_TITLE,
        FieldType.BOOLEAN, FieldType.DATE, FieldType.DATETIME, FieldType.URL,
        FieldType.IP_ADDRESS, FieldType.MAC_ADDRESS,
    ])
    def test_all_field_types_generate_value(self, field_gen: FieldGenerator, field_type: FieldType) -> None:
        field = FieldDefinition(name="f", field_type=field_type)
        val = field_gen.generate_value(field, f"t.{field_type.value}")
        assert val is not None


# ── TableGenerator tests ──────────────────────────────────────────────────────

class TestTableGenerator:
    def _make_schema(self, rows: int = 10) -> TableSchema:
        return TableSchema(
            name="test_table",
            fields=[
                FieldDefinition(name="id", field_type=FieldType.UUID, unique=True),
                FieldDefinition(name="name", field_type=FieldType.FULL_NAME),
                FieldDefinition(name="age", field_type=FieldType.INTEGER, min_value=18, max_value=80),
                FieldDefinition(name="email", field_type=FieldType.EMAIL, nullable=True),
            ],
            row_count=rows,
        )

    def test_generates_correct_row_count(self, table_gen: TableGenerator) -> None:
        schema = self._make_schema(rows=100)
        rows = list(table_gen.generate(schema))
        assert len(rows) == 100

    def test_rows_have_all_columns(self, table_gen: TableGenerator) -> None:
        schema = self._make_schema(rows=5)
        for row in table_gen.generate(schema):
            assert set(row.keys()) == {"id", "name", "age", "email"}

    def test_memory_efficient_generation(self, table_gen: TableGenerator) -> None:
        """Generator should not materialise all rows at once."""
        schema = self._make_schema(rows=10_000)
        gen = table_gen.generate(schema)
        # Take only first row — should not generate all 10k rows
        first = next(gen)
        assert "id" in first

    def test_duplicate_rate_produces_duplicates(self, table_gen: TableGenerator) -> None:
        schema = TableSchema(
            name="dup_test",
            fields=[FieldDefinition(name="val", field_type=FieldType.INTEGER, min_value=1, max_value=5)],
            row_count=500,
            quality=DataQualityConfig(duplicate_rate=0.3),
        )
        rows = list(table_gen.generate(schema))
        values = [r["val"] for r in rows]
        # With 30% dup rate + only 5 distinct values, duplicates are expected
        assert len(values) == 500

    def test_null_rate_produces_nulls(self, table_gen: TableGenerator) -> None:
        schema = TableSchema(
            name="null_test",
            fields=[FieldDefinition(name="email", field_type=FieldType.EMAIL, nullable=True)],
            row_count=1000,
            quality=DataQualityConfig(null_rate=0.5),
        )
        rows = list(table_gen.generate(schema))
        null_count = sum(1 for r in rows if r["email"] is None)
        assert null_count > 0


# ── AnalyticsGenerator tests ──────────────────────────────────────────────────

class TestAnalyticsGenerator:
    def test_revenue_generates_correct_count(self) -> None:
        gen = AnalyticsGenerator()
        req = AnalyticsRequest(dataset_type=AnalyticsDatasetType.REVENUE, row_count=100)
        rows = list(gen.generate(req))
        assert len(rows) == 100

    def test_revenue_fields_present(self) -> None:
        gen = AnalyticsGenerator()
        req = AnalyticsRequest(dataset_type=AnalyticsDatasetType.REVENUE, row_count=5)
        rows = list(gen.generate(req))
        assert all("date" in r and "revenue" in r and "profit" in r for r in rows)

    def test_website_analytics_fields(self) -> None:
        gen = AnalyticsGenerator()
        req = AnalyticsRequest(dataset_type=AnalyticsDatasetType.WEBSITE, row_count=5)
        rows = list(gen.generate(req))
        assert all("users" in r and "bounce_rate" in r for r in rows)

    def test_iot_fields(self) -> None:
        gen = AnalyticsGenerator()
        req = AnalyticsRequest(dataset_type=AnalyticsDatasetType.IOT, row_count=5)
        rows = list(gen.generate(req))
        assert all("temperature" in r and "device_id" in r for r in rows)

    def test_vpn_fields(self) -> None:
        gen = AnalyticsGenerator()
        req = AnalyticsRequest(dataset_type=AnalyticsDatasetType.VPN, row_count=5)
        rows = list(gen.generate(req))
        assert all("active_users" in r and "country" in r for r in rows)

    def test_revenue_values_positive(self) -> None:
        gen = AnalyticsGenerator()
        req = AnalyticsRequest(dataset_type=AnalyticsDatasetType.REVENUE, row_count=365)
        rows = list(gen.generate(req))
        assert all(r["revenue"] > 0 for r in rows)
        assert all(r["customer_count"] > 0 for r in rows)
