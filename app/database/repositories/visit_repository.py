"""Data access for :class:`~app.database.models.visit.Visit`."""

from __future__ import annotations

from sqlalchemy import select

from app.database.models import Visit
from app.database.repositories.base_repository import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    """Queries and persistence for visits."""

    model = Visit

    def list_by_service(self, service_id: int) -> list[Visit]:
        """Return the visits of a service, most recent first."""
        statement = (
            select(Visit)
            .where(Visit.service_id == service_id)
            .order_by(Visit.visit_date.desc(), Visit.id.desc())
        )
        return list(self._session.scalars(statement).all())
