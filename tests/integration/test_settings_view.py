"""Integration tests for the settings view backup actions."""

from __future__ import annotations

import pytest

from app.config.settings import Settings
from app.database import Database
from app.services import Services
from app.views.context import AppContext
from app.views.settings_view import SettingsView

from tests.conftest import FakePage


def _view(
    database: Database,
    settings: Settings,
    page: FakePage,
) -> SettingsView:
    context = AppContext(
        page=page,
        settings=settings,
        services=Services(database, settings),
    )
    view = SettingsView(context)
    view.build()
    return view


@pytest.mark.integration
def test_handle_backup_creates_an_archive(
    database: Database,
    settings: Settings,
) -> None:
    page = FakePage()
    view = _view(database, settings, page)

    view._handle_backup(None)  # noqa: SLF001

    archives = list(settings.backups_dir.glob("FieldDesk_Backup_*.zip"))
    assert archives
    assert page.dialogs, "debe notificarse el resultado"


@pytest.mark.integration
def test_restore_without_file_picker_reports(
    database: Database,
    settings: Settings,
) -> None:
    page = FakePage()
    view = _view(database, settings, page)

    view._handle_restore(None)  # noqa: SLF001

    assert page.dialogs, "debe avisarse de que no hay selector de archivos"
