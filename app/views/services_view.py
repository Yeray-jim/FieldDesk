"""Services screen (integrated in Phase 6)."""

from __future__ import annotations

import flet as ft

from app.views.placeholder import PlaceholderView


class ServicesView(PlaceholderView):
    """Placeholder for the services module."""

    title = "Servicios"
    icon = ft.Icons.ASSIGNMENT_OUTLINED
    message = (
        "Aquí se gestionarán los servicios, sus visitas, materiales e "
        "incidencias."
    )
