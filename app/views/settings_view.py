"""Settings screen: application information, appearance and storage."""

from __future__ import annotations

import flet as ft

from app.components.cards import GlassCard, InfoRow, SectionHeader
from app.components.dialogs import notify
from app.components.forms import GlassDropdown
from app.components.theme import Metrics
from app.views.base_view import BaseView

_THEME_MODES: dict[str, ft.ThemeMode] = {
    "system": ft.ThemeMode.SYSTEM,
    "light": ft.ThemeMode.LIGHT,
    "dark": ft.ThemeMode.DARK,
}


class SettingsView(BaseView):
    """Configuration and information about the application."""

    title = "Ajustes"
    icon = ft.Icons.SETTINGS_OUTLINED

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                SectionHeader("Ajustes", icon=ft.Icons.SETTINGS_OUTLINED),
                self._appearance_card(),
                self._information_card(),
                self._storage_card(),
            ],
            spacing=Metrics.SPACING,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

    def _appearance_card(self) -> GlassCard:
        current = "system"
        if self.page.theme_mode is not None:
            current = str(getattr(self.page.theme_mode, "value", "system"))
        dropdown = GlassDropdown(
            "Tema de la aplicación",
            [
                ("system", "Sistema"),
                ("light", "Claro"),
                ("dark", "Oscuro"),
            ],
            value=current,
            on_select=self._on_theme_change,
        )
        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Apariencia", icon=ft.Icons.PALETTE_OUTLINED
                    ),
                    dropdown,
                ],
                spacing=Metrics.SPACING,
            )
        )

    def _information_card(self) -> GlassCard:
        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Información", icon=ft.Icons.INFO_OUTLINED
                    ),
                    InfoRow("Aplicación", self.settings.app_name),
                    InfoRow("Versión", self.settings.app_version),
                    InfoRow("Entorno", self.settings.environment),
                ],
                spacing=Metrics.SPACING_SMALL,
            )
        )

    def _storage_card(self) -> GlassCard:
        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Almacenamiento", icon=ft.Icons.FOLDER_OUTLINED
                    ),
                    InfoRow(
                        "Base de datos", str(self.settings.database_path)
                    ),
                    InfoRow("Imágenes", str(self.settings.images_dir)),
                    InfoRow("Documentos", str(self.settings.documents_dir)),
                    InfoRow("Copias de seguridad", str(self.settings.backups_dir)),
                ],
                spacing=Metrics.SPACING_SMALL,
            )
        )

    def _on_theme_change(self, event: ft.ControlEvent) -> None:
        key = event.control.value or "system"
        self.page.theme_mode = _THEME_MODES.get(key, ft.ThemeMode.SYSTEM)
        self.page.update()
        notify(self.page, "Tema actualizado.")
