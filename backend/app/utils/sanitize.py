"""Filename sanitization utilities."""

from __future__ import annotations

import re
import unicodedata


_SAFE_RE = re.compile(r"[^\w\-.]")


def sanitize_filename(name: str, extension: str = "") -> str:
    """Return a filesystem-safe filename.

    Normalises unicode, strips dangerous characters, and enforces a
    maximum length so filenames can never exceed OS limits.
    """
    # Normalize unicode → ASCII
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")

    # Replace whitespace with underscores
    ascii_name = re.sub(r"\s+", "_", ascii_name.strip())

    # Remove any character that isn't alphanumeric, hyphen, or dot
    safe = _SAFE_RE.sub("", ascii_name)

    # Truncate to 200 chars (leaving room for extension)
    safe = safe[:200] or "export"

    if extension:
        ext = extension.lstrip(".")
        return f"{safe}.{ext}"
    return safe
