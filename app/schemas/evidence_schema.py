"""Input schemas for the evidence module."""

from __future__ import annotations

from pydantic import Field

from app.schemas.base import SchemaBaseModel


class EvidenceCreate(SchemaBaseModel):
    """Validated data required to attach evidence to a service.

    The image file itself is provided separately to the service as a source
    path; this schema only carries the metadata.
    """

    service_id: int = Field(gt=0)
    description: str | None = None
