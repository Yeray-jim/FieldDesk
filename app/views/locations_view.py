"""Locations screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.forms import FormField, GlassDropdown, GlassTextField
from app.components.tables import text_cell
from app.schemas import LocationCreate, LocationUpdate
from app.views.crud_view import CrudView

FULL = 12
HALF = {"sm": 12, "md": 6}


class LocationsView(CrudView):
    """List, create, edit and delete locations, optionally filtered by client."""

    title = "Ubicaciones"
    singular = "ubicación"
    icon = ft.Icons.LOCATION_ON_OUTLINED
    add_label = "Nueva ubicación"
    search_hint = "Buscar por nombre o dirección"
    empty_title = "Sin ubicaciones"
    empty_message = "Registra la primera ubicación de un cliente."

    def prepare(self) -> None:
        self._client_filter = ""
        self._client_names = {
            client.id: client.name
            for client in self.services.clients.list_clients()
        }

    def load_records(self) -> list:
        if self._client_filter:
            return self.services.locations.list_locations_by_client(
                int(self._client_filter)
            )
        return self.services.locations.list_locations()

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(None, [record.name, record.address, record.reference])
        )

    def columns(self) -> list[str]:
        return ["Nombre", "Cliente", "Dirección", "Referencia"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.name),
            text_cell(
                self._client_names.get(record.client_id, "—"), muted=True
            ),
            text_cell(record.address or "—", muted=True),
            text_cell(record.reference or "—", muted=True),
        ]

    def filter_controls(self) -> list[ft.Control]:
        dropdown = GlassDropdown(
            "Cliente",
            [
                ("", "Todos los clientes"),
                *[
                    (str(client_id), name)
                    for client_id, name in self._client_names.items()
                ],
            ],
            value=self._client_filter,
            on_select=self._on_client_filter,
        )
        dropdown.width = 220
        return [dropdown]

    def _on_client_filter(self, event: ft.ControlEvent) -> None:
        self._client_filter = event.control.value or ""
        self._reload()

    def build_fields(self, record) -> list[FormField]:
        client_options = [
            (str(client_id), name)
            for client_id, name in self._client_names.items()
        ]
        current_client = (
            str(record.client_id) if record else None
        )
        return [
            FormField(
                "client_id",
                GlassDropdown(
                    "Cliente",
                    client_options,
                    required=True,
                    value=current_client,
                    col=FULL,
                ),
                required=True,
            ),
            FormField(
                "name",
                GlassTextField(
                    "Nombre",
                    required=True,
                    value=record.name if record else None,
                    col=FULL,
                ),
                required=True,
            ),
            FormField(
                "address",
                GlassTextField(
                    "Dirección",
                    value=record.address if record else None,
                    col=FULL,
                ),
            ),
            FormField(
                "reference",
                GlassTextField(
                    "Referencia",
                    value=record.reference if record else None,
                    col=HALF,
                ),
            ),
            FormField(
                "notes",
                GlassTextField(
                    "Notas",
                    value=record.notes if record else None,
                    multiline=True,
                    col=HALF,
                ),
            ),
        ]

    def create_record(self, values: dict) -> None:
        self.services.locations.create_location(LocationCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.locations.update_location(
            record.id, LocationUpdate(**values)
        )

    def delete_record(self, record) -> None:
        self.services.locations.delete_location(record.id)

    def record_label(self, record) -> str:
        return record.name
