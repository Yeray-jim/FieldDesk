"""Shared pytest fixtures for the FieldDesk test suite."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pytest

from app.database import Database
from app.database.models import (
    Client,
    Equipment,
    Evidence,
    Incident,
    Location,
    Material,
    Service,
    ServiceMaterial,
    Visit,
)
from app.utils.dates import today


@pytest.fixture
def database(tmp_path: Path) -> Iterator[Database]:
    """Provide an isolated SQLite database created from the ORM metadata."""
    db = Database(f"sqlite:///{tmp_path / 'fielddesk_test.db'}")
    db.create_all()
    try:
        yield db
    finally:
        db.dispose()


@dataclass(frozen=True)
class SampleGraph:
    """Identifiers of a fully linked sample aggregate."""

    client_id: int
    location_id: int
    equipment_id: int
    service_id: int
    incident_id: int
    material_id: int
    evidence_id: int


@pytest.fixture
def sample_graph(database: Database) -> SampleGraph:
    """Persist a representative graph of related records."""
    with database.session() as session:
        client = Client(name="Empresa XYZ", company="XYZ S.A.", phone="555-0101")
        location = Location(client=client, name="Sucursal Centro")
        equipment = Equipment(
            location=location,
            name="Bomba principal",
            type="Hidráulica",
        )
        material = Material(name="Aceite", unit="L")

        service = Service(
            client=client,
            equipment=equipment,
            service_type="Mantenimiento",
        )
        service.visits.append(
            Visit(visit_date=today(), work_performed="Revisión general")
        )
        service.service_materials.append(
            ServiceMaterial(material=material, quantity=Decimal("2.5"))
        )
        service.evidences.append(
            Evidence(filename="foto.jpg", filepath="images/foto.jpg")
        )
        incident = Incident(equipment=equipment, title="Fuga de aceite")

        session.add_all([service, incident])
        session.flush()

        return SampleGraph(
            client_id=client.id,
            location_id=location.id,
            equipment_id=equipment.id,
            service_id=service.id,
            incident_id=incident.id,
            material_id=material.id,
            evidence_id=service.evidences[0].id,
        )
