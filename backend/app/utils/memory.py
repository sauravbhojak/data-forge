"""Memory usage utilities for observability."""

from __future__ import annotations

import os

import psutil


def current_process_memory_mb() -> float:
    """Return the RSS memory of the current process in megabytes."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)


class MemorySnapshot:
    """Context manager that measures memory delta."""

    def __init__(self) -> None:
        self._start_mb: float = 0.0
        self.delta_mb: float = 0.0

    def __enter__(self) -> "MemorySnapshot":
        self._start_mb = current_process_memory_mb()
        return self

    def __exit__(self, *args: object) -> None:
        self.delta_mb = round(current_process_memory_mb() - self._start_mb, 3)
