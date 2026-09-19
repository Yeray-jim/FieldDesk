"""Integration tests for the demonstration data loader."""

from __future__ import annotations

import pytest

from app.config.settings import Settings
from app.database import Database
from app.services import DemoDataService
from app.utils.exceptions import ConflictError


@pytest.mark.integration
def test_load_creates_the_demo_dataset(
    database: Database,
    settings: Settings,
) -> None:
    service = DemoDataService(database, settings)
    assert service.has_data() is False

    summary = service.load()

    assert summary.clients == 5
    assert summary.locations == 8
    assert summary.equipment == 12
    assert summary.services == 15
    assert summary.incidents == 8
    assert summary.materials == 20
    assert summary.evidences == 3
    assert service.has_data() is True


@pytest.mark.integration
def test_load_is_refused_when_data_exists(
    database: Database,
    settings: Settings,
) -> None:
    service = DemoDataService(database, settings)
    service.load()

    with pytest.raises(ConflictError):
        service.load()
