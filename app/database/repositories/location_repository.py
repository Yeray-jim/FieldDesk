"""Data access for :class:`~app.database.models.location.Location`."""

from __future__ import annotations

from sqlalchemy import func, select

from app.database.models import Location
from app.database.repositories.base_repository import BaseRepository


class LocationRepository(BaseRepository[Location]):
    """Queries and persistence for locations."""

    model = Location

    def list_all_ordered(self) -> list[Location]:
        """Return every location sorted by name."""
        statement = select(Location).order_by(Location.name)
        return list(self._session.scalars(statement).all())

    def list_by_client(self, client_id: int) -> list[Location]:
        """Return the locations of a client sorted by name."""
        statement = (
            select(Location)
            .where(Location.client_id == client_id)
            .order_by(Location.name)
        )
        return list(self._session.scalars(statement).all())

    def count_by_client(self, client_id: int) -> int:
        """Return how many locations a client owns."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Location)
            .where(Location.client_id == client_id)
        )
        return int(total or 0)
