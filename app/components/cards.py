"""Reusable glassmorphism cards and layout helpers."""

from __future__ import annotations

import flet as ft

from app.components.theme import (
    FontSize,
    Metrics,
    Palette,
    glass_border,
    glass_surface_color,
    soft_shadow,
)
from app.utils.i18n import t


class GlassCard(ft.Container):
    """A translucent surface with blur, border and soft shadow."""

    def __init__(
        self,
        content: ft.Control | None = None,
        *,
        padding: int = Metrics.SPACING,
        col: int | dict | None = None,
        expand: bool | int | None = None,
        on_click=None,
        tooltip: str | None = None,
    ) -> None:
        extra: dict = {
            "content": content,
            "padding": padding,
            "bgcolor": glass_surface_color(),
            "border": glass_border(),
            "border_radius": Metrics.RADIUS,
            "blur": ft.Blur(18, 18),
            "shadow": soft_shadow(),
        }
        if col is not None:
            extra["col"] = col
        if expand is not None:
            extra["expand"] = expand
        if on_click is not None:
            extra["on_click"] = on_click
        if tooltip is not None:
            extra["tooltip"] = tooltip
        super().__init__(**extra)


class SectionHeader(ft.Row):
    """A title with an optional icon and trailing actions."""

    def __init__(
        self,
        title: str,
        icon: ft.IconData | None = None,
        actions: list[ft.Control] | None = None,
    ) -> None:
        leading: list[ft.Control] = []
        if icon is not None:
            leading.append(ft.Icon(icon, size=20, color=Palette.PRIMARY))
        leading.append(
            ft.Text(
                t(title),
                size=FontSize.HEADING,
                weight=ft.FontWeight.W_600,
                color=Palette.TEXT,
            )
        )
        super().__init__(
            controls=[
                ft.Row(leading, spacing=Metrics.SPACING_SMALL, expand=True),
                *(actions or []),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )


class StatCard(GlassCard):
    """A compact metric card for the dashboard."""

    def __init__(
        self,
        label: str,
        value: str | int,
        icon: ft.IconData,
        accent: str = Palette.PRIMARY,
        col: int | dict | None = None,
        on_click=None,
    ) -> None:
        icon_badge = ft.Container(
            content=ft.Icon(icon, size=22, color=accent),
            width=44,
            height=44,
            border_radius=Metrics.RADIUS_SMALL,
            bgcolor=ft.Colors.with_opacity(0.12, accent),
            alignment=ft.Alignment.CENTER,
        )
        text_column = ft.Column(
            controls=[
                ft.Text(
                    str(value),
                    size=FontSize.TITLE,
                    weight=ft.FontWeight.BOLD,
                    color=Palette.TEXT,
                ),
                ft.Text(
                    t(label),
                    size=FontSize.CAPTION,
                    color=Palette.TEXT_MUTED,
                ),
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        super().__init__(
            content=ft.Row(
                controls=[icon_badge, text_column],
                spacing=Metrics.SPACING,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            col=col,
            on_click=on_click,
        )


class EmptyState(ft.Column):
    """A friendly placeholder shown when there is no data to display."""

    def __init__(
        self,
        title: str,
        message: str,
        icon: ft.IconData = ft.Icons.INBOX_OUTLINED,
    ) -> None:
        super().__init__(
            controls=[
                ft.Icon(icon, size=40, color=Palette.TEXT_MUTED),
                ft.Text(
                    t(title),
                    size=FontSize.BODY,
                    weight=ft.FontWeight.W_600,
                    color=Palette.TEXT,
                ),
                ft.Text(
                    t(message),
                    size=FontSize.CAPTION,
                    color=Palette.TEXT_MUTED,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=Metrics.SPACING_SMALL,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        )


class InfoRow(ft.Row):
    """A label/value pair used in detail panels."""

    def __init__(self, label: str, value: str, icon: ft.IconData | None = None):
        leading: list[ft.Control] = []
        if icon is not None:
            leading.append(ft.Icon(icon, size=16, color=Palette.TEXT_MUTED))
        leading.append(
            ft.Text(t(label), size=FontSize.CAPTION, color=Palette.TEXT_MUTED)
        )
        super().__init__(
            controls=[
                ft.Row(leading, spacing=6, expand=True),
                ft.Text(
                    value,
                    size=FontSize.BODY,
                    color=Palette.TEXT,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.RIGHT,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
