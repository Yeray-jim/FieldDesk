"""Reusable dialogs and user feedback helpers."""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.buttons import danger_button, ghost_button, primary_button
from app.components.theme import FontSize, Metrics, Palette


class GlassDialog(ft.AlertDialog):
    """A modal dialog styled with the FieldDesk visual language."""

    def __init__(
        self,
        title: str,
        content: ft.Control,
        actions: list[ft.Control],
        *,
        icon: ft.IconData | None = None,
    ) -> None:
        super().__init__(
            modal=True,
            title=ft.Text(
                title,
                size=FontSize.HEADING,
                weight=ft.FontWeight.W_600,
                color=Palette.TEXT,
            ),
            content=content,
            actions=actions,
            icon=ft.Icon(icon, color=Palette.PRIMARY) if icon else None,
            shape=ft.RoundedRectangleBorder(radius=Metrics.RADIUS_LARGE),
            bgcolor=Palette.SURFACE,
            actions_alignment=ft.MainAxisAlignment.END,
        )


def open_dialog(page: ft.Page, dialog: ft.AlertDialog) -> None:
    """Display a dialog, ignoring a repeated open attempt."""
    try:
        page.show_dialog(dialog)
    except RuntimeError:
        page.pop_dialog()
        page.show_dialog(dialog)


def confirm_dialog(
    page: ft.Page,
    *,
    title: str,
    message: str,
    on_confirm: Callable[[], None],
    confirm_label: str = "Eliminar",
    danger: bool = True,
    icon: ft.IconData = ft.Icons.WARNING_AMBER_OUTLINED,
) -> None:
    """Show a confirmation dialog before a destructive action.

    The dialog explains the consequence and keeps destructive and cancel
    actions visually distinct.
    """

    def handle_cancel(_event: ft.ControlEvent) -> None:
        page.pop_dialog()

    def handle_confirm(_event: ft.ControlEvent) -> None:
        page.pop_dialog()
        on_confirm()

    dialog = GlassDialog(
        title=title,
        content=ft.Text(
            message,
            size=FontSize.BODY,
            color=Palette.TEXT_MUTED,
        ),
        actions=[
            ghost_button("Cancelar", on_click=handle_cancel),
            (
                danger_button(confirm_label, on_click=handle_confirm)
                if danger
                else primary_button(confirm_label, on_click=handle_confirm)
            ),
        ],
        icon=icon,
    )
    open_dialog(page, dialog)


def notify(page: ft.Page, message: str, *, error: bool = False) -> None:
    """Show a transient message at the bottom of the page."""
    snack = ft.SnackBar(
        content=ft.Text(
            message,
            color=Palette.ON_PRIMARY,
            size=FontSize.BODY,
        ),
        bgcolor=Palette.DANGER if error else "#0F172A",
        show_close_icon=True,
        close_icon_color=Palette.ON_PRIMARY,
        duration=4000,
    )
    page.show_dialog(snack)
