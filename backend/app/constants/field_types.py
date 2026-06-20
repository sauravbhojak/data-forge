"""Enum registry of all supported field types."""

from __future__ import annotations

from enum import Enum


class FieldType(str, Enum):
    """All field types that DataForge can generate."""

    # Identity
    UUID = "uuid"

    # Personal
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    FULL_NAME = "full_name"
    EMAIL = "email"
    PHONE = "phone"
    AGE = "age"
    GENDER = "gender"
    USERNAME = "username"
    PASSWORD = "password"

    # Location
    ADDRESS = "address"
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    ZIPCODE = "zipcode"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"

    # Business
    COMPANY = "company"
    JOB_TITLE = "job_title"
    DEPARTMENT = "department"

    # Commerce
    PRODUCT_NAME = "product_name"
    CATEGORY = "category"
    CURRENCY = "currency"

    # Numeric
    SALARY = "salary"
    REVENUE = "revenue"
    INTEGER = "integer"
    FLOAT = "float"
    PERCENTAGE = "percentage"

    # Boolean
    BOOLEAN = "boolean"

    # Temporal
    DATE = "date"
    DATETIME = "datetime"

    # Network / Tech
    URL = "url"
    IP_ADDRESS = "ip_address"
    MAC_ADDRESS = "mac_address"

    # Text
    TEXT = "text"
    PARAGRAPH = "paragraph"
    JSON = "json"

    # Custom
    CUSTOM_STRING = "custom_string"


# Human-readable labels for UI display
FIELD_TYPE_LABELS: dict[FieldType, str] = {
    FieldType.UUID: "UUID",
    FieldType.FIRST_NAME: "First Name",
    FieldType.LAST_NAME: "Last Name",
    FieldType.FULL_NAME: "Full Name",
    FieldType.EMAIL: "Email",
    FieldType.PHONE: "Phone Number",
    FieldType.AGE: "Age",
    FieldType.GENDER: "Gender",
    FieldType.USERNAME: "Username",
    FieldType.PASSWORD: "Password",
    FieldType.ADDRESS: "Address",
    FieldType.CITY: "City",
    FieldType.STATE: "State / Province",
    FieldType.COUNTRY: "Country",
    FieldType.ZIPCODE: "ZIP / Postal Code",
    FieldType.LATITUDE: "Latitude",
    FieldType.LONGITUDE: "Longitude",
    FieldType.COMPANY: "Company",
    FieldType.JOB_TITLE: "Job Title",
    FieldType.DEPARTMENT: "Department",
    FieldType.PRODUCT_NAME: "Product Name",
    FieldType.CATEGORY: "Category",
    FieldType.CURRENCY: "Currency Code",
    FieldType.SALARY: "Salary",
    FieldType.REVENUE: "Revenue",
    FieldType.INTEGER: "Integer",
    FieldType.FLOAT: "Float",
    FieldType.PERCENTAGE: "Percentage",
    FieldType.BOOLEAN: "Boolean",
    FieldType.DATE: "Date",
    FieldType.DATETIME: "DateTime",
    FieldType.URL: "URL",
    FieldType.IP_ADDRESS: "IP Address",
    FieldType.MAC_ADDRESS: "MAC Address",
    FieldType.TEXT: "Short Text",
    FieldType.PARAGRAPH: "Paragraph",
    FieldType.JSON: "JSON Object",
    FieldType.CUSTOM_STRING: "Custom String",
}

# Field types that are numeric (support min/max)
NUMERIC_FIELD_TYPES: frozenset[FieldType] = frozenset(
    {
        FieldType.INTEGER,
        FieldType.FLOAT,
        FieldType.SALARY,
        FieldType.REVENUE,
        FieldType.AGE,
        FieldType.PERCENTAGE,
        FieldType.LATITUDE,
        FieldType.LONGITUDE,
    }
)

# Field types that produce string values
STRING_FIELD_TYPES: frozenset[FieldType] = frozenset(
    {
        FieldType.UUID,
        FieldType.FIRST_NAME,
        FieldType.LAST_NAME,
        FieldType.FULL_NAME,
        FieldType.EMAIL,
        FieldType.PHONE,
        FieldType.ADDRESS,
        FieldType.CITY,
        FieldType.STATE,
        FieldType.COUNTRY,
        FieldType.ZIPCODE,
        FieldType.COMPANY,
        FieldType.JOB_TITLE,
        FieldType.DEPARTMENT,
        FieldType.PRODUCT_NAME,
        FieldType.CATEGORY,
        FieldType.CURRENCY,
        FieldType.GENDER,
        FieldType.USERNAME,
        FieldType.PASSWORD,
        FieldType.URL,
        FieldType.IP_ADDRESS,
        FieldType.MAC_ADDRESS,
        FieldType.TEXT,
        FieldType.PARAGRAPH,
        FieldType.CUSTOM_STRING,
    }
)
