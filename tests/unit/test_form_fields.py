"""Unit tests for the date and time form fields."""

from __future__ import annotations

from datetime import date, datetime, time
from types import SimpleNamespace

import pytest

from app.components.forms import GlassDateField, GlassTimeField

from tests.conftest import FakePage


@pytest.mark.unit
def test_date_field_formats_selected_date() -> None:
    page = FakePage()
    field = GlassDateField(page, "Fecha", required=True)

    assert field.read_only is True
    assert field.label.endswith("*")

    field._on_date_change(  # noqa: SLF001
        SimpleNamespace(control=SimpleNamespace(value=datetime(2026, 1, 15)))
    )

    assert field.value == "2026-01-15"


@pytest.mark.unit
def test_date_field_accepts_plain_date() -> None:
    page = FakePage()
    field = GlassDateField(page, "Fecha")

    field._on_date_change(  # noqa: SLF001
        SimpleNamespace(control=SimpleNamespace(value=date(2026, 3, 2)))
    )

    assert field.value == "2026-03-02"


@pytest.mark.unit
def test_time_field_formats_selected_time() -> None:
    page = FakePage()
    field = GlassTimeField(page, "Hora")

    field._on_time_change(  # noqa: SLF001
        SimpleNamespace(control=SimpleNamespace(value=time(9, 30)))
    )

    assert field.value == "09:30"
