"""Business operations for visits."""

from __future__ import annotations

from app.database.models import Visit
from app.schemas.visit_schema import VisitCreate, VisitUpdate
from app.services.base_service import BaseService
from app.utils.exceptions import NotFoundError, ValidationError


class VisitService(BaseService):
    """Provides business operations related to visits."""

    def create_visit(self, data: VisitCreate) -> Visit:
        """Create a visit for an existing service.

        Raises:
            NotFoundError: If the service does not exist.
        """
        with self._repositories() as repositories:
            if repositories.services.get(data.service_id) is None:
                raise NotFoundError(
                    f"No existe el servicio con id {data.service_id}."
                )
            visit = Visit(**data.model_dump())
            return repositories.visits.add(visit)

    def get_visit(self, visit_id: int) -> Visit | None:
        """Return a visit by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.visits.get(visit_id)

    def get_visit_or_raise(self, visit_id: int) -> Visit:
        """Return a visit by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            visit = repositories.visits.get(visit_id)
            if visit is None:
                raise NotFoundError(f"No existe la visita con id {visit_id}.")
            return visit

    def list_visits(self) -> list[Visit]:
        """Return every visit, most recent first."""
        with self._repositories() as repositories:
            return repositories.visits.list_all_ordered()

    def list_visits_by_service(self, service_id: int) -> list[Visit]:
        """Return the visits of a service, most recent first."""
        with self._repositories() as repositories:
            return repositories.visits.list_by_service(service_id)

    def update_visit(self, visit_id: int, data: VisitUpdate) -> Visit:
        """Update an existing visit.

        Raises:
            NotFoundError: If the visit does not exist.
            ValidationError: If the resulting time range is inconsistent.
        """
        with self._repositories() as repositories:
            visit = repositories.visits.get(visit_id)
            if visit is None:
                raise NotFoundError(f"No existe la visita con id {visit_id}.")

            changes = data.model_dump(exclude_unset=True)
            start_time = changes.get("start_time", visit.start_time)
            end_time = changes.get("end_time", visit.end_time)
            if (
                start_time is not None
                and end_time is not None
                and end_time < start_time
            ):
                raise ValidationError(
                    "La hora de fin no puede ser anterior a la de inicio."
                )

            for field, value in changes.items():
                setattr(visit, field, value)
            repositories.session.flush()
            return visit

    def delete_visit(self, visit_id: int) -> None:
        """Delete a visit.

        Raises:
            NotFoundError: If the visit does not exist.
        """
        with self._repositories() as repositories:
            visit = repositories.visits.get(visit_id)
            if visit is None:
                raise NotFoundError(f"No existe la visita con id {visit_id}.")
            repositories.visits.delete(visit)
