"""Evidence ORM model.

Only metadata is stored in the database. The actual image files live under
``storage/images/`` and are referenced through :attr:`filepath`, which is
relative to the storage directory (see ADR-003).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.database.models.service import Service


class Evidence(TimestampMixin, Base):
    """A photographic record attached to a service."""

    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    service: Mapped[Service] = relationship(back_populates="evidences")

    def __repr__(self) -> str:
        return f"Evidence(id={self.id!r}, filename={self.filename!r})"
