"""Domain exceptions raised by the business layer.

These exceptions carry user-comprehensible messages. The interface layer is
responsible for presenting them, while technical errors such as
``IntegrityError`` are translated into one of these types.
"""

from __future__ import annotations


class FieldDeskError(Exception):
    """Base class for every controlled FieldDesk error."""


class ValidationError(FieldDeskError):
    """Raised when business rules reject the provided data."""


class NotFoundError(FieldDeskError):
    """Raised when a required entity does not exist."""


class ConflictError(FieldDeskError):
    """Raised when an operation conflicts with existing related data."""


class StorageError(FieldDeskError):
    """Raised when a file operation cannot be completed."""
