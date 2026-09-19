"""Integration tests for :class:`IncidentService`."""

from __future__ import annotations

import pytest

from app.database.models import IncidentStatus
from app.schemas import EquipmentCreate, IncidentCreate, IncidentUpdate
from app.utils.exceptions import NotFoundError, ValidationError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_incident(workflow: Workflow) -> None:
    incident = workflow.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga de aceite")
    )

    assert incident.id is not None
    assert incident.status == IncidentStatus.OPEN
    assert workflow.incidents.count_open_incidents() == 1


@pytest.mark.integration
def test_create_incident_requires_existing_equipment(workflow: Workflow) -> None:
    with pytest.raises(NotFoundError):
        workflow.incidents.create_incident(
            IncidentCreate(equipment_id=999, title="Fuga")
        )


@pytest.mark.integration
def test_service_must_belong_to_the_same_equipment(workflow: Workflow) -> None:
    other = workflow.equipment.create_equipment(
        EquipmentCreate(
            location_id=workflow.location_id,
            name="Otro equipo",
            type="Eléctrica",
        )
    )

    with pytest.raises(ValidationError):
        workflow.incidents.create_incident(
            IncidentCreate(
                equipment_id=other.id,
                service_id=workflow.service_id,
                title="Inconsistente",
            )
        )


@pytest.mark.integration
def test_resolved_incident_requires_resolution(workflow: Workflow) -> None:
    with pytest.raises(ValidationError):
        workflow.incidents.create_incident(
            IncidentCreate(
                equipment_id=workflow.equipment_id,
                title="Fuga",
                status=IncidentStatus.RESOLVED,
            )
        )


@pytest.mark.integration
def test_update_incident_to_resolved_requires_resolution(
    workflow: Workflow,
) -> None:
    incident = workflow.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga")
    )

    with pytest.raises(ValidationError):
        workflow.incidents.update_incident(
            incident.id,
            IncidentUpdate(status=IncidentStatus.RESOLVED),
        )

    updated = workflow.incidents.update_incident(
        incident.id,
        IncidentUpdate(
            status=IncidentStatus.RESOLVED,
            resolution="Se reemplazó la junta.",
        ),
    )

    assert updated.status == IncidentStatus.RESOLVED
    assert workflow.incidents.count_open_incidents() == 0


@pytest.mark.integration
def test_delete_incident(workflow: Workflow) -> None:
    incident = workflow.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga")
    )

    workflow.incidents.delete_incident(incident.id)

    assert workflow.incidents.list_incidents_by_equipment(
        workflow.equipment_id
    ) == []
