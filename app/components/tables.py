"""Reusable table components built on top of ``ft.DataTable``."""

from __future__ import annotations

import flet as ft

from app.components.badges import StatusBadge
from app.components.cards import EmptyState
from app.components.theme import (
    FontSize,
    Metrics,
    Palette,
    glass_border,
    glass_surface_color,
    soft_shadow,
    table_heading_color,
    table_row_color,
)
from app.utils.i18n import t


class GlassTable(ft.Container):
    """A glass surface wrapping a responsive data table.

    When there are no rows it renders an :class:`EmptyState` instead of an
    empty grid.
    """

    def __init__(
        self,
        headers: list[str],
        rows: list[list[ft.Control]],
        *,
        empty_title: str = "Sin resultados",
        empty_message: str = "Todavía no hay información para mostrar.",
        col: int | dict | None = None,
    ) -> None:
        if rows:
            table = ft.DataTable(
                columns=[
                    ft.DataColumn(
                        ft.Text(
                            t(header),
                            size=FontSize.CAPTION,
                            weight=ft.FontWeight.W_600,
                            color=Palette.TEXT_MUTED,
                        )
                    )
                    for header in headers
                ],
                rows=[
                    ft.DataRow(
                        cells=[ft.DataCell(cell) for cell in row],
                        color={ft.ControlState.DEFAULT: table_row_color()},
                    )
                    for row in rows
                ],
                heading_row_color=table_heading_color(),
                border_radius=Metrics.RADIUS,
                column_spacing=14,
                horizontal_margin=8,
                data_row_min_height=48,
                data_text_style=ft.TextStyle(
                    size=FontSize.BODY, color=Palette.TEXT
                ),
            )
            content: ft.Control = ft.Row(
                controls=[table],
                scroll=ft.ScrollMode.AUTO,
            )
        else:
            content = ft.Container(
                content=EmptyState(t(empty_title), t(empty_message)),
                padding=Metrics.SPACING_LARGE,
                alignment=ft.Alignment.CENTER,
            )

        extra: dict = {
            "content": content,
            "padding": Metrics.SPACING_SMALL,
            "bgcolor": glass_surface_color(),
            "border": glass_border(),
            "border_radius": Metrics.RADIUS,
            "shadow": soft_shadow(),
        }
        if col is not None:
            extra["col"] = col
        super().__init__(**extra)


def text_cell(value: str, muted: bool = False) -> ft.Text:
    """Build a standard table text cell."""
    return ft.Text(
        value,
        size=FontSize.BODY,
        color=Palette.TEXT_MUTED if muted else Palette.TEXT,
    )


def badge_cell(status: object) -> StatusBadge:
    """Build a table cell containing a status badge."""
    return StatusBadge(status)
