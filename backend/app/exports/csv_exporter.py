"""Streaming CSV exporter — never loads full dataset into memory."""

from __future__ import annotations

import csv
import io
from collections.abc import Iterator
from itertools import islice
from typing import Any

# Number of rows to buffer before flushing to the network.
# Larger = faster (fewer syscalls), smaller = lower memory. 5k is a sweet spot.
_CHUNK_SIZE = 5_000


class CSVExporter:
    """
    Streams CSV bytes in chunks using Python's csv module.

    Memory: O(chunk_size) — only one chunk of rows is live at a time.
    """

    def export(self, data: Iterator[dict[str, Any]]) -> Iterator[bytes]:
        """
        Yield UTF-8 encoded CSV bytes in chunks of _CHUNK_SIZE rows.

        The first row determines headers.  All subsequent rows must have
        the same set of keys (standard table generation guarantees this).
        """
        buffer = io.StringIO()
        writer: csv.DictWriter | None = None
        first_chunk = True

        while True:
            chunk = list(islice(data, _CHUNK_SIZE))
            if not chunk:
                break

            if writer is None:
                writer = csv.DictWriter(
                    buffer,
                    fieldnames=list(chunk[0].keys()),
                    lineterminator="\r\n",
                    extrasaction="ignore",
                )
                writer.writeheader()

            writer.writerows(chunk)
            buffer.seek(0)
            content = buffer.read()
            buffer.truncate(0)
            buffer.seek(0)
            if content:
                # BOM only on first chunk so Excel opens it correctly
                encoding = "utf-8-sig" if first_chunk else "utf-8"
                first_chunk = False
                yield content.encode(encoding)
