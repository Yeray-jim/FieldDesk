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
            scrollable=True,
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


class AppBottomBar(ft.Container):
    """A horizontally scrollable bottom navigation bar for mobile.

    Unlike the Material ``NavigationBar`` it scrolls, so every destination
    stays reachable on small screens and in landscape orientation.
    """

    def __init__(
        self,
        items: list[NavigationItem],
        *,
        selected_index: int = 0,
        on_select: Callable[[int], None] | None = None,
    ) -> None:
        self._items = items
        self._on_select = on_select
        self._selected = selected_index
        self._row = ft.Row(
            controls=self._buttons(),
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        super().__init__(
            content=self._row,
            bgcolor=chrome_color(),
            padding=ft.Padding.symmetric(vertical=4, horizontal=4),
        )

    def _buttons(self) -> list[ft.Control]:
        buttons: list[ft.Control] = []
        for index, item in enumerate(self._items):
            selected = index == self._selected
            icon = item.selected_icon if selected else item.icon
            color = Palette.PRIMARY if selected else Palette.TEXT_MUTED
            buttons.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(icon, color=color, size=22),
                            ft.Text(
                                t(item.label),
                                size=10,
                                color=color,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    width=84,
                    padding=ft.Padding.symmetric(vertical=6, horizontal=6),
                    border_radius=Metrics.RADIUS,
                    bgcolor=(
                        ft.Colors.with_opacity(0.14, Palette.PRIMARY)
                        if selected
                        else None
                    ),
                    alignment=ft.Alignment.CENTER,
                    tooltip=item.label,
                    on_click=lambda _event, i=index: self._select(i),
                )
            )
        return buttons

    def _select(self, index: int) -> None:
        if self._on_select is not None:
            self._on_select(index)

    def set_selected(self, index: int) -> None:
        """Update the highlighted destination without rebuilding the shell."""
        self._selected = index
        self._row.controls = self._buttons()
