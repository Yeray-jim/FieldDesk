"""Application configuration package.

Exposes the shared :data:`settings` instance and the logging bootstrap so the
rest of the application can depend on a single configuration entry point.
"""

from app.config.logging_config import configure_logging
from app.config.settings import Settings, settings

__all__ = ["Settings", "settings", "configure_logging"]
