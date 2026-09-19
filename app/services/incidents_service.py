"""Business operations for incidents."""

from __future__ import annotations

from app.database.models import Incident, IncidentStatus
from app.database.repositories import Repositories
from app.schemas.incident_schema import IncidentCreate, IncidentUpdate
from app.services.base_service import BaseService
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.validators import is_blank

_OPEN_STATES = (IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS)


class IncidentService(BaseService):
    """Provides business operations related to incidents."""

    def create_incident(self, data: IncidentCreate) -> Incident:
        """Create an incident for an existing equipment.

        Raises:
            NotFoundError: If the equipment or the referenced service does not
                exist.
            ValidationError: If the service belongs to another equipment, or a
                resolved incident has no resolution text.
        """
        with self._repositories() as repositories:
            if repositories.equipment.get(data.equipment_id) is None:
                raise NotFoundError(
                    f"No existe el equipo con id {data.equipment_id}."
                )
            if data.service_id is not None:
                self._validate_service(
                    repositories, data.service_id, data.equipment_id
                )
            self._validate_resolution(data.status, data.resolution)

            incident = Incident(**data.model_dump())
            return repositories.incidents.add(incident)

    def get_incident(self, incident_id: int) -> Incident | None:
        """Return an incident by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.incidents.get(incident_id)

    def get_incident_or_raise(self, incident_id: int) -> Incident:
        """Return an incident by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            incident = repositories.incidents.get(incident_id)
            if incident is None:
                raise NotFoundError(
                    f"No existe la incidencia con id {incident_id}."
                )
            return incident

    def list_incidents(self) -> list[Incident]:
        """Return every incident, most recent first."""
        with self._repositories() as repositories:
            return repositories.incidents.list_all_ordered()

    def list_incidents_by_equipment(self, equipment_id: int) -> list[Incident]:
        """Return the incidents reported for an equipment."""
        with self._repositories() as repositories:
            return repositories.incidents.list_by_equipment(equipment_id)

    def list_incidents_by_service(self, service_id: int) -> list[Incident]:
        """Return the incidents linked to a service."""
        with self._repositories() as repositories:
            return repositories.incidents.list_by_service(service_id)

    def list_open_incidents(self, limit: int | None = None) -> list[Incident]:
        """Return unresolved incidents, most recent first."""
        with self._repositories() as repositories:
            return repositories.incidents.list_open(limit)

    def count_open_incidents(self) -> int:
        """Return how many incidents are still open or in progress."""
        with self._repositories() as repositories:
            return sum(
                repositories.incidents.count_by_status(status)
                for status in _OPEN_STATES
            )

    def update_incident(
        self,
        incident_id: int,
        data: IncidentUpdate,
    ) -> Incident:
        """Update an existing incident.

        Raises:
            NotFoundError: If the incident or the new service does not exist.
            ValidationError: If the service belongs to another equipment, or a
                resolved incident has no resolution text.
        """
        with self._repositories() as repositories:
            incident = repositories.incidents.get(incident_id)
            if incident is None:
                raise NotFoundError(
                    f"No existe la incidencia con id {incident_id}."
                )

            changes = data.model_dump(exclude_unset=True)
            service_id = changes.get("service_id", incident.service_id)
            if service_id is not None:
                self._validate_service(
                    repositories, service_id, incident.equipment_id
                )

            for field, value in changes.items():
                setattr(incident, field, value)

            self._validate_resolution(incident.status, incident.resolution)
            repositories.session.flush()
            return incident

    def delete_incident(self, incident_id: int) -> None:
        """Delete an incident.

        Raises:
            NotFoundError: If the incident does not exist.
        """
        with self._repositories() as repositories:
            incident = repositories.incidents.get(incident_id)
            if incident is None:
                raise NotFoundError(
                    f"No existe la incidencia con id {incident_id}."
                )
            repositories.incidents.delete(incident)

    @staticmethod
    def _validate_service(
        repositories: Repositories,
        service_id: int,
        equipment_id: int,
    ) -> None:
        service = repositories.services.get(service_id)
        if service is None:
            raise NotFoundError(f"No existe el servicio con id {service_id}.")
        if service.equipment_id != equipment_id:
            raise ValidationError(
                "La incidencia y el servicio deben estar asociados al mismo "
                "equipo."
            )

    @staticmethod
    def _validate_resolution(
        status: IncidentStatus,
        resolution: str | None,
    ) -> None:
        if status == IncidentStatus.RESOLVED and is_blank(resolution):
            raise ValidationError(
                "Debes indicar la resolución de la incidencia antes de "
                "marcarla como resuelta."
            )
