"""Data access for :class:`~app.database.models.evidence.Evidence`."""

from __future__ import annotations

from sqlalchemy import func, select

from app.database.models import Evidence
from app.database.repositories.base_repository import BaseRepository


class EvidenceRepository(BaseRepository[Evidence]):
    """Queries and persistence for evidence metadata."""

    model = Evidence

    def list_by_service(self, service_id: int) -> list[Evidence]:
        """Return the evidence attached to a service."""
        statement = (
            select(Evidence)
            .where(Evidence.service_id == service_id)
            .order_by(Evidence.created_at.asc())
        )
        return list(self._session.scalars(statement).all())

    def count_by_service(self, service_id: int) -> int:
        """Return how many evidence files a service has."""
        total = self._session.scalar(
            select(func.count())
            .select_from(Evidence)
            .where(Evidence.service_id == service_id)
        )
        return int(total or 0)
