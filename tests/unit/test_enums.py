"""Unit tests for the domain enumerations."""

from __future__ import annotations

import pytest

from app.database.models import (
    EquipmentStatus,
    IncidentStatus,
    Priority,
    ServiceStatus,
)


@pytest.mark.unit
def test_equipment_status_values() -> None:
    assert [status.value for status in EquipmentStatus] == [
        "OPERATIONAL",
        "MAINTENANCE",
        "OUT_OF_SERVICE",
        "RETIRED",
    ]


@pytest.mark.unit
def test_service_status_values() -> None:
    assert [status.value for status in ServiceStatus] == [
        "PENDING",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
    ]


@pytest.mark.unit
def test_incident_status_values() -> None:
    assert [status.value for status in IncidentStatus] == [
        "OPEN",
        "IN_PROGRESS",
        "RESOLVED",
        "CANCELLED",
    ]


@pytest.mark.unit
def test_priority_values() -> None:
    assert [priority.value for priority in Priority] == ["LOW", "MEDIUM", "HIGH"]
