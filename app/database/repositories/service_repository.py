"""Data access for :class:`~app.database.models.service.Service`."""

from __future__ import annotations

from sqlalchemy import func, select

from app.database.models import Service, ServiceStatus
from app.database.repositories.base_repository import BaseRepository
from app.utils.dates import utcnow


class ServiceRepository(BaseRepository[Service]):
    """Queries and persistence for services."""

    model = Service

    def list_by_client(self, client_id: int) -> list[Service]:
        """Return the services requested by a client."""
        statement = (
            select(Service)
            .where(Service.client_id == client_id)
            .order_by(Service.created_at.desc())
        )
        return list(self._session.scalars(statement).all())

    def list_by_equipment(self, equipment_id: int) -> list[Service]:
        """Return the services performed on an equipment."""
        statement = (
            select(Service)
            .where(Service.equipment_id == equipment_id)
            .order_by(Service.created_at.desc())
        )
        return list(self._session.scalars(statement).all())

    def list_by_status(self, status: ServiceStatus) -> list[Service]:
        """Return services in a given lifecycle state."""
        statement = (
            select(Service)
            .where(Service.status == status)
            .order_by(Service.created_at.desc())
        )
        return list(self._session.scalars(statement).all())

    def list_recent(self, limit: int = 5) -> list[Service]:
        """Return the most recently created services."""
        statement = select(Service).order_by(Service.created_at.desc()).limit(limit)
        return list(self._session.scalars(statement).all())

    def list_upcoming(self, limit: int = 5) -> list[Service]:
        """Return scheduled services that are still open, soonest first."""
        statement = (
            select(Service)
            .where(
                Service.scheduled_date.is_not(None),
                Service.scheduled_date >= utcnow(),
                Service.status.in_(
                    [ServiceStatus.PENDING, ServiceStatus.IN_PROGRESS]
                ),
            )
            .order_by(Service.scheduled_date.asc())
            .limit(limit)
        )
        return list(self._session.scalars(statement).all())

    def count_by_status(self, status: ServiceStatus) -> int:
        """Return how many services are in a given state."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Service)
            .where(Service.status == status)
        )
        return int(total or 0)

    def count_by_client(self, client_id: int) -> int:
        """Return how many services a client requested."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Service)
            .where(Service.client_id == client_id)
        )
        return int(total or 0)

    def count_by_equipment(self, equipment_id: int) -> int:
        """Return how many services an equipment received."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Service)
            .where(Service.equipment_id == equipment_id)
        )
        return int(total or 0)
