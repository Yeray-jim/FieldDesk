"""Integration tests for the ORM models and their relationships."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.database import Database
from app.database.models import (
    Client,
    Equipment,
    Location,
    Material,
    Service,
    ServiceMaterial,
)

from tests.conftest import SampleGraph


@pytest.mark.integration
def test_service_relationships_are_consistent(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        service = session.get(Service, sample_graph.service_id)

        assert service is not None
        assert service.client.id == sample_graph.client_id
        assert service.equipment.id == sample_graph.equipment_id
        assert service.equipment.location.id == sample_graph.location_id
        assert len(service.visits) == 1
        assert len(service.evidences) == 1
        assert [material.name for material in service.materials] == ["Aceite"]
        assert service.service_materials[0].quantity == Decimal("2.500")


@pytest.mark.integration
def test_client_reaches_equipment_through_location(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        client = session.get(Client, sample_graph.client_id)

        assert client is not None
        assert [location.id for location in client.locations] == [
            sample_graph.location_id
        ]
        assert [equipment.id for equipment in client.equipment] == [
            sample_graph.equipment_id
        ]


@pytest.mark.integration
def test_timestamps_are_populated(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        client = session.get(Client, sample_graph.client_id)

        assert client is not None
        assert client.created_at is not None
        assert client.updated_at is not None


@pytest.mark.integration
def test_quantity_must_be_positive(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with pytest.raises(IntegrityError):
        with database.session() as session:
            session.add(
                ServiceMaterial(
                    service_id=sample_graph.service_id,
                    material_id=sample_graph.material_id,
                    quantity=Decimal("0"),
                )
            )


@pytest.mark.integration
def test_default_equipment_status_is_operational(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        equipment = session.get(Equipment, sample_graph.equipment_id)

        assert equipment is not None
        assert equipment.status.value == "OPERATIONAL"


@pytest.mark.integration
def test_location_belongs_to_client(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        location = session.get(Location, sample_graph.location_id)

        assert location is not None
        assert location.client_id == sample_graph.client_id


@pytest.mark.integration
def test_material_catalog_is_independent(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        material = session.get(Material, sample_graph.material_id)

        assert material is not None
        assert material.unit == "L"
