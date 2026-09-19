"""FieldDesk application entry point.

Bootstraps logging, guarantees runtime directories exist, applies pending
database migrations and launches the responsive Flet interface.
"""

from __future__ import annotations

import logging

import flet as ft

from app.config import configure_logging, settings
from app.database import Database
from app.database.migrations import run_migrations
from app.services import Services
from app.utils import i18n
from app.utils.constants import (
    DEFAULT_WINDOW_HEIGHT,
    DEFAULT_WINDOW_MIN_HEIGHT,
    DEFAULT_WINDOW_MIN_WIDTH,
    DEFAULT_WINDOW_WIDTH,
)
from app.views.app_shell import AppShell
from app.views.context import AppContext

logger = logging.getLogger(__name__)


def _configure_window(page: ft.Page) -> None:
    """Apply the default desktop window configuration."""
    page.title = f"{settings.app_name} {settings.app_version}"
    page.window.width = DEFAULT_WINDOW_WIDTH
    page.window.height = DEFAULT_WINDOW_HEIGHT
    page.window.min_width = DEFAULT_WINDOW_MIN_WIDTH
    page.window.min_height = DEFAULT_WINDOW_MIN_HEIGHT


def build_app(page: ft.Page, database: Database) -> None:
    """Build the application on the given Flet page."""
    _configure_window(page)
    services = Services(database, settings)
    # FilePicker is a page-level service; creating it in the page handler
    # registers it with the page service registry automatically.
    file_picker = ft.FilePicker()
    url_launcher = ft.UrlLauncher()
    context = AppContext(
        page=page,
        settings=settings,
        services=services,
        file_picker=file_picker,
        url_launcher=url_launcher,
    )
    AppShell(context).render()


def run() -> None:
    """Configure the application and start the Flet runtime."""
    configure_logging(settings)
    settings.ensure_directories()
    i18n.set_language(
        i18n.load_language(settings.storage_dir / "preferences.json")
    )
    run_migrations(settings)

    database = Database(settings.database_url, echo=settings.debug)
    logger.info(
        "Starting %s %s (%s)",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )
    try:
        ft.run(
            lambda page: build_app(page, database),
            assets_dir=str(settings.project_root / "assets"),
        )
    finally:
        database.dispose()


if __name__ == "__main__":
    run()
