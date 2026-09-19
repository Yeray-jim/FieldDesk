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


def format_date(value: date | datetime | None) -> str:
    """Format a date as ``dd/mm/yyyy`` for display."""
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y")


def format_datetime(value: datetime | None) -> str:
    """Format a datetime as ``dd/mm/yyyy HH:MM`` for display."""
    if value is None:
        return "—"
    return value.strftime("%d/%m/%Y %H:%M")


def format_time(value: time | None) -> str:
    """Format a time as ``HH:MM`` for display."""
    if value is None:
        return "—"
    return value.strftime("%H:%M")


def to_12h(value: str | time | None) -> str | None:
    """Convert a 24-hour time to ``hh:MM AM/PM`` for display."""
    if value is None:
        return None
    if isinstance(value, time):
        value = value.strftime("%H:%M")
    try:
        parsed = datetime.strptime(str(value), "%H:%M")
    except ValueError:
        return str(value)
    return parsed.strftime("%I:%M %p")


def to_24h(value: str | None) -> str | None:
    """Convert a 12- or 24-hour time into the ``HH:MM`` 24-hour format.

    Returns the original text when it cannot be parsed, so the schema reports
    a clear validation error.
    """
    if not value:
        return value
    text = value.strip().upper().replace(".", "")
    for pattern in ("%I:%M %p", "%I:%M%p", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(text, pattern).strftime("%H:%M")
        except ValueError:
            continue
    return value
