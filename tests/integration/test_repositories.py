"""Integration tests for the repository layer."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from app.database import Database
from app.database.models import (
    Client,
    Equipment,
    EquipmentStatus,
    IncidentStatus,
    Location,
    Service,
    ServiceStatus,
)
from app.database.repositories import (
    ClientRepository,
    EquipmentRepository,
    EvidenceRepository,
    IncidentRepository,
    LocationRepository,
    MaterialRepository,
    ServiceMaterialRepository,
    ServiceRepository,
    VisitRepository,
)
from app.utils.dates import utcnow

from tests.conftest import SampleGraph


@pytest.mark.integration
def test_client_repository_crud(database: Database) -> None:
    with database.session() as session:
        repository = ClientRepository(session)

        client = repository.add(Client(name="Acme", company="Acme S.A."))
        assert client.id is not None
        assert repository.count() == 1
        assert repository.exists(client.id) is True
        assert repository.get(client.id) is client

        client.name = "Acme Renombrada"
        session.flush()
        assert repository.get_or_raise(client.id).name == "Acme Renombrada"

        repository.delete(client)
        assert repository.count() == 0


@pytest.mark.integration
def test_get_or_raise_reports_missing_entity(database: Database) -> None:
    with database.session() as session:
        repository = ClientRepository(session)

        with pytest.raises(LookupError):
            repository.get_or_raise(999)


@pytest.mark.integration
def test_client_repository_search_and_order(database: Database) -> None:
    with database.session() as session:
        repository = ClientRepository(session)
        repository.add(Client(name="Zeta"))
        repository.add(Client(name="Alpha"))
        repository.add(Client(name="Beta", company="Alphabet Inc."))

        assert [c.name for c in repository.list_ordered()] == [
            "Alpha",
            "Beta",
            "Zeta",
        ]
        assert {c.name for c in repository.search("alph")} == {"Alpha", "Beta"}
        assert repository.search("   ") != []


@pytest.mark.integration
def test_location_repository_queries(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = LocationRepository(session)

        locations = repository.list_by_client(sample_graph.client_id)
        assert [location.id for location in locations] == [sample_graph.location_id]
        assert repository.count_by_client(sample_graph.client_id) == 1


@pytest.mark.integration
def test_equipment_repository_queries(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = EquipmentRepository(session)

        equipment = repository.list_by_location(sample_graph.location_id)
        assert [item.id for item in equipment] == [sample_graph.equipment_id]
        assert repository.count_by_location(sample_graph.location_id) == 1
        assert repository.list_by_status(EquipmentStatus.OPERATIONAL) == equipment
        assert repository.search("bomba") == equipment


@pytest.mark.integration
def test_service_repository_queries(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = ServiceRepository(session)

        assert len(repository.list_by_client(sample_graph.client_id)) == 1
        assert len(repository.list_by_equipment(sample_graph.equipment_id)) == 1
        assert len(repository.list_by_status(ServiceStatus.PENDING)) == 1
        assert repository.count_by_client(sample_graph.client_id) == 1
        assert repository.count_by_equipment(sample_graph.equipment_id) == 1
        assert repository.count_by_status(ServiceStatus.PENDING) == 1
        assert len(repository.list_recent()) == 1


@pytest.mark.integration
def test_service_repository_lists_upcoming_services(database: Database) -> None:
    with database.session() as session:
        client = Client(name="Cliente")
        location = Location(client=client, name="Sede")
        equipment = Equipment(location=location, name="Equipo", type="Tipo")
        repository = ServiceRepository(session)
        repository.add(
            Service(
                client=client,
                equipment=equipment,
                service_type="Futuro",
                scheduled_date=utcnow() + timedelta(days=1),
            )
        )
        repository.add(
            Service(
                client=client,
                equipment=equipment,
                service_type="Pasado",
                scheduled_date=utcnow() - timedelta(days=1),
            )
        )

        upcoming = repository.list_upcoming()
        assert [service.service_type for service in upcoming] == ["Futuro"]


@pytest.mark.integration
def test_visit_repository_lists_by_service(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = VisitRepository(session)

        visits = repository.list_by_service(sample_graph.service_id)
        assert len(visits) == 1
        assert visits[0].work_performed == "Revisión general"


@pytest.mark.integration
def test_incident_repository_queries(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = IncidentRepository(session)

        incidents = repository.list_by_equipment(sample_graph.equipment_id)
        assert [incident.id for incident in incidents] == [sample_graph.incident_id]
        assert repository.list_open() == incidents
        assert repository.count_by_status(IncidentStatus.OPEN) == 1
        assert repository.count_by_equipment(sample_graph.equipment_id) == 1


@pytest.mark.integration
def test_material_repository_search(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = MaterialRepository(session)

        assert [material.name for material in repository.list_ordered()] == [
            "Aceite"
        ]
        assert [material.name for material in repository.search("ACEI")] == [
            "Aceite"
        ]


@pytest.mark.integration
def test_service_material_repository_queries(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = ServiceMaterialRepository(session)

        record = repository.find(sample_graph.service_id, sample_graph.material_id)
        assert record is not None
        assert record.quantity == Decimal("2.500")
        assert len(repository.list_by_service(sample_graph.service_id)) == 1
        assert repository.count_by_material(sample_graph.material_id) == 1


@pytest.mark.integration
def test_evidence_repository_queries(
    database: Database,
    sample_graph: SampleGraph,
) -> None:
    with database.session() as session:
        repository = EvidenceRepository(session)

        evidences = repository.list_by_service(sample_graph.service_id)
        assert [evidence.id for evidence in evidences] == [
            sample_graph.evidence_id
        ]
        assert repository.count_by_service(sample_graph.service_id) == 1
