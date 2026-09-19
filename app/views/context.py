"""Shared application context passed to every view."""

from __future__ import annotations

from dataclasses import dataclass

import flet as ft

from app.config.settings import Settings
from app.services import Services


@dataclass
class AppContext:
    """Runtime dependencies available to the user interface."""

    page: ft.Page
    settings: Settings
    services: Services
    file_picker: ft.FilePicker | None = None
    url_launcher: ft.UrlLauncher | None = None
