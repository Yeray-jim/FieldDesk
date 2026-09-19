"""Integration tests for referential integrity rules."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.database import Database
from app.database.models import (
    Client,
    Equipment,
    Evidence,
    Incident,
    Material,
    Service,
    Visit,
)

from tests.conftest import SampleGraph


@pytest.mark.integration
def test_cannot_delete_client_with_locations(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with pytest.raises(IntegrityError):
        with database.session() as session:
            session.delete(session.get(Client, sample_graph.client_id))


@pytest.mark.integration
def test_cannot_delete_equipment_with_services(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with pytest.raises(IntegrityError):
        with database.session() as session:
            session.delete(session.get(Equipment, sample_graph.equipment_id))


@pytest.mark.integration
def test_cannot_delete_material_in_use(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with pytest.raises(IntegrityError):
        with database.session() as session:
            session.delete(session.get(Material, sample_graph.material_id))


@pytest.mark.integration
def test_deleting_service_cascades_children_and_keeps_incident(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        session.delete(session.get(Service, sample_graph.service_id))

    with database.session() as session:
        assert session.scalar(select(func.count()).select_from(Visit)) == 0
        assert session.scalar(select(func.count()).select_from(Evidence)) == 0

        incident = session.get(Incident, sample_graph.incident_id)
        assert incident is not None
        assert incident.service_id is None
