"""Association between services and the materials they consume."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, ForeignKey, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.material import Material
    from app.database.models.service import Service


class ServiceMaterial(Base):
    """A material consumed by a service, with the used quantity."""

    __tablename__ = "service_material"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id", ondelete="CASCADE"),
        primary_key=True,
    )
    material_id: Mapped[int] = mapped_column(
        ForeignKey("material.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(12, 3), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    service: Mapped[Service] = relationship(back_populates="service_materials")
    material: Mapped[Material] = relationship(back_populates="service_materials")

    def __repr__(self) -> str:
        return (
            f"ServiceMaterial(service_id={self.service_id!r}, "
            f"material_id={self.material_id!r}, quantity={self.quantity!r})"
        )
