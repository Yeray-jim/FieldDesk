"""Business operations for materials and their consumption in services."""

from __future__ import annotations

from decimal import Decimal

from app.database.models import Material, ServiceMaterial
from app.schemas.material_schema import (
    MaterialCreate,
    MaterialUpdate,
    ServiceMaterialCreate,
)
from app.services.base_service import BaseService
from app.utils.exceptions import ConflictError, NotFoundError, ValidationError


class MaterialService(BaseService):
    """Provides business operations related to materials."""

    def create_material(self, data: MaterialCreate) -> Material:
        """Create a catalog material."""
        with self._repositories() as repositories:
            material = Material(**data.model_dump())
            return repositories.materials.add(material)

    def get_material(self, material_id: int) -> Material | None:
        """Return a material by id, or ``None`` when it does not exist."""
        with self._repositories() as repositories:
            return repositories.materials.get(material_id)

    def get_material_or_raise(self, material_id: int) -> Material:
        """Return a material by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            material = repositories.materials.get(material_id)
            if material is None:
                raise NotFoundError(
                    f"No existe el material con id {material_id}."
                )
            return material

    def list_materials(self) -> list[Material]:
        """Return the catalog sorted by name."""
        with self._repositories() as repositories:
            return repositories.materials.list_ordered()

    def search_materials(self, term: str) -> list[Material]:
        """Return materials matching the given search term."""
        with self._repositories() as repositories:
            return repositories.materials.search(term)

    def update_material(
        self,
        material_id: int,
        data: MaterialUpdate,
    ) -> Material:
        """Update an existing material.

        Raises:
            NotFoundError: If the material does not exist.
        """
        with self._repositories() as repositories:
            material = repositories.materials.get(material_id)
            if material is None:
                raise NotFoundError(
                    f"No existe el material con id {material_id}."
                )

            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(material, field, value)
            repositories.session.flush()
            return material

    def delete_material(self, material_id: int) -> None:
        """Delete a material that is not used by any service.

        Raises:
            NotFoundError: If the material does not exist.
            ConflictError: If the material has been consumed in services.
        """
        with self._repositories() as repositories:
            material = repositories.materials.get(material_id)
            if material is None:
                raise NotFoundError(
                    f"No existe el material con id {material_id}."
                )

            usages = repositories.service_materials.count_by_material(material_id)
            if usages:
                relation = self._relation_label(
                    usages, "servicio", "servicios"
                )
                raise ConflictError(
                    self._blocking_message("este material", [relation])
                )
            repositories.materials.delete(material)

    def set_service_material(
        self,
        data: ServiceMaterialCreate,
    ) -> ServiceMaterial:
        """Create or update the quantity of a material used by a service.

        Raises:
            NotFoundError: If the service or material does not exist.
        """
        with self._repositories() as repositories:
            if repositories.services.get(data.service_id) is None:
                raise NotFoundError(
                    f"No existe el servicio con id {data.service_id}."
                )
            material = repositories.materials.get(data.material_id)
            if material is None:
                raise NotFoundError(
                    f"No existe el material con id {data.material_id}."
                )
            service = repositories.services.get(data.service_id)
            applied = bool(service and service.materials_applied)

            record = repositories.service_materials.find(
                data.service_id, data.material_id
            )
            if record is None:
                if applied:
                    self._consume(material, data.quantity)
                record = ServiceMaterial(
                    service_id=data.service_id,
                    material_id=data.material_id,
                    quantity=data.quantity,
                    notes=data.notes,
                )
                repositories.session.add(record)
            else:
                difference = data.quantity - record.quantity
                if applied and difference > 0:
                    self._consume(material, difference)
                elif applied and difference < 0:
                    material.stock = (
                        material.stock or Decimal("0")
                    ) - difference
                record.quantity = data.quantity
                record.notes = data.notes
            repositories.session.flush()
            return record

    @staticmethod
    def _consume(material: Material, quantity: Decimal) -> None:
        available = material.stock or Decimal("0")
        if available < quantity:
            raise ValidationError(
                "No hay existencias suficientes de "
                f"«{material.name}». Disponible: {available}, "
                f"requerido: {quantity}."
            )
        material.stock = available - quantity

    def remove_service_material(
        self,
        service_id: int,
        material_id: int,
    ) -> None:
        """Remove a material from a service.

        Raises:
            NotFoundError: If the consumption record does not exist.
        """
        with self._repositories() as repositories:
            record = repositories.service_materials.find(
                service_id, material_id
            )
            if record is None:
                raise NotFoundError(
                    "El servicio no tiene registrado ese material."
                )
            service = repositories.services.get(service_id)
            if service is not None and service.materials_applied:
                material = repositories.materials.get(material_id)
                if material is not None:
                    material.stock = (
                        material.stock or Decimal("0")
                    ) + record.quantity
            repositories.service_materials.delete(record)

    def list_service_materials(self, service_id: int) -> list[ServiceMaterial]:
        """Return the materials consumed by a service."""
        with self._repositories() as repositories:
            return repositories.service_materials.list_by_service(service_id)
