"""Pre-built dataset template definitions."""

from __future__ import annotations

from typing import Any

# Each template maps template_id -> metadata + field list.
# Field dicts match the FieldDefinition schema (subset of keys required).
TEMPLATES: dict[str, dict[str, Any]] = {
    "ecommerce": {
        "id": "ecommerce",
        "name": "E-Commerce Dataset",
        "description": "Multi-table e-commerce data containing customers, products, and orders.",
        "icon": "database",
        "tags": ["E-Commerce", "Relational", "SQL"],
        "template_type": "relational",
        "tables": [
            {
                "name": "customers",
                "row_count": 100,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "first_name", "field_type": "first_name", "nullable": False},
                    {"name": "last_name", "field_type": "last_name", "nullable": False},
                    {"name": "email", "field_type": "email", "nullable": False, "unique": True},
                ]
            },
            {
                "name": "products",
                "row_count": 50,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "name", "field_type": "product_name", "nullable": False},
                    {"name": "price", "field_type": "revenue", "nullable": False, "min_value": 10, "max_value": 1000},
                ]
            },
            {
                "name": "orders",
                "row_count": 500,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "customer_id", "field_type": "uuid", "nullable": False},
                    {"name": "product_id", "field_type": "uuid", "nullable": False},
                    {"name": "quantity", "field_type": "integer", "nullable": False, "min_value": 1, "max_value": 5},
                    {"name": "order_date", "field_type": "date", "nullable": False},
                ]
            }
        ],
        "relationships": [
            {
                "parent_table": "customers",
                "parent_field": "id",
                "child_table": "orders",
                "child_field": "customer_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "products",
                "parent_field": "id",
                "child_table": "orders",
                "child_field": "product_id",
                "relationship_type": "one_to_many"
            }
        ]
    },
    "employee": {
        "id": "employee",
        "name": "Employee Dataset",
        "description": "Multi-table employee data containing departments, employees, and salaries.",
        "icon": "database",
        "tags": ["HR", "People", "Relational"],
        "template_type": "relational",
        "tables": [
            {
                "name": "departments",
                "row_count": 10,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "name", "field_type": "department", "nullable": False},
                    {"name": "location", "field_type": "city", "nullable": False},
                ]
            },
            {
                "name": "employees",
                "row_count": 100,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "first_name", "field_type": "first_name", "nullable": False},
                    {"name": "last_name", "field_type": "last_name", "nullable": False},
                    {"name": "email", "field_type": "email", "nullable": False, "unique": True},
                    {"name": "department_id", "field_type": "uuid", "nullable": False},
                    {"name": "joining_date", "field_type": "date", "nullable": False},
                ]
            },
            {
                "name": "salaries",
                "row_count": 100,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "employee_id", "field_type": "uuid", "nullable": False},
                    {"name": "amount", "field_type": "salary", "nullable": False, "min_value": 30000, "max_value": 250000},
                    {"name": "effective_date", "field_type": "date", "nullable": False},
                ]
            }
        ],
        "relationships": [
            {
                "parent_table": "departments",
                "parent_field": "id",
                "child_table": "employees",
                "child_field": "department_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "employees",
                "parent_field": "id",
                "child_table": "salaries",
                "child_field": "employee_id",
                "relationship_type": "one_to_one"
            }
        ]
    },
    "hospital": {
        "id": "hospital",
        "name": "Hospital / Patient Dataset",
        "description": "Multi-table hospital data containing patients, doctors, admissions, and billing.",
        "icon": "database",
        "tags": ["Healthcare", "Relational", "SQL"],
        "template_type": "relational",
        "tables": [
            {
                "name": "patients",
                "row_count": 500,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "patient_name", "field_type": "full_name", "nullable": False},
                    {"name": "contact_number", "field_type": "phone", "nullable": True},
                ]
            },
            {
                "name": "doctors",
                "row_count": 50,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "doctor_name", "field_type": "full_name", "nullable": False},
                    {"name": "specialization", "field_type": "department", "nullable": False},
                ]
            },
            {
                "name": "admissions",
                "row_count": 1000,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "patient_id", "field_type": "uuid", "nullable": False},
                    {"name": "doctor_id", "field_type": "uuid", "nullable": False},
                    {"name": "admission_date", "field_type": "date", "nullable": False},
                    {"name": "discharge_date", "field_type": "date", "nullable": True},
                    {
                        "name": "diagnosis",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["Hypertension", "Diabetes Type 2", "Pneumonia", "Appendicitis", "Fracture"]
                    },
                ]
            },
            {
                "name": "billing",
                "row_count": 1000,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "admission_id", "field_type": "uuid", "nullable": False},
                    {"name": "bill_amount", "field_type": "revenue", "nullable": False, "min_value": 500, "max_value": 150000},
                    {
                        "name": "status",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["Paid", "Pending", "Overdue"]
                    },
                ]
            }
        ],
        "relationships": [
            {
                "parent_table": "patients",
                "parent_field": "id",
                "child_table": "admissions",
                "child_field": "patient_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "doctors",
                "parent_field": "id",
                "child_table": "admissions",
                "child_field": "doctor_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "admissions",
                "parent_field": "id",
                "child_table": "billing",
                "child_field": "admission_id",
                "relationship_type": "one_to_one"
            }
        ]
    },
    "sales": {
        "id": "sales",
        "name": "Sales Dataset",
        "description": "Multi-table sales data containing customers, products, and orders.",
        "icon": "database",
        "tags": ["Sales", "Relational", "SQL"],
        "template_type": "relational",
        "tables": [
            {
                "name": "customers",
                "row_count": 200,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "customer_name", "field_type": "full_name", "nullable": False},
                    {"name": "email", "field_type": "email", "nullable": False},
                    {
                        "name": "region",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East & Africa"],
                    },
                ]
            },
            {
                "name": "products",
                "row_count": 50,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "product_name", "field_type": "product_name", "nullable": False},
                    {"name": "category", "field_type": "category", "nullable": False},
                    {"name": "price", "field_type": "revenue", "nullable": False, "min_value": 10, "max_value": 5000},
                ]
            },
            {
                "name": "orders",
                "row_count": 1000,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "customer_id", "field_type": "uuid", "nullable": False},
                    {"name": "product_id", "field_type": "uuid", "nullable": False},
                    {"name": "quantity", "field_type": "integer", "nullable": False, "min_value": 1, "max_value": 100},
                    {"name": "order_date", "field_type": "date", "nullable": False},
                    {"name": "total_amount", "field_type": "revenue", "nullable": False, "min_value": 10, "max_value": 50000},
                ]
            }
        ],
        "relationships": [
            {
                "parent_table": "customers",
                "parent_field": "id",
                "child_table": "orders",
                "child_field": "customer_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "products",
                "parent_field": "id",
                "child_table": "orders",
                "child_field": "product_id",
                "relationship_type": "one_to_many"
            }
        ]
    },
    "vpn": {
        "id": "vpn",
        "name": "VPN Server Dataset",
        "description": "Multi-table VPN data containing servers, users, and sessions.",
        "icon": "database",
        "tags": ["Network", "Relational", "SQL"],
        "template_type": "relational",
        "tables": [
            {
                "name": "servers",
                "row_count": 20,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {
                        "name": "server_name",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["us-east-1", "us-west-2", "eu-central-1", "eu-west-1", "ap-southeast-1"],
                    },
                    {"name": "country", "field_type": "country", "nullable": False},
                    {
                        "name": "status",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["online", "maintenance", "offline"],
                    },
                ]
            },
            {
                "name": "users",
                "row_count": 500,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "username", "field_type": "full_name", "nullable": False},
                    {"name": "email", "field_type": "email", "nullable": False, "unique": True},
                    {
                        "name": "subscription_tier",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["Free", "Basic", "Premium", "Enterprise"]
                    },
                ]
            },
            {
                "name": "sessions",
                "row_count": 5000,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "user_id", "field_type": "uuid", "nullable": False},
                    {"name": "server_id", "field_type": "uuid", "nullable": False},
                    {"name": "start_time", "field_type": "date", "nullable": False},
                    {"name": "duration_mins", "field_type": "integer", "nullable": False, "min_value": 1, "max_value": 1440},
                    {"name": "bandwidth_mb", "field_type": "float", "nullable": False, "min_value": 0.1, "max_value": 5000.0},
                    {"name": "latency_ms", "field_type": "float", "nullable": False, "min_value": 5.0, "max_value": 300.0},
                ]
            }
        ],
        "relationships": [
            {
                "parent_table": "users",
                "parent_field": "id",
                "child_table": "sessions",
                "child_field": "user_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "servers",
                "parent_field": "id",
                "child_table": "sessions",
                "child_field": "server_id",
                "relationship_type": "one_to_many"
            }
        ]
    },
    "hr": {
        "id": "hr",
        "name": "HR Dataset",
        "description": "Multi-table HR data containing departments, roles, employees, and performance reviews.",
        "icon": "database",
        "tags": ["HR", "Relational", "SQL"],
        "template_type": "relational",
        "tables": [
            {
                "name": "departments",
                "row_count": 10,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "name", "field_type": "department", "nullable": False},
                    {"name": "budget", "field_type": "revenue", "nullable": False, "min_value": 100000, "max_value": 5000000},
                ]
            },
            {
                "name": "employees",
                "row_count": 200,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "name", "field_type": "full_name", "nullable": False},
                    {"name": "designation", "field_type": "job_title", "nullable": False},
                    {"name": "department_id", "field_type": "uuid", "nullable": False},
                    {"name": "joining_date", "field_type": "date", "nullable": False},
                    {"name": "salary", "field_type": "salary", "nullable": False, "min_value": 30000, "max_value": 200000},
                ]
            },
            {
                "name": "performance_reviews",
                "row_count": 400,
                "fields": [
                    {"name": "id", "field_type": "uuid", "nullable": False, "unique": True},
                    {"name": "employee_id", "field_type": "uuid", "nullable": False},
                    {"name": "review_date", "field_type": "date", "nullable": False},
                    {
                        "name": "rating",
                        "field_type": "custom_string",
                        "nullable": False,
                        "enum_values": ["Exceeds Expectations", "Meets Expectations", "Needs Improvement", "Outstanding"]
                    },
                ]
            }
        ],
        "relationships": [
            {
                "parent_table": "departments",
                "parent_field": "id",
                "child_table": "employees",
                "child_field": "department_id",
                "relationship_type": "one_to_many"
            },
            {
                "parent_table": "employees",
                "parent_field": "id",
                "child_table": "performance_reviews",
                "child_field": "employee_id",
                "relationship_type": "one_to_many"
            }
        ]
    },
}
