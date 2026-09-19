"""Input schemas for the client module."""

from __future__ import annotations

from pydantic import Field, field_validator

from app.schemas.base import SchemaBaseModel
from app.utils.validators import is_valid_email


class ClientCreate(SchemaBaseModel):
    """Validated data required to create a client."""

    name: str = Field(min_length=1, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        if not is_valid_email(value):
            raise ValueError("El correo electrónico no tiene un formato válido.")
        return value


class ClientUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing client."""

    name: str | None = Field(default=None, min_length=1, max_length=150)
    company: str | None = Field(default=None, max_length=150)
    phone: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=150)
    address: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        if not is_valid_email(value):
            raise ValueError("El correo electrónico no tiene un formato válido.")
        return value
