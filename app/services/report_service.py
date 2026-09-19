"""Business service that generates PDF reports for services.

The service gathers the full service graph inside a session and materialises
it into a :class:`ServiceReportData` value object; the PDF itself is rendered
by :class:`~app.services.report_builder.ReportBuilder`.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.config.settings import Settings
from app.database import Database
from app.database.repositories import Repositories
from app.services.base_service import BaseService
from app.services.report_builder import (
    ReportBuilder,
    ReportEvidence,
    ReportIncident,
    ReportMaterial,
    ReportVisit,
    ServiceReportData,
)
from app.utils.dates import format_date, format_datetime, format_time, utcnow
from app.utils.exceptions import NotFoundError
from app.utils.labels import status_label

logger = logging.getLogger(__name__)


class ReportService(BaseService):
    """Generates professional PDF reports for services."""

    def __init__(self, database: Database, settings: Settings) -> None:
        super().__init__(database)
        self._settings = settings

    def generate_service_report(self, service_id: int) -> Path:
        """Generate a PDF report for a service.

        Args:
            service_id: Identifier of the service to report.

        Returns:
            The path of the generated PDF file.

        Raises:
            NotFoundError: If the service does not exist.
        """
        with self._repositories() as repositories:
            service = repositories.services.get(service_id)
            if service is None:
                raise NotFoundError(
                    f"No existe el servicio con id {service_id}."
                )
            data = self._collect(repositories, service)

        output_path = self._settings.documents_dir / self._filename(service_id)
        logger.info("Generating service report %s", output_path.name)
        return ReportBuilder(data).build(output_path)

    # ------------------------------------------------------------------
    # Data gathering
    # ------------------------------------------------------------------
    def _collect(
        self,
        repositories: Repositories,
        service,
    ) -> ServiceReportData:
        client = repositories.clients.get(service.client_id)
        equipment = repositories.equipment.get(service.equipment_id)
        location = (
            repositories.locations.get(equipment.location_id)
            if equipment is not None
            else None
        )
        visits = repositories.visits.list_by_service(service.id)
        incidents = repositories.incidents.list_by_service(service.id)
        materials = repositories.service_materials.list_by_service(service.id)
        evidences = repositories.evidences.list_by_service(service.id)

        return ServiceReportData(
            generated_at=utcnow(),
            client=self._client_rows(client),
            location=self._location_rows(location),
            equipment=self._equipment_rows(equipment),
            service=self._service_rows(service),
            visits=[
                ReportVisit(
                    date=format_date(visit.visit_date),
                    schedule=(
                        f"{format_time(visit.start_time)} - "
                        f"{format_time(visit.end_time)}"
                    ),
                    work_performed=visit.work_performed or "",
                    observations=visit.observations or "",
                )
                for visit in visits
            ],
            incidents=[
                ReportIncident(
                    title=incident.title,
                    priority=status_label(incident.priority),
                    status=status_label(incident.status),
                    description=incident.description or "",
                    resolution=incident.resolution or "",
                )
                for incident in incidents
            ],
            materials=self._material_rows(repositories, materials),
            evidences=[
                ReportEvidence(
                    path=self._settings.storage_dir / evidence.filepath,
                    description=evidence.description or "",
                )
                for evidence in evidences
            ],
        )

    @staticmethod
    def _client_rows(client) -> list[tuple[str, str]]:
        if client is None:
            return []
        return [
            ("Nombre", client.name),
            ("Empresa", client.company),
            ("Teléfono", client.phone),
            ("Email", client.email),
            ("Dirección", client.address),
        ]

    @staticmethod
    def _location_rows(location) -> list[tuple[str, str]]:
        if location is None:
            return []
        return [
            ("Nombre", location.name),
            ("Dirección", location.address),
            ("Referencia", location.reference),
        ]

    @staticmethod
    def _equipment_rows(equipment) -> list[tuple[str, str]]:
        if equipment is None:
            return []
        return [
            ("Nombre", equipment.name),
            ("Tipo", equipment.type),
            ("Marca", equipment.brand),
            ("Modelo", equipment.model),
            ("N.º de serie", equipment.serial_number),
            ("Estado", status_label(equipment.status)),
            ("Fecha de instalación", format_date(equipment.installation_date)),
            ("Fin de garantía", format_date(equipment.warranty_expiration)),
        ]

    @staticmethod
    def _service_rows(service) -> list[tuple[str, str]]:
        return [
            ("Tipo de servicio", service.service_type),
            ("Estado", status_label(service.status)),
            ("Prioridad", status_label(service.priority)),
            ("Fecha programada", format_datetime(service.scheduled_date)),
            ("Fecha de registro", format_datetime(service.created_at)),
            ("Descripción", service.description),
        ]

    @staticmethod
    def _material_rows(
        repositories: Repositories,
        records,
    ) -> list[ReportMaterial]:
        rows: list[ReportMaterial] = []
        for record in records:
            material = repositories.materials.get(record.material_id)
            rows.append(
                ReportMaterial(
                    name=(
                        material.name
                        if material is not None
                        else f"Material #{record.material_id}"
                    ),
                    quantity=str(record.quantity),
                    unit=(material.unit or "") if material is not None else "",
                    notes=record.notes or "",
                )
            )
        return rows

    @staticmethod
    def _filename(service_id: int) -> str:
        stamp = utcnow().strftime("%Y%m%d_%H%M%S")
        return f"Reporte_servicio_{service_id}_{stamp}.pdf"
