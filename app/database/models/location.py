"""Location ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.client import Client
    from app.database.models.equipment import Equipment


class Location(TimestampMixin, Base):
    """A physical site belonging to a client."""

    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255))
    reference: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)

    client: Mapped[Client] = relationship(back_populates="locations")
    equipment: Mapped[list[Equipment]] = relationship(
        back_populates="location",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Location(id={self.id!r}, name={self.name!r})"
