"""Programmatic Alembic migration runner.

The application applies pending migrations on startup so the SQLite schema is
always up to date without requiring a manual command from the technician.
"""

from __future__ import annotations

import logging

from alembic import command
from alembic.config import Config

from app.config.settings import Settings

logger = logging.getLogger(__name__)


def run_migrations(settings: Settings) -> None:
    """Apply all pending migrations to the configured database."""
    config = Config(str(settings.project_root / "alembic.ini"))
    config.set_main_option(
        "script_location", str(settings.project_root / "migrations")
    )
    config.set_main_option("sqlalchemy.url", settings.database_url)
    config.attributes["database_url"] = settings.database_url
    config.attributes["configure_logger"] = False

    logger.info("Applying database migrations")
    command.upgrade(config, "head")
