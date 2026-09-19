"""Declarative base and shared mixins for the ORM models.

Every model inherits from :class:`Base`. The metadata uses an explicit naming
convention so that indexes, constraints and foreign keys receive predictable
names, which keeps Alembic migrations stable and readable.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.utils.dates import utcnow

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Shared declarative base for all FieldDesk ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` columns to a model.

    Both values are naive UTC datetimes. ``updated_at`` is refreshed
    automatically by SQLAlchemy on every update.
    """

    created_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )
