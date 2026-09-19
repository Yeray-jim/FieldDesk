"""Responsive navigation controls.

Desktop uses a :class:`ft.NavigationRail`; mobile uses a bottom
:class:`ft.NavigationBar`. Both are built from the same
:class:`NavigationItem` definitions so destinations stay consistent.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import flet as ft

from app.components.theme import Metrics, Palette, chrome_color
from app.utils.i18n import t


@dataclass(frozen=True)
class NavigationItem:
    """A single navigation destination."""

    key: str
    label: str
    icon: ft.IconData
    selected_icon: ft.IconData


class AppNavigationRail(ft.NavigationRail):
    """Desktop side navigation with a translucent background."""

    def __init__(
        self,
        items: list[NavigationItem],
        *,
        selected_index: int = 0,
        on_change: Callable | None = None,
        leading: ft.Control | None = None,
    ) -> None:
        super().__init__(
            selected_index=selected_index,
            on_change=on_change,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icon(item.icon, color=Palette.TEXT_MUTED),
                    selected_icon=ft.Icon(
                        item.selected_icon, color=Palette.PRIMARY
                    ),
                    label=t(item.label),
                )
                for item in items
            ],
            label_type=ft.NavigationRailLabelType.ALL,
            bgcolor=chrome_color(),
            indicator_color=ft.Colors.with_opacity(0.14, Palette.PRIMARY),
            min_width=96,
            leading=leading,
            group_alignment=-0.9,
        )


class AppNavigationBar(ft.NavigationBar):
    """Mobile bottom navigation with a translucent background."""

    def __init__(
        self,
        items: list[NavigationItem],
        *,
        selected_index: int = 0,
        on_change: Callable | None = None,
    ) -> None:
        super().__init__(
            selected_index=selected_index,
            on_change=on_change,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icon(item.icon, color=Palette.TEXT_MUTED),
                    selected_icon=ft.Icon(
                        item.selected_icon, color=Palette.PRIMARY
                    ),
                    label=t(item.label),
                )
                for item in items
            ],
            bgcolor=chrome_color(),
            indicator_color=ft.Colors.with_opacity(0.14, Palette.PRIMARY),
            label_behavior=ft.NavigationBarLabelBehavior.ONLY_SHOW_SELECTED,
        )
