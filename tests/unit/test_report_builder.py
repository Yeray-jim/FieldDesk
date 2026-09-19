"""Unit tests for the ReportLab report builder."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.report_builder import ReportBuilder, ServiceReportData
from app.utils.dates import utcnow


@pytest.mark.unit
def test_builds_a_valid_pdf(tmp_path: Path) -> None:
    data = ServiceReportData(
        generated_at=utcnow(),
        client=[("Nombre", "Empresa XYZ"), ("Email", "a@b.com")],
        location=[("Nombre", "Sucursal Centro")],
        equipment=[("Nombre", "Bomba"), ("Estado", "Operativo")],
        service=[("Tipo de servicio", "Mantenimiento")],
    )
    output = tmp_path / "reporte.pdf"

    result = ReportBuilder(data).build(output)

    assert result == output
    assert output.read_bytes()[:4] == b"%PDF"
    assert output.stat().st_size > 0


@pytest.mark.unit
def test_builds_with_empty_sections(tmp_path: Path) -> None:
    data = ServiceReportData(
        generated_at=utcnow(),
        client=[],
        location=[],
        equipment=[],
        service=[],
    )
    output = tmp_path / "vacio.pdf"

    ReportBuilder(data).build(output)

    assert output.read_bytes()[:4] == b"%PDF"
