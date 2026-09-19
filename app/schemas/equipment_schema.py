"""Input schemas for the equipment module."""

from __future__ import annotations

from datetime import date

from pydantic import Field, model_validator

from app.database.models.enums import EquipmentStatus
from app.schemas.base import SchemaBaseModel


class _EquipmentBase(SchemaBaseModel):
    """Shared fields and date validation for equipment schemas."""

    installation_date: date | None = None
    warranty_expiration: date | None = None

    @model_validator(mode="after")
    def check_dates(self) -> "_EquipmentBase":
        if (
            self.installation_date is not None
            and self.warranty_expiration is not None
            and self.warranty_expiration < self.installation_date
        ):
            raise ValueError(
                "La garantía no puede vencer antes de la fecha de instalación."
            )
        return self


class EquipmentCreate(_EquipmentBase):
    """Validated data required to create an equipment."""

    location_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    type: str = Field(min_length=1, max_length=100)
    brand: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    serial_number: str | None = Field(default=None, max_length=100)
    status: EquipmentStatus = EquipmentStatus.OPERATIONAL
    notes: str | None = None


class EquipmentUpdate(_EquipmentBase):
    """Fields that can be changed on an existing equipment."""

    location_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    type: str | None = Field(default=None, min_length=1, max_length=100)
    brand: str | None = Field(default=None, max_length=100)
    model: str | None = Field(default=None, max_length=100)
    serial_number: str | None = Field(default=None, max_length=100)
    status: EquipmentStatus | None = None
    notes: str | None = None
