"""Clients screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.forms import FormField, GlassTextField
from app.components.tables import text_cell
from app.schemas import ClientCreate, ClientUpdate
from app.views.crud_view import CrudView

HALF = {"sm": 12, "md": 6}


class ClientsView(CrudView):
    """List, create, edit and delete clients."""

    title = "Clientes"
    singular = "cliente"
    icon = ft.Icons.PEOPLE_OUTLINED
    add_label = "Nuevo cliente"
    search_hint = "Buscar por nombre, empresa, teléfono o email"
    empty_title = "Sin clientes"
    empty_message = "Registra tu primer cliente para empezar."

    def load_records(self) -> list:
        return self.services.clients.list_clients()

    def searchable_text(self, record) -> str:
        return " ".join(
            filter(
                None,
                [record.name, record.company, record.phone, record.email],
            )
        )

    def columns(self) -> list[str]:
        return ["Nombre", "Empresa", "Teléfono", "Email"]

    def render_row(self, record) -> list[ft.Control]:
        return [
            text_cell(record.name),
            text_cell(record.company or "—", muted=True),
            text_cell(record.phone or "—", muted=True),
            text_cell(record.email or "—", muted=True),
        ]

    def build_fields(self, record) -> list[FormField]:
        return [
            FormField(
                "name",
                GlassTextField(
                    "Nombre",
                    required=True,
                    value=record.name if record else None,
                    col=12,
                ),
                required=True,
            ),
            FormField(
                "company",
                GlassTextField(
                    "Empresa",
                    value=record.company if record else None,
                    col=HALF,
                ),
            ),
            FormField(
                "phone",
                GlassTextField(
                    "Teléfono",
                    value=record.phone if record else None,
                    keyboard_type=ft.KeyboardType.PHONE,
                    col=HALF,
                ),
            ),
            FormField(
                "email",
                GlassTextField(
                    "Email",
                    value=record.email if record else None,
                    keyboard_type=ft.KeyboardType.EMAIL,
                    col=HALF,
                ),
            ),
            FormField(
                "address",
                GlassTextField(
                    "Dirección",
                    value=record.address if record else None,
                    col=HALF,
                ),
            ),
            FormField(
                "notes",
                GlassTextField(
                    "Notas",
                    value=record.notes if record else None,
                    multiline=True,
                    col=12,
                ),
            ),
        ]

    def create_record(self, values: dict) -> None:
        self.services.clients.create_client(ClientCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.clients.update_client(record.id, ClientUpdate(**values))

    def delete_record(self, record) -> None:
        self.services.clients.delete_client(record.id)

    def record_label(self, record) -> str:
        return record.name
