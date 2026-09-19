"""Visits screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.forms import (
    FormField,
    GlassDateField,
    GlassDropdown,
    GlassTextField,
    GlassTimeField,
)
from app.components.tables import text_cell
from app.schemas import VisitCreate, VisitUpdate
from app.utils.dates import format_date, format_time
from app.views.crud_view import CrudView

FULL = 12
HALF = {"sm": 12, "md": 6}


class VisitsView(CrudView):
    """List, create, edit and delete visits."""

    title = "Visitas"
    singular = "visita"
    icon = ft.Icons.EVENT_NOTE_OUTLINED
    add_label = "Nueva visita"
    search_hint = "Buscar por trabajo u observaciones"
    empty_title = "Sin visitas"
    empty_message = "Registra la primera visita de un servicio."

    def prepare(self) -> None:
        self._service_filter = ""
        self._services_list = self.services.services.list_services()
        self._service_labels = {
            service.id: f"#{service.id} · {service.service_type}"
            for service in self._services_list
        }

    def load_records(self) -> list:
        if self._service_filter:
            return self.services.visits.list_visits_by_service(
                int(self._service_filter)
            )
        return self.services.visits.list_visits()

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(None, [record.work_performed, record.observations])
        )

    def columns(self) -> list[str]:
        return ["Servicio", "Fecha", "Horario", "Trabajo realizado"]

    def render_row(self, record) -> list[ft.Control]:
        schedule = (
            f"{format_time(record.start_time)} - "
            f"{format_time(record.end_time)}"
        )
        work = (record.work_performed or "—").strip()
        if len(work) > 60:
            work = f"{work[:57]}..."
        return [
            text_cell(self._service_labels.get(record.service_id, "—")),
            text_cell(format_date(record.visit_date), muted=True),
            text_cell(schedule, muted=True),
            text_cell(work, muted=True),
        ]

    def filter_controls(self) -> list[ft.Control]:
        dropdown = GlassDropdown(
            "Servicio",
            [
                ("", "Todos los servicios"),
                *[
                    (str(service_id), label)
                    for service_id, label in self._service_labels.items()
                ],
            ],
            value=self._service_filter,
            on_select=self._on_service_filter,
        )
        dropdown.width = 220
        return [dropdown]

    def _on_service_filter(self, event: ft.ControlEvent) -> None:
        self._service_filter = event.control.value or ""
        self._reload()

    def build_fields(self, record) -> list[FormField]:
        service_options = [
            (str(service.id), self._service_labels[service.id])
            for service in self._services_list
        ]
        return [
            FormField(
                "service_id",
                GlassDropdown(
                    "Servicio",
                    service_options,
                    required=True,
                    value=str(record.service_id) if record else None,
                    col=FULL,
                ),
                required=True,
            ),
            FormField(
                "visit_date",
                GlassDateField(
                    self.page,
                    "Fecha de la visita",
                    required=True,
                    value=record.visit_date.isoformat() if record else None,
                    col=HALF,
                ),
                required=True,
            ),
            FormField(
                "start_time",
                GlassTimeField(
                    self.page,
                    "Hora de inicio",
                    value=(
                        record.start_time.strftime("%H:%M")
                        if record and record.start_time
                        else None
                    ),
                    col=HALF,
                ),
            ),
            FormField(
                "end_time",
                GlassTimeField(
                    self.page,
                    "Hora de fin",
                    value=(
                        record.end_time.strftime("%H:%M")
                        if record and record.end_time
                        else None
                    ),
                    col=HALF,
                ),
            ),
            FormField(
                "work_performed",
                GlassTextField(
                    "Trabajo realizado",
                    value=record.work_performed if record else None,
                    multiline=True,
                    col=FULL,
                ),
            ),
            FormField(
                "observations",
                GlassTextField(
                    "Observaciones",
                    value=record.observations if record else None,
                    multiline=True,
                    col=FULL,
                ),
            ),
        ]

    def create_record(self, values: dict) -> None:
        self.services.visits.create_visit(VisitCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.visits.update_visit(record.id, VisitUpdate(**values))

    def delete_record(self, record) -> None:
        self.services.visits.delete_visit(record.id)

    def record_label(self, record) -> str:
        return f"{format_date(record.visit_date)}"
