"""Unit tests for image helpers and the evidence gallery."""

from __future__ import annotations

from pathlib import Path

import flet as ft
import pytest
from PIL import Image

from app.components.gallery import image_thumbnail
from app.utils.files import make_thumbnail, read_image_bytes


def _create_png(tmp_path: Path) -> Path:
    path = tmp_path / "captura.png"
    Image.new("RGB", (80, 60), (30, 90, 160)).save(path)
    return path


@pytest.mark.unit
def test_make_thumbnail_returns_jpeg_bytes(tmp_path: Path) -> None:
    data = make_thumbnail(_create_png(tmp_path))

    assert data is not None
    assert data[:2] == b"\xff\xd8"


@pytest.mark.unit
def test_make_thumbnail_handles_non_image(tmp_path: Path) -> None:
    path = tmp_path / "nota.txt"
    path.write_text("no soy una imagen")

    assert make_thumbnail(path) is None


@pytest.mark.unit
def test_read_image_bytes(tmp_path: Path) -> None:
    path = _create_png(tmp_path)

    assert read_image_bytes(path) == path.read_bytes()
    assert read_image_bytes(tmp_path / "no-existe.png") is None


@pytest.mark.unit
def test_image_thumbnail_control(tmp_path: Path) -> None:
    assert isinstance(image_thumbnail(_create_png(tmp_path)), ft.Image)

    broken = tmp_path / "roto.jpg"
    broken.write_bytes(b"contenido invalido")
    assert isinstance(image_thumbnail(broken), ft.Container)
