"""Build every view with seeded data to catch detached-relationship errors."""

from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace

import flet as ft
import pytest

from app.components.forms import FormDialog
from app.config.settings import Settings
from app.database import Database
from app.schemas import (
    IncidentCreate,
    MaterialCreate,
    ServiceMaterialCreate,
    VisitCreate,
)
from app.services import Services
from app.utils.dates import today
from app.views.clients_view import ClientsView
from app.views.context import AppContext
from app.views.dashboard_view import DashboardView
from app.views.equipment_view import EquipmentView
from app.views.incidents_view import IncidentsView
from app.views.locations_view import LocationsView
from app.views.materials_view import MaterialsView
from app.views.services_view import ServicesView
from app.views.settings_view import SettingsView
from app.views.visits_view import VisitsView

from tests.conftest import FakePage, Workflow

_VIEWS = [
    DashboardView,
    ClientsView,
    LocationsView,
    EquipmentView,
    ServicesView,
    VisitsView,
    IncidentsView,
    MaterialsView,
    SettingsView,
]


@pytest.mark.integration
def test_views_build_with_seeded_data(
    database: Database,
    settings: Settings,
    workflow: Workflow,
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

    context = AppContext(page=FakePage(), settings=settings, services=services)

    for view_class in _VIEWS:
        control = view_class(context).build()
        assert isinstance(control, ft.Control), view_class.__name__


@pytest.mark.integration
def test_equipment_location_options_include_new_location(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    view = EquipmentView(
        AppContext(page=FakePage(), settings=settings, services=services)
    )
    view.prepare()

    keys = [key for key, _label in view._location_options()]  # noqa: SLF001

    assert "__new__" in keys
    assert str(workflow.location_id) in keys


@pytest.mark.integration
def test_services_view_combines_date_and_time() -> None:
    assert ServicesView._combine_schedule(  # noqa: SLF001
        {"scheduled_date": "2026-01-15", "scheduled_time": "09:30"}
    ) == {"scheduled_date": "2026-01-15 09:30"}
    assert ServicesView._combine_schedule(  # noqa: SLF001
        {"scheduled_date": "2026-01-15"}
    ) == {"scheduled_date": "2026-01-15 00:00"}
    assert ServicesView._combine_schedule(  # noqa: SLF001
        {"scheduled_date": None, "scheduled_time": None}
    ) == {"scheduled_date": None}


@pytest.mark.integration
def test_form_dialog_creates_a_client(
    database: Database,
    settings: Settings,
) -> None:
    services = Services(database, settings)
    page = FakePage()
    view = ClientsView(AppContext(page=page, settings=settings, services=services))
    view.build()

    view._open_create(SimpleNamespace())  # noqa: SLF001
    dialog = page.dialogs[-1]
    dialog._fields["name"].control.value = "Cliente nuevo"  # noqa: SLF001

    dialog._handle_save(SimpleNamespace())  # noqa: SLF001

    assert services.clients.count_clients() == 1
    assert not any(isinstance(item, FormDialog) for item in page.dialogs)


@pytest.mark.integration
def test_form_dialog_keeps_open_on_validation_error(
    database: Database,
    settings: Settings,
) -> None:
    services = Services(database, settings)
    page = FakePage()
    view = ClientsView(AppContext(page=page, settings=settings, services=services))
    view.build()

    view._open_create(SimpleNamespace())  # noqa: SLF001
    dialog = page.dialogs[-1]

    dialog._handle_save(SimpleNamespace())  # noqa: SLF001

    assert page.dialogs, "el diálogo debe permanecer abierto"
    assert dialog._fields["name"].control.error  # noqa: SLF001
    assert services.clients.count_clients() == 0


@pytest.mark.integration
def test_delete_with_relations_reports_conflict(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    page = FakePage()
    view = ClientsView(AppContext(page=page, settings=settings, services=services))
    view.build()
    client = services.clients.get_client_or_raise(workflow.client_id)

    view._delete(client)  # noqa: SLF001

    assert services.clients.count_clients() == 1
    assert page.dialogs, "debe mostrarse un aviso al usuario"
