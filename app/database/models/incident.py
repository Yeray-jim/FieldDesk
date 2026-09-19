"""Incident ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.database.models.enums import IncidentStatus, Priority

if TYPE_CHECKING:
    from app.database.models.equipment import Equipment
    from app.database.models.service import Service


class Incident(TimestampMixin, Base):
    """A problem detected on an equipment, optionally tied to a service."""

    __tablename__ = "incident"

    id: Mapped[int] = mapped_column(primary_key=True)
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("service.id", ondelete="SET NULL"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, native_enum=False, length=10, name="incident_priority"),
        default=Priority.MEDIUM,
        nullable=False,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(IncidentStatus, native_enum=False, length=20, name="incident_status"),
        default=IncidentStatus.OPEN,
        nullable=False,
        index=True,
    )
    resolution: Mapped[str | None] = mapped_column(Text)

    equipment: Mapped[Equipment] = relationship(back_populates="incidents")
    service: Mapped[Service | None] = relationship(back_populates="incidents")

    def __repr__(self) -> str:
        return f"Incident(id={self.id!r}, title={self.title!r})"
