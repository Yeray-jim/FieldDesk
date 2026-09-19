"""Data access for :class:`~app.database.models.service_material.ServiceMaterial`."""

from __future__ import annotations

from sqlalchemy import func, select

from app.database.models import ServiceMaterial
from app.database.repositories.base_repository import BaseRepository


class ServiceMaterialRepository(BaseRepository[ServiceMaterial]):
    """Queries and persistence for material consumption records."""

    model = ServiceMaterial

    def find(self, service_id: int, material_id: int) -> ServiceMaterial | None:
        """Return the consumption record for a service and material."""
        return self._session.get(ServiceMaterial, (service_id, material_id))

    def list_by_service(self, service_id: int) -> list[ServiceMaterial]:
        """Return the materials consumed by a service."""
        statement = (
            select(ServiceMaterial)
            .where(ServiceMaterial.service_id == service_id)
            .order_by(ServiceMaterial.material_id)
        )
        return list(self._session.scalars(statement).all())

    def list_by_material(self, material_id: int) -> list[ServiceMaterial]:
        """Return the services that consumed a given material."""
        statement = select(ServiceMaterial).where(
            ServiceMaterial.material_id == material_id
        )
        return list(self._session.scalars(statement).all())

    def count_by_material(self, material_id: int) -> int:
        """Return how many services consumed a given material."""
        total = self._session.scalar(
            select(func.count())
            .select_from(ServiceMaterial)
            .where(ServiceMaterial.material_id == material_id)
        )
        return int(total or 0)
