"""Lightweight internationalisation (Spanish and English).

Spanish is the source language: component labels and messages are written in
Spanish and translated with :func:`t`. The active language is stored in a
small preferences file so it survives restarts; the default is Spanish.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ("es", "en")
DEFAULT_LANGUAGE = "es"

_LANGUAGE = DEFAULT_LANGUAGE

_ENGLISH: dict[str, str] = {
    # Navigation
    "Panel": "Dashboard",
    "Clientes": "Clients",
    "Equipos": "Equipment",
    "Servicios": "Services",
    "Incidencias": "Incidents",
    "Materiales": "Materials",
    "Ajustes": "Settings",
    # Buttons
    "Cancelar": "Cancel",
    "Guardar": "Save",
    "Eliminar": "Delete",
    "Nuevo": "New",
    "Añadir": "Add",
    "Cerrar": "Close",
    "Restaurar": "Restore",
    "Crear copia": "Create backup",
    "Restaurar copia": "Restore backup",
    "Exportar a CSV": "Export to CSV",
    "Cargar datos de demostración": "Load demo data",
    "Editar": "Edit",
    "Ver historial": "View history",
    "Reporte PDF": "PDF report",
    "Añadir imágenes": "Add images",
    "Más acciones": "More actions",
    # Status and priorities
    "Operativo": "Operational",
    "Mantenimiento": "Maintenance",
    "Fuera de servicio": "Out of service",
    "Retirado": "Retired",
    "Pendiente": "Pending",
    "En progreso": "In progress",
    "Completado": "Completed",
    "Cancelado": "Cancelled",
    "Cancelada": "Cancelled",
    "Abierta": "Open",
    "Resuelta": "Resolved",
    "Baja": "Low",
    "Media": "Medium",
    "Alta": "High",
    # Titles and sections
    "Panel de control": "Dashboard",
    "Servicios recientes": "Recent services",
    "Próximos servicios": "Upcoming services",
    "Incidencias prioritarias": "Priority incidents",
    "Apariencia": "Appearance",
    "Copias de seguridad": "Backups",
    "Exportación": "Export",
    "Datos de demostración": "Demo data",
    "Información": "Information",
    "Almacenamiento": "Storage",
    "Trabajo realizado y observaciones": "Work performed and observations",
    "Incidencias": "Incidents",
    "Materiales": "Materials",
    "Evidencias fotográficas": "Photo evidence",
    "Materiales del servicio": "Service materials",
    "Evidencias del servicio": "Service evidence",
    "Historial": "History",
    "Nueva ubicación": "New location",
    "Nuevo material": "New material",
    # Clients
    "Nombre": "Name",
    "Empresa": "Company",
    "Teléfono": "Phone",
    "Email": "Email",
    "Dirección": "Address",
    "Notas": "Notes",
    # Locations
    "Nombre de la ubicación": "Location name",
    "Estado": "State",
    "Municipio": "Municipality",
    "Colonia / Fraccionamiento": "Neighbourhood",
    "Calle y número": "Street and number",
    "Lote": "Lot",
    "Manzana": "Block",
    "Referencias": "References",
    "Cliente": "Client",
    "Referencia": "Reference",
    # Equipment
    "Tipo": "Type",
    "Marca": "Brand",
    "Modelo": "Model",
    "N.º de serie": "Serial number",
    "Fecha de instalación": "Installation date",
    "Fin de garantía": "Warranty end",
    "Ubicación": "Location",
    # Services
    "Tipo de servicio": "Service type",
    "Descripción": "Description",
    "Fecha programada": "Scheduled date",
    "Hora programada": "Scheduled time",
    "Prioridad": "Priority",
    "Servicio": "Service",
    # Visits
    "Fecha de la visita": "Visit date",
    "Hora de inicio": "Start time",
    "Hora de fin": "End time",
    "Trabajo realizado": "Work performed",
    "Observaciones": "Observations",
    # Incidents
    "Título": "Title",
    "Resolución": "Resolution",
    # Materials
    "Unidad": "Unit",
    "Existencias": "Stock",
    "Cantidad": "Quantity",
    # Table headers / CRUD
    "Acciones": "Actions",
    "Buscar...": "Search...",
    "Sin registros": "No records",
    "Añade el primero con el botón «Nuevo».": (
        "Add the first one with the «New» button."
    ),
    # Settings / appearance
    "Tema de la aplicación": "Application theme",
    "Idioma": "Language",
    "Sistema": "System",
    "Claro": "Light",
    "Oscuro": "Dark",
    "Español": "Spanish",
    "English": "English",
    # Dashboard metrics
    "Servicios pendientes": "Pending services",
    "Servicios completados": "Completed services",
    "Incidencias abiertas": "Open incidents",
    "Creado": "Created",
    "Programado": "Scheduled",
    "Registrada": "Registered",
    # Messages
    "Este campo es obligatorio.": "This field is required.",
    "El texto es demasiado largo.": "The text is too long.",
    "Introduce un número válido.": "Enter a valid number.",
    "Introduce una fecha válida (AAAA-MM-DD).": "Enter a valid date (YYYY-MM-DD).",
    "Introduce una hora válida (HH:MM).": "Enter a valid time (HH:MM).",
    "Selecciona una opción válida.": "Select a valid option.",
    "El valor debe ser mayor que cero.": "The value must be greater than zero.",
    "Guardado correctamente.": "Saved successfully.",
    "Eliminado correctamente.": "Deleted successfully.",
    "Tema actualizado.": "Theme updated.",
    "Idioma actualizado.": "Language updated.",
    "No se pudo guardar. Verifica los datos e inténtalo nuevamente.": (
        "Could not save. Check the data and try again."
    ),
    "Los campos marcados con * son obligatorios.": (
        "Fields marked with * are required."
    ),
    "Selecciona un material.": "Select a material.",
    "Introduce una cantidad válida.": "Enter a valid quantity.",
    "Material añadido.": "Material added.",
    "Material eliminado.": "Material removed.",
    "Este servicio no tiene materiales asignados.": (
        "This service has no materials assigned."
    ),
    "Este servicio no tiene evidencias.": "This service has no evidence.",
    "Sin evidencias": "No evidence",
    "Sin materiales": "No materials",
    "Sin historial": "No history",
    "Sin registros": "No records",
    "Guarda la base de datos, las imágenes y los documentos en un archivo ZIP, o restaura una copia anterior. Antes de restaurar se crea automáticamente una copia de seguridad.": (
        "Saves the database, images and documents into a ZIP file, or "
        "restores a previous backup. A safety backup is created "
        "automatically before restoring."
    ),
    "Exporta clientes, equipos, servicios, incidencias y materiales a archivos CSV compatibles con Excel y LibreOffice.": (
        "Exports clients, equipment, services, incidents and materials to "
        "CSV files compatible with Excel and LibreOffice."
    ),
    "Carga clientes, ubicaciones, equipos, servicios e incidencias de ejemplo. Solo está disponible si la base de datos está vacía.": (
        "Loads sample clients, locations, equipment, services and "
        "incidents. Only available when the database is empty."
    ),
}


def get_language() -> str:
    """Return the active language code."""
    return _LANGUAGE


def set_language(code: str | None) -> str:
    """Set the active language, falling back to Spanish."""
    global _LANGUAGE
    _LANGUAGE = code if code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    return _LANGUAGE


def t(text: str) -> str:
    """Translate a Spanish source string into the active language."""
    if _LANGUAGE == "es":
        return text
    return _ENGLISH.get(text, text)


def load_language(path: Path) -> str:
    """Read the saved language from a preferences file."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        code = data.get("language")
        if code in SUPPORTED_LANGUAGES:
            return code
    except (OSError, json.JSONDecodeError):
        logger.debug("No preferences file found at %s", path)
    return DEFAULT_LANGUAGE


def save_language(path: Path, code: str) -> None:
    """Persist the language in a preferences file."""
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"language": set_language(code)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        logger.exception("Could not save the language preference")
