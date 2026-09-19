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
    """Apply all pending migrations to the configured database.

    When the application is packaged (for example an Android APK) the Alembic
    configuration may not be bundled, so the schema is created directly from
    the ORM metadata instead.
    """
    config_path = settings.project_root / "alembic.ini"
    if not config_path.is_file():
        logger.info("Alembic config not found; creating the schema directly")
        from app.database import models  # noqa: F401  (register models)
        from app.database.base import Base
        from app.database.connection import create_db_engine

        engine = create_db_engine(settings.database_url)
        Base.metadata.create_all(engine)
        engine.dispose()
        return

    config = Config(str(config_path))
    config.set_main_option(
        "script_location", str(settings.project_root / "migrations")
    )
    config.set_main_option("sqlalchemy.url", settings.database_url)
    config.attributes["database_url"] = settings.database_url
    config.attributes["configure_logger"] = False

    logger.info("Applying database migrations")
    command.upgrade(config, "head")
