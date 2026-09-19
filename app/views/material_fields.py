"""Reusable form fields for materials.

Shared by the materials screen and by the quick "new material" dialog used
when selecting materials inside a service.
"""

from __future__ import annotations

from collections.abc import Callable

import flet as ft

from app.components.dialogs import open_dialog
from app.components.forms import FormDialog, FormField, GlassTextField
from app.schemas import MaterialCreate
from app.services import Services

FULL = 12
HALF = {"sm": 12, "md": 6}


def build_material_fields(record) -> list[FormField]:
    """Return the form fields that describe a catalog material."""
    return [
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
            "unit",
            GlassTextField(
                "Unidad",
                hint="ud, m, L...",
                value=record.unit if record else None,
                col=HALF,
            ),
        ),
        FormField(
            "stock",
            GlassTextField(
                "Existencias",
                value=str(record.stock) if record else "0",
                keyboard_type=ft.KeyboardType.NUMBER,
                col=HALF,
            ),
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
    ]


def open_material_form(
    page: ft.Page,
    services: Services,
    on_created: Callable[[object], None],
) -> None:
    """Open a dialog to create a material and notify the caller on success."""

    def submit(values: dict) -> str:
        material = services.materials.create_material(MaterialCreate(**values))
        on_created(material)
        return "Material creado."

    dialog = FormDialog(
        page,
        title="Nuevo material",
        fields=build_material_fields(None),
        on_submit=submit,
        icon=ft.Icons.INVENTORY_2_OUTLINED,
    )
    open_dialog(page, dialog)
