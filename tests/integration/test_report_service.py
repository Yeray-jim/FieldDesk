"""Integration tests for :class:`ReportService`."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

import pytest
from PIL import Image

from app.config.settings import Settings
from app.database import Database
from app.schemas import (
    EvidenceCreate,
    IncidentCreate,
    MaterialCreate,
    ServiceMaterialCreate,
    VisitCreate,
)
from app.services import Services
from app.utils.dates import today
from app.utils.exceptions import NotFoundError

from tests.conftest import Workflow


def _create_image(tmp_path: Path) -> Path:
    path = tmp_path / "evidencia.png"
    Image.new("RGB", (120, 90), (60, 130, 200)).save(path)
    return path


@pytest.mark.integration
def test_generates_a_pdf_report(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)

    path = services.reports.generate_service_report(workflow.service_id)

    assert path.is_file()
    assert path.suffix == ".pdf"
    assert path.parent == settings.documents_dir
    assert path.read_bytes()[:4] == b"%PDF"


@pytest.mark.integration
def test_report_includes_visits_incidents_materials_and_evidence(
    database: Database,
    settings: Settings,
    workflow: Workflow,
    tmp_path: Path,
) -> None:
    services = Services(database, settings)
    services.visits.create_visit(
        VisitCreate(
            service_id=workflow.service_id,
            visit_date=today(),
            work_performed="Revisión general",
            observations="Sin novedades",
        )
    )
    services.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga leve")
    )
    material = services.materials.create_material(
        MaterialCreate(name="Aceite", unit="L")
    )
    services.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("2"),
        )
    )
    services.evidence.add_evidence(
        EvidenceCreate(
            service_id=workflow.service_id,
            description="Estado final",
        ),
        _create_image(tmp_path),
    )

    path = services.reports.generate_service_report(workflow.service_id)

    assert path.is_file()
    assert path.read_bytes()[:4] == b"%PDF"
    assert path.stat().st_size > 1024


@pytest.mark.integration
def test_missing_service_raises(
    database: Database,
    settings: Settings,
) -> None:
    services = Services(database, settings)

    with pytest.raises(NotFoundError):
        services.reports.generate_service_report(999)
