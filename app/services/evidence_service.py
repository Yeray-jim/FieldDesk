"""Business operations for evidence images.

Images are copied to ``storage/images`` and only their metadata is persisted,
following ADR-003. The service validates the file, stores it and keeps the
database and the filesystem consistent: if persistence fails, the copied file
is removed.
"""

from __future__ import annotations

from pathlib import Path

from app.config.settings import Settings
from app.database import Database
from app.database.models import Evidence
from app.schemas.evidence_schema import EvidenceCreate
from app.services.base_service import BaseService
from app.utils.exceptions import NotFoundError
from app.utils.files import delete_file, store_image


class EvidenceService(BaseService):
    """Provides business operations related to service evidence."""

    def __init__(self, database: Database, settings: Settings) -> None:
        super().__init__(database)
        self._settings = settings

    def add_evidence(
        self,
        data: EvidenceCreate,
        source_path: str | Path,
    ) -> Evidence:
        """Attach an image to a service.

        Args:
            data: Evidence metadata (service and description).
            source_path: Path of the selected image file.

        Returns:
            The created evidence record.

        Raises:
            NotFoundError: If the service does not exist.
            ValidationError: If the file is missing or not a supported image.
            StorageError: If the image cannot be stored.
        """
        with self._repositories() as repositories:
            if repositories.services.get(data.service_id) is None:
                raise NotFoundError(
                    f"No existe el servicio con id {data.service_id}."
                )

            stored_path = store_image(Path(source_path), self._settings.images_dir)
            try:
                relative_path = stored_path.relative_to(
                    self._settings.storage_dir
                ).as_posix()
                evidence = Evidence(
                    service_id=data.service_id,
                    filename=stored_path.name,
                    filepath=relative_path,
                    description=data.description,
                )
                return repositories.evidences.add(evidence)
            except Exception:
                delete_file(stored_path)
                raise

    def get_evidence_or_raise(self, evidence_id: int) -> Evidence:
        """Return an evidence by id or raise :class:`NotFoundError`."""
        with self._repositories() as repositories:
            evidence = repositories.evidences.get(evidence_id)
            if evidence is None:
                raise NotFoundError(
                    f"No existe la evidencia con id {evidence_id}."
                )
            return evidence

    def list_evidence_by_service(self, service_id: int) -> list[Evidence]:
        """Return the evidence attached to a service."""
        with self._repositories() as repositories:
            return repositories.evidences.list_by_service(service_id)

    def count_evidence_by_service(self, service_id: int) -> int:
        """Return how many evidence files a service has."""
        with self._repositories() as repositories:
            return repositories.evidences.count_by_service(service_id)

    def delete_evidence(self, evidence_id: int) -> None:
        """Delete an evidence record and its stored file.

        Raises:
            NotFoundError: If the evidence does not exist.
            StorageError: If the stored file cannot be removed.
        """
        with self._repositories() as repositories:
            evidence = repositories.evidences.get(evidence_id)
            if evidence is None:
                raise NotFoundError(
                    f"No existe la evidencia con id {evidence_id}."
                )

            stored_path = self._settings.storage_dir / evidence.filepath
            repositories.evidences.delete(evidence)
            delete_file(stored_path)

    def absolute_path(self, evidence: Evidence) -> Path:
        """Return the absolute path of an evidence file."""
        return self._settings.storage_dir / evidence.filepath
