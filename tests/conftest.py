"""Shared pytest fixtures for the FieldDesk test suite."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import flet as ft
import pytest

from app.config.settings import Settings
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
from app.schemas import (
    ClientCreate,
    EquipmentCreate,
    LocationCreate,
    ServiceCreate,
)
from app.services import (
    ClientService,
    EquipmentService,
    EvidenceService,
    IncidentService,
    LocationService,
    MaterialService,
    ServiceService,
    VisitService,
)
from app.utils.dates import today


@pytest.fixture
def database(settings: Settings) -> Iterator[Database]:
    """Provide an isolated SQLite database created from the ORM metadata.

    It uses the same database path as the ``settings`` fixture so backup and
    file operations behave exactly as in production.
    """
    settings.ensure_directories()
    db = Database(settings.database_url)
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


class FakePage:
    """Minimal stand-in for ``ft.Page`` used to build controls in tests."""

    def __init__(self, width: int = 1280) -> None:
        self.width = width
        self.height = 800
        self.title = None
        self.theme = None
        self.dark_theme = None
        self.theme_mode = None
        self.platform_brightness = ft.Brightness.LIGHT
        self.bgcolor = None
        self.padding = None
        self.spacing = None
        self.fonts = None
        self.on_resize = None
        self.window = SimpleNamespace(
            width=0, height=0, min_width=0, min_height=0
        )
        self.added: list[ft.Control] = []
        self.dialogs: list[ft.Control] = []
        self.update_count = 0

    def add(self, *controls: ft.Control) -> None:
        self.added.extend(controls)

    def update(self) -> None:
        self.update_count += 1

    def show_dialog(self, dialog: ft.Control) -> None:
        self.dialogs.append(dialog)

    def pop_dialog(self) -> ft.Control | None:
        return self.dialogs.pop() if self.dialogs else None


@pytest.fixture
def fake_page() -> FakePage:
    """Provide a fake page for constructing controls."""
    return FakePage()


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    """Provide settings whose storage lives inside the test temporary folder."""
    storage = tmp_path / "storage"
    return replace(
        Settings.from_env(),
        project_root=tmp_path,
        storage_dir=storage,
        database_path=storage / "database" / "fielddesk.db",
        images_dir=storage / "images",
        documents_dir=storage / "documents",
        backups_dir=storage / "backups",
        logs_dir=storage / "logs",
    )


@dataclass(frozen=True)
class Workflow:
    """Service instances plus a pre-built client/location/equipment/service."""

    clients: ClientService
    locations: LocationService
    equipment: EquipmentService
    services: ServiceService
    visits: VisitService
    incidents: IncidentService
    materials: MaterialService
    client_id: int
    location_id: int
    equipment_id: int
    service_id: int


@pytest.fixture
def workflow(database: Database) -> Workflow:
    """Build a representative workflow through the service layer."""
    clients = ClientService(database)
    locations = LocationService(database)
    equipment = EquipmentService(database)
    services = ServiceService(database)

    client = clients.create_client(ClientCreate(name="Empresa XYZ"))
    location = locations.create_location(
        LocationCreate(client_id=client.id, name="Sucursal Centro")
    )
    device = equipment.create_equipment(
        EquipmentCreate(
            location_id=location.id,
            name="Bomba principal",
            type="Hidráulica",
        )
    )
    service = services.create_service(
        ServiceCreate(
            client_id=client.id,
            equipment_id=device.id,
            service_type="Mantenimiento",
        )
    )

    return Workflow(
        clients=clients,
        locations=locations,
        equipment=equipment,
        services=services,
        visits=VisitService(database),
        incidents=IncidentService(database),
        materials=MaterialService(database),
        client_id=client.id,
        location_id=location.id,
        equipment_id=device.id,
        service_id=service.id,
    )


@pytest.fixture
def evidence_service(
    database: Database,
    settings: Settings,
) -> EvidenceService:
    """Provide an evidence service bound to temporary storage."""
    return EvidenceService(database, settings)
