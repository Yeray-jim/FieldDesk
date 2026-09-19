"""Client ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.equipment import Equipment
    from app.database.models.location import Location
    from app.database.models.service import Service


class Client(TimestampMixin, Base):
    """A customer the technician provides service to."""

    __tablename__ = "client"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    company: Mapped[str | None] = mapped_column(String(150))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(150))
    address: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    locations: Mapped[list[Location]] = relationship(
        back_populates="client",
        passive_deletes=True,
    )
    services: Mapped[list[Service]] = relationship(
        back_populates="client",
        passive_deletes=True,
    )
    equipment: Mapped[list[Equipment]] = relationship(
        secondary="location",
        primaryjoin="Client.id == Location.client_id",
        secondaryjoin="Location.id == Equipment.location_id",
        viewonly=True,
    )

    def __repr__(self) -> str:
        return f"Client(id={self.id!r}, name={self.name!r})"
