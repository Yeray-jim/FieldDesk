"""Input schemas for the incident module."""

from __future__ import annotations

from pydantic import Field

from app.database.models.enums import IncidentStatus, Priority
from app.schemas.base import SchemaBaseModel


class IncidentCreate(SchemaBaseModel):
    """Validated data required to create an incident."""

    equipment_id: int = Field(gt=0)
    service_id: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    status: IncidentStatus = IncidentStatus.OPEN
    resolution: str | None = None


class IncidentUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing incident."""

    service_id: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    priority: Priority | None = None
    status: IncidentStatus | None = None
    resolution: str | None = None
