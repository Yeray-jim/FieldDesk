"""Business operations for services."""

from __future__ import annotations

from app.database.models import Equipment, Service, ServiceStatus
from app.database.repositories import Repositories
from app.schemas.service_schema import ServiceCreate, ServiceUpdate
from app.services.base_service import BaseService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError


class ServiceService(BaseService):
    """Provides business operations related to services."""

    def create_service(self, data: ServiceCreate) -> Service:
        """Create a service for a client and one of its equipment.

        Raises:
            NotFoundError: If the client or equipment does not exist.
            ValidationError: If the equipment does not belong to the client.
        """
        with self._repositories() as repositories:
            self._validate_client(repositories, data.client_id)
            equipment = self._validate_equipment(
                repositories, data.equipment_id
            )
            self._validate_ownership(equipment, data.client_id)

            service = Service(**data.model_dump())
            return repositories.services.add(service)

    def get_service(self, service_id: int) -> Service | None:
        """Return a service by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.services.get(service_id)

    def get_service_or_raise(self, service_id: int) -> Service:
        """Return a service by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            service = repositories.services.get(service_id)
            if service is None:
                raise NotFoundError(f"No existe el servicio con id {service_id}.")
            return service

    def list_services(self) -> list[Service]:
        """Return every service, most recent first."""
        with self._repositories() as repositories:
            return repositories.services.list_all_ordered()

    def list_services_by_client(self, client_id: int) -> list[Service]:
        """Return the services requested by a client."""
        with self._repositories() as repositories:
            return repositories.services.list_by_client(client_id)

    def list_services_by_equipment(self, equipment_id: int) -> list[Service]:
        """Return the services performed on an equipment."""
        with self._repositories() as repositories:
            return repositories.services.list_by_equipment(equipment_id)

    def list_services_by_status(self, status: ServiceStatus) -> list[Service]:
        """Return services in the given lifecycle state."""
        with self._repositories() as repositories:
            return repositories.services.list_by_status(status)

    def list_recent_services(self, limit: int = 5) -> list[Service]:
        """Return the most recently created services."""
        with self._repositories() as repositories:
            return repositories.services.list_recent(limit)

    def list_upcoming_services(self, limit: int = 5) -> list[Service]:
        """Return scheduled services that are still open."""
        with self._repositories() as repositories:
            return repositories.services.list_upcoming(limit)

    def count_services(self) -> int:
        """Return the total number of services."""
        with self._repositories() as repositories:
            return repositories.services.count()

    def count_services_by_status(self, status: ServiceStatus) -> int:
        """Return how many services are in the given state."""
        with self._repositories() as repositories:
            return repositories.services.count_by_status(status)

    def update_service(
        self,
        service_id: int,
        data: ServiceUpdate,
    ) -> Service:
        """Update an existing service.

        Raises:
            NotFoundError: If the service, client or equipment does not exist.
            ValidationError: If the resulting equipment does not belong to the
                resulting client.
        """
        with self._repositories() as repositories:
            service = repositories.services.get(service_id)
            if service is None:
                raise NotFoundError(f"No existe el servicio con id {service_id}.")

            changes = data.model_dump(exclude_unset=True)

            client_id = changes.get("client_id", service.client_id)
            equipment_id = changes.get("equipment_id", service.equipment_id)
            self._validate_client(repositories, client_id)
            equipment = self._validate_equipment(repositories, equipment_id)
            self._validate_ownership(equipment, client_id)

            for field, value in changes.items():
                setattr(service, field, value)
            repositories.session.flush()
            return service

    def delete_service(self, service_id: int) -> None:
        """Delete a service that has no related records.

        Raises:
            NotFoundError: If the service does not exist.
            ConflictError: If the service still has visits, incidents,
                materials or evidence.
        """
        with self._repositories() as repositories:
            service = repositories.services.get(service_id)
            if service is None:
                raise NotFoundError(f"No existe el servicio con id {service_id}.")

            relations: list[str] = []
            visits = len(repositories.visits.list_by_service(service_id))
            incidents = len(repositories.incidents.list_by_service(service_id))
            materials = len(
                repositories.service_materials.list_by_service(service_id)
            )
            evidences = repositories.evidences.count_by_service(service_id)

            if visits:
                relations.append(
                    self._relation_label(visits, "visita", "visitas")
                )
            if incidents:
                relations.append(
                    self._relation_label(incidents, "incidencia", "incidencias")
                )
            if materials:
                relations.append(
                    self._relation_label(materials, "material", "materiales")
                )
            if evidences:
                relations.append(
                    self._relation_label(evidences, "evidencia", "evidencias")
                )
            if relations:
                raise ConflictError(
                    self._blocking_message("este servicio", relations)
                )

            repositories.services.delete(service)

    @staticmethod
    def _validate_client(repositories: Repositories, client_id: int) -> None:
        if repositories.clients.get(client_id) is None:
            raise NotFoundError(f"No existe el cliente con id {client_id}.")

    @staticmethod
    def _validate_equipment(
        repositories: Repositories,
        equipment_id: int,
    ) -> Equipment:
        equipment = repositories.equipment.get(equipment_id)
        if equipment is None:
            raise NotFoundError(
                f"No existe el equipo con id {equipment_id}."
            )
        return equipment

    @staticmethod
    def _validate_ownership(equipment: Equipment, client_id: int) -> None:
        if equipment.location.client_id != client_id:
            raise ValidationError(
                "El equipo seleccionado no pertenece al cliente indicado."
            )
