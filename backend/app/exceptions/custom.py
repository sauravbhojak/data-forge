"""Custom exception classes for DataForge."""

from __future__ import annotations


class DataForgeError(Exception):
    """Base exception for all DataForge errors."""

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail or message


class GenerationError(DataForgeError):
    """Raised when data generation fails."""


class ExportError(DataForgeError):
    """Raised when export processing fails."""


class SchemaValidationError(DataForgeError):
    """Raised when a user-provided schema is semantically invalid."""


class RowLimitExceededError(DataForgeError):
    """Raised when requested row count exceeds the configured limit."""

    def __init__(self, requested: int, limit: int) -> None:
        super().__init__(
            message=f"Row count {requested:,} exceeds maximum allowed {limit:,}",
            detail=f"Reduce row_count to {limit:,} or fewer.",
        )
        self.requested = requested
        self.limit = limit


class TemplateNotFoundError(DataForgeError):
    """Raised when a requested template ID does not exist."""

    def __init__(self, template_id: str) -> None:
        super().__init__(
            message=f"Template '{template_id}' not found",
            detail="Call GET /templates to list available templates.",
        )
        self.template_id = template_id


class RateLimitError(DataForgeError):
    """Raised when a client exceeds the rate limit."""


class PayloadTooLargeError(DataForgeError):
    """Raised when request payload exceeds size limits."""
