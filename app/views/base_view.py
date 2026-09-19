"""Base class for the application screens."""

from __future__ import annotations

import flet as ft

from app.views.context import AppContext


class BaseView:
    """A screen built from the application context.

    Subclasses implement :meth:`build`, returning the root control of the
    screen. Views must not contain business logic; they call services and
    render the result.
    """

    title: str = ""
    icon: ft.IconData | None = None

    def __init__(self, context: AppContext) -> None:
        self.context = context
        self.page = context.page
        self.settings = context.settings
        self.services = context.services

    def build(self) -> ft.Control:
        """Build and return the screen content."""
        raise NotImplementedError

    def refresh(self) -> None:
        """Hook for views that need to reload their data."""
