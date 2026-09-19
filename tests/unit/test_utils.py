"""Unit tests for the shared utilities."""

from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path

import pytest

from app.database.models import EquipmentStatus, Priority
from app.utils import dates, files, labels, validators
from app.utils.exceptions import ValidationError


@pytest.mark.unit
def test_email_validator() -> None:
    assert validators.is_valid_email("contacto@empresa.com")
    assert not validators.is_valid_email("no-es-email")
    assert not validators.is_valid_email("sin-arroba.com")


@pytest.mark.unit
def test_blank_validator() -> None:
    assert validators.is_blank(None)
    assert validators.is_blank("   ")
    assert not validators.is_blank("texto")


@pytest.mark.unit
def test_status_labels() -> None:
    assert labels.status_label(EquipmentStatus.OPERATIONAL) == "Operativo"
    assert labels.status_label("PENDING") == "Pendiente"
    assert labels.status_label(Priority.HIGH) == "Alta"
    assert labels.status_label("DESCONOCIDO_X") == "Desconocido X"
    assert labels.normalize_status(Priority.MEDIUM) == "MEDIUM"


@pytest.mark.unit
def test_date_formatting() -> None:
    assert dates.utcnow().tzinfo is None
    assert dates.format_date(None) == "—"
    assert dates.format_datetime(None) == "—"
    assert dates.format_time(None) == "—"
    assert dates.format_date(date(2026, 1, 2)) == "02/01/2026"
    assert dates.format_datetime(datetime(2026, 1, 2, 15, 30)) == "02/01/2026 15:30"
    assert dates.format_time(time(9, 5)) == "09:05"


@pytest.mark.unit
def test_twelve_hour_conversions() -> None:
    assert dates.to_12h(time(9, 30)) == "09:30 AM"
    assert dates.to_12h(time(15, 5)) == "03:05 PM"
    assert dates.to_12h(None) is None

    assert dates.to_24h("09:30 AM") == "09:30"
    assert dates.to_24h("3:05 PM") == "15:05"
    assert dates.to_24h("12:00 AM") == "00:00"
    assert dates.to_24h("12:00 PM") == "12:00"
    assert dates.to_24h("21:45") == "21:45"


@pytest.mark.unit
def test_combine_date_and_time() -> None:
    assert dates.combine(date(2026, 1, 2), None) is None
    assert dates.combine(date(2026, 1, 2), time(8, 0)) == datetime(
        2026, 1, 2, 8, 0
    )


@pytest.mark.unit
def test_unique_filename_keeps_extension() -> None:
    first = files.unique_filename("FOTO.JPG")
    second = files.unique_filename("FOTO.JPG")

    assert first.endswith(".jpg")
    assert first != second


@pytest.mark.unit
def test_supported_image_extensions() -> None:
    assert files.is_supported_image(Path("foto.png"))
    assert files.is_supported_image(Path("foto.JPEG"))
    assert not files.is_supported_image(Path("nota.txt"))


@pytest.mark.unit
def test_store_image_rejects_missing_and_unsupported(tmp_path: Path) -> None:
    with pytest.raises(ValidationError):
        files.store_image(tmp_path / "no-existe.jpg", tmp_path / "destino")

    unsupported = tmp_path / "nota.txt"
    unsupported.write_text("texto")
    with pytest.raises(ValidationError):
        files.store_image(unsupported, tmp_path / "destino")


@pytest.mark.unit
def test_delete_file_is_idempotent(tmp_path: Path) -> None:
    files.delete_file(tmp_path / "no-existe.bin")

    target = tmp_path / "archivo.bin"
    target.write_bytes(b"x")
    files.delete_file(target)
    assert not target.exists()
