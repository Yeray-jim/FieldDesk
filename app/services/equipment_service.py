"""Business operations for equipment."""

from __future__ import annotations

from app.database.models import Equipment, EquipmentStatus
from app.schemas.equipment_schema import EquipmentCreate, EquipmentUpdate
from app.services.base_service import BaseService
from app.utils.exceptions import ConflictError, NotFoundError


class EquipmentService(BaseService):
    """Provides business operations related to equipment."""

    def create_equipment(self, data: EquipmentCreate) -> Equipment:
        """Create equipment installed at an existing location.

        Raises:
            NotFoundError: If the referenced location does not exist.
        """
        with self._repositories() as repositories:
            if repositories.locations.get(data.location_id) is None:
                raise NotFoundError(
                    f"No existe la ubicación con id {data.location_id}."
                )
            equipment = Equipment(**data.model_dump())
            return repositories.equipment.add(equipment)

    def get_equipment(self, equipment_id: int) -> Equipment | None:
        """Return equipment by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.equipment.get(equipment_id)

    def get_equipment_or_raise(self, equipment_id: int) -> Equipment:
        """Return equipment by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            equipment = repositories.equipment.get(equipment_id)
            if equipment is None:
                raise NotFoundError(f"No existe el equipo con id {equipment_id}.")
            return equipment

    def list_equipment_by_location(self, location_id: int) -> list[Equipment]:
        """Return the equipment installed at a location."""
        with self._repositories() as repositories:
            return repositories.equipment.list_by_location(location_id)

    def list_equipment_by_status(
        self,
        status: EquipmentStatus,
    ) -> list[Equipment]:
        """Return equipment in the given operational state."""
        with self._repositories() as repositories:
            return repositories.equipment.list_by_status(status)

    def search_equipment(self, term: str) -> list[Equipment]:
        """Return equipment matching the given search term."""
        with self._repositories() as repositories:
            return repositories.equipment.search(term)

    def count_equipment(self) -> int:
        """Return the total number of equipment."""
        with self._repositories() as repositories:
            return repositories.equipment.count()

    def count_equipment_by_location(self, location_id: int) -> int:
        """Return how many equipment a location hosts."""
        with self._repositories() as repositories:
            return repositories.equipment.count_by_location(location_id)

    def update_equipment(
        self,
        equipment_id: int,
        data: EquipmentUpdate,
    ) -> Equipment:
        """Update existing equipment.

        Raises:
            NotFoundError: If the equipment or the new location does not exist.
        """
        with self._repositories() as repositories:
            equipment = repositories.equipment.get(equipment_id)
            if equipment is None:
                raise NotFoundError(f"No existe el equipo con id {equipment_id}.")

            changes = data.model_dump(exclude_unset=True)
            new_location_id = changes.get("location_id")
            if new_location_id is not None:
                if repositories.locations.get(new_location_id) is None:
                    raise NotFoundError(
                        f"No existe la ubicación con id {new_location_id}."
                    )

            for field, value in changes.items():
                setattr(equipment, field, value)
            repositories.session.flush()
            return equipment

    def delete_equipment(self, equipment_id: int) -> None:
        """Delete equipment when it has no services or incidents.

        Raises:
            NotFoundError: If the equipment does not exist.
            ConflictError: If the equipment still has services or incidents.
        """
        with self._repositories() as repositories:
            equipment = repositories.equipment.get(equipment_id)
            if equipment is None:
                raise NotFoundError(f"No existe el equipo con id {equipment_id}.")

            services = repositories.services.count_by_equipment(equipment_id)
            incidents = repositories.incidents.count_by_equipment(equipment_id)
            relations: list[str] = []
            if services:
                relations.append(
                    self._relation_label(services, "servicio", "servicios")
                )
            if incidents:
                relations.append(
                    self._relation_label(incidents, "incidencia", "incidencias")
                )
            if relations:
                raise ConflictError(
                    self._blocking_message("este equipo", relations)
                )

            repositories.equipment.delete(equipment)
