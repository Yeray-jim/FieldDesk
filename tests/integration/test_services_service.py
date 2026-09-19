"""Integration tests for :class:`ServiceService`."""

from __future__ import annotations

import pytest

from app.database.models import ServiceStatus
from app.schemas import (
    ClientCreate,
    ServiceCreate,
    ServiceUpdate,
    VisitCreate,
)
from app.utils.dates import today
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_service_requires_existing_client_and_equipment(
    workflow: Workflow,
) -> None:
    with pytest.raises(NotFoundError):
        workflow.services.create_service(
            ServiceCreate(
                client_id=999,
                equipment_id=workflow.equipment_id,
                service_type="X",
            )
        )

    with pytest.raises(NotFoundError):
        workflow.services.create_service(
            ServiceCreate(
                client_id=workflow.client_id,
                equipment_id=999,
                service_type="X",
            )
        )


@pytest.mark.integration
def test_equipment_must_belong_to_client(workflow: Workflow) -> None:
    other = workflow.clients.create_client(ClientCreate(name="Otro cliente"))

    with pytest.raises(ValidationError):
        workflow.services.create_service(
            ServiceCreate(
                client_id=other.id,
                equipment_id=workflow.equipment_id,
                service_type="Visita",
            )
        )


@pytest.mark.integration
def test_list_and_count_services(workflow: Workflow) -> None:
    assert workflow.services.count_services() == 1
    assert workflow.services.count_services_by_status(ServiceStatus.PENDING) == 1
    assert [
        service.id
        for service in workflow.services.list_services_by_client(
            workflow.client_id
        )
    ] == [workflow.service_id]
    assert len(
        workflow.services.list_services_by_equipment(workflow.equipment_id)
    ) == 1
    assert len(
        workflow.services.list_services_by_status(ServiceStatus.PENDING)
    ) == 1


@pytest.mark.integration
def test_update_service_status(workflow: Workflow) -> None:
    updated = workflow.services.update_service(
        workflow.service_id,
        ServiceUpdate(status=ServiceStatus.COMPLETED),
    )

    assert updated.status == ServiceStatus.COMPLETED
    assert workflow.services.count_services_by_status(
        ServiceStatus.COMPLETED
    ) == 1


@pytest.mark.integration
def test_delete_service_with_children_is_blocked(workflow: Workflow) -> None:
    workflow.visits.create_visit(
        VisitCreate(service_id=workflow.service_id, visit_date=today())
    )

    with pytest.raises(ConflictError) as error:
        workflow.services.delete_service(workflow.service_id)

    assert "visita" in str(error.value)


@pytest.mark.integration
def test_delete_service_without_children(workflow: Workflow) -> None:
    workflow.services.delete_service(workflow.service_id)

    assert workflow.services.count_services() == 0
