"""Generic data access base shared by every repository.

Repositories are the only place that talks to SQLAlchemy. They receive an
already open :class:`~sqlalchemy.orm.Session` and never commit: transaction
boundaries belong to the caller (usually :meth:`Database.session`). Write
operations ``flush`` so that generated primary keys and integrity errors
surface immediately inside the transaction.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)


def contains_pattern(term: str) -> str:
    """Build a SQL ``LIKE`` pattern for a case-insensitive contains match."""
    return f"%{term.strip()}%"


class BaseRepository(Generic[ModelT]):
    """Common CRUD operations for a single ORM model.

    Subclasses must declare the ``model`` class attribute.
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        """The session this repository operates on."""
        return self._session

    def get(self, primary_key: object) -> ModelT | None:
        """Return the entity with the given primary key, or ``None``."""
        return self._session.get(self.model, primary_key)

    def get_or_raise(self, primary_key: object) -> ModelT:
        """Return the entity or raise :class:`LookupError` when missing."""
        entity = self.get(primary_key)
        if entity is None:
            raise LookupError(
                f"{self.model.__name__} with primary key {primary_key!r} "
                "does not exist"
            )
        return entity

    def list_all(self) -> list[ModelT]:
        """Return every stored entity."""
        return list(self._session.scalars(select(self.model)).all())

    def add(self, entity: ModelT) -> ModelT:
        """Persist a new entity and flush it to obtain its primary key."""
        self._session.add(entity)
        self._session.flush()
        return entity

    def delete(self, entity: ModelT) -> None:
        """Delete an entity and flush the change."""
        self._session.delete(entity)
        self._session.flush()

    def count(self) -> int:
        """Return the total number of stored entities."""
        total = self._session.scalar(
            select(func.count()).select_from(self.model)
        )
        return int(total or 0)

    def exists(self, primary_key: object) -> bool:
        """Return whether an entity with the given primary key exists."""
        return self.get(primary_key) is not None
