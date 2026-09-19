"""Integration tests for application bootstrap and migrations."""

from __future__ import annotations

import sqlite3
from dataclasses import replace
from pathlib import Path

import pytest

from app.config.settings import Settings
from app.database import Database
from app.database.migrations import run_migrations
from app.main import build_app

from tests.conftest import FakePage


@pytest.mark.integration
def test_build_app_mounts_the_shell(
    database: Database,
    settings: Settings,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("app.main.settings", settings)
    page = FakePage()

    build_app(page, database)

    assert page.added, "la shell debe montarse en la página"
    assert page.title == f"{settings.app_name} {settings.app_version}"


@pytest.mark.integration
def test_run_migrations_creates_the_schema(tmp_path: Path) -> None:
    base = Settings.from_env()
    storage = tmp_path / "storage"
    target = replace(
        base,
        storage_dir=storage,
        database_path=storage / "database" / "fielddesk.db",
    )
    target.ensure_directories()

    run_migrations(target)

    connection = sqlite3.connect(target.database_path)
    try:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
    finally:
        connection.close()
    assert {"client", "service", "equipment", "alembic_version"}.issubset(
        tables
    )
