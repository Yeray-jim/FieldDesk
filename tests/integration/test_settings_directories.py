"""Integration test for runtime directory creation."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from app.config.settings import Settings


@pytest.mark.integration
def test_ensure_directories_creates_expected_tree(tmp_path: Path) -> None:
    storage = tmp_path / "storage"
    settings = replace(
        Settings.from_env(),
        project_root=tmp_path,
        storage_dir=storage,
        database_path=storage / "database" / "fielddesk.db",
        images_dir=storage / "images",
        documents_dir=storage / "documents",
        backups_dir=storage / "backups",
        logs_dir=storage / "logs",
    )

    settings.ensure_directories()

    for directory in (
        storage,
        storage / "database",
        storage / "images",
        storage / "documents",
        storage / "backups",
        storage / "logs",
    ):
        assert directory.is_dir()


@pytest.mark.integration
def test_project_root_contains_expected_layout() -> None:
    settings = Settings.from_env()

    assert (settings.project_root / "app" / "main.py").is_file()
    assert (settings.project_root / "requirements.txt").is_file()
