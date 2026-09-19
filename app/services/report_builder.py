"""PDF report composition using ReportLab.

:class:`ReportBuilder` receives a fully materialised
:class:`ServiceReportData` value object, so it can be tested without a
database session and keeps the report layout independent from the data
gathering performed by :class:`~app.services.report_service.ReportService`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image as RLImage,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

PRIMARY = colors.HexColor("#4F46E5")
TEXT = colors.HexColor("#0F172A")
MUTED = colors.HexColor("#64748B")
LIGHT = colors.HexColor("#EEF2FF")
BORDER = colors.HexColor("#CBD5E1")

_MARGIN_X = 18 * mm
_MARGIN_TOP = 16 * mm
_MARGIN_BOTTOM = 18 * mm


@dataclass
class ReportVisit:
    """A visit rendered in the report."""

    date: str
    schedule: str
    work_performed: str
    observations: str


@dataclass
class ReportIncident:
    """An incident rendered in the report."""

    title: str
    priority: str
    status: str
    description: str
    resolution: str


@dataclass
class ReportMaterial:
    """A consumed material rendered in the report."""

    name: str
    quantity: str
    unit: str
    notes: str


@dataclass
class ReportEvidence:
    """An evidence image rendered in the report."""

    path: Path
    description: str


@dataclass
class ServiceReportData:
    """All the information required to render a service report."""

    generated_at: datetime
    client: list[tuple[str, str]]
    location: list[tuple[str, str]]
    equipment: list[tuple[str, str]]
    service: list[tuple[str, str]]
    visits: list[ReportVisit] = field(default_factory=list)
    incidents: list[ReportIncident] = field(default_factory=list)
    materials: list[ReportMaterial] = field(default_factory=list)
    evidences: list[ReportEvidence] = field(default_factory=list)


def _text(value: object) -> str:
    """Escape a value for safe use inside a ReportLab paragraph."""
    if value is None or value == "":
        return "—"
    return escape(str(value))


class ReportBuilder:
    """Renders a :class:`ServiceReportData` into a professional PDF."""

    def __init__(self, data: ServiceReportData) -> None:
        self._data = data
        self._styles = self._build_styles()

    def build(self, output_path: Path) -> Path:
        """Write the PDF to ``output_path`` and return it."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        document = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=_MARGIN_X,
            rightMargin=_MARGIN_X,
            topMargin=_MARGIN_TOP,
            bottomMargin=_MARGIN_BOTTOM,
            title="FieldDesk · Reporte de servicio",
            author="FieldDesk",
            subject="Reporte de servicio técnico",
        )
        document.build(
            self._story(),
            onFirstPage=self._decorate_page,
            onLaterPages=self._decorate_page,
        )
        return output_path

    # ------------------------------------------------------------------
    # Styles and page decoration
    # ------------------------------------------------------------------
    def _build_styles(self) -> dict[str, ParagraphStyle]:
        styles = getSampleStyleSheet()
        return {
            "title": ParagraphStyle(
                "FDTitle",
                parent=styles["Heading1"],
                fontName="Helvetica-Bold",
                fontSize=22,
                textColor=TEXT,
                spaceAfter=2,
            ),
            "subtitle": ParagraphStyle(
                "FDSubtitle",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=10,
                textColor=MUTED,
                spaceAfter=10,
            ),
            "section": ParagraphStyle(
                "FDSection",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=12,
                textColor=PRIMARY,
                spaceBefore=12,
                spaceAfter=6,
            ),
            "label": ParagraphStyle(
                "FDLabel",
                parent=styles["Normal"],
                fontName="Helvetica-Bold",
                fontSize=9.5,
                textColor=MUTED,
            ),
            "body": ParagraphStyle(
                "FDBody",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                textColor=TEXT,
            ),
            "caption": ParagraphStyle(
                "FDCaption",
                parent=styles["Normal"],
                fontName="Helvetica",
                fontSize=8,
                leading=10,
                textColor=MUTED,
                alignment=1,
            ),
        }

    def _decorate_page(self, canvas, document) -> None:
        width, _height = A4
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(_MARGIN_X, 14 * mm, width - _MARGIN_X, 14 * mm)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(
            _MARGIN_X,
            10 * mm,
            "FieldDesk · Gestión de servicio técnico",
        )
        canvas.drawRightString(
            width - _MARGIN_X,
            10 * mm,
            f"Página {document.page}",
        )
        canvas.restoreState()

    # ------------------------------------------------------------------
    # Story
    # ------------------------------------------------------------------
    def _story(self) -> list:
        generated = self._data.generated_at.strftime("%d/%m/%Y %H:%M")
        story: list = [
            Paragraph("FieldDesk", self._styles["title"]),
            Paragraph(
                f"Reporte de servicio · generado el {generated}",
                self._styles["subtitle"],
            ),
        ]
        story += self._info_section(
            "Información del cliente", self._data.client
        )
        story += self._info_section(
            "Información de ubicación", self._data.location
        )
        story += self._info_section(
            "Información del equipo", self._data.equipment
        )
        story += self._info_section(
            "Información del servicio", self._data.service
        )
        story += self._visits_section()
        story += self._incidents_section()
        story += self._materials_section()
        story += self._evidences_section()
        return story

    def _info_section(
        self,
        title: str,
        rows: list[tuple[str, str]],
    ) -> list:
        flowables: list = [Paragraph(title, self._styles["section"])]
        if not rows:
            flowables.append(Paragraph("Sin información.", self._styles["body"]))
            return flowables
        data = [
            [
                Paragraph(_text(label), self._styles["label"]),
                Paragraph(_text(value), self._styles["body"]),
            ]
            for label, value in rows
        ]
        table = Table(data, colWidths=[45 * mm, None])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("LINEBELOW", (0, 0), (-1, -2), 0.4, BORDER),
                ]
            )
        )
        flowables.append(table)
        return flowables

    def _visits_section(self) -> list:
        flowables: list = [
            Paragraph(
                "Trabajo realizado y observaciones",
                self._styles["section"],
            )
        ]
        if not self._data.visits:
            flowables.append(
                Paragraph("No se registraron visitas.", self._styles["body"])
            )
            return flowables
        for visit in self._data.visits:
            block = [
                Paragraph(
                    _text(f"Visita del {visit.date} · {visit.schedule}"),
                    self._styles["label"],
                ),
                Spacer(1, 2),
                Paragraph(
                    f"<b>Trabajo realizado:</b> "
                    f"{_text(visit.work_performed)}",
                    self._styles["body"],
                ),
                Paragraph(
                    f"<b>Observaciones:</b> {_text(visit.observations)}",
                    self._styles["body"],
                ),
                Spacer(1, 6),
            ]
            flowables.append(KeepTogether(block))
        return flowables

    def _incidents_section(self) -> list:
        flowables: list = [
            Paragraph("Incidencias", self._styles["section"])
        ]
        if not self._data.incidents:
            flowables.append(
                Paragraph(
                    "Sin incidencias registradas.", self._styles["body"]
                )
            )
            return flowables
        data = [
            [
                Paragraph("<b>Título</b>", self._styles["label"]),
                Paragraph("<b>Prioridad</b>", self._styles["label"]),
                Paragraph("<b>Estado</b>", self._styles["label"]),
            ]
        ]
        for incident in self._data.incidents:
            data.append(
                [
                    Paragraph(_text(incident.title), self._styles["body"]),
                    Paragraph(_text(incident.priority), self._styles["body"]),
                    Paragraph(_text(incident.status), self._styles["body"]),
                ]
            )
        table = Table(data, colWidths=[None, 30 * mm, 30 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDER),
                ]
            )
        )
        flowables.append(table)
        for incident in self._data.incidents:
            if incident.description:
                flowables.append(
                    Paragraph(
                        f"<b>Descripción:</b> {_text(incident.description)}",
                        self._styles["body"],
                    )
                )
            if incident.resolution:
                flowables.append(
                    Paragraph(
                        f"<b>Resolución:</b> {_text(incident.resolution)}",
                        self._styles["body"],
                    )
                )
        return flowables

    def _materials_section(self) -> list:
        flowables: list = [Paragraph("Materiales", self._styles["section"])]
        if not self._data.materials:
            flowables.append(
                Paragraph("No se utilizaron materiales.", self._styles["body"])
            )
            return flowables
        data = [
            [
                Paragraph("<b>Material</b>", self._styles["label"]),
                Paragraph("<b>Cantidad</b>", self._styles["label"]),
                Paragraph("<b>Unidad</b>", self._styles["label"]),
                Paragraph("<b>Notas</b>", self._styles["label"]),
            ]
        ]
        for material in self._data.materials:
            data.append(
                [
                    Paragraph(_text(material.name), self._styles["body"]),
                    Paragraph(_text(material.quantity), self._styles["body"]),
                    Paragraph(_text(material.unit), self._styles["body"]),
                    Paragraph(_text(material.notes), self._styles["body"]),
                ]
            )
        table = Table(data, colWidths=[None, 22 * mm, 20 * mm, 45 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LINEBELOW", (0, 0), (-1, -1), 0.4, BORDER),
                ]
            )
        )
        flowables.append(table)
        return flowables

    def _evidences_section(self) -> list:
        flowables: list = [
            Paragraph("Evidencias fotográficas", self._styles["section"])
        ]
        if not self._data.evidences:
            flowables.append(
                Paragraph("Sin evidencias adjuntas.", self._styles["body"])
            )
            return flowables

        cells: list[list] = []
        for evidence in self._data.evidences:
            cell: list = []
            image = self._image_flowable(evidence.path)
            if image is not None:
                cell.append(image)
            caption = evidence.description or evidence.path.name
            cell.append(Spacer(1, 3))
            cell.append(Paragraph(_text(caption), self._styles["caption"]))
            cells.append(cell)

        rows: list[list] = []
        for index in range(0, len(cells), 2):
            pair = cells[index:index + 2]
            if len(pair) == 1:
                pair.append("")
            rows.append(pair)

        table = Table(rows, colWidths=[84 * mm, 84 * mm])
        table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        flowables.append(table)
        return flowables

    def _image_flowable(self, path: Path) -> RLImage | None:
        if not path.is_file():
            return None
        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as image:
                width, height = image.size
        except Exception:  # noqa: BLE001 - broken image, skip it
            return None

        if not width or not height:
            return None
        max_width = 78 * mm
        max_height = 58 * mm
        ratio = height / width
        draw_width = max_width
        draw_height = draw_width * ratio
        if draw_height > max_height:
            draw_height = max_height
            draw_width = draw_height / ratio if ratio else max_width
        try:
            return RLImage(
                str(path),
                width=draw_width,
                height=draw_height,
            )
        except Exception:  # noqa: BLE001 - unsupported image format
            return None
