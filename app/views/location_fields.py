"""Reusable form fields for locations.

They are shared by the locations screen and by the quick "new location"
dialog used when creating equipment, so the address is always captured with
the same fields.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.dialogs import open_dialog
from app.components.forms import FormDialog, FormField, GlassDropdown, GlassTextField
from app.schemas import LocationCreate
from app.services import Services

FULL = 12
HALF = {"sm": 12, "md": 6}


def build_location_fields(record, client_options: list[tuple[str, str]]) -> list[FormField]:
    """Return the form fields that describe a location.

    Args:
        record: Existing location to prefill, or ``None`` when creating.
        client_options: ``(id, name)`` pairs of the available clients.
    """
    return [
        FormField(
            "client_id",
            GlassDropdown(
                "Cliente",
                client_options,
                required=True,
                value=str(record.client_id) if record else None,
                col=FULL,
            ),
            required=True,
        ),
        FormField(
            "name",
            GlassTextField(
                "Nombre de la ubicación",
                required=True,
                hint="Sucursal Centro, Almacén...",
                value=record.name if record else None,
                col=FULL,
            ),
            required=True,
        ),
        FormField(
            "state",
            GlassTextField(
                "Estado",
                hint="Nombre del estado",
                value=record.state if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "municipality",
            GlassTextField(
                "Municipio",
                value=record.municipality if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "neighborhood",
            GlassTextField(
                "Colonia / Fraccionamiento",
                value=record.neighborhood if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "street",
            GlassTextField(
                "Calle y número",
                value=record.street if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "lot",
            GlassTextField(
                "Lote",
                value=record.lot if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "block",
            GlassTextField(
                "Manzana",
                value=record.block if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "reference",
            GlassTextField(
                "Referencias",
                hint="Entre calles, portón, color...",
                value=record.reference if record else None,
                col=FULL,
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


def open_location_form(
    page: ft.Page,
    services: Services,
    client_options: list[tuple[str, str]],
    on_created: Callable[[object], None],
) -> None:
    """Open a dialog to create a location and notify the caller on success."""

    def submit(values: dict) -> str:
        location = services.locations.create_location(LocationCreate(**values))
        on_created(location)
        return "Ubicación creada."

    dialog = FormDialog(
        page,
        title="Nueva ubicación",
        fields=build_location_fields(None, client_options),
        on_submit=submit,
        icon=ft.Icons.ADD_LOCATION_ALT_OUTLINED,
    )
    open_dialog(page, dialog)
