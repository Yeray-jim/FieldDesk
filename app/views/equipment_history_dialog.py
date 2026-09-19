"""Dialog showing the chronological technical history of an equipment."""

from __future__ import annotations

import logging

import flet as ft

from app.components.buttons import ghost_button
from app.components.cards import EmptyState
from app.components.dialogs import GlassDialog, notify, open_dialog
from app.components.theme import FontSize, Metrics, Palette
from app.services import Services
from app.utils.dates import format_datetime
from app.utils.exceptions import FieldDeskError

logger = logging.getLogger(__name__)

_KIND_ICONS: dict[str, ft.IconData] = {
    "Servicio": ft.Icons.ASSIGNMENT_OUTLINED,
    "Visita": ft.Icons.EVENT_NOTE_OUTLINED,
    "Incidencia": ft.Icons.WARNING_AMBER_OUTLINED,
    "Material": ft.Icons.INVENTORY_2_OUTLINED,
    "Evidencia": ft.Icons.PHOTO_LIBRARY_OUTLINED,
}


class EquipmentHistoryDialog(GlassDialog):
    """Displays the services, visits, incidents, materials and evidence."""

    def __init__(self, page: ft.Page, services: Services, equipment) -> None:
        self._page = page
        self._services = services
        self._equipment = equipment

        entries = self._load()
        content = ft.Container(
            width=760,
            height=560,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Servicios, visitas, incidencias, materiales y "
                        "evidencias ordenados del más reciente al más antiguo.",
                        size=FontSize.CAPTION,
                        color=Palette.TEXT_MUTED,
                    ),
                    self._timeline(entries),
                ],
                spacing=Metrics.SPACING,
                expand=True,
            ),
        )
        super().__init__(
            title=f"Historial · {equipment.name}",
            content=content,
            actions=[
                ghost_button("Cerrar", on_click=lambda _event: page.pop_dialog())
            ],
            icon=ft.Icons.HISTORY_OUTLINED,
        )

    def show(self) -> None:
        """Display the dialog."""
        open_dialog(self._page, self)

    def _load(self) -> list:
        try:
            return self._services.history.get_equipment_history(
                self._equipment.id
            )
        except FieldDeskError as error:
            notify(self._page, str(error), error=True)
            return []
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudo cargar el historial del equipo")
            notify(
                self._page,
                "No se pudo cargar el historial del equipo.",
                error=True,
            )
            return []

    def _timeline(self, entries: list) -> ft.Control:
        if not entries:
            return ft.Container(
                content=EmptyState(
                    "Sin historial",
                    "Todavía no hay eventos registrados para este equipo.",
                    icon=ft.Icons.HISTORY_OUTLINED,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )

        rows = [self._entry(entry) for entry in entries]
        return ft.Column(
            controls=rows,
            spacing=Metrics.SPACING_SMALL,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _entry(self, entry) -> ft.Control:
        icon = _KIND_ICONS.get(entry.kind, ft.Icons.CIRCLE_OUTLINED)
        details: list[ft.Control] = [
            ft.Text(
                entry.title,
                size=FontSize.BODY,
                weight=ft.FontWeight.W_500,
                color=Palette.TEXT,
            )
        ]
        if entry.detail:
            details.append(
                ft.Text(
                    entry.detail,
                    size=FontSize.CAPTION,
                    color=Palette.TEXT_MUTED,
                )
            )
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Icon(icon, size=18, color=Palette.PRIMARY),
                    width=36,
                    height=36,
                    border_radius=Metrics.RADIUS_SMALL,
                    bgcolor=ft.Colors.with_opacity(0.12, Palette.PRIMARY),
                    alignment=ft.Alignment.CENTER,
                ),
                ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    entry.kind,
                                    size=FontSize.CAPTION,
                                    weight=ft.FontWeight.W_600,
                                    color=Palette.PRIMARY,
                                ),
                                ft.Text(
                                    format_datetime(entry.date),
                                    size=FontSize.CAPTION,
                                    color=Palette.TEXT_MUTED,
                                ),
                            ],
                            spacing=Metrics.SPACING_SMALL,
                        ),
                        *details,
                    ],
                    spacing=2,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=Metrics.SPACING_SMALL,
        )
