"""Integration tests for all API endpoints."""

from __future__ import annotations

import json

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from app.core.lifespan import _app_state
from app.main import app


@pytest.fixture(autouse=True)
def warm_faker() -> None:
    """Pre-warm Faker so lifespan-dependent DI works in tests."""
    if "faker" not in _app_state:
        _app_state["faker"] = Faker()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app, raise_server_exceptions=True)


EMPLOYEE_SCHEMA = {
    "table": {
        "name": "employee",
        "fields": [
            {"name": "id", "field_type": "uuid", "unique": True},
            {"name": "name", "field_type": "full_name"},
            {"name": "email", "field_type": "email", "unique": True},
            {"name": "salary", "field_type": "salary", "min_value": 30000, "max_value": 200000},
        ],
        "row_count": 20,
    }
}


class TestHealth:
    def test_health_returns_200(self, client: TestClient) -> None:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_ready_returns_200(self, client: TestClient) -> None:
        r = client.get("/ready")
        assert r.status_code == 200
        assert r.json()["status"] == "ready"


class TestTemplates:
    def test_lists_templates(self, client: TestClient) -> None:
        r = client.get("/templates")
        assert r.status_code == 200
        templates = r.json()
        assert len(templates) == 6
        ids = {t["id"] for t in templates}
        assert "employee" in ids
        assert "hospital" in ids

    def test_template_has_required_fields(self, client: TestClient) -> None:
        r = client.get("/templates")
        tmpl = r.json()[0]
        assert "id" in tmpl
        assert "name" in tmpl
        assert "field_count" in tmpl
        assert "field_names" in tmpl


class TestPreview:
    def test_preview_returns_50_rows(self, client: TestClient) -> None:
        r = client.post("/preview", json=EMPLOYEE_SCHEMA)
        assert r.status_code == 200
        data = r.json()
        assert data["preview_count"] <= 50
        assert len(data["rows"]) == data["preview_count"]

    def test_preview_has_correct_columns(self, client: TestClient) -> None:
        r = client.post("/preview", json=EMPLOYEE_SCHEMA)
        data = r.json()
        assert set(data["columns"]) == {"id", "name", "email", "salary"}

    def test_preview_validation_error_on_bad_schema(self, client: TestClient) -> None:
        r = client.post("/preview", json={"table": {"name": "t", "fields": [], "row_count": 10}})
        assert r.status_code == 422

    def test_preview_row_limit_exceeded(self, client: TestClient) -> None:
        schema = {
            "table": {
                "name": "t",
                "fields": [{"name": "id", "field_type": "uuid"}],
                "row_count": 9_999_999,
            }
        }
        r = client.post("/preview", json=schema)
        assert r.status_code == 422


class TestGenerate:
    def test_generate_returns_metrics(self, client: TestClient) -> None:
        r = client.post("/generate", json=EMPLOYEE_SCHEMA)
        assert r.status_code == 200
        data = r.json()
        assert data["row_count"] == 20
        assert "metrics" in data
        assert data["metrics"]["generation_time_ms"] > 0


class TestSQLSchema:
    def test_generates_postgresql_ddl(self, client: TestClient) -> None:
        body = {
            "tables": [EMPLOYEE_SCHEMA["table"]],
            "dialect": "postgresql",
        }
        r = client.post("/generate-schema", json=body)
        assert r.status_code == 200
        ddl = r.json()["ddl"]
        assert "CREATE TABLE" in ddl
        assert '"employee"' in ddl

    def test_generates_mysql_ddl_with_backticks(self, client: TestClient) -> None:
        body = {
            "tables": [EMPLOYEE_SCHEMA["table"]],
            "dialect": "mysql",
        }
        r = client.post("/generate-schema", json=body)
        ddl = r.json()["ddl"]
        assert "`employee`" in ddl


class TestERD:
    def test_generates_mermaid_text(self, client: TestClient) -> None:
        body = {
            "tables": [EMPLOYEE_SCHEMA["table"]],
            "relationships": [],
        }
        r = client.post("/generate-erd", json=body)
        assert r.status_code == 200
        data = r.json()
        assert "erDiagram" in data["mermaid"]
        assert data["table_count"] == 1


class TestExports:
    def test_csv_export_streams_valid_csv(self, client: TestClient) -> None:
        r = client.post("/export/csv", json=EMPLOYEE_SCHEMA)
        assert r.status_code == 200
        assert "text/csv" in r.headers["content-type"]
        content = r.content.decode("utf-8-sig")
        assert "id" in content.split("\r\n")[0]

    def test_json_export_valid_array(self, client: TestClient) -> None:
        r = client.post("/export/json", json=EMPLOYEE_SCHEMA)
        assert r.status_code == 200
        data = json.loads(r.content)
        assert isinstance(data, list)
        assert len(data) == 20

    def test_sql_export_contains_inserts(self, client: TestClient) -> None:
        r = client.post("/export/sql", json=EMPLOYEE_SCHEMA)
        assert r.status_code == 200
        content = r.content.decode("utf-8")
        assert "INSERT INTO" in content

    def test_excel_export_returns_xlsx_bytes(self, client: TestClient) -> None:
        r = client.post("/export/excel", json=EMPLOYEE_SCHEMA)
        assert r.status_code == 200
        assert r.content[:2] == b"PK"  # ZIP/XLSX magic bytes


class TestAnalytics:
    def test_revenue_preview(self, client: TestClient) -> None:
        r = client.post("/analytics/preview", json={"dataset_type": "revenue", "row_count": 30})
        assert r.status_code == 200
        data = r.json()
        assert data["preview_count"] <= 50
        assert "revenue" in data["columns"]

    def test_iot_preview(self, client: TestClient) -> None:
        r = client.post("/analytics/preview", json={"dataset_type": "iot", "row_count": 20})
        assert r.status_code == 200
        assert "temperature" in r.json()["columns"]
