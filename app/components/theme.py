"""Visual design system for FieldDesk.

Moderate glassmorphism: translucent white surfaces over a soft gradient with
a light blur and a subtle shadow. The priority is usability and legibility,
so transparency and blur are restrained.
"""

from __future__ import annotations

import flet as ft


class Palette:
    """Application colour tokens."""

    BACKGROUND_START = "#EEF2FF"
    BACKGROUND_MID = "#E0E7FF"
    BACKGROUND_END = "#E0F2FE"

    SURFACE = "#FFFFFF"
    TEXT = "#0F172A"
    TEXT_MUTED = "#334155"
    BORDER = "#CBD5E1"

    PRIMARY = "#4F46E5"
    PRIMARY_DARK = "#4338CA"
    ON_PRIMARY = "#FFFFFF"

    SUCCESS = "#15803D"
    WARNING = "#B45309"
    DANGER = "#B91C1C"
    INFO = "#0369A1"
    NEUTRAL = "#475569"


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
    return ft.Colors.with_opacity(Metrics.GLASS_OPACITY, ft.Colors.WHITE)


def glass_border() -> ft.Border:
    """Return the subtle border used by glass surfaces."""
    return ft.Border.all(
        1,
        ft.Colors.with_opacity(Metrics.BORDER_OPACITY, Palette.BORDER),
    )


def soft_shadow() -> ft.BoxShadow:
    """Return the soft shadow used by glass surfaces."""
    return ft.BoxShadow(
        blur_radius=18,
        spread_radius=-6,
        color=ft.Colors.with_opacity(0.18, "#0F172A"),
        offset=ft.Offset(0, 8),
    )


def build_theme() -> ft.Theme:
    """Build the Flet theme derived from the design tokens."""
    return ft.Theme(
        color_scheme_seed=Palette.PRIMARY,
        use_material3=True,
        primary_text_theme=ft.TextTheme(
            body_medium=ft.TextStyle(color=Palette.TEXT, size=FontSize.BODY)
        ),
        hint_color=Palette.TEXT_MUTED,
        unselected_control_color=Palette.TEXT_MUTED,
        secondary_header_color=Palette.TEXT_MUTED,
        navigation_rail_theme=ft.NavigationRailTheme(
            unselected_label_text_style=ft.TextStyle(
                color=Palette.TEXT_MUTED
            ),
            selected_label_text_style=ft.TextStyle(color=Palette.PRIMARY),
        ),
        navigation_bar_theme=ft.NavigationBarTheme(
            label_text_style=ft.TextStyle(color=Palette.TEXT_MUTED),
        ),
    )


def apply_theme(page: ft.Page) -> None:
    """Apply the FieldDesk theme and page defaults."""
    page.theme = build_theme()
    page.bgcolor = Palette.BACKGROUND_START
    page.padding = 0
    page.spacing = 0
    page.fonts = {}
