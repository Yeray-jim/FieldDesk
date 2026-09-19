"""Optional demonstration data.

Loading this data makes the application easy to showcase in a portfolio. It is
created in a single transaction and refused when the database already contains
clients, to avoid duplicates.
"""

from __future__ import annotations

import logging
import tempfile
from dataclasses import dataclass
from datetime import date, time, timedelta
from decimal import Decimal
from pathlib import Path

from app.config.settings import Settings
from app.database import Database
from app.database.models import (
    Client,
    Equipment,
    EquipmentStatus,
    Evidence,
    Incident,
    IncidentStatus,
    Location,
    Material,
    Priority,
    Service,
    ServiceMaterial,
    ServiceStatus,
    Visit,
)
from app.services.base_service import BaseService
from app.utils.dates import utcnow
from app.utils.exceptions import ConflictError
from app.utils.files import store_image

logger = logging.getLogger(__name__)

_CLIENTS = [
    ("Hospital San Rafael", "Grupo San Rafael", "555-0101", "mantenimiento@sanrafael.es", "Av. de la Salud 45"),
    ("Industrias Norte", "Industrias Norte S.L.", "555-0102", "planta@industriasnorte.es", "Polígono Norte, nave 7"),
    ("Clínica Dental Sonrisa", "Sonrisa S.C.", "555-0103", "admin@dentalsonrisa.es", "Calle Mayor 12"),
    ("Supermercados El Sol", "El Sol Distribución", "555-0104", "soporte@elsol.es", "Ronda Sur 89"),
    ("Hotel Costa Azul", "Costa Azul Hoteles", "555-0105", "operaciones@costaazul.es", "Paseo Marítimo 3"),
]

_LOCATIONS = [
    (0, "Urgencias", "Ciudad de México", "Cuauhtémoc", "Centro", "Av. de la Salud 45", "12", "4", "Junto a recepción"),
    (0, "Quirófano 2", "Ciudad de México", "Cuauhtémoc", "Centro", "Av. de la Salud 45", "12", "4", "Planta segunda, acceso restringido"),
    (1, "Planta de producción", "Nuevo León", "Apodaca", "Parque Industrial", "Carr. Miguel Alemán 300", "7", "2", "Puerta de carga 3"),
    (1, "Almacén central", "Nuevo León", "Apodaca", "Parque Industrial", "Carr. Miguel Alemán 320", "8", "2", "Nave anexa, llave en conserjería"),
    (2, "Recepción", "Jalisco", "Guadalajara", "Americana", "Calle Mayor 12", "5", "1", ""),
    (3, "Sucursal Centro", "Jalisco", "Zapopan", "Centro", "Av. Hidalgo 210", "3", "1", "Frente a la plaza"),
    (3, "Sucursal Norte", "Jalisco", "Zapopan", "Industrial", "Av. Norte 210", "18", "6", "Frigorífico principal"),
    (4, "Azotea", "Quintana Roo", "Benito Juárez", "Zona Hotelera", "Paseo Marítimo 3", "1", "1", "Acceso por escalera técnica"),
]

_EQUIPMENT = [
    ("Climatizador quirófano", "Climatización", "Daikin", "VRV-IV", "SN-CL-1001", EquipmentStatus.OPERATIONAL),
    ("Bomba de vacío", "Hidráulica", "Busch", "RA-0025", "SN-BV-1002", EquipmentStatus.MAINTENANCE),
    ("Compresor de aire", "Neumática", "Atlas Copco", "GA-15", "SN-CP-1003", EquipmentStatus.OPERATIONAL),
    ("Cámara frigorífica", "Refrigeración", "Frimetal", "CF-800", "SN-CR-1004", EquipmentStatus.OPERATIONAL),
    ("Autoclave", "Esterilización", "Tuttnauer", "3870EA", "SN-AU-1005", EquipmentStatus.OUT_OF_SERVICE),
    ("Cinta transportadora", "Transporte", "Interroll", "CT-200", "SN-CT-1006", EquipmentStatus.OPERATIONAL),
    ("Generador diésel", "Energía", "Caterpillar", "DE-150", "SN-GE-1007", EquipmentStatus.OPERATIONAL),
    ("Grupo de presión", "Hidráulica", "Grundfos", "CR-15", "SN-GP-1008", EquipmentStatus.MAINTENANCE),
    ("Montacargas", "Elevación", "Otis", "MC-300", "SN-MC-1009", EquipmentStatus.OPERATIONAL),
    ("Caldera de vapor", "Térmica", "Bosch", "UT-L", "SN-CV-1010", EquipmentStatus.OPERATIONAL),
    ("Climatizador sala", "Climatización", "Mitsubishi", "PX-71", "SN-CL-1011", EquipmentStatus.RETIRED),
    ("Central de alarma", "Seguridad", "Honeywell", "AW-200", "SN-AL-1012", EquipmentStatus.OPERATIONAL),
]

_SERVICES = [
    ("Mantenimiento preventivo", ServiceStatus.COMPLETED, Priority.MEDIUM),
    ("Reparación de fuga", ServiceStatus.IN_PROGRESS, Priority.HIGH),
    ("Inspección anual", ServiceStatus.PENDING, Priority.MEDIUM),
    ("Puesta en marcha", ServiceStatus.COMPLETED, Priority.LOW),
    ("Mantenimiento preventivo", ServiceStatus.PENDING, Priority.HIGH),
    ("Reparación de compresor", ServiceStatus.IN_PROGRESS, Priority.HIGH),
    ("Sustitución de filtros", ServiceStatus.COMPLETED, Priority.MEDIUM),
    ("Revisión eléctrica", ServiceStatus.PENDING, Priority.LOW),
    ("Mantenimiento preventivo", ServiceStatus.CANCELLED, Priority.LOW),
    ("Reparación de cámara", ServiceStatus.IN_PROGRESS, Priority.HIGH),
    ("Instalación de sensor", ServiceStatus.PENDING, Priority.MEDIUM),
    ("Inspección de seguridad", ServiceStatus.COMPLETED, Priority.MEDIUM),
    ("Mantenimiento de caldera", ServiceStatus.PENDING, Priority.HIGH),
    ("Reparación de montacargas", ServiceStatus.IN_PROGRESS, Priority.HIGH),
    ("Revisión de alarma", ServiceStatus.COMPLETED, Priority.MEDIUM),
]

_INCIDENTS = [
    ("Fuga de aceite", Priority.HIGH, IncidentStatus.OPEN),
    ("Ruido anómalo en el motor", Priority.MEDIUM, IncidentStatus.IN_PROGRESS),
    ("Temperatura fuera de rango", Priority.HIGH, IncidentStatus.OPEN),
    ("Vibración excesiva", Priority.MEDIUM, IncidentStatus.RESOLVED),
    ("Fallo de encendido", Priority.HIGH, IncidentStatus.OPEN),
    ("Mensaje de error en panel", Priority.LOW, IncidentStatus.CANCELLED),
    ("Pérdida de presión", Priority.HIGH, IncidentStatus.IN_PROGRESS),
    ("Desgaste de correa", Priority.MEDIUM, IncidentStatus.OPEN),
]

_MATERIALS = [
    ("Aceite hidráulico", "L"), ("Filtro de aire", "ud"), ("Filtro de aceite", "ud"),
    ("Correa trapezoidal", "ud"), ("Junta tórica", "ud"), ("Refrigerante R-410A", "kg"),
    ("Limpiador de contactos", "ml"), ("Grasa de silicona", "g"), ("Cinta aislante", "rollo"),
    ("Tornillería variada", "ud"), ("Manguera flexible", "m"), ("Válvula de retención", "ud"),
    ("Manómetro", "ud"), ("Rodamiento", "ud"), ("Sellador térmico", "ml"),
    ("Batería 12V", "ud"), ("Fusible cerámico", "ud"), ("Luminaria LED", "ud"),
    ("Guantes de nitrilo", "par"), ("Paño de microfibra", "ud"),
]


@dataclass
class DemoSummary:
    """Number of records created by the demonstration loader."""

    clients: int
    locations: int
    equipment: int
    services: int
    incidents: int
    materials: int
    evidences: int


class DemoDataService(BaseService):
    """Loads a complete set of fictional data for demonstration purposes."""

    def __init__(self, database: Database, settings: Settings) -> None:
        super().__init__(database)
        self._settings = settings

    def has_data(self) -> bool:
        """Return whether the database already contains clients."""
        with self._repositories() as repositories:
            return repositories.clients.count() > 0

    def load(self) -> DemoSummary:
        """Create the demonstration data in a single transaction.

        Raises:
            ConflictError: If the database already contains clients.
        """
        if self.has_data():
            raise ConflictError(
                "Ya existen datos en la aplicación. Los datos de demostración "
                "solo pueden cargarse en una base de datos vacía."
            )

        with self._repositories() as repositories:
            clients = self._seed_clients(repositories)
            locations = self._seed_locations(repositories, clients)
            equipment = self._seed_equipment(repositories, locations)
            services = self._seed_services(repositories, equipment, locations)
            self._seed_visits(repositories, services)
            self._seed_incidents(repositories, equipment)
            materials = self._seed_materials(repositories)
            self._seed_service_materials(repositories, services, materials)
            evidences = self._seed_evidences(repositories, services)

            summary = DemoSummary(
                clients=len(clients),
                locations=len(locations),
                equipment=len(equipment),
                services=len(services),
                incidents=len(_INCIDENTS),
                materials=len(materials),
                evidences=evidences,
            )
        logger.info("Demo data loaded: %s", summary)
        return summary

    # ------------------------------------------------------------------
    # Seeds
    # ------------------------------------------------------------------
    @staticmethod
    def _seed_clients(repositories) -> list[Client]:
        return [
            repositories.clients.add(
                Client(
                    name=name,
                    company=company,
                    phone=phone,
                    email=email,
                    address=address,
                )
            )
            for name, company, phone, email, address in _CLIENTS
        ]

    @staticmethod
    def _seed_locations(repositories, clients) -> list[Location]:
        return [
            repositories.locations.add(
                Location(
                    client_id=clients[client_index].id,
                    name=name,
                    state=state,
                    municipality=municipality,
                    neighborhood=neighborhood,
                    street=street,
                    lot=lot,
                    block=block,
                    reference=reference or None,
                )
            )
            for (
                client_index,
                name,
                state,
                municipality,
                neighborhood,
                street,
                lot,
                block,
                reference,
            ) in _LOCATIONS
        ]

    @staticmethod
    def _seed_equipment(repositories, locations) -> list[Equipment]:
        equipment: list[Equipment] = []
        for index, (name, type_, brand, model, serial, status) in enumerate(
            _EQUIPMENT
        ):
            location = locations[index % len(locations)]
            equipment.append(
                repositories.equipment.add(
                    Equipment(
                        location_id=location.id,
                        name=name,
                        type=type_,
                        brand=brand,
                        model=model,
                        serial_number=serial,
                        status=status,
                    )
                )
            )
        return equipment

    @staticmethod
    def _seed_services(repositories, equipment, locations) -> list[Service]:
        location_clients = {
            location.id: location.client_id for location in locations
        }
        services: list[Service] = []
        for index, (service_type, status, priority) in enumerate(_SERVICES):
            item = equipment[index % len(equipment)]
            client_id = location_clients[item.location_id]
            scheduled = utcnow() + timedelta(days=index - 5)
            services.append(
                repositories.services.add(
                    Service(
                        client_id=client_id,
                        equipment_id=item.id,
                        service_type=service_type,
                        description=(
                            f"{service_type} del equipo {item.name}."
                        ),
                        scheduled_date=scheduled,
                        status=status,
                        priority=priority,
                    )
                )
            )
        return services

    @staticmethod
    def _seed_visits(repositories, services) -> None:
        performed = [
            service
            for service in services
            if service.status
            in (ServiceStatus.IN_PROGRESS, ServiceStatus.COMPLETED)
        ]
        for index, service in enumerate(performed):
            day = (utcnow() - timedelta(days=index)).date()
            repositories.visits.add(
                Visit(
                    service_id=service.id,
                    visit_date=day,
                    start_time=time(9, 0),
                    end_time=time(11, 30),
                    work_performed=(
                        "Se revisó el equipo y se realizaron las tareas "
                        "programadas."
                    ),
                    observations=(
                        "Sin incidencias relevantes."
                        if index % 2 == 0
                        else "Se recomienda revisar en la próxima visita."
                    ),
                )
            )

    @staticmethod
    def _seed_incidents(repositories, equipment) -> None:
        for index, (title, priority, status) in enumerate(_INCIDENTS):
            item = equipment[index % len(equipment)]
            repositories.incidents.add(
                Incident(
                    equipment_id=item.id,
                    title=title,
                    description=f"{title} detectado en {item.name}.",
                    priority=priority,
                    status=status,
                    resolution=(
                        "Resuelto en la visita."
                        if status == IncidentStatus.RESOLVED
                        else None
                    ),
                )
            )

    @staticmethod
    def _seed_materials(repositories) -> list[Material]:
        return [
            repositories.materials.add(
                Material(
                    name=name,
                    unit=unit,
                    stock=Decimal("50"),
                )
            )
            for name, unit in _MATERIALS
        ]

    @staticmethod
    def _seed_service_materials(repositories, services, materials) -> None:
        for index, service in enumerate(services[:8]):
            first = materials[(index * 2) % len(materials)]
            second = materials[(index * 2 + 1) % len(materials)]
            repositories.service_materials.add(
                ServiceMaterial(
                    service_id=service.id,
                    material_id=first.id,
                    quantity=Decimal(str(index + 1)),
                )
            )
            repositories.service_materials.add(
                ServiceMaterial(
                    service_id=service.id,
                    material_id=second.id,
                    quantity=Decimal("1.5"),
                )
            )

    def _seed_evidences(self, repositories, services) -> int:
        colors = [(70, 120, 190), (190, 120, 70), (90, 160, 110)]
        created = 0
        self._settings.images_dir.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as temporary:
            for index, color in enumerate(colors):
                service = services[index]
                try:
                    from PIL import Image
                except ImportError:  # pragma: no cover - Pillow is required
                    return created
                source = Path(temporary) / f"demostracion_{index}.png"
                Image.new("RGB", (640, 420), color).save(source)
                stored = store_image(source, self._settings.images_dir)
                relative = stored.relative_to(
                    self._settings.storage_dir
                ).as_posix()
                repositories.evidences.add(
                    Evidence(
                        service_id=service.id,
                        filename=stored.name,
                        filepath=relative,
                        description="Estado del equipo tras la intervención.",
                    )
                )
                created += 1
        return created
