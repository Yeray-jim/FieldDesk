"""Service ORM model."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.database.models.enums import Priority, ServiceStatus

if TYPE_CHECKING:
    from app.database.models.client import Client
    from app.database.models.equipment import Equipment
    from app.database.models.evidence import Evidence
    from app.database.models.incident import Incident
    from app.database.models.material import Material
    from app.database.models.service_material import ServiceMaterial
    from app.database.models.visit import Visit


class Service(TimestampMixin, Base):
    """A technical job requested for an equipment."""

    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(
        ForeignKey("client.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    equipment_id: Mapped[int] = mapped_column(
        ForeignKey("equipment.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    service_type: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    scheduled_date: Mapped[datetime | None] = mapped_column(DateTime)
    status: Mapped[ServiceStatus] = mapped_column(
        Enum(ServiceStatus, native_enum=False, length=20, name="service_status"),
        default=ServiceStatus.PENDING,
        nullable=False,
        index=True,
    )
    priority: Mapped[Priority] = mapped_column(
        Enum(Priority, native_enum=False, length=10, name="service_priority"),
        default=Priority.MEDIUM,
        nullable=False,
    )

    client: Mapped[Client] = relationship(back_populates="services")
    equipment: Mapped[Equipment] = relationship(back_populates="services")
    visits: Mapped[list[Visit]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    incidents: Mapped[list[Incident]] = relationship(
        back_populates="service",
        passive_deletes=True,
    )
    service_materials: Mapped[list[ServiceMaterial]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    evidences: Mapped[list[Evidence]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    materials: Mapped[list[Material]] = association_proxy(
        "service_materials",
        "material",
    )

    def __repr__(self) -> str:
        return f"Service(id={self.id!r}, type={self.service_type!r})"
