"""Integration tests for :class:`EvidenceService`."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config.settings import Settings
from app.schemas import EvidenceCreate
from app.services import EvidenceService
from app.utils.exceptions import NotFoundError, ValidationError

from tests.conftest import Workflow


def _fake_image(tmp_path: Path, name: str = "foto.jpg") -> Path:
    """Create a small file with a supported image extension."""
    path = tmp_path / name
    path.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-content")
    return path


@pytest.mark.integration
def test_add_evidence_stores_file_and_metadata(
    workflow: Workflow,
    evidence_service: EvidenceService,
    settings: Settings,
    tmp_path: Path,
) -> None:
    source = _fake_image(tmp_path)

    evidence = evidence_service.add_evidence(
        EvidenceCreate(service_id=workflow.service_id, description="Antes"),
        source,
    )

    assert evidence.filepath.startswith("images/")
    assert (settings.storage_dir / evidence.filepath).is_file()
    assert evidence_service.count_evidence_by_service(workflow.service_id) == 1


@pytest.mark.integration
def test_add_evidence_rejects_unsupported_file(
    workflow: Workflow,
    evidence_service: EvidenceService,
    tmp_path: Path,
) -> None:
    path = tmp_path / "nota.txt"
    path.write_text("no soy una imagen")

    with pytest.raises(ValidationError):
        evidence_service.add_evidence(
            EvidenceCreate(service_id=workflow.service_id), path
        )


@pytest.mark.integration
def test_add_evidence_rejects_missing_file(
    workflow: Workflow,
    evidence_service: EvidenceService,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValidationError):
        evidence_service.add_evidence(
            EvidenceCreate(service_id=workflow.service_id),
            tmp_path / "no-existe.jpg",
        )


@pytest.mark.integration
def test_add_evidence_requires_existing_service(
    evidence_service: EvidenceService,
    tmp_path: Path,
) -> None:
    with pytest.raises(NotFoundError):
        evidence_service.add_evidence(
            EvidenceCreate(service_id=999),
            _fake_image(tmp_path),
        )


@pytest.mark.integration
def test_delete_evidence_removes_record_and_file(
    workflow: Workflow,
    evidence_service: EvidenceService,
    settings: Settings,
    tmp_path: Path,
) -> None:
    evidence = evidence_service.add_evidence(
        EvidenceCreate(service_id=workflow.service_id),
        _fake_image(tmp_path),
    )
    stored = settings.storage_dir / evidence.filepath
    assert stored.is_file()

    evidence_service.delete_evidence(evidence.id)

    assert not stored.exists()
    assert evidence_service.count_evidence_by_service(workflow.service_id) == 0
