"""Bundle of repositories bound to a single session.

Services receive a :class:`Repositories` instance instead of constructing one
repository per dependency, which keeps their ``__init__`` and their unit of
work simple.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.repositories.client_repository import ClientRepository
from app.database.repositories.equipment_repository import EquipmentRepository
from app.database.repositories.evidence_repository import EvidenceRepository
from app.database.repositories.incident_repository import IncidentRepository
from app.database.repositories.location_repository import LocationRepository
from app.database.repositories.material_repository import MaterialRepository
from app.database.repositories.service_material_repository import (
    ServiceMaterialRepository,
)
from app.database.repositories.service_repository import ServiceRepository
from app.database.repositories.visit_repository import VisitRepository


class Repositories:
    """All repositories sharing one session and one transaction."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.clients = ClientRepository(session)
        self.locations = LocationRepository(session)
        self.equipment = EquipmentRepository(session)
        self.services = ServiceRepository(session)
        self.visits = VisitRepository(session)
        self.incidents = IncidentRepository(session)
        self.materials = MaterialRepository(session)
        self.service_materials = ServiceMaterialRepository(session)
        self.evidences = EvidenceRepository(session)
