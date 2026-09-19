"""Integration tests for the service materials dialog."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.config.settings import Settings
from app.database import Database
from app.schemas import MaterialCreate
from app.services import Services
from app.views.service_materials_dialog import ServiceMaterialsDialog

from tests.conftest import FakePage, Workflow


@pytest.mark.integration
def test_add_and_remove_material(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    material = services.materials.create_material(
        MaterialCreate(name="Aceite", unit="L")
    )
    service = services.services.get_service_or_raise(workflow.service_id)
    dialog = ServiceMaterialsDialog(FakePage(), services, service)

    dialog._material_dropdown.value = str(material.id)  # noqa: SLF001
    dialog._quantity_field.value = "3"  # noqa: SLF001
    dialog._handle_add(None)  # noqa: SLF001

    records = services.materials.list_service_materials(workflow.service_id)
    assert len(records) == 1
    assert records[0].quantity == Decimal("3.000")

    dialog._handle_remove(material.id)  # noqa: SLF001
    assert (
        services.materials.list_service_materials(workflow.service_id) == []
    )


@pytest.mark.integration
def test_empty_state_has_a_message(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    service = services.services.get_service_or_raise(workflow.service_id)

    dialog = ServiceMaterialsDialog(FakePage(), services, service)

    assert dialog._build_rows()  # noqa: SLF001
