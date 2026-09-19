"""Enumerations that define the allowed states in the FieldDesk domain.

They are plain ``StrEnum`` types so their values are stored as readable
strings in SQLite and exported cleanly to CSV or PDF.
"""

from __future__ import annotations

from enum import StrEnum


class EquipmentStatus(StrEnum):
    """Operational state of an equipment."""

    OPERATIONAL = "OPERATIONAL"
    MAINTENANCE = "MAINTENANCE"
    OUT_OF_SERVICE = "OUT_OF_SERVICE"
    RETIRED = "RETIRED"


class ServiceStatus(StrEnum):
    """Lifecycle state of a service."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Priority(StrEnum):
    """Priority shared by services and incidents."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class IncidentStatus(StrEnum):
    """Lifecycle state of an incident."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"
