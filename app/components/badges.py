"""Status badges for domain enumerations.

Badges always combine colour **and** text so that states are never
communicated by colour alone (accessibility).
"""

from __future__ import annotations

import flet as ft

from app.components.theme import FontSize, Metrics, Palette

_STATUS_STYLES: dict[str, tuple[str, str]] = {
    "OPERATIONAL": ("Operativo", Palette.SUCCESS),
    "MAINTENANCE": ("Mantenimiento", Palette.WARNING),
    "OUT_OF_SERVICE": ("Fuera de servicio", Palette.DANGER),
    "RETIRED": ("Retirado", Palette.NEUTRAL),
    "PENDING": ("Pendiente", Palette.INFO),
    "IN_PROGRESS": ("En progreso", Palette.WARNING),
    "COMPLETED": ("Completado", Palette.SUCCESS),
    "CANCELLED": ("Cancelado", Palette.NEUTRAL),
    "OPEN": ("Abierta", Palette.DANGER),
    "RESOLVED": ("Resuelta", Palette.SUCCESS),
    "LOW": ("Baja", Palette.NEUTRAL),
    "MEDIUM": ("Media", Palette.INFO),
    "HIGH": ("Alta", Palette.DANGER),
}


def _normalize(status: object) -> str:
    value = getattr(status, "value", status)
    return str(value).upper()


class StatusBadge(ft.Container):
    """A pill-shaped, colour-coded status label."""

    def __init__(self, status: object, label: str | None = None) -> None:
        key = _normalize(status)
        default_label, color = _STATUS_STYLES.get(
            key, (key.replace("_", " ").title(), Palette.NEUTRAL)
        )
        super().__init__(
            content=ft.Text(
                label or default_label,
                size=FontSize.CAPTION,
                weight=ft.FontWeight.W_600,
                color=color,
            ),
            padding=ft.Padding.symmetric(horizontal=10, vertical=4),
            bgcolor=ft.Colors.with_opacity(0.12, color),
            border=ft.Border.all(1, ft.Colors.with_opacity(0.35, color)),
            border_radius=Metrics.RADIUS_LARGE,
            tooltip=label or default_label,
        )
