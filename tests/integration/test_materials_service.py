"""Integration tests for :class:`MaterialService`."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.schemas import MaterialCreate, MaterialUpdate, ServiceMaterialCreate
from app.utils.exceptions import ConflictError, NotFoundError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_and_update_material(workflow: Workflow) -> None:
    material = workflow.materials.create_material(
        MaterialCreate(name="Aceite", unit="L")
    )

    assert material.id is not None
    assert [item.name for item in workflow.materials.list_materials()] == ["Aceite"]

    updated = workflow.materials.update_material(
        material.id, MaterialUpdate(unit="litro")
    )

    assert updated.unit == "litro"


@pytest.mark.integration
def test_set_service_material_creates_then_updates(workflow: Workflow) -> None:
    material = workflow.materials.create_material(MaterialCreate(name="Aceite"))

    first = workflow.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("2"),
        )
    )
    assert first.quantity == Decimal("2.000")

    second = workflow.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("5"),
        )
    )
    assert second.quantity == Decimal("5.000")
    assert len(
        workflow.materials.list_service_materials(workflow.service_id)
    ) == 1


@pytest.mark.integration
def test_delete_material_in_use_is_blocked(workflow: Workflow) -> None:
    material = workflow.materials.create_material(MaterialCreate(name="Aceite"))
    workflow.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("1"),
        )
    )

    with pytest.raises(ConflictError):
        workflow.materials.delete_material(material.id)


@pytest.mark.integration
def test_remove_service_material_then_delete(workflow: Workflow) -> None:
    material = workflow.materials.create_material(MaterialCreate(name="Aceite"))
    workflow.materials.set_service_material(
        ServiceMaterialCreate(
            service_id=workflow.service_id,
            material_id=material.id,
            quantity=Decimal("1"),
        )
    )

    workflow.materials.remove_service_material(workflow.service_id, material.id)

    assert workflow.materials.list_service_materials(workflow.service_id) == []
    workflow.materials.delete_material(material.id)
    assert workflow.materials.list_materials() == []


@pytest.mark.integration
def test_set_material_requires_existing_service_and_material(
    workflow: Workflow,
) -> None:
    material = workflow.materials.create_material(MaterialCreate(name="Aceite"))

    with pytest.raises(NotFoundError):
        workflow.materials.set_service_material(
            ServiceMaterialCreate(
                service_id=999,
                material_id=material.id,
                quantity=Decimal("1"),
            )
        )

    with pytest.raises(NotFoundError):
        workflow.materials.set_service_material(
            ServiceMaterialCreate(
                service_id=workflow.service_id,
                material_id=999,
                quantity=Decimal("1"),
            )
        )


@pytest.mark.integration
def test_remove_missing_service_material_raises(workflow: Workflow) -> None:
    with pytest.raises(NotFoundError):
        workflow.materials.remove_service_material(workflow.service_id, 999)
