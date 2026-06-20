"""FastAPI dependency for the shared, pre-warmed Faker instance."""

from __future__ import annotations

from typing import Annotated

from faker import Faker
from fastapi import Depends

from app.core.lifespan import get_faker


def faker_dependency() -> Faker:
    """Provide the application-wide Faker instance via DI."""
    return get_faker()


FakerDep = Annotated[Faker, Depends(faker_dependency)]
