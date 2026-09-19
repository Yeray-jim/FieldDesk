"""Reusable, consistently styled buttons."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.theme import FontSize, Metrics, Palette


def _style(
    bgcolor: str | None = None,
    color: str | None = None,
) -> ft.ButtonStyle:
    return ft.ButtonStyle(
        shape=ft.RoundedRectangleBorder(radius=Metrics.RADIUS_SMALL),
        padding=ft.Padding.symmetric(horizontal=18, vertical=14),
        bgcolor=bgcolor,
        color=color,
        elevation=0,
    )


def primary_button(
    text: str,
    on_click: Callable | None = None,
    icon: ft.IconData | None = None,
    disabled: bool = False,
    expand: bool | None = None,
) -> ft.FilledButton:
    """A prominent call-to-action button."""
    extra: dict = {}
    if expand is not None:
        extra["expand"] = expand
    return ft.FilledButton(
        content=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=_style(),
        **extra,
    )


def secondary_button(
    text: str,
    on_click: Callable | None = None,
    icon: ft.IconData | None = None,
    disabled: bool = False,
    expand: bool | None = None,
) -> ft.OutlinedButton:
    """A neutral secondary action."""
    extra: dict = {}
    if expand is not None:
        extra["expand"] = expand
    return ft.OutlinedButton(
        content=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=_style(),
        **extra,
    )


def danger_button(
    text: str,
    on_click: Callable | None = None,
    icon: ft.IconData | None = None,
    disabled: bool = False,
) -> ft.FilledButton:
    """A destructive action, visually distinct from the primary action."""
    return ft.FilledButton(
        content=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=_style(bgcolor=Palette.DANGER, color=Palette.ON_PRIMARY),
    )


def ghost_button(
    text: str,
    on_click: Callable | None = None,
    icon: ft.IconData | None = None,
    disabled: bool = False,
) -> ft.TextButton:
    """A low-emphasis text button."""
    return ft.TextButton(
        content=text,
        icon=icon,
        on_click=on_click,
        disabled=disabled,
        style=_style(),
    )


def icon_action_button(
    icon: ft.IconData,
    tooltip: str,
    on_click: Callable | None = None,
    color: str = Palette.TEXT_MUTED,
) -> ft.IconButton:
    """A compact icon button with an accessible tooltip."""
    return ft.IconButton(
        icon=icon,
        tooltip=tooltip,
        on_click=on_click,
        icon_color=color,
        icon_size=20,
    )


def app_bar(
    title: str,
    subtitle: str | None = None,
    actions: list[ft.Control] | None = None,
) -> ft.Container:
    """A lightweight translucent header used on mobile layouts."""
    title_controls: list[ft.Control] = [
        ft.Text(
            title,
            size=FontSize.HEADING,
            weight=ft.FontWeight.BOLD,
            color=Palette.TEXT,
        )
    ]
    if subtitle:
        title_controls.append(
            ft.Text(subtitle, size=FontSize.CAPTION, color=Palette.TEXT_MUTED)
        )
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Column(title_controls, spacing=0, expand=True),
                *(actions or []),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.Padding.symmetric(
            horizontal=Metrics.SPACING, vertical=Metrics.SPACING_SMALL
        ),
        bgcolor=ft.Colors.with_opacity(0.65, ft.Colors.WHITE),
    )
