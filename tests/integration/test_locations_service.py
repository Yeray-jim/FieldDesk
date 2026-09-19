"""Integration tests for :class:`LocationService`."""

from __future__ import annotations

import pytest

from app.database import Database
from app.schemas import ClientCreate, LocationCreate, LocationUpdate
from app.services import ClientService, LocationService
from app.utils.exceptions import ConflictError, NotFoundError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_requires_existing_client(database: Database) -> None:
    service = LocationService(database)

    with pytest.raises(NotFoundError):
        service.create_location(
            LocationCreate(client_id=999, name="Sede fantasma")
        )


@pytest.mark.integration
def test_create_and_list_locations(
    database: Database,
    workflow: Workflow,
) -> None:
    service = LocationService(database)
    other = ClientService(database).create_client(ClientCreate(name="Otro"))
    service.create_location(LocationCreate(client_id=other.id, name="Almacén"))

    mine = service.list_locations_by_client(workflow.client_id)
    assert [location.id for location in mine] == [workflow.location_id]
    assert len(service.list_locations()) == 2


@pytest.mark.integration
def test_update_location(
    database: Database,
    workflow: Workflow,
) -> None:
    service = LocationService(database)

    updated = service.update_location(
        workflow.location_id,
        LocationUpdate(name="Sucursal Norte"),
    )

    assert updated.name == "Sucursal Norte"


@pytest.mark.integration
def test_update_with_missing_client_raises(
    database: Database,
    workflow: Workflow,
) -> None:
    service = LocationService(database)

    with pytest.raises(NotFoundError):
        service.update_location(
            workflow.location_id,
            LocationUpdate(client_id=999),
        )


@pytest.mark.integration
def test_delete_location_with_equipment_is_blocked(
    workflow: Workflow,
) -> None:
    with pytest.raises(ConflictError):
        workflow.locations.delete_location(workflow.location_id)


@pytest.mark.integration
def test_delete_empty_location(database: Database) -> None:
    client = ClientService(database).create_client(ClientCreate(name="Cliente"))
    service = LocationService(database)
    location = service.create_location(
        LocationCreate(client_id=client.id, name="Efímera")
    )

    service.delete_location(location.id)

    assert service.list_locations() == []


@pytest.mark.integration
def test_get_or_raise_missing(database: Database) -> None:
    with pytest.raises(NotFoundError):
        LocationService(database).get_location_or_raise(999)
