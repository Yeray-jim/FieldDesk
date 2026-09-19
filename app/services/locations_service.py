"""Business operations for locations."""

from __future__ import annotations

from app.database.models import Location
from app.schemas.location_schema import LocationCreate, LocationUpdate
from app.services.base_service import BaseService
from app.utils.exceptions import ConflictError, NotFoundError


class LocationService(BaseService):
    """Provides business operations related to locations."""

    def create_location(self, data: LocationCreate) -> Location:
        """Create a location for an existing client.

        Raises:
            NotFoundError: If the referenced client does not exist.
        """
        with self._repositories() as repositories:
            if repositories.clients.get(data.client_id) is None:
                raise NotFoundError(
                    f"No existe el cliente con id {data.client_id}."
                )
            location = Location(**data.model_dump())
            return repositories.locations.add(location)

    def get_location(self, location_id: int) -> Location | None:
        """Return a location by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.locations.get(location_id)

    def get_location_or_raise(self, location_id: int) -> Location:
        """Return a location by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            location = repositories.locations.get(location_id)
            if location is None:
                raise NotFoundError(f"No existe la ubicación con id {location_id}.")
            return location

    def list_locations_by_client(self, client_id: int) -> list[Location]:
        """Return the locations of a client sorted by name."""
        with self._repositories() as repositories:
            return repositories.locations.list_by_client(client_id)

    def update_location(
        self,
        location_id: int,
        data: LocationUpdate,
    ) -> Location:
        """Update an existing location.

        Raises:
            NotFoundError: If the location or the new client does not exist.
        """
        with self._repositories() as repositories:
            location = repositories.locations.get(location_id)
            if location is None:
                raise NotFoundError(f"No existe la ubicación con id {location_id}.")

            changes = data.model_dump(exclude_unset=True)
            new_client_id = changes.get("client_id")
            if new_client_id is not None:
                if repositories.clients.get(new_client_id) is None:
                    raise NotFoundError(
                        f"No existe el cliente con id {new_client_id}."
                    )

            for field, value in changes.items():
                setattr(location, field, value)
            repositories.session.flush()
            return location

    def delete_location(self, location_id: int) -> None:
        """Delete a location when it hosts no equipment.

        Raises:
            NotFoundError: If the location does not exist.
            ConflictError: If the location still has equipment.
        """
        with self._repositories() as repositories:
            location = repositories.locations.get(location_id)
            if location is None:
                raise NotFoundError(f"No existe la ubicación con id {location_id}.")

            equipment = repositories.equipment.count_by_location(location_id)
            if equipment:
                relation = self._relation_label(equipment, "equipo", "equipos")
                raise ConflictError(
                    self._blocking_message("esta ubicación", [relation])
                )
            repositories.locations.delete(location)
