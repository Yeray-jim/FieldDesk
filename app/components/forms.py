"""Reusable form controls.

Fields validate through Pydantic in the service layer; these controls render
the result: they show required markers and display errors next to the field
while keeping the entered data.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.buttons import ghost_button, primary_button
from app.components.theme import FontSize, Metrics, Palette, glass_surface_color


class GlassTextField(ft.TextField):
    """A translucent text field with inline error support."""

    def __init__(
        self,
        label: str,
        *,
        required: bool = False,
        hint: str | None = None,
        value: str | None = None,
        error: str | None = None,
        password: bool = False,
        multiline: bool = False,
        min_lines: int = 1,
        max_lines: int = 4,
        prefix_icon: ft.IconData | None = None,
        keyboard_type: ft.KeyboardType | None = None,
        on_change: Callable | None = None,
        on_submit: Callable | None = None,
        col: int | dict | None = None,
        read_only: bool = False,
        max_length: int | None = None,
        autofocus: bool = False,
    ) -> None:
        extra: dict = {
            "label": f"{label} *" if required else label,
            "hint_text": hint,
            "value": value,
            "error": error,
            "password": password,
            "multiline": multiline,
            "min_lines": min_lines,
            "max_lines": max_lines,
            "prefix_icon": prefix_icon,
            "border": ft.OutlineInputBorder(),
            "border_radius": Metrics.RADIUS_SMALL,
            "filled": True,
            "fill_color": glass_surface_color(),
            "text_size": FontSize.BODY,
            "read_only": read_only,
            "autofocus": autofocus,
            "content_padding": ft.Padding.symmetric(horizontal=14, vertical=14),
        }
        if keyboard_type is not None:
            extra["keyboard_type"] = keyboard_type
        if max_length is not None:
            extra["max_length"] = max_length
        if on_change is not None:
            extra["on_change"] = on_change
        if on_submit is not None:
            extra["on_submit"] = on_submit
        if col is not None:
            extra["col"] = col
        super().__init__(**extra)

    def show_error(self, message: str) -> None:
        """Display an inline validation error."""
        self.error = message

    def clear_error(self) -> None:
        """Remove any inline validation error."""
        self.error = None


class GlassDropdown(ft.Dropdown):
    """A translucent dropdown with required marker and inline errors."""

    def __init__(
        self,
        label: str,
        options: list[tuple[str, str]],
        *,
        required: bool = False,
        value: str | None = None,
        error: str | None = None,
        on_select: Callable | None = None,
        col: int | dict | None = None,
    ) -> None:
        extra: dict = {
            "label": f"{label} *" if required else label,
            "options": [
                ft.DropdownOption(key=key, text=text) for key, text in options
            ],
            "value": value,
            "error_text": error,
            "border": ft.OutlineInputBorder(),
            "border_radius": Metrics.RADIUS_SMALL,
            "filled": True,
            "fill_color": glass_surface_color(),
            "text_size": FontSize.BODY,
            "content_padding": ft.Padding.symmetric(horizontal=14, vertical=14),
        }
        if on_select is not None:
            extra["on_select"] = on_select
        if col is not None:
            extra["col"] = col
        super().__init__(**extra)

    def show_error(self, message: str) -> None:
        """Display an inline validation error."""
        self.error_text = message

    def clear_error(self) -> None:
        """Remove any inline validation error."""
        self.error_text = None


def form_actions(
    on_save: Callable | None,
    on_cancel: Callable | None = None,
    save_label: str = "Guardar",
) -> ft.Row:
    """Build the standard cancel/save action row."""
    controls: list[ft.Control] = []
    if on_cancel is not None:
        controls.append(ghost_button("Cancelar", on_click=on_cancel))
    if on_save is not None:
        controls.append(
            primary_button(
                save_label,
                on_click=on_save,
                icon=ft.Icons.CHECK_OUTLINED,
            )
        )
    return ft.Row(
        controls=controls,
        alignment=ft.MainAxisAlignment.END,
        spacing=Metrics.SPACING_SMALL,
        wrap=True,
    )


def required_hint() -> ft.Text:
    """Explain the meaning of the required-field marker."""
    return ft.Text(
        "Los campos marcados con * son obligatorios.",
        size=FontSize.CAPTION,
        color=Palette.TEXT_MUTED,
    )
