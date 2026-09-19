"""Bundle of business services sharing one database and settings.

The interface layer receives a single :class:`Services` instance instead of
building every service itself, which keeps the application wiring in one place.
"""

from __future__ import annotations

from app.config.settings import Settings
from app.database import Database
from app.services.backup_service import BackupService
from app.services.clients_service import ClientService
from app.services.demo_data import DemoDataService
from app.services.equipment_service import EquipmentService
from app.services.evidence_service import EvidenceService
from app.services.export_service import ExportService
from app.services.history_service import HistoryService
from app.services.incidents_service import IncidentService
from app.services.locations_service import LocationService
from app.services.materials_service import MaterialService
from app.services.report_service import ReportService
from app.services.services_service import ServiceService
from app.services.visits_service import VisitService


class Services:
    """All business services used by the application."""

    def __init__(self, database: Database, settings: Settings) -> None:
        self.clients = ClientService(database)
        self.locations = LocationService(database)
        self.equipment = EquipmentService(database)
        self.services = ServiceService(database)
        self.visits = VisitService(database)
        self.incidents = IncidentService(database)
        self.materials = MaterialService(database)
        self.evidence = EvidenceService(database, settings)
        self.reports = ReportService(database, settings)
        self.backups = BackupService(database, settings)
        self.demo = DemoDataService(database, settings)
        self.exports = ExportService(database, settings)
        self.history = HistoryService(database)
