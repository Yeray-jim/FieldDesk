"""Reusable form controls.

Fields validate through Pydantic in the service layer; these controls render
the result: they show required markers and display errors next to the field
while keeping the entered data.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import flet as ft
from pydantic import ValidationError as PydanticValidationError

from app.components.buttons import ghost_button, primary_button
from app.components.dialogs import GlassDialog, notify, open_dialog
from app.components.theme import FontSize, Metrics, Palette, glass_surface_color
from app.utils.exceptions import FieldDeskError
from app.utils.i18n import t

logger = logging.getLogger(__name__)

_PYDANTIC_MESSAGES: dict[str, str] = {
    "missing": "Este campo es obligatorio.",
    "string_too_short": "Este campo es obligatorio.",
    "string_too_long": "El texto es demasiado largo.",
    "int_parsing": "Introduce un número válido.",
    "int_type": "Introduce un número válido.",
    "decimal_parsing": "Introduce un número válido.",
    "decimal_type": "Introduce un número válido.",
    "date_parsing": "Introduce una fecha válida (AAAA-MM-DD).",
    "date_from_datetime_parsing": "Introduce una fecha válida (AAAA-MM-DD).",
    "time_parsing": "Introduce una hora válida (HH:MM).",
    "enum": "Selecciona una opción válida.",
    "greater_than": "El valor debe ser mayor que cero.",
}


def _friendly_message(error: dict) -> str:
    """Translate a Pydantic error into a user-friendly message."""
    error_type = error.get("type", "")
    if error_type in _PYDANTIC_MESSAGES:
        return t(_PYDANTIC_MESSAGES[error_type])
    message = error.get("msg", "Valor inválido.")
    prefix = "Value error, "
    if message.startswith(prefix):
        message = message[len(prefix):]
    return t(message)


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
            "label": f"{t(label)} *" if required else t(label),
            "hint_text": t(hint) if hint else hint,
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
            "color": Palette.TEXT,
            "label_style": ft.TextStyle(color=Palette.TEXT),
            "hint_style": ft.TextStyle(color=Palette.TEXT_MUTED),
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
            "label": f"{t(label)} *" if required else t(label),
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
            "color": Palette.TEXT,
            "label_style": ft.TextStyle(color=Palette.TEXT),
            "hint_style": ft.TextStyle(color=Palette.TEXT_MUTED),
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


class GlassDateField(ft.TextField):
    """A read-only field that opens a calendar to pick a date."""

    def __init__(
        self,
        page: ft.Page,
        label: str,
        *,
        required: bool = False,
        value: str | None = None,
        error: str | None = None,
        col: int | dict | None = None,
    ) -> None:
        self._page = page
        self._picker = ft.DatePicker(
            entry_mode=ft.DatePickerEntryMode.CALENDAR,
            on_change=self._on_date_change,
        )
        extra: dict = {
            "label": f"{t(label)} *" if required else t(label),
            "value": value,
            "error": error,
            "hint_text": "AAAA-MM-DD",
            "read_only": True,
            "suffix_icon": ft.Icons.CALENDAR_MONTH_OUTLINED,
            "border": ft.OutlineInputBorder(),
            "border_radius": Metrics.RADIUS_SMALL,
            "filled": True,
            "fill_color": glass_surface_color(),
            "text_size": FontSize.BODY,
            "color": Palette.TEXT,
            "label_style": ft.TextStyle(color=Palette.TEXT),
            "on_click": self._open_picker,
            "content_padding": ft.Padding.symmetric(
                horizontal=14, vertical=14
            ),
        }
        if col is not None:
            extra["col"] = col
        super().__init__(**extra)

    def _open_picker(self, _event: ft.ControlEvent) -> None:
        open_dialog(self._page, self._picker)

    def _on_date_change(self, event: ft.ControlEvent) -> None:
        value = event.control.value
        if value is None:
            return
        if isinstance(value, datetime):
            value = value.date()
        self.value = value.isoformat()
        self._page.update()

    def show_error(self, message: str) -> None:
        """Display an inline validation error."""
        self.error = message

    def clear_error(self) -> None:
        """Remove any inline validation error."""
        self.error = None


class GlassTimeField(ft.TextField):
    """A read-only field that opens a clock to pick a time."""

    def __init__(
        self,
        page: ft.Page,
        label: str,
        *,
        required: bool = False,
        value: str | None = None,
        error: str | None = None,
        col: int | dict | None = None,
    ) -> None:
        self._page = page
        self._picker = ft.TimePicker(on_change=self._on_time_change)
        extra: dict = {
            "label": f"{t(label)} *" if required else t(label),
            "value": value,
            "error": error,
            "hint_text": "HH:MM",
            "read_only": True,
            "suffix_icon": ft.Icons.SCHEDULE_OUTLINED,
            "border": ft.OutlineInputBorder(),
            "border_radius": Metrics.RADIUS_SMALL,
            "filled": True,
            "fill_color": glass_surface_color(),
            "text_size": FontSize.BODY,
            "color": Palette.TEXT,
            "label_style": ft.TextStyle(color=Palette.TEXT),
            "on_click": self._open_picker,
            "content_padding": ft.Padding.symmetric(
                horizontal=14, vertical=14
            ),
        }
        if col is not None:
            extra["col"] = col
        super().__init__(**extra)

    def _open_picker(self, _event: ft.ControlEvent) -> None:
        open_dialog(self._page, self._picker)

    def _on_time_change(self, event: ft.ControlEvent) -> None:
        value = event.control.value
        if value is None:
            return
        self.value = value.strftime("%H:%M")
        self._page.update()

    def show_error(self, message: str) -> None:
        """Display an inline validation error."""
        self.error = message

    def clear_error(self) -> None:
        """Remove any inline validation error."""
        self.error = None


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
        t("Los campos marcados con * son obligatorios."),
        size=FontSize.CAPTION,
        color=Palette.TEXT_MUTED,
    )


@dataclass
class FormField:
    """Binds a form field name to the control that renders it."""

    name: str
    control: ft.Control
    required: bool = False

    @property
    def value(self) -> Any:
        """Return the current raw value of the control."""
        return getattr(self.control, "value", None)

    def show_error(self, message: str) -> None:
        """Display a validation error next to the field."""
        if hasattr(self.control, "show_error"):
            self.control.show_error(message)
        elif hasattr(self.control, "error_text"):
            self.control.error_text = message
        elif hasattr(self.control, "error"):
            self.control.error = message

    def clear_error(self) -> None:
        """Remove the validation error from the field."""
        if hasattr(self.control, "clear_error"):
            self.control.clear_error()
        elif hasattr(self.control, "error_text"):
            self.control.error_text = None
        elif hasattr(self.control, "error"):
            self.control.error = None


class FormDialog(GlassDialog):
    """A modal form that validates through Pydantic and maps errors to fields.

    The ``on_submit`` callback receives a dictionary of raw values. It should
    build the Pydantic schema and call the service; any validation error is
    displayed next to the corresponding field and the dialog stays open.
    """

    def __init__(
        self,
        page: ft.Page,
        *,
        title: str,
        fields: list[FormField],
        on_submit: Callable[[dict[str, Any]], str | None],
        submit_label: str = "Guardar",
        icon: ft.IconData | None = None,
        width: int = 620,
    ) -> None:
        self._page = page
        self._fields = {field.name: field for field in fields}
        self._on_submit = on_submit

        form = ft.ResponsiveRow(
            controls=[field.control for field in fields],
            spacing=Metrics.SPACING_SMALL,
            run_spacing=Metrics.SPACING_SMALL,
        )
        content = ft.Container(
            content=ft.Column(
                controls=[form, required_hint()],
                spacing=Metrics.SPACING,
                scroll=ft.ScrollMode.AUTO,
            ),
            width=width,
        )
        actions = [
            ghost_button("Cancelar", on_click=self._handle_cancel),
            primary_button(
                submit_label,
                icon=ft.Icons.CHECK_OUTLINED,
                on_click=self._handle_save,
            ),
        ]
        super().__init__(title=title, content=content, actions=actions, icon=icon)

    def _collect(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for name, field in self._fields.items():
            value = field.value
            if isinstance(value, str):
                value = value.strip()
                if value == "" and not field.required:
                    value = None
            values[name] = value
        return values

    def _clear_errors(self) -> None:
        for field in self._fields.values():
            field.clear_error()

    def _apply_errors(self, error: PydanticValidationError) -> None:
        for item in error.errors():
            message = _friendly_message(item)
            location = item.get("loc", ())
            if location and location[0] in self._fields:
                self._fields[location[0]].show_error(message)
            else:
                notify(self._page, message, error=True)

    def _handle_cancel(self, _event: ft.ControlEvent) -> None:
        self._page.pop_dialog()

    def _handle_save(self, _event: ft.ControlEvent) -> None:
        self._clear_errors()
        values = self._collect()
        try:
            message = self._on_submit(values)
        except PydanticValidationError as error:
            self._apply_errors(error)
            self._page.update()
            return
        except FieldDeskError as error:
            notify(self._page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback to the user
            logger.exception("Error inesperado al guardar un formulario")
            notify(
                self._page,
                "No se pudo guardar. Verifica los datos e inténtalo "
                "nuevamente.",
                error=True,
            )
            return
        # Close the form first, then show the confirmation so that the
        # notification does not end up on top of the dialog stack.
        self._page.pop_dialog()
        if message:
            notify(self._page, message)
