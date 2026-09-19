"""Data access for :class:`~app.database.models.material.Material`."""

from __future__ import annotations

from sqlalchemy import select

from app.database.models import Material
from app.database.repositories.base_repository import (
    BaseRepository,
    contains_pattern,
)


class MaterialRepository(BaseRepository[Material]):
    """Queries and persistence for the material catalog."""

    model = Material

    def list_ordered(self) -> list[Material]:
        """Return the catalog sorted by name."""
        statement = select(Material).order_by(Material.name)
        return list(self._session.scalars(statement).all())

    def search(self, term: str) -> list[Material]:
        """Return materials whose name or description match ``term``."""
        pattern = contains_pattern(term)
        statement = (
            select(Material)
            .where(
                Material.name.ilike(pattern) | Material.description.ilike(pattern)
            )
            .order_by(Material.name)
        )
        return list(self._session.scalars(statement).all())
