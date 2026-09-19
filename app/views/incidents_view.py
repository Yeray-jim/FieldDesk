"""Incidents screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.forms import FormField, GlassDropdown, GlassTextField
from app.components.tables import badge_cell, text_cell
from app.database.models import IncidentStatus, Priority
from app.schemas import IncidentCreate, IncidentUpdate
from app.views.crud_view import CrudView

FULL = 12
HALF = {"sm": 12, "md": 6}

_STATUS_OPTIONS = [
    (IncidentStatus.OPEN.value, "Abierta"),
    (IncidentStatus.IN_PROGRESS.value, "En progreso"),
    (IncidentStatus.RESOLVED.value, "Resuelta"),
    (IncidentStatus.CANCELLED.value, "Cancelada"),
]
_PRIORITY_OPTIONS = [
    (Priority.LOW.value, "Baja"),
    (Priority.MEDIUM.value, "Media"),
    (Priority.HIGH.value, "Alta"),
]


class IncidentsView(CrudView):
    """List, create, edit and delete incidents."""

    title = "Incidencias"
    singular = "incidencia"
    icon = ft.Icons.WARNING_AMBER_OUTLINED
    add_label = "Nueva incidencia"
    search_hint = "Buscar por título o descripción"
    empty_title = "Sin incidencias"
    empty_message = "Registra la primera incidencia de un equipo."

    def prepare(self) -> None:
        self._status_filter = ""
        self._equipment = self.services.equipment.list_equipment()
        self._services_list = self.services.services.list_services()
        self._equipment_names = {
            equipment.id: equipment.name for equipment in self._equipment
        }
        self._service_labels = {
            service.id: f"#{service.id} · {service.service_type}"
            for service in self._services_list
        }

    def load_records(self) -> list:
        records = self.services.incidents.list_incidents()
        if self._status_filter:
            records = [
                record
                for record in records
                if record.status.value == self._status_filter
            ]
        return records

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(None, [record.title, record.description, record.resolution])
        )

    def columns(self) -> list[str]:
        return ["Título", "Equipo", "Prioridad", "Estado"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.title),
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

    def build_fields(self, record) -> list[FormField]:
        equipment_options = [
            (str(equipment.id), f"{equipment.name} · {equipment.type}")
            for equipment in self._equipment
        ]
        service_options = [
            ("", "Sin servicio asociado"),
            *[
                (str(service.id), self._service_labels[service.id])
                for service in self._services_list
            ],
        ]
        return [
            FormField(
                "equipment_id",
                GlassDropdown(
                    "Equipo",
                    equipment_options,
                    required=True,
                    value=str(record.equipment_id) if record else None,
                    col=FULL,
                ),
                required=True,
            ),
            FormField(
                "service_id",
                GlassDropdown(
                    "Servicio",
                    service_options,
                    value=(
                        str(record.service_id)
                        if record and record.service_id
                        else ""
                    ),
                    col=FULL,
                ),
            ),
            FormField(
                "title",
                GlassTextField(
                    "Título",
                    required=True,
                    value=record.title if record else None,
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
            FormField(
                "status",
                GlassDropdown(
                    "Estado",
                    _STATUS_OPTIONS,
                    required=True,
                    value=(
                        record.status.value
                        if record
                        else IncidentStatus.OPEN.value
                    ),
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "resolution",
                GlassTextField(
                    "Resolución",
                    value=record.resolution if record else None,
                    multiline=True,
                    col=FULL,
                ),
            ),
        ]

    def create_record(self, values: dict) -> None:
        self.services.incidents.create_incident(IncidentCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.incidents.update_incident(
            record.id, IncidentUpdate(**values)
        )

    def delete_record(self, record) -> None:
        self.services.incidents.delete_incident(record.id)

    def record_label(self, record) -> str:
        return record.title
