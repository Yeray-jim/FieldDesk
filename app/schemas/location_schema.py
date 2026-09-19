"""Input schemas for the location module."""

from __future__ import annotations

from pydantic import Field

from app.schemas.base import SchemaBaseModel


class LocationCreate(SchemaBaseModel):
    """Validated data required to create a location."""

    client_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=150)
    state: str | None = Field(default=None, max_length=150)
    municipality: str | None = Field(default=None, max_length=150)
    neighborhood: str | None = Field(default=None, max_length=150)
    street: str | None = Field(default=None, max_length=200)
    lot: str | None = Field(default=None, max_length=50)
    block: str | None = Field(default=None, max_length=50)
    reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None


class LocationUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing location."""

    client_id: int | None = Field(default=None, gt=0)
    name: str | None = Field(default=None, min_length=1, max_length=150)
    state: str | None = Field(default=None, max_length=150)
    municipality: str | None = Field(default=None, max_length=150)
    neighborhood: str | None = Field(default=None, max_length=150)
    street: str | None = Field(default=None, max_length=200)
    lot: str | None = Field(default=None, max_length=50)
    block: str | None = Field(default=None, max_length=50)
    reference: str | None = Field(default=None, max_length=255)
    notes: str | None = None
