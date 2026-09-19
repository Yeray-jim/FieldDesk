"""SQLAlchemy ORM models representing the FieldDesk domain.

Importing this package registers every model in ``Base.metadata``, which is
required both for schema creation and for Alembic autogeneration.
"""

from app.database.models.client import Client
from app.database.models.enums import (
    EquipmentStatus,
    IncidentStatus,
    Priority,
    ServiceStatus,
)
from app.database.models.equipment import Equipment
from app.database.models.evidence import Evidence
from app.database.models.incident import Incident
from app.database.models.location import Location
from app.database.models.material import Material
from app.database.models.service import Service
from app.database.models.service_material import ServiceMaterial
from app.database.models.visit import Visit

__all__ = [
    "Client",
    "Equipment",
    "EquipmentStatus",
    "Evidence",
    "Incident",
    "IncidentStatus",
    "Location",
    "Material",
    "Priority",
    "Service",
    "ServiceMaterial",
    "ServiceStatus",
    "Visit",
]
