"""Core field-level value generator supporting all 40+ field types."""

from __future__ import annotations

import json
import random
import re
import uuid
from datetime import date, datetime, timedelta
from typing import Any

import rstr
from faker import Faker

from app.constants.field_types import FieldType, NUMERIC_FIELD_TYPES
from app.constants.distributions import Distribution
from app.schemas.generation import FieldDefinition


# Pre-computed product categories (reused across all rows)
_CATEGORIES = [
    "Electronics", "Clothing", "Books", "Sports", "Home & Garden",
    "Toys", "Beauty", "Automotive", "Food & Beverages", "Health",
    "Office Supplies", "Music", "Movies", "Software", "Jewelry",
]

_DEPARTMENTS = [
    "Engineering", "Marketing", "Sales", "Finance", "Operations",
    "Human Resources", "Legal", "Product", "Design", "Support",
    "Data Science", "Security", "IT", "Research", "Customer Success",
]

_GENDERS = ["Male", "Female", "Non-binary", "Prefer not to say"]

_DATE_START = date(2018, 1, 1)
_DATE_END = date(2025, 12, 31)
_DATE_RANGE_DAYS = (_DATE_END - _DATE_START).days

_DATETIME_START = datetime(2018, 1, 1, 0, 0, 0)
_DATETIME_RANGE_SECONDS = int(
    (datetime(2025, 12, 31, 23, 59, 59) - _DATETIME_START).total_seconds()
)


class FieldGenerator:
    """
    Stateful per-table field value generator.

    Manages:
    - Faker instance reuse
    - Unique value tracking per field
    - Sequential counters per field
    """

    _MAX_UNIQUE_RETRIES = 100

    def __init__(self, fake: Faker) -> None:
        self._fake = fake
        self._unique_sets: dict[str, set[Any]] = {}
        self._counters: dict[str, int] = {}

    def reset(self) -> None:
        """Reset state between table generations."""
        self._unique_sets.clear()
        self._counters.clear()

    def generate_value(self, field: FieldDefinition, field_key: str, null_rate: float = 0.0) -> Any:
        """Generate a single value for the given field definition."""

        # ── Nullable ─────────────────────────────────────────────────────────
        if field.nullable and null_rate > 0 and random.random() < null_rate:
            return None

        # ── Enum shortcut ─────────────────────────────────────────────────────
        if field.enum_values:
            val = random.choice(field.enum_values)
            return self._wrap(val, field)

        # ── Default shortcut ──────────────────────────────────────────────────
        if field.default is not None:
            return self._wrap(field.default, field)

        # ── Sequential ────────────────────────────────────────────────────────
        if field.sequential:
            cnt = self._counters.get(field_key, 0) + 1
            self._counters[field_key] = cnt
            return self._wrap(cnt, field)

        # ── Regex ─────────────────────────────────────────────────────────────
        if field.regex:
            try:
                val = rstr.xeger(field.regex)
                return self._wrap(val, field)
            except Exception:
                pass  # fall through to typed generation

        # ── Typed generation ──────────────────────────────────────────────────
        if field.unique:
            return self._generate_unique(field, field_key, null_rate)

        raw = self._typed_value(field)
        return self._wrap(raw, field)

    def _generate_unique(self, field: FieldDefinition, field_key: str, null_rate: float) -> Any:
        seen = self._unique_sets.setdefault(field_key, set())
        for _ in range(self._MAX_UNIQUE_RETRIES):
            raw = self._typed_value(field)
            val = self._wrap(raw, field)
            if val not in seen:
                seen.add(val)
                return val
        # Last resort: append UUID suffix to ensure uniqueness
        raw = self._typed_value(field)
        val = self._wrap(f"{raw}_{uuid.uuid4().hex[:6]}", field)
        seen.add(val)
        return val

    # ── Typed value dispatch ──────────────────────────────────────────────────

    def _typed_value(self, field: FieldDefinition) -> Any:  # noqa: PLR0911
        ft = field.field_type
        fake = self._fake

        match ft:
            case FieldType.UUID:
                return str(uuid.uuid4())

            case FieldType.FIRST_NAME:
                return fake.first_name()

            case FieldType.LAST_NAME:
                return fake.last_name()

            case FieldType.FULL_NAME:
                return fake.name()

            case FieldType.EMAIL:
                return fake.email()

            case FieldType.PHONE:
                return fake.phone_number()

            case FieldType.ADDRESS:
                return fake.address().replace("\n", ", ")

            case FieldType.CITY:
                return fake.city()

            case FieldType.STATE:
                return fake.state()

            case FieldType.COUNTRY:
                return fake.country()

            case FieldType.ZIPCODE:
                return fake.postcode()

            case FieldType.LATITUDE:
                min_v = field.min_value if field.min_value is not None else -90.0
                max_v = field.max_value if field.max_value is not None else 90.0
                return round(random.uniform(max(min_v, -90.0), min(max_v, 90.0)), 6)

            case FieldType.LONGITUDE:
                min_v = field.min_value if field.min_value is not None else -180.0
                max_v = field.max_value if field.max_value is not None else 180.0
                return round(random.uniform(max(min_v, -180.0), min(max_v, 180.0)), 6)

            case FieldType.COMPANY:
                return fake.company()

            case FieldType.JOB_TITLE:
                return fake.job()

            case FieldType.DEPARTMENT:
                return random.choice(_DEPARTMENTS)

            case FieldType.PRODUCT_NAME:
                return fake.catch_phrase()

            case FieldType.CATEGORY:
                return random.choice(_CATEGORIES)

            case FieldType.CURRENCY:
                return fake.currency_code()

            case FieldType.SALARY:
                return self._numeric(field, default_min=30_000, default_max=250_000, as_int=True)

            case FieldType.REVENUE:
                return self._numeric(field, default_min=100.0, default_max=1_000_000.0, as_int=False)

            case FieldType.INTEGER:
                return self._numeric(field, default_min=1, default_max=10_000, as_int=True)

            case FieldType.FLOAT:
                return self._numeric(field, default_min=0.0, default_max=1_000.0, as_int=False)

            case FieldType.PERCENTAGE:
                min_v = field.min_value if field.min_value is not None else 0.0
                max_v = field.max_value if field.max_value is not None else 100.0
                return round(random.uniform(min_v, max_v), 2)

            case FieldType.BOOLEAN:
                return random.choice([True, False])

            case FieldType.DATE:
                return (_DATE_START + timedelta(days=random.randint(0, _DATE_RANGE_DAYS))).isoformat()

            case FieldType.DATETIME:
                return (_DATETIME_START + timedelta(seconds=random.randint(0, _DATETIME_RANGE_SECONDS))).isoformat(
                    sep="T", timespec="seconds"
                )

            case FieldType.AGE:
                min_v = int(field.min_value) if field.min_value is not None else 18
                max_v = int(field.max_value) if field.max_value is not None else 80
                return random.randint(min_v, max_v)

            case FieldType.GENDER:
                return random.choice(_GENDERS)

            case FieldType.USERNAME:
                return fake.user_name()

            case FieldType.PASSWORD:
                length = field.length or 12
                return fake.password(length=length, special_chars=True, digits=True, upper_case=True)

            case FieldType.URL:
                return fake.url()

            case FieldType.IP_ADDRESS:
                return fake.ipv4()

            case FieldType.MAC_ADDRESS:
                return fake.mac_address()

            case FieldType.TEXT:
                length = field.length or 80
                return fake.text(max_nb_chars=length).replace("\n", " ")

            case FieldType.PARAGRAPH:
                return fake.paragraph(nb_sentences=random.randint(3, 8))

            case FieldType.JSON:
                return json.dumps(
                    {
                        "id": str(uuid.uuid4()),
                        "key": fake.word(),
                        "value": random.randint(1, 1000),
                        "active": random.choice([True, False]),
                    }
                )

            case FieldType.CUSTOM_STRING:
                length = field.length or 10
                return fake.lexify(text="?" * length)

            case _:
                return fake.word()

    def _numeric(
        self,
        field: FieldDefinition,
        *,
        default_min: float,
        default_max: float,
        as_int: bool,
    ) -> int | float:
        """Generate a numeric value with optional distribution."""
        min_v = field.min_value if field.min_value is not None else default_min
        max_v = field.max_value if field.max_value is not None else default_max

        dist = field.distribution
        if dist == Distribution.NORMAL:
            mean = (min_v + max_v) / 2
            std = (max_v - min_v) / 6
            raw = random.gauss(mean, std)
            raw = max(min_v, min(max_v, raw))
        elif dist == Distribution.EXPONENTIAL:
            scale = (max_v - min_v) / 4
            raw = min_v + random.expovariate(1 / scale) if scale > 0 else min_v
            raw = min(raw, max_v)
        elif dist == Distribution.SKEWED_RIGHT:
            # Use log-normal to produce right skew
            import math
            sigma = 0.8
            mu = math.log((min_v + max_v) / 2) - sigma ** 2 / 2
            raw = min(max_v, max(min_v, random.lognormvariate(mu, sigma)))
        elif dist == Distribution.SKEWED_LEFT:
            # Mirror of right skew
            import math
            sigma = 0.8
            mu = math.log((min_v + max_v) / 2) - sigma ** 2 / 2
            raw_r = min(max_v, max(min_v, random.lognormvariate(mu, sigma)))
            raw = max_v - (raw_r - min_v)
        else:
            raw = random.uniform(min_v, max_v)

        return int(round(raw)) if as_int else round(raw, 2)

    @staticmethod
    def _wrap(value: Any, field: FieldDefinition) -> Any:
        """Apply prefix/suffix wrappers if defined."""
        if field.prefix or field.suffix:
            return f"{field.prefix or ''}{value}{field.suffix or ''}"
        return value
