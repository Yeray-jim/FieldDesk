"""Clients screen (integrated in Phase 6)."""

from __future__ import annotations

import flet as ft

from app.views.placeholder import PlaceholderView


class ClientsView(PlaceholderView):
    """Placeholder for the clients module."""

    title = "Clientes"
    icon = ft.Icons.PEOPLE_OUTLINED
    message = (
        "Aquí se administrarán los clientes, sus ubicaciones y sus servicios. "
        "La integración con los servicios de negocio llega en la Fase 6."
    )
