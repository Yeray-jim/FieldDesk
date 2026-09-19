"""Integration tests for the CSV export service."""

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

from tests.conftest import Workflow


def _create_image(tmp_path: Path) -> Path:
    path = tmp_path / "evidencia.png"
    Image.new("RGB", (40, 30), (90, 140, 200)).save(path)
    return path


@pytest.mark.integration
def test_export_all_creates_five_csv_files(
    database: Database,
    settings: Settings,
    workflow: Workflow,
    tmp_path: Path,
) -> None:
    services = Services(database, settings)
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
    services.visits.create_visit(
        VisitCreate(service_id=workflow.service_id, visit_date=today())
    )
    services.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga")
    )
    services.evidence.add_evidence(
        EvidenceCreate(service_id=workflow.service_id),
        _create_image(tmp_path),
    )

    paths = services.exports.export_all()

    assert len(paths) == 5
    for path in paths:
        assert path.is_file()
        # UTF-8 BOM so Excel detects the encoding.
        assert path.read_bytes()[:3] == b"\xef\xbb\xbf"

    clients_csv = next(path for path in paths if path.name.startswith("Clientes"))
    content = clients_csv.read_text(encoding="utf-8-sig")
    assert "nombre" in content
    assert "Empresa XYZ" in content


@pytest.mark.integration
def test_export_specific_dataset(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    path = Services(database, settings).exports.export_equipment()

    assert path.name.startswith("Equipos")
    content = path.read_text(encoding="utf-8-sig")
    assert "numero_serie" in content
    assert "Bomba principal" in content
