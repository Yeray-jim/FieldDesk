"""Placeholder screen for modules not yet integrated.

These screens reuse the design system so the application is navigable and
consistent while the CRUD screens are implemented in later phases.
"""

from __future__ import annotations

import flet as ft

from app.components.cards import EmptyState, GlassCard, SectionHeader
from app.components.theme import Metrics
from app.views.base_view import BaseView


class PlaceholderView(BaseView):
    """Generic placeholder for a module pending integration."""

    message = "Este módulo se conectará a los servicios en la siguiente fase."

    def build(self) -> ft.Control:
        return ft.Column(
            controls=[
                SectionHeader(self.title, icon=self.icon),
                GlassCard(
                    content=ft.Container(
                        content=EmptyState(
                            self.title,
                            self.message,
                            icon=self.icon or ft.Icons.CONSTRUCTION_OUTLINED,
                        ),
                        padding=Metrics.SPACING_LARGE,
                        alignment=ft.Alignment.CENTER,
                    )
                ),
            ],
            spacing=Metrics.SPACING,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
