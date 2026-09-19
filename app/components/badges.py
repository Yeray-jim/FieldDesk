"""Status badges for domain enumerations.

Badges always combine colour **and** text so that states are never
communicated by colour alone (accessibility). Labels come from
:mod:`app.utils.labels` to stay consistent with the reports.
"""

from __future__ import annotations

import flet as ft

from app.components.theme import FontSize, Metrics, Palette
from app.utils.labels import normalize_status, status_label

_STATUS_COLORS: dict[str, str] = {
    "OPERATIONAL": Palette.SUCCESS,
    "MAINTENANCE": Palette.WARNING,
    "OUT_OF_SERVICE": Palette.DANGER,
    "RETIRED": Palette.NEUTRAL,
    "PENDING": Palette.INFO,
    "IN_PROGRESS": Palette.WARNING,
    "COMPLETED": Palette.SUCCESS,
    "CANCELLED": Palette.NEUTRAL,
    "OPEN": Palette.DANGER,
    "RESOLVED": Palette.SUCCESS,
    "LOW": Palette.NEUTRAL,
    "MEDIUM": Palette.INFO,
    "HIGH": Palette.DANGER,
}


class StatusBadge(ft.Container):
    """A pill-shaped, colour-coded status label."""

    def __init__(self, status: object, label: str | None = None) -> None:
        color = _STATUS_COLORS.get(normalize_status(status), Palette.NEUTRAL)
        text = label or status_label(status)
        super().__init__(
            content=ft.Text(
                text,
                size=FontSize.CAPTION,
                weight=ft.FontWeight.W_600,
                color=color,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.12, color),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.35, color)),
            border_radius=Metrics.RADIUS_LARGE,
            tooltip=text,
        )
