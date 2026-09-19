"""FieldDesk application entry point.

This module bootstraps the application: it configures logging, guarantees that
runtime directories exist and launches the Flet user interface. Functional
screens are added in later development phases; for now the entry point renders
a minimal placeholder view so the project can be executed and verified.
"""

from __future__ import annotations

import logging

import flet as ft

from app.config import configure_logging, settings
from app.utils.constants import (
    APP_TAGLINE,
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_MIN_HEIGHT,
    DEFAULT_WINDOW_MIN_WIDTH,
    DEFAULT_WINDOW_WIDTH,
)

logger = logging.getLogger(__name__)


def _configure_window(page: ft.Page) -> None:
    """Apply the default window configuration for desktop platforms."""
    page.title = f"{settings.app_name} {settings.app_version}"
    page.window.width = DEFAULT_WINDOW_WIDTH
    page.window.height = DEFAULT_WINDOW_HEIGHT
    page.window.min_width = DEFAULT_WINDOW_MIN_WIDTH
    page.window.min_height = DEFAULT_WINDOW_MIN_HEIGHT


def _build_placeholder() -> ft.Control:
    """Build the temporary welcome view shown during early development."""
    return ft.Container(
        expand=True,
        alignment=ft.Alignment.CENTER,
        padding=40,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Icon(ft.Icons.HANDYMAN_OUTLINED, size=64),
                ft.Text(
                    settings.app_name,
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(APP_TAGLINE, size=16),
                ft.Text(
                    f"Versión {settings.app_version} — Fase 1 (Arquitectura)",
                    size=12,
                    italic=True,
                ),
            ],
        ),
    )


def main(page: ft.Page) -> None:
    """Render the application on the given page.

    Args:
        page: Flet page provided by the runtime.
    """
    _configure_window(page)
    page.add(_build_placeholder())
    logger.info("FieldDesk interface ready on platform %s", page.platform)


def run() -> None:
    """Configure the application and start the Flet runtime."""
    configure_logging(settings)
    settings.ensure_directories()
    logger.info(
        "Starting %s %s (%s)",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    ft.run(main, assets_dir=str(settings.project_root / "assets"))


if __name__ == "__main__":
    run()
