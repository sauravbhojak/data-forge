"""Structured JSON logging setup with request correlation IDs."""

from __future__ import annotations

import logging
import sys
import time
import uuid
from contextvars import ContextVar
from typing import Any

request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class StructuredFormatter(logging.Formatter):
    """JSON-compatible structured log formatter."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(""),
        }

        # Attach any extra structured fields
        for key, val in record.__dict__.items():
            if key.startswith("_") or key in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "taskName",
            ):
                continue
            payload[key] = val

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


class PlainFormatter(logging.Formatter):
    """Human-readable formatter for local development."""

    GREY = "\x1b[38;5;246m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[31m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"
    CYAN = "\x1b[36m"

    LEVEL_COLORS = {
        "DEBUG": "\x1b[38;5;246m",
        "INFO": "\x1b[32m",
        "WARNING": "\x1b[33m",
        "ERROR": "\x1b[31m",
        "CRITICAL": "\x1b[31;1m",
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelname, self.RESET)
        rid = request_id_var.get("")
        rid_part = f" {self.CYAN}[{rid[:8]}]{self.RESET}" if rid else ""
        ts = time.strftime("%H:%M:%S", time.gmtime(record.created))
        return (
            f"{self.GREY}{ts}{self.RESET} "
            f"{color}{record.levelname:<8}{self.RESET}"
            f"{rid_part} "
            f"{self.GREY}{record.name}{self.RESET} — "
            f"{record.getMessage()}"
        )


def setup_logging(level: str = "INFO", json_logs: bool = True) -> None:
    """Configure root logger with appropriate formatter."""
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers
    root.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter() if json_logs else PlainFormatter())
    root.addHandler(handler)

    # Silence noisy third-party loggers
    for noisy in ("uvicorn.access", "faker"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance."""
    return logging.getLogger(name)


def new_request_id() -> str:
    """Generate a new request correlation ID and store it in context."""
    rid = uuid.uuid4().hex
    request_id_var.set(rid)
    return rid
