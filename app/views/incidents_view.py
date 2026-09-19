"""Incidents screen (integrated in Phase 6)."""

from __future__ import annotations

import flet as ft

from app.views.placeholder import PlaceholderView


class IncidentsView(PlaceholderView):
    """Placeholder for the incidents module."""

    title = "Incidencias"
    icon = ft.Icons.WARNING_AMBER_OUTLINED
    message = (
        "Aquí se registrarán las incidencias de los equipos y su resolución."
    )
