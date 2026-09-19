"""Logging configuration for FieldDesk.

The application never relies on :func:`print` for diagnostics. Instead, a
single call to :func:`configure_logging` wires the root logger with a console
handler and a rotating file handler so that errors can be audited later.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.config.settings import Settings

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_MAX_BYTES = 1_000_000
_BACKUP_COUNT = 5


def configure_logging(settings: Settings) -> None:
    """Configure the root logger.

    Args:
        settings: Application settings providing the log level and log
            directory.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    formatter = logging.Formatter(_LOG_FORMAT)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        settings.logs_dir / "fielddesk.log",
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
