"""Equipment ORM model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.database.models.enums import EquipmentStatus

if TYPE_CHECKING:
    from app.database.models.incident import Incident
    from app.database.models.location import Location
    from app.database.models.service import Service


class Equipment(TimestampMixin, Base):
    """A piece of equipment installed at a client location."""

    __tablename__ = "equipment"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("location.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(100))
    model: Mapped[str | None] = mapped_column(String(100))
    serial_number: Mapped[str | None] = mapped_column(String(100), index=True)
    installation_date: Mapped[date | None] = mapped_column(Date)
    warranty_expiration: Mapped[date | None] = mapped_column(Date)
    status: Mapped[EquipmentStatus] = mapped_column(
        Enum(
            EquipmentStatus,
            native_enum=False,
            length=20,
            name="equipment_status",
        ),
        default=EquipmentStatus.OPERATIONAL,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text)

    location: Mapped[Location] = relationship(back_populates="equipment")
    services: Mapped[list[Service]] = relationship(
        back_populates="equipment",
        passive_deletes=True,
    )
    incidents: Mapped[list[Incident]] = relationship(
        back_populates="equipment",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Equipment(id={self.id!r}, name={self.name!r})"
