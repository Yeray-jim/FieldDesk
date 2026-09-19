"""Equipment screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.forms import (
    FormField,
    GlassDateField,
    GlassDropdown,
    GlassTextField,
)
from app.components.tables import badge_cell, text_cell
from app.database.models import EquipmentStatus
from app.schemas import EquipmentCreate, EquipmentUpdate
from app.views.crud_view import CrudView
from app.views.equipment_history_dialog import EquipmentHistoryDialog
from app.views.location_fields import open_location_form

_NEW_LOCATION = "__new__"

FULL = 12
HALF = {"sm": 12, "md": 6}

_STATUS_OPTIONS = [
    (EquipmentStatus.OPERATIONAL.value, "Operativo"),
    (EquipmentStatus.MAINTENANCE.value, "Mantenimiento"),
    (EquipmentStatus.OUT_OF_SERVICE.value, "Fuera de servicio"),
    (EquipmentStatus.RETIRED.value, "Retirado"),
]


class EquipmentView(CrudView):
    """List, create, edit and delete equipment."""

    title = "Equipos"
    singular = "equipo"
    icon = ft.Icons.BUILD_OUTLINED
    add_label = "Nuevo equipo"
    search_hint = "Buscar por nombre, marca, modelo o serie"
    empty_title = "Sin equipos"
    empty_message = "Registra el primer equipo de una ubicación."

    def prepare(self) -> None:
        self._status_filter = ""
        self._selected_location_id = ""
        self._locations = self.services.locations.list_locations()
        self._location_names = {
            location.id: location.name for location in self._locations
        }
        self._clients = self.services.clients.list_clients()
        self._client_options = [
            (str(client.id), client.name) for client in self._clients
        ]

    def load_records(self) -> list:
        if self._status_filter:
            return self.services.equipment.list_equipment_by_status(
                EquipmentStatus(self._status_filter)
            )
        return self.services.equipment.list_equipment()

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(
                None,
                [
                    record.name,
                    record.type,
                    record.brand,
                    record.model,
                    record.serial_number,
                ],
            )
        )

    def columns(self) -> list[str]:
        return ["Nombre", "Tipo", "N.º de serie", "Ubicación", "Estado"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.name),
            text_cell(record.type, muted=True),
            text_cell(record.serial_number or "—", muted=True),
            text_cell(
                self._location_names.get(record.location_id, "—"), muted=True
            ),
            badge_cell(record.status),
        ]

    def filter_controls(self) -> list[ft.Control]:
        dropdown = GlassDropdown(
            "Estado",
            [("", "Todos los estados"), *_STATUS_OPTIONS],
            value=self._status_filter,
            on_select=self._on_status_filter,
        )
        dropdown.width = 200
        return [dropdown]

    def _on_status_filter(self, event: ft.ControlEvent) -> None:
        self._status_filter = event.control.value or ""
        self._reload()

    def _on_location_select(self, event: ft.ControlEvent) -> None:
        value = event.control.value or ""
        if value == _NEW_LOCATION:
            event.control.value = self._selected_location_id
            open_location_form(
                self.page,
                self.services,
                self._client_options,
                self._on_location_created,
            )
            self.page.update()
        else:
            self._selected_location_id = value

    def _on_location_created(self, location) -> None:
        self._locations = self.services.locations.list_locations()
        self._location_names = {
            item.id: item.name for item in self._locations
        }
        self._selected_location_id = str(location.id)
        dropdown = self._location_dropdown
        dropdown.options = [
            ft.DropdownOption(key=key, text=text)
            for key, text in self._location_options()
        ]
        dropdown.value = str(location.id)
        dropdown.clear_error()
        self.page.update()

    def extra_row_menu_items(self, record) -> list[ft.PopupMenuItem]:
        return [
            ft.PopupMenuItem(
                content=ft.Text("Ver historial"),
                icon=ft.Icons.HISTORY_OUTLINED,
                on_click=lambda _event, item=record: self._open_history(item),
            )
        ]

    def _open_history(self, record) -> None:
        EquipmentHistoryDialog(self.page, self.services, record).show()

    def _location_options(self) -> list[tuple[str, str]]:
        return [
            (str(location.id), location.name)
            for location in self._locations
        ] + [(_NEW_LOCATION, "+ Crear nueva ubicación…")]

    def build_fields(self, record) -> list[FormField]:
        self._selected_location_id = (
            str(record.location_id) if record else ""
        )
        self._location_dropdown = GlassDropdown(
            "Ubicación",
            self._location_options(),
            required=True,
            value=str(record.location_id) if record else None,
            on_select=self._on_location_select,
            col=FULL,
        )
        return [
            FormField(
                "location_id",
                self._location_dropdown,
                required=True,
            ),
            FormField(
                "name",
                GlassTextField(
                    "Nombre",
                    required=True,
                    value=record.name if record else None,
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "type",
                GlassTextField(
                    "Tipo",
                    required=True,
                    value=record.type if record else None,
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "brand",
                GlassTextField(
                    "Marca", value=record.brand if record else None, col=HALF
                ),
            ),
            FormField(
                "model",
                GlassTextField(
                    "Modelo", value=record.model if record else None, col=HALF
                ),
            ),
            FormField(
                "serial_number",
                GlassTextField(
                    "N.º de serie",
                    value=record.serial_number if record else None,
                    col=HALF,
                ),
            ),
            FormField(
                "status",
                GlassDropdown(
                    "Estado",
                    _STATUS_OPTIONS,
                    required=True,
                    value=(
                        record.status.value
                        if record
                        else EquipmentStatus.OPERATIONAL.value
                    ),
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "installation_date",
                GlassDateField(
                    self.page,
                    "Fecha de instalación",
                    value=(
                        record.installation_date.isoformat()
                        if record and record.installation_date
                        else None
                    ),
                    col=HALF,
                ),
            ),
            FormField(
                "warranty_expiration",
                GlassDateField(
                    self.page,
                    "Fin de garantía",
                    value=(
                        record.warranty_expiration.isoformat()
                        if record and record.warranty_expiration
                        else None
                    ),
                    col=HALF,
                ),
            ),
            FormField(
                "notes",
                GlassTextField(
                    "Notas",
                    value=record.notes if record else None,
                    multiline=True,
                    col=FULL,
                ),
            ),
        ]

    def create_record(self, values: dict) -> None:
        self.services.equipment.create_equipment(EquipmentCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.equipment.update_equipment(
            record.id, EquipmentUpdate(**values)
        )

    def delete_record(self, record) -> None:
        self.services.equipment.delete_equipment(record.id)

    def record_label(self, record) -> str:
        return record.name
