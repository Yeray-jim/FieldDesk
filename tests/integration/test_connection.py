"""Integration tests for the SQLite connection layer."""

from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import func, select

from app.database import Database
from app.database.connection import create_db_engine
from app.database.models import Client


@pytest.mark.integration
def test_sqlite_foreign_keys_are_enabled(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'x.db'}")
    try:
        with engine.connect() as connection:
            value = connection.exec_driver_sql("PRAGMA foreign_keys").scalar()
        assert value == 1
    finally:
        engine.dispose()


@pytest.mark.integration
def test_session_commits_on_success(database: Database) -> None:
    with database.session() as session:
        session.add(Client(name="Commit"))

    with database.session() as session:
        total = session.scalar(select(func.count()).select_from(Client))
    assert total == 1


@pytest.mark.integration
def test_session_rolls_back_on_error(database: Database) -> None:
    with pytest.raises(RuntimeError):
        with database.session() as session:
            session.add(Client(name="Rollback"))
            session.flush()
            raise RuntimeError("boom")

    with database.session() as session:
        total = session.scalar(select(func.count()).select_from(Client))
    assert total == 0
