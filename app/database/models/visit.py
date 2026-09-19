"""Visit ORM model."""

from __future__ import annotations

from datetime import date, time
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Text, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.service import Service


class Visit(TimestampMixin, Base):
    """A site visit performed within a service."""

    __tablename__ = "visit"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time | None] = mapped_column(Time)
    end_time: Mapped[time | None] = mapped_column(Time)
    work_performed: Mapped[str | None] = mapped_column(Text)
    observations: Mapped[str | None] = mapped_column(Text)

    service: Mapped[Service] = relationship(back_populates="visits")

    def __repr__(self) -> str:
        return f"Visit(id={self.id!r}, date={self.visit_date!r})"
