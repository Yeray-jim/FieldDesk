"""Unit tests for the light/dark theme resolution."""

from __future__ import annotations

import flet as ft
import pytest

from app.components import theme

from tests.conftest import FakePage


@pytest.mark.unit
def test_apply_light_theme() -> None:
    page = FakePage()
    page.theme_mode = ft.ThemeMode.LIGHT

    theme.apply_theme(page)

    assert theme.is_dark() is False
    assert theme.Palette.TEXT == "#0F172A"
    assert page.theme is not None
    assert page.dark_theme is not None


@pytest.mark.unit
def test_apply_dark_theme_updates_palette() -> None:
    page = FakePage()
    page.theme_mode = ft.ThemeMode.DARK

    theme.apply_theme(page)
    dark_text = theme.Palette.TEXT
    dark_surface = theme.Palette.SURFACE

    assert theme.is_dark() is True
    assert dark_text == "#E2E8F0"
    assert dark_surface == "#1E293B"

    # Restore the light palette for the rest of the suite.
    page.theme_mode = ft.ThemeMode.LIGHT
    theme.apply_theme(page)
