"""Materials screen (integrated in Phase 6)."""

from __future__ import annotations

import flet as ft

from app.views.placeholder import PlaceholderView


class MaterialsView(PlaceholderView):
    """Placeholder for the materials module."""

    title = "Materiales"
    icon = ft.Icons.INVENTORY_2_OUTLINED
    message = (
        "Aquí se administrará el catálogo de materiales y su consumo en los "
        "servicios."
    )
