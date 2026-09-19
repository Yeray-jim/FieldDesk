"""Integration tests for :class:`VisitService`."""

from __future__ import annotations

from datetime import time

import pytest

from app.schemas import VisitCreate, VisitUpdate
from app.utils.dates import today
from app.utils.exceptions import NotFoundError, ValidationError

from tests.conftest import Workflow


@pytest.mark.integration
def test_create_visit(workflow: Workflow) -> None:
    visit = workflow.visits.create_visit(
        VisitCreate(
            service_id=workflow.service_id,
            visit_date=today(),
            work_performed="Revisión general",
        )
    )

    assert visit.id is not None
    assert len(workflow.visits.list_visits_by_service(workflow.service_id)) == 1


@pytest.mark.integration
def test_create_visit_requires_existing_service(workflow: Workflow) -> None:
    with pytest.raises(NotFoundError):
        workflow.visits.create_visit(
            VisitCreate(service_id=999, visit_date=today())
        )


@pytest.mark.integration
def test_update_visit_rejects_inconsistent_times(workflow: Workflow) -> None:
    visit = workflow.visits.create_visit(
        VisitCreate(
            service_id=workflow.service_id,
            visit_date=today(),
            start_time=time(9, 0),
        )
    )

    with pytest.raises(ValidationError):
        workflow.visits.update_visit(visit.id, VisitUpdate(end_time=time(8, 0)))


@pytest.mark.integration
def test_update_visit_accepts_valid_times(workflow: Workflow) -> None:
    visit = workflow.visits.create_visit(
        VisitCreate(
            service_id=workflow.service_id,
            visit_date=today(),
            start_time=time(9, 0),
        )
    )

    updated = workflow.visits.update_visit(
        visit.id, VisitUpdate(end_time=time(11, 0))
    )

    assert updated.end_time == time(11, 0)


@pytest.mark.integration
def test_delete_visit(workflow: Workflow) -> None:
    visit = workflow.visits.create_visit(
        VisitCreate(service_id=workflow.service_id, visit_date=today())
    )

    workflow.visits.delete_visit(visit.id)

    assert workflow.visits.list_visits_by_service(workflow.service_id) == []


@pytest.mark.integration
def test_delete_missing_visit_raises(workflow: Workflow) -> None:
    with pytest.raises(NotFoundError):
        workflow.visits.delete_visit(999)
