"""Supported data quality distributions and quality control enums."""

from __future__ import annotations

from enum import Enum


class Distribution(str, Enum):
    """Statistical distribution for numeric field generation."""

    NORMAL = "normal"
    UNIFORM = "uniform"
    EXPONENTIAL = "exponential"
    SKEWED_LEFT = "skewed_left"
    SKEWED_RIGHT = "skewed_right"
    CUSTOM = "custom"


class RelationshipType(str, Enum):
    """Cardinality of a table relationship."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"


class SQLDialect(str, Enum):
    """SQL target dialects."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    SQLSERVER = "sqlserver"


class AnalyticsDatasetType(str, Enum):
    """Pre-built analytics dataset types."""

    REVENUE = "revenue"
    WEBSITE = "website"
    IOT = "iot"
    VPN = "vpn"


class ExportFormat(str, Enum):
    """Supported export file formats."""

    CSV = "csv"
    JSON = "json"
    SQL = "sql"
    EXCEL = "excel"
