"""Services screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.buttons import icon_action_button
from app.components.forms import FormField, GlassDropdown, GlassTextField
from app.components.tables import badge_cell, text_cell
from app.components.theme import Palette
from app.database.models import Priority, ServiceStatus
from app.schemas import ServiceCreate, ServiceUpdate
from app.views.crud_view import CrudView
from app.views.service_materials_dialog import ServiceMaterialsDialog

FULL = 12
HALF = {"sm": 12, "md": 6}

_STATUS_OPTIONS = [
    (ServiceStatus.PENDING.value, "Pendiente"),
    (ServiceStatus.IN_PROGRESS.value, "En progreso"),
    (ServiceStatus.COMPLETED.value, "Completado"),
    (ServiceStatus.CANCELLED.value, "Cancelado"),
]
_PRIORITY_OPTIONS = [
    (Priority.LOW.value, "Baja"),
    (Priority.MEDIUM.value, "Media"),
    (Priority.HIGH.value, "Alta"),
]


class ServicesView(CrudView):
    """List, create, edit and delete services."""

    title = "Servicios"
    singular = "servicio"
    icon = ft.Icons.ASSIGNMENT_OUTLINED
    add_label = "Nuevo servicio"
    search_hint = "Buscar por tipo o descripción"
    empty_title = "Sin servicios"
    empty_message = "Registra el primer servicio para un equipo."

    def prepare(self) -> None:
        self._status_filter = ""
        self._clients = self.services.clients.list_clients()
        self._equipment = self.services.equipment.list_equipment()
        self._client_names = {client.id: client.name for client in self._clients}
        self._equipment_names = {
            equipment.id: equipment.name for equipment in self._equipment
        }

    def load_records(self) -> list:
        if self._status_filter:
            return self.services.services.list_services_by_status(
                ServiceStatus(self._status_filter)
            )
        return self.services.services.list_services()

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(None, [record.service_type, record.description])
        )

    def columns(self) -> list[str]:
        return ["Servicio", "Cliente", "Equipo", "Prioridad", "Estado"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.service_type),
            text_cell(
                self._client_names.get(record.client_id, "—"), muted=True
            ),
            text_cell(
                self._equipment_names.get(record.equipment_id, "—"), muted=True
            ),
            badge_cell(record.priority),
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

    def extra_row_actions(self, record) -> list[ft.Control]:
        return [
            icon_action_button(
                ft.Icons.INVENTORY_2_OUTLINED,
                "Materiales",
                on_click=lambda _event, item=record: self._open_materials(item),
                color=Palette.PRIMARY,
            )
        ]

    def _open_materials(self, record) -> None:
        ServiceMaterialsDialog(self.page, self.services, record).open()

    def build_fields(self, record) -> list[FormField]:
        client_options = [
            (str(client.id), client.name) for client in self._clients
        ]
        equipment_options = [
            (
                str(equipment.id),
                f"{equipment.name} · {equipment.type}",
            )
            for equipment in self._equipment
        ]
        scheduled = (
            record.scheduled_date.strftime("%Y-%m-%d %H:%M")
            if record and record.scheduled_date
            else None
        )
        return [
            FormField(
                "client_id",
                GlassDropdown(
                    "Cliente",
                    client_options,
                    required=True,
                    value=str(record.client_id) if record else None,
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "equipment_id",
                GlassDropdown(
                    "Equipo",
                    equipment_options,
                    required=True,
                    value=str(record.equipment_id) if record else None,
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "service_type",
                GlassTextField(
                    "Tipo de servicio",
                    required=True,
                    value=record.service_type if record else None,
                    col=FULL,
                ),
                required=True,
            ),
            FormField(
                "description",
                GlassTextField(
                    "Descripción",
                    value=record.description if record else None,
                    multiline=True,
                    col=FULL,
                ),
            ),
            FormField(
                "scheduled_date",
                GlassTextField(
                    "Fecha programada",
                    hint="AAAA-MM-DD HH:MM",
                    value=scheduled,
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
                        else ServiceStatus.PENDING.value
                    ),
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "priority",
                GlassDropdown(
                    "Prioridad",
                    _PRIORITY_OPTIONS,
                    required=True,
                    value=(
                        record.priority.value
                        if record
                        else Priority.MEDIUM.value
                    ),
                    col=HALF,
                ),
                required=True,
            ),
        ]

    def create_record(self, values: dict) -> None:
        self.services.services.create_service(ServiceCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.services.update_service(
            record.id, ServiceUpdate(**values)
        )

    def delete_record(self, record) -> None:
        self.services.services.delete_service(record.id)

    def record_label(self, record) -> str:
        return record.service_type
