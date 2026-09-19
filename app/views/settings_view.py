"""Settings screen: application information, appearance, storage and backup."""

from __future__ import annotations

import logging

import flet as ft

from app.components.buttons import primary_button, secondary_button
from app.components.cards import GlassCard, InfoRow, SectionHeader
from app.components.dialogs import confirm_dialog, notify
from app.components.forms import GlassDropdown
from app.components.theme import FontSize, Metrics, Palette
from app.utils.exceptions import FieldDeskError
from app.views.base_view import BaseView

logger = logging.getLogger(__name__)

_THEME_MODES: dict[str, ft.ThemeMode] = {
    "system": ft.ThemeMode.SYSTEM,
    "light": ft.ThemeMode.LIGHT,
    "dark": ft.ThemeMode.DARK,
}


class SettingsView(BaseView):
    """Configuration, backup and information about the application."""

    title = "Ajustes"
    icon = ft.Icons.SETTINGS_OUTLINED

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                SectionHeader("Ajustes", icon=ft.Icons.SETTINGS_OUTLINED),
                self._appearance_card(),
                self._backup_card(),
                self._export_card(),
                self._demo_card(),
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

    def _backup_card(self) -> GlassCard:
        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Copias de seguridad", icon=ft.Icons.BACKUP_OUTLINED
                    ),
                    ft.Text(
                        "Guarda la base de datos, las imágenes y los "
                        "documentos en un archivo ZIP, o restaura una copia "
                        "anterior. Antes de restaurar se crea "
                        "automáticamente una copia de seguridad.",
                        size=FontSize.CAPTION,
                        color=Palette.TEXT_MUTED,
                    ),
                    ft.Row(
                        controls=[
                            primary_button(
                                "Crear copia",
                                icon=ft.Icons.SAVE_ALT_OUTLINED,
                                on_click=self._handle_backup,
                            ),
                            secondary_button(
                                "Restaurar copia",
                                icon=ft.Icons.RESTORE_OUTLINED,
                                on_click=self._handle_restore,
                            ),
                        ],
                        spacing=Metrics.SPACING_SMALL,
                        wrap=True,
                    ),
                ],
                spacing=Metrics.SPACING,
            )
        )

    def _export_card(self) -> GlassCard:
        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Exportación", icon=ft.Icons.TABLE_VIEW_OUTLINED
                    ),
                    ft.Text(
                        "Exporta clientes, equipos, servicios, incidencias y "
                        "materiales a archivos CSV compatibles con Excel y "
                        "LibreOffice.",
                        size=FontSize.CAPTION,
                        color=Palette.TEXT_MUTED,
                    ),
                    secondary_button(
                        "Exportar a CSV",
                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                        on_click=self._handle_export,
                    ),
                ],
                spacing=Metrics.SPACING,
            )
        )

    def _demo_card(self) -> GlassCard:
        return GlassCard(
            content=ft.Column(
                controls=[
                    SectionHeader(
                        "Datos de demostración",
                        icon=ft.Icons.AUTO_AWESOME_OUTLINED,
                    ),
                    ft.Text(
                        "Carga clientes, ubicaciones, equipos, servicios e "
                        "incidencias de ejemplo. Solo está disponible si la "
                        "base de datos está vacía.",
                        size=FontSize.CAPTION,
                        color=Palette.TEXT_MUTED,
                    ),
                    secondary_button(
                        "Cargar datos de demostración",
                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                        on_click=self._handle_demo,
                    ),
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
                    InfoRow(
                        "Copias de seguridad", str(self.settings.backups_dir)
                    ),
                ],
                spacing=Metrics.SPACING_SMALL,
            )
        )

    # ------------------------------------------------------------------
    # Handlers
    # ------------------------------------------------------------------
    def _on_theme_change(self, event: ft.ControlEvent) -> None:
        key = event.control.value or "system"
        self.page.theme_mode = _THEME_MODES.get(key, ft.ThemeMode.SYSTEM)
        self.page.update()
        notify(self.page, "Tema actualizado.")

    def _handle_backup(self, _event: ft.ControlEvent) -> None:
        try:
            path = self.services.backups.create_backup()
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudo crear la copia de seguridad")
            notify(
                self.page,
                "No se pudo crear la copia de seguridad.",
                error=True,
            )
            return
        notify(self.page, f"Copia creada: {path.name}")

    def _handle_restore(self, _event: ft.ControlEvent) -> None:
        if self.context.file_picker is None:
            notify(
                self.page,
                "La selección de archivos no está disponible.",
                error=True,
            )
            return
        self.page.run_task(self._pick_backup)

    async def _pick_backup(self) -> None:
        files = await self.context.file_picker.pick_files(
            dialog_title="Seleccionar copia de seguridad",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["zip"],
            allow_multiple=False,
        )
        if not files:
            return
        source = getattr(files[0], "path", None)
        if not source:
            return

        try:
            manifest = self.services.backups.validate_backup(source)
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return

        confirm_dialog(
            self.page,
            title="¿Restaurar copia de seguridad?",
            message=(
                "Se reemplazarán todos los datos actuales por los de la copia "
                f"del {manifest.created_at}. Se creará automáticamente una "
                "copia de seguridad de los datos actuales antes de continuar."
            ),
            confirm_label="Restaurar",
            on_confirm=lambda: self._restore(source),
        )

    def _handle_export(self, _event: ft.ControlEvent) -> None:
        try:
            paths = self.services.exports.export_all()
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudieron exportar los datos")
            notify(
                self.page,
                "No se pudieron exportar los datos a CSV.",
                error=True,
            )
            return
        notify(
            self.page,
            f"Se exportaron {len(paths)} archivos CSV a "
            f"{self.settings.documents_dir}.",
        )

    def _handle_demo(self, _event: ft.ControlEvent) -> None:
        confirm_dialog(
            self.page,
            title="¿Cargar datos de demostración?",
            message=(
                "Se añadirán datos de ejemplo para la presentación. Esta "
                "opción solo funciona en una base de datos vacía."
            ),
            confirm_label="Cargar",
            danger=False,
            on_confirm=self._load_demo,
        )

    def _load_demo(self) -> None:
        try:
            summary = self.services.demo.load()
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudieron cargar los datos de demostración")
            notify(
                self.page,
                "No se pudieron cargar los datos de demostración.",
                error=True,
            )
            return
        notify(
            self.page,
            "Datos cargados: "
            f"{summary.clients} clientes, {summary.equipment} equipos, "
            f"{summary.services} servicios.",
        )
        self.page.update()

    def _restore(self, source: str) -> None:
        try:
            self.services.backups.restore_backup(source)
        except FieldDeskError as error:
            notify(self.page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudo restaurar la copia de seguridad")
            notify(
                self.page,
                "No se pudo restaurar la copia de seguridad.",
                error=True,
            )
            return
        notify(self.page, "Copia restaurada correctamente.")
        self.page.update()
