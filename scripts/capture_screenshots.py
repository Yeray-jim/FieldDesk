"""Development utility that generates the documentation screenshots.

It creates a throw-away database, loads the demonstration data, renders the
application and captures each main screen into ``docs/images/``.

Usage:
    python scripts/capture_screenshots.py
"""

from __future__ import annotations

import asyncio
import shutil
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import flet as ft  # noqa: E402

from app.config.settings import Settings  # noqa: E402
from app.database import Database  # noqa: E402
from app.database.migrations import run_migrations  # noqa: E402
from app.components.theme import apply_theme  # noqa: E402
from app.services import Services  # noqa: E402
from app.views.app_shell import AppShell  # noqa: E402
from app.views.context import AppContext  # noqa: E402

IMAGES_DIR = ROOT / "docs" / "images"

# (navigation index, output file name)
SCREENS = [
    (1, "02_clientes"),
    (3, "03_servicios"),
    (4, "04_incidencias"),
    (6, "05_ajustes"),
]


def _demo_settings() -> Settings:
    demo_dir = ROOT / "storage" / "demo"
    shutil.rmtree(demo_dir, ignore_errors=True)
    base = Settings.from_env()
    settings = replace(
        base,
        storage_dir=demo_dir,
        database_path=demo_dir / "database" / "fielddesk.db",
        images_dir=demo_dir / "images",
        documents_dir=demo_dir / "documents",
        backups_dir=demo_dir / "backups",
        logs_dir=demo_dir / "logs",
    )
    settings.ensure_directories()
    return settings


async def _capture(screenshot: ft.Screenshot, name: str) -> None:
    data = await screenshot.capture(pixel_ratio=1.0, delay=400)
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    (IMAGES_DIR / f"{name}.png").write_bytes(data)
    print(f"saved {name}.png ({len(data)} bytes)")


def main(page: ft.Page) -> None:
    page.window.width = 940
    page.window.height = 1000
    page.enable_screenshots = True
    page.theme_mode = ft.ThemeMode.LIGHT

    settings = _demo_settings()
    run_migrations(settings)
    database = Database(settings.database_url)
    services = Services(database, settings)
    services.demo.load()

    context = AppContext(
        page=page,
        settings=settings,
        services=services,
        file_picker=ft.FilePicker(),
        url_launcher=ft.UrlLauncher(),
    )
    apply_theme(page)
    shell = AppShell(context)
    screenshot = ft.Screenshot(content=shell.build_root(), expand=True)
    page.add(screenshot)
    page.update()

    async def sequence() -> None:
        await asyncio.sleep(2.5)
        await _capture(screenshot, "01_dashboard")
        for index, name in SCREENS:
            shell._on_nav_change(  # noqa: SLF001
                SimpleNamespace(
                    control=SimpleNamespace(selected_index=index)
                )
            )
            await asyncio.sleep(1.0)
            await _capture(screenshot, name)

        page.theme_mode = ft.ThemeMode.DARK
        shell._on_nav_change(  # noqa: SLF001
            SimpleNamespace(control=SimpleNamespace(selected_index=0))
        )
        await asyncio.sleep(1.2)
        await _capture(screenshot, "06_panel_oscuro")
        print("screenshots done")

    page.run_task(sequence)


if __name__ == "__main__":
    ft.run(main, assets_dir=str(ROOT / "assets"))
