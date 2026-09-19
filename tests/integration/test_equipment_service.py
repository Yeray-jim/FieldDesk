"""Integration tests for :class:`EquipmentService`."""

from __future__ import annotations

import pytest

from app.database import Database
from app.database.models import EquipmentStatus
from app.schemas import (
    ClientCreate,
    EquipmentCreate,
    EquipmentUpdate,
    IncidentCreate,
    LocationCreate,
)
from app.services import ClientService, EquipmentService, LocationService
from app.utils.exceptions import ConflictError, NotFoundError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_equipment_requires_existing_location(database: Database) -> None:
    service = EquipmentService(database)

    with pytest.raises(NotFoundError):
        service.create_equipment(
            EquipmentCreate(location_id=999, name="Bomba", type="Hidráulica")
        )


@pytest.mark.integration
def test_create_and_list_equipment(workflow: Workflow) -> None:
    equipment = workflow.equipment.list_equipment_by_location(workflow.location_id)

    assert [item.id for item in equipment] == [workflow.equipment_id]
    assert workflow.equipment.count_equipment_by_location(workflow.location_id) == 1


@pytest.mark.integration
def test_update_equipment_status(workflow: Workflow) -> None:
    updated = workflow.equipment.update_equipment(
        workflow.equipment_id,
        EquipmentUpdate(status=EquipmentStatus.MAINTENANCE),
    )

    assert updated.status == EquipmentStatus.MAINTENANCE
    assert workflow.equipment.get_equipment(workflow.equipment_id).status == (
        EquipmentStatus.MAINTENANCE
    )


@pytest.mark.integration
def test_delete_equipment_with_service_is_blocked(workflow: Workflow) -> None:
    with pytest.raises(ConflictError) as error:
        workflow.equipment.delete_equipment(workflow.equipment_id)

    assert "servicio" in str(error.value)


@pytest.mark.integration
def test_delete_equipment_with_incident_is_blocked(workflow: Workflow) -> None:
    workflow.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga")
    )

    with pytest.raises(ConflictError):
        workflow.equipment.delete_equipment(workflow.equipment_id)


@pytest.mark.integration
def test_delete_unused_equipment(database: Database) -> None:
    client = ClientService(database).create_client(ClientCreate(name="Cliente"))
    location = LocationService(database).create_location(
        LocationCreate(client_id=client.id, name="Sede")
    )
    service = EquipmentService(database)
    equipment = service.create_equipment(
        EquipmentCreate(location_id=location.id, name="Libre", type="Tipo")
    )

    service.delete_equipment(equipment.id)

    assert service.count_equipment() == 0
