"""Dialog to manage the evidence images attached to a service."""

from __future__ import annotations

import logging

import flet as ft

from app.components.buttons import ghost_button, icon_action_button, primary_button
from app.components.cards import EmptyState
from app.components.dialogs import (
    GlassDialog,
    confirm_dialog,
    notify,
    open_dialog,
)
from app.components.gallery import ImagePreviewDialog, image_thumbnail
from app.components.theme import FontSize, Metrics, Palette, glass_border
from app.schemas import EvidenceCreate
from app.services import Services
from app.utils.exceptions import FieldDeskError

logger = logging.getLogger(__name__)


class ServiceEvidenceDialog(GlassDialog):
    """Add, preview and delete the evidence of a service."""

    def __init__(
        self,
        page: ft.Page,
        services: Services,
        service,
        file_picker: ft.FilePicker | None = None,
    ) -> None:
        self._page = page
        self._services = services
        self._service = service
        self._file_picker = file_picker
        self._count_text = ft.Text(
            self._count_label(),
            size=FontSize.CAPTION,
            color=Palette.TEXT_MUTED,
        )
        self._gallery_slot = ft.Container(
            content=self._build_gallery(),
            expand=True,
        )
        add_button = primary_button(
            "Añadir imágenes",
            icon=ft.Icons.ADD_A_PHOTO_OUTLINED,
            on_click=self._handle_add,
        )
        header = ft.Row(
            controls=[
                self._count_text,
                ft.Container(expand=True),
                add_button,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )
        content = ft.Container(
            width=820,
            height=560,
            content=ft.Column(
                controls=[header, self._gallery_slot],
                spacing=Metrics.SPACING,
                expand=True,
            ),
        )
        super().__init__(
            title=f"Evidencias · {service.service_type}",
            content=content,
            actions=[
                ghost_button("Cerrar", on_click=lambda _event: page.pop_dialog())
            ],
            icon=ft.Icons.PHOTO_LIBRARY_OUTLINED,
        )

    def show(self) -> None:
        """Display the dialog."""
        open_dialog(self._page, self)

    def _count_label(self) -> str:
        total = self._services.evidence.count_evidence_by_service(
            self._service.id
        )
        if total == 0:
            return "Sin evidencias"
        return f"{total} evidencia{'s' if total != 1 else ''}"

    def _build_gallery(self) -> ft.Control:
        records = self._services.evidence.list_evidence_by_service(
            self._service.id
        )
        if not records:
            return ft.Container(
                content=EmptyState(
                    "Sin evidencias",
                    "Añade la primera imagen del servicio realizado.",
                    icon=ft.Icons.IMAGE_OUTLINED,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
            )
        return ft.GridView(
            controls=[self._item(record) for record in records],
            max_extent=190,
            spacing=Metrics.SPACING_SMALL,
            run_spacing=Metrics.SPACING_SMALL,
            child_aspect_ratio=0.9,
            expand=True,
        )

    def _item(self, evidence) -> ft.Control:
        path = self._services.evidence.absolute_path(evidence)
        name = evidence.filename
        if len(name) > 20:
            name = f"{name[:17]}..."
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Container(
                        content=image_thumbnail(path),
                        expand=True,
                        border_radius=Metrics.RADIUS_SMALL,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                        on_click=lambda _event, item=evidence: self._preview(
                            item
                        ),
                        tooltip="Ver imagen",
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                name,
                                size=FontSize.CAPTION,
                                color=Palette.TEXT_MUTED,
                                expand=True,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            icon_action_button(
                                ft.Icons.DELETE_OUTLINE,
                                "Eliminar",
                                on_click=lambda _event, item=evidence: (
                                    self._confirm_delete(item)
                                ),
                                color=Palette.DANGER,
                            ),
                        ],
                        spacing=0,
                    ),
                ],
                spacing=4,
                expand=True,
            ),
            padding=6,
            bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.WHITE),
            border=glass_border(),
            border_radius=Metrics.RADIUS,
        )

    def _reload(self) -> None:
        self._count_text.value = self._count_label()
        self._gallery_slot.content = self._build_gallery()
        self._page.update()

    def _preview(self, evidence) -> None:
        ImagePreviewDialog(
            self._page,
            self._services.evidence.absolute_path(evidence),
            title=evidence.filename,
            description=evidence.description,
        ).show()

    def _confirm_delete(self, evidence) -> None:
        confirm_dialog(
            self._page,
            title="¿Eliminar evidencia?",
            message=(
                f"«{evidence.filename}» se eliminará permanentemente. "
                "Esta acción no puede deshacerse."
            ),
            on_confirm=lambda: self._delete(evidence),
        )

    def _delete(self, evidence) -> None:
        try:
            self._services.evidence.delete_evidence(evidence.id)
        except FieldDeskError as error:
            notify(self._page, str(error), error=True)
            return
        except Exception:  # noqa: BLE001 - never leak a traceback
            logger.exception("No se pudo eliminar la evidencia")
            notify(
                self._page,
                "No se pudo eliminar la evidencia. Inténtalo nuevamente.",
                error=True,
            )
            return
        notify(self._page, "Evidencia eliminada.")
        self._reload()

    def _handle_add(self, _event: ft.ControlEvent) -> None:
        if self._file_picker is None:
            notify(
                self._page,
                "La selección de archivos no está disponible.",
                error=True,
            )
            return
        self._page.run_task(self._pick_images)

    async def _pick_images(self) -> None:
        files = await self._file_picker.pick_files(
            dialog_title="Seleccionar imágenes",
            file_type=ft.FilePickerFileType.IMAGE,
            allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp", "webp"],
            allow_multiple=True,
        )
        if not files:
            return

        added = 0
        for file in files:
            source = getattr(file, "path", None)
            if not source:
                continue
            try:
                self._services.evidence.add_evidence(
                    EvidenceCreate(service_id=self._service.id),
                    source,
                )
                added += 1
            except FieldDeskError as error:
                notify(self._page, str(error), error=True)
            except Exception:  # noqa: BLE001 - protective boundary
                logger.exception("No se pudo añadir una evidencia")
                notify(
                    self._page,
                    "No se pudo añadir una de las imágenes.",
                    error=True,
                )

        if added:
            notify(
                self._page,
                f"{added} imagen{'es' if added != 1 else ''} añadida"
                f"{'s' if added != 1 else ''}.",
            )
        self._reload()
