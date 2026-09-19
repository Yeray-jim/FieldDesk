"""Input schemas for the material module."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field

from app.schemas.base import SchemaBaseModel


class MaterialCreate(SchemaBaseModel):
    """Validated data required to create a catalog material."""

    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    unit: str | None = Field(default=None, max_length=50)


class MaterialUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing material."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    unit: str | None = Field(default=None, max_length=50)


class ServiceMaterialCreate(SchemaBaseModel):
    """Validated data required to consume a material in a service."""

    service_id: int = Field(gt=0)
    material_id: int = Field(gt=0)
    quantity: Decimal = Field(gt=0)
    notes: str | None = None
