"""Human-readable Spanish labels for domain enumerations.

Centralising the labels here keeps the badges, the tables and the PDF reports
consistent.
"""

from __future__ import annotations

_STATUS_LABELS: dict[str, str] = {
    "OPERATIONAL": "Operativo",
    "MAINTENANCE": "Mantenimiento",
    "OUT_OF_SERVICE": "Fuera de servicio",
    "RETIRED": "Retirado",
    "PENDING": "Pendiente",
    "IN_PROGRESS": "En progreso",
    "COMPLETED": "Completado",
    "CANCELLED": "Cancelado",
    "OPEN": "Abierta",
    "RESOLVED": "Resuelta",
    "LOW": "Baja",
    "MEDIUM": "Media",
    "HIGH": "Alta",
}


def normalize_status(value: object) -> str:
    """Return the upper-case string value of an enum or string."""
    return str(getattr(value, "value", value)).upper()


def status_label(value: object) -> str:
    """Return the Spanish label for a status or priority value."""
    key = normalize_status(value)
    return _STATUS_LABELS.get(key, key.replace("_", " ").title())
