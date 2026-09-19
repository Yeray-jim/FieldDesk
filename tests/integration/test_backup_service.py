"""Integration tests for :class:`BackupService`."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
from PIL import Image

from app.config.settings import Settings
from app.database import Database
from app.schemas import ClientCreate, EvidenceCreate
from app.services import Services
from app.utils.exceptions import StorageError, ValidationError

from tests.conftest import Workflow


def _create_image(tmp_path: Path) -> Path:
    path = tmp_path / "evidencia.png"
    Image.new("RGB", (48, 36), (120, 80, 40)).save(path)
    return path


@pytest.mark.integration
def test_backup_contains_expected_members(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    services.evidence.add_evidence(
        EvidenceCreate(service_id=workflow.service_id),
        _create_image(settings.project_root),
    )

    archive = services.backups.create_backup()

    assert archive.is_file()
    with zipfile.ZipFile(archive) as archive_file:
        names = set(archive_file.namelist())
    assert "manifest.json" in names
    assert "database/fielddesk.db" in names
    assert any(name.startswith("images/") for name in names)


@pytest.mark.integration
def test_validate_rejects_non_zip(
    database: Database,
    settings: Settings,
    tmp_path: Path,
) -> None:
    path = tmp_path / "no-es-backup.txt"
    path.write_text("hola")

    with pytest.raises(ValidationError):
        Services(database, settings).backups.validate_backup(path)


@pytest.mark.integration
def test_validate_rejects_zip_without_manifest(
    database: Database,
    settings: Settings,
    tmp_path: Path,
) -> None:
    archive = tmp_path / "sin-manifiesto.zip"
    with zipfile.ZipFile(archive, "w") as archive_file:
        archive_file.writestr("database/fielddesk.db", b"dummy")

    with pytest.raises(ValidationError):
        Services(database, settings).backups.validate_backup(archive)


@pytest.mark.integration
def test_restore_replaces_current_data(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    backup = services.backups.create_backup()
    services.clients.create_client(ClientCreate(name="Cliente posterior"))
    assert services.clients.count_clients() == 2

    services.backups.restore_backup(backup)

    assert services.clients.count_clients() == 1
    names = [client.name for client in services.clients.list_clients()]
    assert "Cliente posterior" not in names
    assert "Empresa XYZ" in names


@pytest.mark.integration
def test_restore_creates_a_safety_backup(
    database: Database,
    settings: Settings,
    workflow: Workflow,
) -> None:
    services = Services(database, settings)
    backup = services.backups.create_backup()

    services.backups.restore_backup(backup)

    safety = list(settings.backups_dir.glob("*pre_restore*.zip"))
    assert safety, "debe crearse una copia de seguridad previa"


@pytest.mark.integration
def test_restore_rejects_unsafe_paths(
    database: Database,
    settings: Settings,
    tmp_path: Path,
) -> None:
    archive = tmp_path / "malicioso.zip"
    with zipfile.ZipFile(archive, "w") as archive_file:
        archive_file.writestr(
            "manifest.json",
            json.dumps({"app_name": "FieldDesk", "app_version": "0.1.0"}),
        )
        archive_file.writestr("database/fielddesk.db", b"dummy")
        archive_file.writestr("../evil.txt", b"boom")

    service = Services(database, settings).backups

    with pytest.raises((ValidationError, StorageError)):
        service.restore_backup(archive)
    assert not (tmp_path / "evil.txt").exists()
