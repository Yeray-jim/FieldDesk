"""Data access for :class:`~app.database.models.equipment.Equipment`."""

from __future__ import annotations

from sqlalchemy import func, or_, select

from app.database.models import Equipment, EquipmentStatus
from app.database.repositories.base_repository import (
    BaseRepository,
    contains_pattern,
)


class EquipmentRepository(BaseRepository[Equipment]):
    """Queries and persistence for equipment."""

    model = Equipment

    def list_by_location(self, location_id: int) -> list[Equipment]:
        """Return the equipment installed at a location."""
        statement = (
            select(Equipment)
            .where(Equipment.location_id == location_id)
            .order_by(Equipment.name)
        )
        return list(self._session.scalars(statement).all())

    def list_by_status(self, status: EquipmentStatus) -> list[Equipment]:
        """Return equipment in a given operational state."""
        statement = (
            select(Equipment)
            .where(Equipment.status == status)
            .order_by(Equipment.name)
        )
        return list(self._session.scalars(statement).all())

    def search(self, term: str) -> list[Equipment]:
        """Return equipment matching name, brand, model or serial number."""
        pattern = contains_pattern(term)
        statement = (
            select(Equipment)
            .where(
                or_(
                    Equipment.name.ilike(pattern),
                    Equipment.brand.ilike(pattern),
                    Equipment.model.ilike(pattern),
                    Equipment.serial_number.ilike(pattern),
                )
            )
            .order_by(Equipment.name)
        )
        return list(self._session.scalars(statement).all())

    def count_by_location(self, location_id: int) -> int:
        """Return how many equipment a location hosts."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Equipment)
            .where(Equipment.location_id == location_id)
        )
        return int(total or 0)
