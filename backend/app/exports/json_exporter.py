"""Streaming JSON array exporter."""

from __future__ import annotations

import json
from collections.abc import Iterator
from itertools import islice
from typing import Any

_CHUNK_SIZE = 5_000


class JSONExporter:
    """
    Streams a JSON array in batches without loading the full dataset.

    Output format:
        [
        {"col": "val", ...},
        ...
        ]

    Memory: O(chunk_size) — one chunk of rows is serialised at a time.
    """

    def export(self, data: Iterator[dict[str, Any]]) -> Iterator[bytes]:
        """Yield UTF-8 encoded bytes forming a valid JSON array, batched."""
        yield b"[\n"
        first_row = True

        while True:
            chunk = list(islice(data, _CHUNK_SIZE))
            if not chunk:
                break

            lines: list[bytes] = []
            for row in chunk:
                prefix = b"" if first_row else b",\n"
                lines.append(
                    prefix
                    + json.dumps(row, default=self._default_serialiser, ensure_ascii=False).encode("utf-8")
                )
                first_row = False

            yield b"".join(lines)

        yield b"\n]\n"

    @staticmethod
    def _default_serialiser(obj: Any) -> Any:
        """Fallback serialiser for non-JSON-native Python types."""
        return str(obj)
