"""Input schemas for the location module."""

from __future__ import annotations

from pydantic import Field

from app.schemas.base import SchemaBaseModel


class LocationCreate(SchemaBaseModel):
    """Validated data required to create a location."""

    client_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class LocationUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing location."""

    client_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None
