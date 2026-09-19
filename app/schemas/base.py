"""Shared configuration for the Pydantic input schemas."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SchemaBaseModel(BaseModel):
    """Base model for every input schema.

    Strings are stripped of surrounding whitespace and unknown fields are
    rejected, so the interface cannot send accidental or misspelled data into
    the business layer.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )
