"""Input schemas for the service module."""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from app.database.models.enums import Priority, ServiceStatus
from app.schemas.base import SchemaBaseModel


class ServiceCreate(SchemaBaseModel):
    """Validated data required to create a service."""

    client_id: int = Field(gt=0)
    equipment_id: int = Field(gt=0)
    service_type: str = Field(min_length=1, max_length=150)
    description: str | None = None
    scheduled_date: datetime | None = None
    status: ServiceStatus = ServiceStatus.PENDING
    priority: Priority = Priority.MEDIUM


class ServiceUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing service."""

    client_id: int | None = Field(default=None, gt=0)
    equipment_id: int | None = Field(default=None, gt=0)
    service_type: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    scheduled_date: datetime | None = None
    status: ServiceStatus | None = None
    priority: Priority | None = None
