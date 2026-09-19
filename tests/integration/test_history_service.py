"""Integration tests for the equipment history service."""

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
    Image.new("RGB", (40, 30), (120, 90, 60)).save(path)
    return path


@pytest.mark.integration
def test_history_aggregates_all_event_kinds(
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
        )
    )
    services.incidents.create_incident(
        IncidentCreate(equipment_id=workflow.equipment_id, title="Fuga")
    )
    material = services.materials.create_material(MaterialCreate(name="Aceite"))
    services.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("2"),
        )
    )
    services.evidence.add_evidence(
        EvidenceCreate(service_id=workflow.service_id),
        _create_image(tmp_path),
    )

    entries = services.history.get_equipment_history(workflow.equipment_id)

    kinds = {entry.kind for entry in entries}
    assert kinds == {"Servicio", "Visita", "Incidencia", "Material", "Evidencia"}
    # Newest first.
    assert entries == sorted(entries, key=lambda entry: entry.date, reverse=True)


@pytest.mark.integration
def test_history_missing_equipment_raises(
    database: Database,
    settings: Settings,
) -> None:
    services = Services(database, settings)

    with pytest.raises(NotFoundError):
        services.history.get_equipment_history(999)
