"""Repositories encapsulating data access for each aggregate."""

from app.database.repositories.base_repository import (
    BaseRepository,
    contains_pattern,
)
from app.database.repositories.client_repository import ClientRepository
from app.database.repositories.equipment_repository import EquipmentRepository
from app.database.repositories.evidence_repository import EvidenceRepository
from app.database.repositories.incident_repository import IncidentRepository
from app.database.repositories.location_repository import LocationRepository
from app.database.repositories.material_repository import MaterialRepository
from app.database.repositories.registry import Repositories
from app.database.repositories.service_material_repository import (
    ServiceMaterialRepository,
)
from app.database.repositories.service_repository import ServiceRepository
from app.database.repositories.visit_repository import VisitRepository

__all__ = [
    "BaseRepository",
    "ClientRepository",
    "EquipmentRepository",
    "EvidenceRepository",
    "IncidentRepository",
    "LocationRepository",
    "MaterialRepository",
    "Repositories",
    "ServiceMaterialRepository",
    "ServiceRepository",
    "VisitRepository",
    "contains_pattern",
]
