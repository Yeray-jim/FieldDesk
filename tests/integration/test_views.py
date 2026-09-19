"""Smoke tests that build every view to catch Flet API misuse."""

from __future__ import annotations

from types import SimpleNamespace

import flet as ft
import pytest

from app.config.settings import Settings
from app.database import Database
from app.services import Services
from app.views.app_shell import AppShell
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


class FakePage:
    """Minimal stand-in for ``ft.Page`` used to build controls in tests."""

    def __init__(self, width: int = 1280) -> None:
        self.width = width
        self.height = 800
        self.title = None
        self.theme = None
        self.theme_mode = None
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


def _context(database: Database, settings: Settings, page: FakePage) -> AppContext:
    return AppContext(page=page, settings=settings, services=Services(database, settings))


@pytest.mark.integration
@pytest.mark.parametrize(
    "view_class",
    [
        DashboardView,
        ClientsView,
        LocationsView,
        EquipmentView,
        ServicesView,
        VisitsView,
        IncidentsView,
        MaterialsView,
        SettingsView,
    ],
)
def test_view_builds(
    database: Database,
    settings: Settings,
    view_class: type,
) -> None:
    context = _context(database, settings, FakePage())

    control = view_class(context).build()

    assert isinstance(control, ft.Control)


@pytest.mark.integration
def test_app_shell_renders_and_navigates(
    database: Database,
    settings: Settings,
) -> None:
    page = FakePage()
    shell = AppShell(_context(database, settings, page))

    shell.render()

    assert page.added, "la shell debe montar su raíz"
    assert page.update_count >= 1

    event = SimpleNamespace(control=SimpleNamespace(selected_index=1))
    shell._on_nav_change(event)  # noqa: SLF001 - exercised on purpose
    assert page.update_count >= 2


@pytest.mark.integration
def test_app_shell_uses_mobile_layout(
    database: Database,
    settings: Settings,
) -> None:
    page = FakePage(width=420)
    shell = AppShell(_context(database, settings, page))

    shell.render()

    assert shell._is_mobile is True  # noqa: SLF001
    root = page.added[0]
    assert isinstance(root, ft.Container)
