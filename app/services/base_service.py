"""Shared behaviour for the business services.

A service owns a unit of work: it opens a session through the
:class:`~app.database.Database`, builds a :class:`Repositories` bundle and
commits or rolls back automatically. Upper layers (the interface) never touch
the session directly.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from app.database import Database
from app.database.repositories import Repositories


class BaseService:
    """Base class for every business service."""

    def __init__(self, database: Database) -> None:
        self._database = database

    @property
    def database(self) -> Database:
        """The database used by this service."""
        return self._database

    @contextmanager
    def _repositories(self) -> Iterator[Repositories]:
        """Open a transactional unit of work bound to fresh repositories."""
        with self._database.session() as session:
            yield Repositories(session)

    @staticmethod
    def _relation_label(count: int, singular: str, plural: str) -> str:
        """Format a count with the matching singular or plural noun."""
        return f"{count} {singular if count == 1 else plural}"

    @classmethod
    def _blocking_message(cls, entity: str, relations: list[str]) -> str:
        """Build a user-friendly message explaining why a deletion is blocked."""
        joined = " y ".join(relations)
        return (
            f"No se puede eliminar {entity} porque tiene {joined} asociados. "
            "Esta acción no puede deshacerse."
        )
