"""Unit tests for the centralized application settings."""

from __future__ import annotations

import pytest

from app.config.settings import Settings


@pytest.mark.unit
def test_metadata_defaults() -> None:
    settings = Settings.from_env()

    assert settings.app_name == "FieldDesk"
    assert settings.app_version == "0.1.0"


@pytest.mark.unit
def test_storage_paths_are_derived_from_storage_dir() -> None:
    settings = Settings.from_env()

    assert settings.images_dir == settings.storage_dir / "images"
    assert settings.documents_dir == settings.storage_dir / "documents"
    assert settings.backups_dir == settings.storage_dir / "backups"
    assert settings.logs_dir == settings.storage_dir / "logs"


@pytest.mark.unit
def test_database_configuration() -> None:
    settings = Settings.from_env()

    assert settings.database_path.name == "fielddesk.db"
    assert settings.database_path.parent == settings.storage_dir / "database"
    assert settings.database_url == f"sqlite:///{settings.database_path}"
