"""Reusable CRUD screen.

Concrete views only declare their columns, rows, form fields and the service
calls for create/update/delete. All the repetitive machinery (search,
listing, dialogs, confirmation and error handling) lives here, following DRY.
"""

from __future__ import annotations

import logging

import flet as ft

from app.components.buttons import icon_action_button, primary_button
from app.components.cards import SectionHeader
from app.components.dialogs import confirm_dialog, notify, open_dialog
from app.components.forms import FormDialog, FormField, GlassTextField
from app.components.tables import GlassTable
from app.components.theme import Metrics, Palette
from app.utils.exceptions import FieldDeskError
from app.views.base_view import BaseView

logger = logging.getLogger(__name__)


class CrudView(BaseView):
    """Base class for list + create/edit/delete screens."""

    title = ""
    singular = "registro"
    icon: ft.IconData | None = None
    form_icon: ft.IconData | None = ft.Icons.EDIT_OUTLINED
    add_label = "Nuevo"
    search_hint = "Buscar..."
    empty_title = "Sin registros"
    empty_message = "Añade el primero con el botón «Nuevo»."

    def __init__(self, context) -> None:
        super().__init__(context)
        self._term = ""
        self._rows: list = []
        self._table_slot = ft.Container()

    # ------------------------------------------------------------------
    # Hooks to implement in subclasses
    # ------------------------------------------------------------------
    def prepare(self) -> None:
        """Load auxiliary lookup data before listing records."""

    def load_records(self) -> list:
        """Return the records to display."""
        return []

    def searchable_text(self, record) -> str:
        """Return the text used for client-side search."""
        return ""

    def columns(self) -> list[str]:
        """Return the table headers (without the actions column)."""
        return []

    def render_row(self, record) -> list[ft.Control]:
        """Return the table cells for a record."""
        return []

    def build_fields(self, record) -> list[FormField]:
        """Return the form fields, optionally prefilled from ``record``."""
        return []

    def filter_controls(self) -> list[ft.Control]:
        """Return optional filter controls for the toolbar."""
        return []

    def extra_row_menu_items(self, record) -> list[ft.PopupMenuItem]:
        """Return extra per-row actions rendered in an overflow menu."""
        return []

    def create_record(self, values: dict) -> None:
        """Create a record from raw form values."""
        raise NotImplementedError

    def update_record(self, record, values: dict) -> None:
        """Update a record from raw form values."""
        raise NotImplementedError

    def delete_record(self, record) -> None:
        """Delete a record."""
        raise NotImplementedError

    def record_label(self, record) -> str:
        """Return a human-readable label used in messages."""
        return str(record)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------
    def build(self) -> ft.Control:
        self.prepare()
        self._rows = self._load()
        self._table_slot.content = self._render_table()
        return ft.Column(
            controls=[
                SectionHeader(
                    self.title,
                    icon=self.icon,
                    actions=[
                        primary_button(
                            self.add_label,
                            icon=ft.Icons.ADD,
                            on_click=self._open_create,
                        )
                    ],
                ),
                self._toolbar(),
                self._table_slot,
            ],
            spacing=Metrics.SPACING,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _toolbar(self) -> ft.Row:
        search = GlassTextField(
            "",
            hint=self.search_hint,
            prefix_icon=ft.Icons.SEARCH,
            on_change=self._on_search,
        )
        search.width = 280
        controls: list[ft.Control] = [search, *self.filter_controls()]
        return ft.Row(
            controls=controls,
            spacing=Metrics.SPACING_SMALL,
            run_spacing=Metrics.SPACING_SMALL,
            wrap=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _render_table(self) -> GlassTable:
        rows: list[list[ft.Control]] = []
        for record in self._rows:
            cells = list(self.render_row(record))
            cells.append(self._actions_cell(record))
            rows.append(cells)
        return GlassTable(
            [*self.columns(), "Acciones"],
            rows,
            empty_title=self.empty_title,
            empty_message=self.empty_message,
        )

    def _actions_cell(self, record) -> ft.Row:
        controls: list[ft.Control] = []
        menu_items = self.extra_row_menu_items(record)
        if menu_items:
            controls.append(
                ft.PopupMenuButton(
                    icon=ft.Icons.MORE_VERT,
                    tooltip="Más acciones",
                    icon_color=Palette.TEXT_MUTED,
                    icon_size=20,
                    items=menu_items,
                )
            )
        controls.append(
            icon_action_button(
                ft.Icons.EDIT_OUTLINED,
                "Editar",
                on_click=lambda _event, item=record: self._open_edit(item),
            )
        )
        controls.append(
            icon_action_button(
                ft.Icons.DELETE_OUTLINE,
                "Eliminar",
                on_click=lambda _event, item=record: self._confirm_delete(item),
                color=Palette.DANGER,
            )
        )
        return ft.Row(controls=controls, spacing=0)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def _load(self) -> list:
        try:
            records = self.load_records()
        except Exception:  # noqa: BLE001 - the screen must not crash
            logger.exception("No se pudieron cargar datos de %s", self.title)
            return []
        if self._term:
            needle = self._term.lower()
            records = [
                record
                for record in records
                if needle in self.searchable_text(record).lower()
            ]
        return records

    def _reload(self) -> None:
        self._rows = self._load()
        self._table_slot.content = self._render_table()
        self.page.update()

    def _on_search(self, event: ft.ControlEvent) -> None:
        self._term = (event.control.value or "").strip()
        self._reload()

    # ------------------------------------------------------------------
    # Create / edit / delete
    # ------------------------------------------------------------------
    def _open_create(self, _event: ft.ControlEvent) -> None:
        self._show_form(None)

    def _open_edit(self, record) -> None:
        self._show_form(record)

    def _show_form(self, record) -> None:
        fields = self.build_fields(record)
        title = (
            f"Editar {self.singular}"
            if record is not None
            else f"Nuevo {self.singular}"
        )
        dialog = FormDialog(
            self.page,
            title=title,
            fields=fields,
            on_submit=lambda values: self._save(record, values),
            icon=self.form_icon,
        )
        open_dialog(self.page, dialog)

    def _save(self, record, values: dict) -> str:
        if record is None:
            self.create_record(values)
        else:
            self.update_record(record, values)
        self._reload()
        return "Guardado correctamente."

    def _confirm_delete(self, record) -> None:
        confirm_dialog(
            self.page,
            title=f"¿Eliminar {self.singular}?",
            message=(
                f"«{self.record_label(record)}» se eliminará de forma "
                "permanente. Esta acción no puede deshacerse."
            ),
            on_confirm=lambda: self._delete(record),
        )

    def _delete(self, record) -> None:
        try:
            self.delete_record(record)
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudo eliminar un registro de %s", self.title)
            notify(
                self.page,
                "No se pudo eliminar el registro. Inténtalo nuevamente.",
                error=True,
            )
            return
        self._reload()
        notify(self.page, "Eliminado correctamente.")
