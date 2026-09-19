"""Application shell: responsive navigation and view hosting."""

from __future__ import annotations

import logging
from collections.abc import Callable

import flet as ft

from app.components.buttons import primary_button
from app.components.cards import EmptyState, GlassCard
from app.components.navigation import (
    AppNavigationBar,
    AppNavigationRail,
    NavigationItem,
)
from app.components.theme import (
    FontSize,
    Metrics,
    Palette,
    apply_theme,
    background_gradient,
)
from app.utils.constants import MOBILE_BREAKPOINT
from app.views.base_view import BaseView
from app.views.clients_view import ClientsView
from app.views.context import AppContext
from app.views.dashboard_view import DashboardView
from app.views.equipment_view import EquipmentView
from app.views.incidents_view import IncidentsView
from app.views.materials_view import MaterialsView
from app.views.services_view import ServicesView
from app.views.settings_view import SettingsView

logger = logging.getLogger(__name__)


def _destinations() -> list[NavigationItem]:
    return [
        NavigationItem(
            "dashboard",
            "Panel",
            ft.Icons.DASHBOARD_OUTLINED,
            ft.Icons.DASHBOARD,
        ),
        NavigationItem(
            "clients", "Clientes", ft.Icons.PEOPLE_OUTLINED, ft.Icons.PEOPLE
        ),
        NavigationItem(
            "equipment", "Equipos", ft.Icons.BUILD_OUTLINED, ft.Icons.BUILD
        ),
        NavigationItem(
            "services",
            "Servicios",
            ft.Icons.ASSIGNMENT_OUTLINED,
            ft.Icons.ASSIGNMENT,
        ),
        NavigationItem(
            "incidents",
            "Incidencias",
            ft.Icons.WARNING_AMBER_OUTLINED,
            ft.Icons.WARNING_AMBER,
        ),
        NavigationItem(
            "materials",
            "Materiales",
            ft.Icons.INVENTORY_2_OUTLINED,
            ft.Icons.INVENTORY_2,
        ),
        NavigationItem(
            "settings",
            "Ajustes",
            ft.Icons.SETTINGS_OUTLINED,
            ft.Icons.SETTINGS,
        ),
    ]


def _view_factories() -> dict[str, Callable[[AppContext], BaseView]]:
    return {
        "dashboard": DashboardView,
        "clients": ClientsView,
        "equipment": EquipmentView,
        "services": ServicesView,
        "incidents": IncidentsView,
        "materials": MaterialsView,
        "settings": SettingsView,
    }


class AppShell:
    """Hosts the navigation and the currently selected view.

    The shell adapts between a desktop side rail and a mobile bottom bar
    based on the page width.
    """

    def __init__(self, context: AppContext) -> None:
        self._context = context
        self._page = context.page
        self._items = _destinations()
        self._factories = _view_factories()
        self._selected = 0
        self._is_mobile = False
        self._content = ft.Container(expand=True)
        self._root: ft.Container | None = None

    def render(self) -> None:
        """Apply the theme and mount the shell on the page."""
        apply_theme(self._page)
        self._is_mobile = self._detect_mobile()
        self._content = ft.Container(
            content=self._build_view(self._selected),
            expand=True,
        )
        self._root = ft.Container(
            expand=True,
            gradient=background_gradient(),
            content=self._build_body(),
        )
        self._page.on_resize = self._on_resize
        self._page.add(self._root)
        self._page.update()

    def _detect_mobile(self) -> bool:
        width = self._page.width or 0
        return bool(width and width < MOBILE_BREAKPOINT)

    def _build_view(self, index: int) -> ft.Control:
        key = self._items[index].key
        try:
            view = self._factories[key](self._context)
            content = view.build()
        except Exception:  # noqa: BLE001 - never show a traceback to the user
            logger.exception("No se pudo construir la vista '%s'", key)
            content = self._error_view()
        return ft.Container(
            content=content,
            padding=Metrics.SPACING,
            expand=True,
            alignment=ft.Alignment.TOP_LEFT,
        )

    def _error_view(self) -> ft.Control:
        return GlassCard(
            content=ft.Container(
                content=EmptyState(
                    "No se pudo cargar la pantalla",
                    "Ocurrió un problema inesperado. Inténtalo de nuevo.",
                    icon=ft.Icons.ERROR_OUTLINE,
                ),
                padding=Metrics.SPACING_LARGE,
                alignment=ft.Alignment.CENTER,
            )
        )

    def _build_body(self) -> ft.Control:
        if self._is_mobile:
            return ft.Column(
                controls=[
                    self._app_bar(),
                    ft.Container(content=self._content, expand=True),
                    AppNavigationBar(
                        self._items,
                        selected_index=self._selected,
                        on_change=self._on_nav_change,
                    ),
                ],
                spacing=0,
                expand=True,
            )

        rail = AppNavigationRail(
            self._items,
            selected_index=self._selected,
            on_change=self._on_nav_change,
            leading=self._brand(),
        )
        return ft.Row(
            controls=[
                rail,
                ft.Container(content=self._content, expand=True),
            ],
            spacing=0,
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
        )

    def _app_bar(self) -> ft.Control:
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(
                        ft.Icons.HANDYMAN_OUTLINED,
                        color=Palette.PRIMARY,
                        size=24,
                    ),
                    ft.Text(
                        self._items[self._selected].label,
                        size=FontSize.HEADING,
                        weight=ft.FontWeight.W_600,
                        color=Palette.TEXT,
                    ),
                ],
                spacing=Metrics.SPACING_SMALL,
            ),
            padding=ft.Padding.symmetric(
                horizontal=Metrics.SPACING,
                vertical=Metrics.SPACING_SMALL,
            ),
            bgcolor=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
        )

    def _brand(self) -> ft.Control:
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.HANDYMAN_OUTLINED,
                        color=Palette.PRIMARY,
                        size=30,
                    ),
                    ft.Text(
                        "FieldDesk",
                        size=FontSize.CAPTION,
                        weight=ft.FontWeight.W_600,
                        color=Palette.TEXT,
                    ),
                ],
                spacing=2,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.Padding.only(top=20, bottom=Metrics.SPACING_SMALL),
        )

    def _on_nav_change(self, event: ft.ControlEvent) -> None:
        index = event.control.selected_index
        if index is None or index == self._selected:
            return
        self._selected = index
        self._remount()

    def _on_resize(self, _event: ft.ControlEvent) -> None:
        mobile = self._detect_mobile()
        if mobile == self._is_mobile:
            return
        self._is_mobile = mobile
        self._remount()

    def _remount(self) -> None:
        """Rebuild the body with a fresh content area for the current view."""
        self._content = ft.Container(
            content=self._build_view(self._selected),
            expand=True,
        )
        if self._root is not None:
            self._root.content = self._build_body()
        self._page.update()
