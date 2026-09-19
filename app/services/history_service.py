"""Chronological technical history of an equipment.

The history aggregates services, visits, incidents, materials and evidence
into a single timeline of plain value objects, ready to be rendered.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time

from app.database import Database
from app.services.base_service import BaseService
from app.utils.exceptions import NotFoundError
from app.utils.labels import status_label


@dataclass(frozen=True)
class HistoryEntry:
    """A single event in the technical history."""

    date: datetime
    kind: str
    title: str
    detail: str


class HistoryService(BaseService):
    """Builds the technical history of an equipment."""

    def get_equipment_history(self, equipment_id: int) -> list[HistoryEntry]:
        """Return the history entries of an equipment, newest first.

        Raises:
            NotFoundError: If the equipment does not exist.
        """
        with self._repositories() as repositories:
            equipment = repositories.equipment.get(equipment_id)
            if equipment is None:
                raise NotFoundError(
                    f"No existe el equipo con id {equipment_id}."
                )

            entries: list[HistoryEntry] = []

            for service in repositories.services.list_by_equipment(equipment_id):
                entries.append(
                    HistoryEntry(
                        date=service.created_at,
                        kind="Servicio",
                        title=service.service_type,
                        detail=(
                            f"{status_label(service.status)} · "
                            f"{status_label(service.priority)}"
                        ),
                    )
                )
                for visit in repositories.visits.list_by_service(service.id):
                    detail = visit.work_performed or "Visita registrada"
                    if visit.observations:
                        detail = f"{detail} · {visit.observations}"
                    entries.append(
                        HistoryEntry(
                            date=datetime.combine(
                                visit.visit_date, visit.start_time or time.min
                            ),
                            kind="Visita",
                            title="Visita técnica",
                            detail=detail,
                        )
                    )
                for record in repositories.service_materials.list_by_service(
                    service.id
                ):
                    material = repositories.materials.get(record.material_id)
                    name = (
                        material.name
                        if material is not None
                        else f"Material #{record.material_id}"
                    )
                    unit = (
                        material.unit
                        if material is not None and material.unit
                        else ""
                    )
                    entries.append(
                        HistoryEntry(
                            date=service.created_at,
                            kind="Material",
                            title=name,
                            detail=f"{record.quantity} {unit}".strip(),
                        )
                    )
                for evidence in repositories.evidences.list_by_service(
                    service.id
                ):
                    entries.append(
                        HistoryEntry(
                            date=evidence.created_at,
                            kind="Evidencia",
                            title=evidence.filename,
                            detail=evidence.description or "",
                        )
                    )

            for incident in repositories.incidents.list_by_equipment(
                equipment_id
            ):
                detail = (
                    f"{status_label(incident.status)} · "
                    f"{status_label(incident.priority)}"
                )
                if incident.resolution:
                    detail = f"{detail} · {incident.resolution}"
                entries.append(
                    HistoryEntry(
                        date=incident.created_at,
                        kind="Incidencia",
                        title=incident.title,
                        detail=detail,
                    )
                )

        entries.sort(key=lambda entry: entry.date, reverse=True)
        return entries
