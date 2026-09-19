"""SQLite connection management.

The :class:`Database` object owns the SQLAlchemy engine and session factory.
Higher layers obtain sessions through :meth:`Database.session`, which commits
on success, rolls back on error and always closes the session.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import Settings
from app.database.base import Base

SQLITE_PREFIX = "sqlite"


def _enable_sqlite_foreign_keys(dbapi_connection: object, _record: object) -> None:
    """Enable ``PRAGMA foreign_keys`` for every SQLite connection.

    SQLite enforces foreign key constraints only when this pragma is enabled
    on the connection; without it, referential integrity silently disappears.
    """
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_engine(database_url: str, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine configured for FieldDesk.

    Args:
        database_url: SQLAlchemy database URL.
        echo: When ``True``, SQL statements are logged to stdout.

    Returns:
        A ready-to-use engine.
    """
    connect_args = (
        {"check_same_thread": False}
        if database_url.startswith(SQLITE_PREFIX)
        else {}
    )
    engine = create_engine(
        database_url,
        echo=echo,
        connect_args=connect_args,
        future=True,
    )
    if database_url.startswith(SQLITE_PREFIX):
        event.listens_for(engine, "connect")(_enable_sqlite_foreign_keys)
    return engine


class Database:
    """Owns the SQLAlchemy engine and exposes transactional sessions."""

    def __init__(self, database_url: str, *, echo: bool = False) -> None:
        self._engine = create_db_engine(database_url, echo=echo)
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> Engine:
        """The underlying SQLAlchemy engine."""
        return self._engine

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Provide a transactional session.

        The session is committed when the block exits successfully, rolled
        back when an exception is raised, and always closed.
        """
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def create_all(self) -> None:
        """Create every table defined in the ORM metadata."""
        from app.database import models  # noqa: F401  (register models)

        Base.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        """Drop every table defined in the ORM metadata."""
        from app.database import models  # noqa: F401  (register models)

        Base.metadata.drop_all(self._engine)

    def dispose(self) -> None:
        """Dispose the engine and its connection pool."""
        self._engine.dispose()


def create_database(settings: Settings) -> Database:
    """Build the application :class:`Database` from settings."""
    return Database(settings.database_url, echo=settings.debug)
