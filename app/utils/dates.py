"""Date and time helpers shared across the application.

Timestamps are stored as **naive UTC** values. SQLite does not preserve
timezone information, so normalising to UTC here keeps ordering and
comparisons consistent regardless of the machine's local timezone.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone


def utcnow() -> datetime:
    """Return the current UTC time as a naive :class:`datetime`."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def today() -> date:
    """Return the current UTC date."""
    return utcnow().date()


def combine(day: date, moment: time | None) -> datetime | None:
    """Combine a date and an optional time into a datetime.

    Args:
        day: Calendar date.
        moment: Optional time of day.

    Returns:
        A datetime when ``moment`` is provided, otherwise ``None``.
    """
    if moment is None:
        return None
    return datetime.combine(day, moment)
