"""Reusable validation helpers.

These functions are intentionally dependency-free so they can be used both by
Pydantic schemas and by the service layer.
"""

from __future__ import annotations

import re

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(value: str) -> bool:
    """Return whether ``value`` looks like a valid email address."""
    return bool(_EMAIL_PATTERN.match(value.strip()))


def is_blank(value: str | None) -> bool:
    """Return whether a string is ``None`` or only whitespace."""
    return value is None or not value.strip()
