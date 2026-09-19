"""Export the main datasets to CSV.

Files are written as UTF-8 with BOM and a semicolon separator so they open
correctly in Excel and LibreOffice with Spanish regional settings.
"""

from __future__ import annotations

import csv
import logging
from pathlib import Path

from app.config.settings import Settings
from app.database import Database
from app.services.base_service import BaseService
from app.utils.dates import format_date, format_datetime, utcnow
from app.utils.exceptions import StorageError
from app.utils.labels import status_label

logger = logging.getLogger(__name__)

_ENCODING = "utf-8-sig"
_DELIMITER = ";"


class ExportService(BaseService):
    """Exports clients, equipment, services, incidents and materials to CSV."""

    def __init__(self, database: Database, settings: Settings) -> None:
        super().__init__(database)
        self._settings = settings

    def export_all(self) -> list[Path]:
        """Export every dataset using the same timestamp."""
        stamp = self._stamp()
        return [
            self._export_clients(stamp),
            self._export_equipment(stamp),
            self._export_services(stamp),
            self._export_incidents(stamp),
            self._export_materials(stamp),
        ]

    def export_clients(self) -> Path:
        """Export the client list to CSV."""
        return self._export_clients(self._stamp())

    def export_equipment(self) -> Path:
        """Export the equipment list to CSV."""
        return self._export_equipment(self._stamp())

    def export_services(self) -> Path:
        """Export the service list to CSV."""
        return self._export_services(self._stamp())

    def export_incidents(self) -> Path:
        """Export the incident list to CSV."""
        return self._export_incidents(self._stamp())

    def export_materials(self) -> Path:
        """Export the material catalog to CSV."""
        return self._export_materials(self._stamp())

    # ------------------------------------------------------------------
    # Per-dataset exports
    # ------------------------------------------------------------------
    def _export_clients(self, stamp: str) -> Path:
        headers = [
            "id",
            "nombre",
            "empresa",
            "telefono",
            "email",
            "direccion",
            "notas",
            "creado",
        ]
        with self._repositories() as repositories:
            rows = [
                [
                    client.id,
                    client.name,
                    client.company or "",
                    client.phone or "",
                    client.email or "",
                    client.address or "",
                    client.notes or "",
                    format_datetime(client.created_at),
                ]
                for client in repositories.clients.list_ordered()
            ]
        return self._export("Clientes", headers, rows, stamp)

    def _export_equipment(self, stamp: str) -> Path:
        headers = [
            "id",
            "nombre",
            "tipo",
            "marca",
            "modelo",
            "numero_serie",
            "estado",
            "ubicacion_id",
            "instalacion",
            "fin_garantia",
        ]
        with self._repositories() as repositories:
            rows = [
                [
                    item.id,
                    item.name,
                    item.type,
                    item.brand or "",
                    item.model or "",
                    item.serial_number or "",
                    status_label(item.status),
                    item.location_id,
                    format_date(item.installation_date),
                    format_date(item.warranty_expiration),
                ]
                for item in repositories.equipment.list_all_ordered()
            ]
        return self._export("Equipos", headers, rows, stamp)

    def _export_services(self, stamp: str) -> Path:
        headers = [
            "id",
            "tipo",
            "cliente_id",
            "equipo_id",
            "estado",
            "prioridad",
            "fecha_programada",
            "fecha_registro",
        ]
        with self._repositories() as repositories:
            rows = [
                [
                    service.id,
                    service.service_type,
                    service.client_id,
                    service.equipment_id,
                    status_label(service.status),
                    status_label(service.priority),
                    format_datetime(service.scheduled_date),
                    format_datetime(service.created_at),
                ]
                for service in repositories.services.list_all_ordered()
            ]
        return self._export("Servicios", headers, rows, stamp)

    def _export_incidents(self, stamp: str) -> Path:
        headers = [
            "id",
            "titulo",
            "equipo_id",
            "servicio_id",
            "prioridad",
            "estado",
            "descripcion",
            "resolucion",
            "registrada",
        ]
        with self._repositories() as repositories:
            rows = [
                [
                    incident.id,
                    incident.title,
                    incident.equipment_id,
                    incident.service_id or "",
                    status_label(incident.priority),
                    status_label(incident.status),
                    incident.description or "",
                    incident.resolution or "",
                    format_datetime(incident.created_at),
                ]
                for incident in repositories.incidents.list_all_ordered()
            ]
        return self._export("Incidencias", headers, rows, stamp)

    def _export_materials(self, stamp: str) -> Path:
        headers = ["id", "nombre", "unidad", "descripcion"]
        with self._repositories() as repositories:
            rows = [
                [
                    material.id,
                    material.name,
                    material.unit or "",
                    material.description or "",
                ]
                for material in repositories.materials.list_ordered()
            ]
        return self._export("Materiales", headers, rows, stamp)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _export(
        self,
        prefix: str,
        headers: list[str],
        rows: list[list[object]],
        stamp: str,
    ) -> Path:
        self._settings.documents_dir.mkdir(parents=True, exist_ok=True)
        path = self._settings.documents_dir / f"{prefix}_{stamp}.csv"
        try:
            with path.open("w", encoding=_ENCODING, newline="") as handle:
                writer = csv.writer(
                    handle,
                    delimiter=_DELIMITER,
                    lineterminator="\n",
                )
                writer.writerow(headers)
                writer.writerows(rows)
        except OSError as error:
            raise StorageError(
                f"No se pudo exportar {prefix} a CSV."
            ) from error
        logger.info("Exported %s to %s", prefix, path.name)
        return path

    @staticmethod
    def _stamp() -> str:
        return utcnow().strftime("%Y%m%d_%H%M%S")
