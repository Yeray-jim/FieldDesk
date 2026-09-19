"""Materials screen with full CRUD integration."""

from __future__ import annotations

import flet as ft

from app.components.tables import text_cell
from app.schemas import MaterialUpdate
from app.views.crud_view import CrudView
from app.views.material_fields import build_material_fields


class MaterialsView(CrudView):
    """List, create, edit and delete catalog materials."""

    title = "Materiales"
    singular = "material"
    icon = ft.Icons.INVENTORY_2_OUTLINED
    add_label = "Nuevo material"
    search_hint = "Buscar por nombre o descripción"
    empty_title = "Sin materiales"
    empty_message = "Crea el primer material del catálogo."

    def load_records(self) -> list:
        return self.services.materials.list_materials()

    def searchable_text(self, record) -> str:
        return " ".join(filter(None, [record.name, record.description]))

    def columns(self) -> list[str]:
        return ["Nombre", "Unidad", "Existencias", "Descripción"]

    def render_row(self, record) -> list[ft.Control]:
        description = (record.description or "—").strip()
        if len(description) > 60:
            description = f"{description[:57]}..."
        stock = record.stock if record.stock is not None else 0
        return [
            text_cell(record.name),
            text_cell(record.unit or "—", muted=True),
            text_cell(f"{stock}", muted=True),
            text_cell(description, muted=True),
        ]

    def build_fields(self, record) -> list:
        return build_material_fields(record)

    def create_record(self, values: dict) -> None:
        from app.schemas import MaterialCreate

        self.services.materials.create_material(MaterialCreate(**values))

    def update_record(self, record, values: dict) -> None:
        self.services.materials.update_material(
            record.id, MaterialUpdate(**values)
        )

    def delete_record(self, record) -> None:
        self.services.materials.delete_material(record.id)

    def record_label(self, record) -> str:
        return record.name
