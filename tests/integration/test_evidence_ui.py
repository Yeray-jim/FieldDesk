"""Integration tests for the service evidence dialog."""

from __future__ import annotations

from pathlib import Path

import flet as ft
import pytest
from PIL import Image

from app.components.gallery import ImagePreviewDialog
from app.config.settings import Settings
from app.database import Database
from app.schemas import EvidenceCreate
from app.services import Services
from app.views.service_evidence_dialog import ServiceEvidenceDialog

from tests.conftest import FakePage, Workflow


def _create_image(tmp_path: Path) -> Path:
    path = tmp_path / "evidencia.png"
    Image.new("RGB", (50, 40), (200, 120, 80)).save(path)
    return path


def _dialog(
    database: Database,
    settings: Settings,
    workflow: Workflow,
    page: FakePage,
    file_picker=None,
) -> ServiceEvidenceDialog:
    services = Services(database, settings)
    service = services.services.get_service_or_raise(workflow.service_id)
    return ServiceEvidenceDialog(page, services, service, file_picker)


@pytest.mark.integration
def test_dialog_shows_gallery_with_evidence(
    database: Database,
    settings: Settings,
    workflow: Workflow,
    tmp_path: Path,
) -> None:
    services = Services(database, settings)
    services.evidence.add_evidence(
        EvidenceCreate(service_id=workflow.service_id),
        _create_image(tmp_path),
    )
    page = FakePage()

    dialog = _dialog(database, settings, workflow, page)

    assert isinstance(dialog._gallery_slot.content, ft.GridView)  # noqa: SLF001


@pytest.mark.integration
def test_dialog_reports_add_without_file_picker(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    page = FakePage()
    dialog = _dialog(database, settings, workflow, page)

    dialog._handle_add(None)  # noqa: SLF001

    assert page.dialogs, "debe avisarse de que no hay selector de archivos"


@pytest.mark.integration
def test_dialog_deletes_evidence_and_file(
    database: Database,
    settings: Settings,
    workflow: Workflow,
    tmp_path: Path,
) -> None:
    services = Services(database, settings)
    evidence = services.evidence.add_evidence(
        EvidenceCreate(service_id=workflow.service_id),
        _create_image(tmp_path),
    )
    stored = settings.storage_dir / evidence.filepath
    page = FakePage()
    dialog = _dialog(database, settings, workflow, page)

    dialog._delete(evidence)  # noqa: SLF001

    assert services.evidence.count_evidence_by_service(workflow.service_id) == 0
    assert not stored.exists()
    assert page.dialogs


@pytest.mark.integration
def test_preview_dialog_builds(
    database: Database,
    settings: Settings,
    workflow: Workflow,
    tmp_path: Path,
) -> None:
    services = Services(database, settings)
    source = _create_image(tmp_path)
    evidence = services.evidence.add_evidence(
        EvidenceCreate(service_id=workflow.service_id), source
    )
    page = FakePage()

    preview = ImagePreviewDialog(
        page,
        services.evidence.absolute_path(evidence),
        title=evidence.filename,
        description="Estado final del equipo",
    )
    preview.show()

    assert page.dialogs
