"""Unit tests for the internationalisation helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.utils import i18n


@pytest.fixture(autouse=True)
def _reset_language():
    i18n.set_language("es")
    yield
    i18n.set_language("es")


@pytest.mark.unit
def test_default_language_is_spanish() -> None:
    assert i18n.get_language() == "es"
    assert i18n.t("Guardar") == "Guardar"


@pytest.mark.unit
def test_english_translation() -> None:
    i18n.set_language("en")

    assert i18n.t("Guardar") == "Save"
    assert i18n.t("Panel de control") == "Dashboard"
    assert i18n.t("Este campo es obligatorio.") == "This field is required."


@pytest.mark.unit
def test_unknown_language_falls_back_to_spanish() -> None:
    assert i18n.set_language("fr") == "es"
    assert i18n.get_language() == "es"


@pytest.mark.unit
def test_missing_translation_returns_source() -> None:
    i18n.set_language("en")

    assert i18n.t("Texto sin traducción") == "Texto sin traducción"


@pytest.mark.unit
def test_preferences_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "preferences.json"

    i18n.save_language(path, "en")

    assert path.is_file()
    assert i18n.load_language(path) == "en"
    assert i18n.get_language() == "en"


@pytest.mark.unit
def test_load_missing_file_defaults_to_spanish(tmp_path: Path) -> None:
    assert i18n.load_language(tmp_path / "nope.json") == "es"
