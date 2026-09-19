"""Integration tests for the material inventory behaviour."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.database.models import ServiceStatus
from app.config.settings import Settings
from app.database import Database
from app.schemas import (
    MaterialCreate,
    ServiceMaterialCreate,
    ServiceUpdate,
)
from app.services import Services
from app.utils.exceptions import ValidationError

from tests.conftest import Workflow


def _material(services: Services, stock: str = "10"):
    return services.materials.create_material(
        MaterialCreate(name="Aceite", unit="L", stock=Decimal(stock))
    )


@pytest.mark.integration
def test_completing_a_service_deducts_stock(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    material = _material(services)
    services.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("3"),
        )
    )

    services.services.update_service(
        workflow.service_id, ServiceUpdate(status=ServiceStatus.COMPLETED)
    )

    updated = services.materials.get_material_or_raise(material.id)
    assert updated.stock == Decimal("7.000")

    # Reopening the service restores the stock.
    services.services.update_service(
        workflow.service_id, ServiceUpdate(status=ServiceStatus.IN_PROGRESS)
    )
    restored = services.materials.get_material_or_raise(material.id)
    assert restored.stock == Decimal("10.000")


@pytest.mark.integration
def test_completing_without_enough_stock_is_rejected(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    material = _material(services, stock="1")
    services.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("5"),
        )
    )

    with pytest.raises(ValidationError):
        services.services.update_service(
            workflow.service_id,
            ServiceUpdate(status=ServiceStatus.COMPLETED),
        )

    assert services.materials.get_material_or_raise(material.id).stock == (
        Decimal("1.000")
    )


@pytest.mark.integration
def test_inventory_tracks_materials_added_after_completion(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    material = _material(services)
    services.services.update_service(
        workflow.service_id, ServiceUpdate(status=ServiceStatus.COMPLETED)
    )

    services.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("4"),
        )
    )
    assert services.materials.get_material_or_raise(material.id).stock == (
        Decimal("6.000")
    )

    services.materials.remove_service_material(
        workflow.service_id, material.id
    )
    assert services.materials.get_material_or_raise(material.id).stock == (
        Decimal("10.000")
    )
