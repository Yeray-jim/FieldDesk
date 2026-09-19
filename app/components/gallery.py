"""Image gallery helpers for evidence visualisation."""

from __future__ import annotations

from pathlib import Path

import flet as ft

from app.components.buttons import ghost_button
from app.components.cards import EmptyState
from app.components.dialogs import GlassDialog, open_dialog
from app.components.theme import FontSize, Metrics, Palette
from app.utils.files import make_thumbnail, read_image_bytes


def image_thumbnail(
    path: Path,
    size: tuple[int, int] = (320, 320),
) -> ft.Control:
    """Return a thumbnail control for an image, or a fallback icon."""
    data = make_thumbnail(path, size)
    if data is None:
        return ft.Container(
            content=ft.Icon(
                ft.Icons.BROKEN_IMAGE_OUTLINED,
                color=Palette.TEXT_MUTED,
                size=28,
            ),
            alignment=ft.Alignment.CENTER,
            bgcolor=ft.Colors.with_opacity(0.06, Palette.TEXT),
        )
    return ft.Image(src=data, fit=ft.BoxFit.COVER)


class ImagePreviewDialog(GlassDialog):
    """Full-size preview of an evidence image."""

    def __init__(
        self,
        page: ft.Page,
        image_path: Path,
        *,
        title: str,
        description: str | None = None,
    ) -> None:
        self._page = page
        data = read_image_bytes(image_path)
        if data is not None:
            body: ft.Control = ft.Container(
                content=ft.Image(src=data, fit=ft.BoxFit.CONTAIN),
                width=760,
                height=520,
                alignment=ft.Alignment.CENTER,
            )
        else:
            body = ft.Container(
                content=EmptyState(
                    "Imagen no disponible",
                    "No se pudo leer el archivo almacenado.",
                    icon=ft.Icons.BROKEN_IMAGE_OUTLINED,
                ),
                width=480,
                height=280,
                alignment=ft.Alignment.CENTER,
            )

        controls: list[ft.Control] = [body]
        if description:
            controls.append(
                ft.Text(
                    description,
                    size=FontSize.BODY,
                    color=Palette.TEXT_MUTED,
                )
            )

        super().__init__(
            title=title,
            content=ft.Column(
                controls=controls,
                spacing=Metrics.SPACING_SMALL,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            actions=[
                ghost_button("Cerrar", on_click=lambda _event: page.pop_dialog())
            ],
            icon=ft.Icons.IMAGE_OUTLINED,
        )

    def show(self) -> None:
        """Display the preview dialog."""
        open_dialog(self._page, self)
