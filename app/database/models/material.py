"""Material catalog ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.service_material import ServiceMaterial


class Material(TimestampMixin, Base):
    """An item that can be consumed while performing a service."""

    __tablename__ = "material"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    unit: Mapped[str | None] = mapped_column(String(50))

    service_materials: Mapped[list[ServiceMaterial]] = relationship(
        back_populates="material",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return f"Material(id={self.id!r}, name={self.name!r})"
