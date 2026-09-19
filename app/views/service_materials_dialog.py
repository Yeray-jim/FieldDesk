"""Dialog to manage the materials consumed by a service."""

from __future__ import annotations

import flet as ft
from pydantic import ValidationError as PydanticValidationError

from app.components.buttons import ghost_button, primary_button
from app.components.dialogs import GlassDialog, notify, open_dialog
from app.components.forms import GlassDropdown, GlassTextField
from app.components.theme import FontSize, Metrics, Palette
from app.schemas import ServiceMaterialCreate
from app.services import Services
from app.utils.exceptions import FieldDeskError


class ServiceMaterialsDialog(GlassDialog):
    """Add, update and remove the materials of a service."""

    def __init__(self, page: ft.Page, services: Services, service) -> None:
        self._page = page
        self._services = services
        self._service = service
        self._list_slot = ft.Column(
            controls=self._build_rows(),
            spacing=Metrics.SPACING_SMALL,
        )
        self._material_dropdown = GlassDropdown(
            "Material",
            self._material_options(),
            col={"sm": 12, "md": 7},
        )
        self._quantity_field = GlassTextField(
            "Cantidad",
            value="1",
            col={"sm": 12, "md": 3},
        )
        add_button = primary_button(
            "Añadir",
            icon=ft.Icons.ADD,
            on_click=self._handle_add,
        )
        add_button.col = {"sm": 12, "md": 2}

        content = ft.Container(
            width=560,
            content=ft.Column(
                controls=[
                    ft.Text(
                        f"Servicio: {service.service_type}",
                        size=FontSize.BODY,
                        weight=ft.FontWeight.W_500,
                        color=Palette.TEXT,
                    ),
                    self._list_slot,
                    ft.Divider(),
                    ft.ResponsiveRow(
                        controls=[
                            self._material_dropdown,
                            self._quantity_field,
                            add_button,
                        ],
                        spacing=Metrics.SPACING_SMALL,
                        run_spacing=Metrics.SPACING_SMALL,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                spacing=Metrics.SPACING,
                scroll=ft.ScrollMode.AUTO,
            ),
        )
        super().__init__(
            title="Materiales del servicio",
            content=content,
            actions=[
                ghost_button("Cerrar", on_click=lambda _event: page.pop_dialog())
            ],
            icon=ft.Icons.INVENTORY_2_OUTLINED,
        )

    def show(self) -> None:
        """Display the dialog."""
        open_dialog(self._page, self)

    def _material_options(self) -> list[tuple[str, str]]:
        return [
            (str(material.id), material.name)
            for material in self._services.materials.list_materials()
        ]

    def _material_names(self) -> dict[int, str]:
        return {
            material.id: material.name
            for material in self._services.materials.list_materials()
        }

    def _build_rows(self) -> list[ft.Control]:
        records = self._services.materials.list_service_materials(
            self._service.id
        )
        if not records:
            return [
                ft.Text(
                    "Este servicio no tiene materiales asignados.",
                    size=FontSize.CAPTION,
                    color=Palette.TEXT_MUTED,
                )
            ]
        names = self._material_names()
        return [self._row(record, names.get(record.material_id, "—")) for record in records]

    def _row(self, record, name: str) -> ft.Control:
        return ft.Row(
            controls=[
                ft.Text(name, size=FontSize.BODY, color=Palette.TEXT, expand=True),
                ft.Text(
                    f"{record.quantity}",
                    size=FontSize.BODY,
                    color=Palette.TEXT_MUTED,
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    tooltip="Quitar material",
                    icon_color=Palette.DANGER,
                    icon_size=20,
                    on_click=lambda _event, item=record: self._handle_remove(
                        item.material_id
                    ),
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _reload(self) -> None:
        self._list_slot.controls = self._build_rows()
        self._page.update()

    def _handle_add(self, _event: ft.ControlEvent) -> None:
        self._material_dropdown.clear_error()
        self._quantity_field.clear_error()
        try:
            data = ServiceMaterialCreate(
                service_id=self._service.id,
                material_id=self._material_dropdown.value,
                quantity=self._quantity_field.value,
            )
            self._services.materials.set_service_material(data)
        except PydanticValidationError as error:
            for item in error.errors():
                message = item.get("msg", "Valor inválido.")
                location = item.get("loc", ())
                if location and location[0] == "material_id":
                    self._material_dropdown.show_error("Selecciona un material.")
                elif location and location[0] == "quantity":
                    self._quantity_field.show_error(
                        "Introduce una cantidad válida."
                    )
                else:
                    notify(self._page, message, error=True)
            self._page.update()
            return
        except FieldDeskError as error:
            notify(self._page, str(error), error=True)
            return
        notify(self._page, "Material añadido.")
        self._reload()

    def _handle_remove(self, material_id: int) -> None:
        try:
            self._services.materials.remove_service_material(
                self._service.id, material_id
            )
        except FieldDeskError as error:
            notify(self._page, str(error), error=True)
            return
        notify(self._page, "Material eliminado.")
        self._reload()
