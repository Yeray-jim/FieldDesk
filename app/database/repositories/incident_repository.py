"""Data access for :class:`~app.database.models.incident.Incident`."""

from __future__ import annotations

from sqlalchemy import func, select

from app.database.models import Incident, IncidentStatus
from app.database.repositories.base_repository import BaseRepository

_OPEN_STATES = [IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS]


class IncidentRepository(BaseRepository[Incident]):
    """Queries and persistence for incidents."""

    model = Incident

    def list_by_equipment(self, equipment_id: int) -> list[Incident]:
        """Return the incidents reported for an equipment."""
        statement = (
            select(Incident)
            .where(Incident.equipment_id == equipment_id)
            .order_by(Incident.created_at.desc())
        )
        return list(self._session.scalars(statement).all())

    def list_by_service(self, service_id: int) -> list[Incident]:
        """Return the incidents linked to a service."""
        statement = (
            select(Incident)
            .where(Incident.service_id == service_id)
            .order_by(Incident.created_at.desc())
        )
        return list(self._session.scalars(statement).all())

    def list_open(self, limit: int | None = None) -> list[Incident]:
        """Return unresolved incidents, most recent first."""
        statement = (
            select(Incident)
            .where(Incident.status.in_(_OPEN_STATES))
            .order_by(Incident.created_at.desc())
        )
        if limit is not None:
            statement = statement.limit(limit)
        return list(self._session.scalars(statement).all())

    def count_by_status(self, status: IncidentStatus) -> int:
        """Return how many incidents are in a given state."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Incident)
            .where(Incident.status == status)
        )
        return int(total or 0)

    def count_by_equipment(self, equipment_id: int) -> int:
        """Return how many incidents an equipment has."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Incident)
            .where(Incident.equipment_id == equipment_id)
        )
        return int(total or 0)
