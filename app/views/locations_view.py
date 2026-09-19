"""Locations screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.forms import GlassDropdown
from app.components.tables import text_cell
from app.schemas import LocationUpdate
from app.views.crud_view import CrudView
from app.views.location_fields import build_location_fields


class LocationsView(CrudView):
    """List, create, edit and delete locations, optionally filtered by client."""

    title = "Ubicaciones"
    singular = "ubicación"
    icon = ft.Icons.LOCATION_ON_OUTLINED
    add_label = "Nueva ubicación"
    search_hint = "Buscar por nombre, municipio, calle o referencia"
    empty_title = "Sin ubicaciones"
    empty_message = "Registra la primera ubicación de un cliente."

    def prepare(self) -> None:
        self._client_filter = ""
        self._clients = self.services.clients.list_clients()
        self._client_names = {
            client.id: client.name for client in self._clients
        }
        self._client_options = [
            (str(client.id), client.name) for client in self._clients
        ]

    def load_records(self) -> list:
        if self._client_filter:
            return self.services.locations.list_locations_by_client(
                int(self._client_filter)
            )
        return self.services.locations.list_locations()

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(
                None,
                [
                    record.name,
                    record.state,
                    record.municipality,
                    record.neighborhood,
                    record.street,
                    record.lot,
                    record.block,
                    record.reference,
                ],
            )
        )

    def columns(self) -> list[str]:
        return ["Nombre", "Cliente", "Municipio", "Calle", "Referencia"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.name),
            text_cell(
                self._client_names.get(record.client_id, "—"), muted=True
            ),
            text_cell(record.municipality or "—", muted=True),
            text_cell(record.street or "—", muted=True),
            text_cell(record.reference or "—", muted=True),
        ]

    def filter_controls(self) -> list[ft.Control]:
        dropdown = GlassDropdown(
            "Cliente",
            [("", "Todos los clientes"), *self._client_options],
            value=self._client_filter,
            on_select=self._on_client_filter,
        )
        dropdown.width = 220
        return [dropdown]

    def _on_client_filter(self, event: ft.ControlEvent) -> None:
        self._client_filter = event.control.value or ""
        self._reload()

    def build_fields(self, record) -> list:
        return build_location_fields(record, self._client_options)

    def create_record(self, values: dict) -> None:
        from app.schemas import LocationCreate

        self.services.locations.create_location(LocationCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.locations.update_location(
            record.id, LocationUpdate(**values)
        )

    def delete_record(self, record) -> None:
        self.services.locations.delete_location(record.id)

    def record_label(self, record) -> str:
        return record.name
