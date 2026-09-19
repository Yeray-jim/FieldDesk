"""Centralized configuration for FieldDesk.

Every filesystem path used by the application is derived from a single
:class:`Settings` instance so that no module hard-codes locations. Values can
be overridden through environment variables, which keeps the application easy
to run in development, testing or portable deployments.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

APP_NAME = "FieldDesk"
APP_VERSION = "0.4.0"

_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean value from an environment variable."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable runtime configuration for FieldDesk.

    Attributes:
        app_name: Human readable application name.
        app_version: Semantic version of the application.
        environment: Execution environment (development, testing, production).
        debug: Whether debug behaviour (such as verbose errors) is enabled.
        log_level: Minimum level handled by the logging subsystem.
        project_root: Absolute path to the project root directory.
        storage_dir: Base directory for all user generated content.
        database_path: Absolute path to the SQLite database file.
        images_dir: Directory that stores evidence images.
        documents_dir: Directory that stores generated documents.
        backups_dir: Directory where backup archives are written.
        logs_dir: Directory that stores log files.
    """

    app_name: str
    app_version: str
    environment: str
    debug: bool
    log_level: str
    project_root: Path
    storage_dir: Path
    database_path: Path
    images_dir: Path
    documents_dir: Path
    backups_dir: Path
    logs_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        """Build a :class:`Settings` instance from environment variables.

        Returns:
            A settings object using environment overrides when present and
            sensible defaults derived from the project root otherwise.
        """
        project_root = (
            Path(os.getenv("FIELDDESK_PROJECT_ROOT", _PROJECT_ROOT))
            .expanduser()
            .resolve()
        )
        # On mobile/packaged builds the project folder is read-only; Flet
        # exposes a writable per-app directory through this variable.
        default_storage = os.getenv("FLET_APP_STORAGE_DATA") or (
            project_root / "storage"
        )
        storage_dir = (
            Path(os.getenv("FIELDDESK_STORAGE_DIR", default_storage))
            .expanduser()
            .resolve()
        )
        database_path = (
            Path(
                os.getenv(
                    "FIELDDESK_DATABASE_PATH",
                    storage_dir / "database" / "fielddesk.db",
                )
            )
            .expanduser()
            .resolve()
        )
        return cls(
            app_name=os.getenv("FIELDDESK_APP_NAME", APP_NAME),
            app_version=APP_VERSION,
            environment=os.getenv("FIELDDESK_ENVIRONMENT", "development"),
            debug=_env_bool("FIELDDESK_DEBUG", False),
            log_level=os.getenv("FIELDDESK_LOG_LEVEL", "INFO").upper(),
            project_root=project_root,
            storage_dir=storage_dir,
            database_path=database_path,
            images_dir=Path(
                os.getenv("FIELDDESK_IMAGES_DIR", storage_dir / "images")
            )
            .expanduser()
            .resolve(),
            documents_dir=Path(
                os.getenv("FIELDDESK_DOCUMENTS_DIR", storage_dir / "documents")
            )
            .expanduser()
            .resolve(),
            backups_dir=Path(
                os.getenv("FIELDDESK_BACKUPS_DIR", storage_dir / "backups")
            )
            .expanduser()
            .resolve(),
            logs_dir=Path(os.getenv("FIELDDESK_LOGS_DIR", storage_dir / "logs"))
            .expanduser()
            .resolve(),
        )

    @property
    def database_url(self) -> str:
        """SQLAlchemy database URL for the configured SQLite database."""
        return f"sqlite:///{self.database_path}"

    def ensure_directories(self) -> None:
        """Create every directory required at runtime if it is missing."""
        for directory in (
            self.storage_dir,
            self.database_path.parent,
            self.images_dir,
            self.documents_dir,
            self.backups_dir,
            self.logs_dir,
        ):
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings.from_env()
