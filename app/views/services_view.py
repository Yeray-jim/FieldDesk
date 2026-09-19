"""Services screen with full CRUD integration."""

from __future__ import annotations

import logging
from pathlib import Path

import flet as ft

from app.components.dialogs import notify
from app.components.forms import (
    FormField,
    GlassDateField,
    GlassDropdown,
    GlassTextField,
    GlassTimeField,
)
from app.components.tables import badge_cell, text_cell
from app.database.models import Priority, ServiceStatus
from app.schemas import ServiceCreate, ServiceUpdate
from app.utils.exceptions import FieldDeskError
from app.views.crud_view import CrudView
from app.views.service_evidence_dialog import ServiceEvidenceDialog
from app.views.service_materials_dialog import ServiceMaterialsDialog

logger = logging.getLogger(__name__)

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
        return ["Servicio", "Equipo", "Prioridad", "Estado"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.service_type),
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

    def extra_row_menu_items(self, record) -> list[ft.PopupMenuItem]:
        return [
            ft.PopupMenuItem(
                content=ft.Text("Materiales"),
                icon=ft.Icons.INVENTORY_2_OUTLINED,
                on_click=lambda _event, item=record: self._open_materials(
                    item
                ),
            ),
            ft.PopupMenuItem(
                content=ft.Text("Evidencias"),
                icon=ft.Icons.PHOTO_LIBRARY_OUTLINED,
                on_click=lambda _event, item=record: self._open_evidence(item),
            ),
            ft.PopupMenuItem(
                content=ft.Text("Reporte PDF"),
                icon=ft.Icons.PICTURE_AS_PDF_OUTLINED,
                on_click=lambda _event, item=record: self._open_report(item),
            ),
        ]

    def _open_materials(self, record) -> None:
        ServiceMaterialsDialog(self.page, self.services, record).show()

    def _open_evidence(self, record) -> None:
        ServiceEvidenceDialog(
            self.page,
            self.services,
            record,
            file_picker=self.context.file_picker,
        ).show()

    def _open_report(self, record) -> None:
        try:
            path = self.services.reports.generate_service_report(record.id)
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudo generar el reporte")
            notify(
                self.page,
                "No se pudo generar el reporte. Inténtalo nuevamente.",
                error=True,
            )
            return
        notify(self.page, f"Reporte generado: {path.name}")
        self._launch(path)

    def _launch(self, path: Path) -> None:
        launcher = self.context.url_launcher
        if launcher is None:
            return
        self.page.run_task(launcher.launch_url, path.as_uri())

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
        scheduled_date = (
            record.scheduled_date.strftime("%Y-%m-%d")
            if record and record.scheduled_date
            else None
        )
        scheduled_time = (
            record.scheduled_date.strftime("%H:%M")
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
                GlassDateField(
                    self.page,
                    "Fecha programada",
                    value=scheduled_date,
                    col=HALF,
                ),
            ),
            FormField(
                "scheduled_time",
                GlassTimeField(
                    self.page,
                    "Hora programada",
                    value=scheduled_time,
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

    @staticmethod
    def _combine_schedule(values: dict) -> dict:
        """Merge the date and time fields into the ``scheduled_date``."""
        data = dict(values)
        moment = data.pop("scheduled_time", None)
        date_value = data.get("scheduled_date")
        if date_value and moment:
            data["scheduled_date"] = f"{date_value} {moment}"
        elif date_value:
            data["scheduled_date"] = f"{date_value} 00:00"
        return data

    def create_record(self, values: dict) -> None:
        self.services.services.create_service(
            ServiceCreate(**self._combine_schedule(values))
        )

    def update_record(self, record, values: dict) -> None:
        self.services.services.update_service(
            record.id, ServiceUpdate(**self._combine_schedule(values))
        )

    def delete_record(self, record) -> None:
        self.services.services.delete_service(record.id)

    def record_label(self, record) -> str:
        return record.service_type
