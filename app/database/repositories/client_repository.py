"""Data access for :class:`~app.database.models.client.Client`."""

from __future__ import annotations

from sqlalchemy import or_, select

from app.database.models import Client
from app.database.repositories.base_repository import (
    BaseRepository,
    contains_pattern,
)


class ClientRepository(BaseRepository[Client]):
    """Queries and persistence for clients."""

    model = Client

    def list_ordered(self) -> list[Client]:
        """Return all clients sorted by name."""
        statement = select(Client).order_by(Client.name)
        return list(self._session.scalars(statement).all())

    def search(self, term: str) -> list[Client]:
        """Return clients whose name, company, phone or email match ``term``."""
        pattern = contains_pattern(term)
        statement = (
            select(Client)
            .where(
                or_(
                    Client.name.ilike(pattern),
                    Client.company.ilike(pattern),
                    Client.phone.ilike(pattern),
                    Client.email.ilike(pattern),
                )
            )
            .order_by(Client.name)
        )
        return list(self._session.scalars(statement).all())
