"""Input schemas for the visit module."""

from __future__ import annotations

from datetime import date, time

from pydantic import Field, model_validator

from app.schemas.base import SchemaBaseModel


class VisitCreate(SchemaBaseModel):
    """Validated data required to create a visit."""

    service_id: int = Field(gt=0)
    visit_date: date
    start_time: time | None = None
    end_time: time | None = None
    work_performed: str | None = None
    observations: str | None = None

    @model_validator(mode="after")
    def check_times(self) -> "VisitCreate":
        if (
            self.start_time is not None
            and self.end_time is not None
            and self.end_time < self.start_time
        ):
            raise ValueError(
                "La hora de fin no puede ser anterior a la de inicio."
            )
        return self


class VisitUpdate(SchemaBaseModel):
    """Fields that can be changed on an existing visit."""

    visit_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    work_performed: str | None = None
    observations: str | None = None
