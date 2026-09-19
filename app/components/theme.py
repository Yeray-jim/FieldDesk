"""Visual design system for FieldDesk.

Moderate glassmorphism with light and dark palettes. The active palette is
resolved at runtime by :func:`apply_theme` based on the page theme mode, so
the components only need to read the :class:`Palette` attributes.
"""

from __future__ import annotations

import flet as ft

_LIGHT: dict[str, str] = {
    "BACKGROUND_START": "#EEF2FF",
    "BACKGROUND_MID": "#E0E7FF",
    "BACKGROUND_END": "#E0F2FE",
    "SURFACE": "#FFFFFF",
    "TEXT": "#0F172A",
    "TEXT_MUTED": "#334155",
    "BORDER": "#CBD5E1",
    "PRIMARY": "#4F46E5",
    "PRIMARY_DARK": "#4338CA",
    "ON_PRIMARY": "#FFFFFF",
    "SUCCESS": "#15803D",
    "WARNING": "#B45309",
    "DANGER": "#B91C1C",
    "INFO": "#0369A1",
    "NEUTRAL": "#475569",
}

_DARK: dict[str, str] = {
    "BACKGROUND_START": "#0B1220",
    "BACKGROUND_MID": "#111C33",
    "BACKGROUND_END": "#0E1626",
    "SURFACE": "#1E293B",
    "TEXT": "#E2E8F0",
    "TEXT_MUTED": "#CBD5E1",
    "BORDER": "#475569",
    "PRIMARY": "#818CF8",
    "PRIMARY_DARK": "#6366F1",
    "ON_PRIMARY": "#0B1220",
    "SUCCESS": "#4ADE80",
    "WARNING": "#FBBF24",
    "DANGER": "#F87171",
    "INFO": "#38BDF8",
    "NEUTRAL": "#94A3B8",
}

_DARK_MODE = False


class Palette:
    """Active colour tokens (values are set by :func:`apply_theme`)."""

    BACKGROUND_START = _LIGHT["BACKGROUND_START"]
    BACKGROUND_MID = _LIGHT["BACKGROUND_MID"]
    BACKGROUND_END = _LIGHT["BACKGROUND_END"]
    SURFACE = _LIGHT["SURFACE"]
    TEXT = _LIGHT["TEXT"]
    TEXT_MUTED = _LIGHT["TEXT_MUTED"]
    BORDER = _LIGHT["BORDER"]
    PRIMARY = _LIGHT["PRIMARY"]
    PRIMARY_DARK = _LIGHT["PRIMARY_DARK"]
    ON_PRIMARY = _LIGHT["ON_PRIMARY"]
    SUCCESS = _LIGHT["SUCCESS"]
    WARNING = _LIGHT["WARNING"]
    DANGER = _LIGHT["DANGER"]
    INFO = _LIGHT["INFO"]
    NEUTRAL = _LIGHT["NEUTRAL"]


class Metrics:
    """Spacing, radius and effect tokens."""

    RADIUS_SMALL = 8
    RADIUS = 14
    RADIUS_LARGE = 20

    SPACING_SMALL = 8
    SPACING = 16
    SPACING_LARGE = 24

    GLASS_OPACITY = 0.72
    BORDER_OPACITY = 0.55


class FontSize:
    """Font size tokens."""

    TITLE = 22
    HEADING = 16
    BODY = 14
    CAPTION = 12


def _apply_palette(dark: bool) -> None:
    global _DARK_MODE
    _DARK_MODE = dark
    source = _DARK if dark else _LIGHT
    for key, value in source.items():
        setattr(Palette, key, value)


def is_dark() -> bool:
    """Return whether the dark palette is active."""
    return _DARK_MODE


def background_gradient() -> ft.LinearGradient:
    """Return the application background gradient."""
    return ft.LinearGradient(
        colors=[
            Palette.BACKGROUND_START,
            Palette.BACKGROUND_MID,
            Palette.BACKGROUND_END,
        ],
        begin=ft.Alignment.TOP_LEFT,
        end=ft.Alignment.BOTTOM_RIGHT,
    )


def glass_surface_color() -> str:
    """Return the translucent colour used by glass surfaces."""
    if _DARK_MODE:
        return ft.Colors.with_opacity(0.55, "#111827")
    return ft.Colors.with_opacity(Metrics.GLASS_OPACITY, ft.Colors.WHITE)


def chrome_color() -> str:
    """Return the translucent colour used by navigation chrome."""
    if _DARK_MODE:
        return ft.Colors.with_opacity(0.65, "#0F172A")
    return ft.Colors.with_opacity(0.5, ft.Colors.WHITE)


def table_heading_color() -> str:
    """Return the colour of a data table heading row."""
    if _DARK_MODE:
        return ft.Colors.with_opacity(0.25, ft.Colors.WHITE)
    return ft.Colors.with_opacity(0.06, "#0F172A")


def table_row_color() -> str:
    """Return the base colour of a data table row."""
    if _DARK_MODE:
        return ft.Colors.with_opacity(0.04, ft.Colors.WHITE)
    return ft.Colors.with_opacity(0.35, ft.Colors.WHITE)


def glass_border() -> ft.Border:
    """Return the subtle border used by glass surfaces."""
    return ft.Border.all(
        1,
        ft.Colors.with_opacity(Metrics.BORDER_OPACITY, Palette.BORDER),
    )


def soft_shadow() -> ft.BoxShadow:
    """Return the soft shadow used by glass surfaces."""
    opacity = 0.45 if _DARK_MODE else 0.18
    return ft.BoxShadow(
        blur_radius=18,
        spread_radius=-6,
        color=ft.Colors.with_opacity(opacity, "#000000"),
        offset=ft.Offset(0, 8),
    )


def _make_theme(values: dict[str, str]) -> ft.Theme:
    return ft.Theme(
        color_scheme_seed=values["PRIMARY"],
        use_material3=True,
        primary_text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(color=values["TEXT"], size=FontSize.BODY)
        ),
        hint_color=values["TEXT_MUTED"],
        unselected_control_color=values["TEXT_MUTED"],
        secondary_header_color=values["TEXT_MUTED"],
        navigation_rail_theme=ft.NavigationRailTheme(
            unselected_label_text_style=ft.TextStyle(
                color=values["TEXT_MUTED"]
            ),
            selected_label_text_style=ft.TextStyle(color=values["PRIMARY"]),
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            label_text_style=ft.TextStyle(color=values["TEXT_MUTED"]),
        ),
    )


def build_theme() -> ft.Theme:
    """Build the light Flet theme."""
    return _make_theme(_LIGHT)


def build_dark_theme() -> ft.Theme:
    """Build the dark Flet theme."""
    return _make_theme(_DARK)


def apply_theme(page: ft.Page) -> None:
    """Resolve and apply the active palette and page defaults."""
    mode = page.theme_mode
    if mode == ft.ThemeMode.DARK:
        dark = True
    elif mode == ft.ThemeMode.LIGHT:
        dark = False
    else:
        dark = page.platform_brightness == ft.Brightness.DARK

    _apply_palette(dark)
    page.theme = build_theme()
    page.dark_theme = build_dark_theme()
    page.bgcolor = Palette.BACKGROUND_START
    page.padding = 0
    page.spacing = 0
    page.fonts = {}
