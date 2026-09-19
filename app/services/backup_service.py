"""Backup and restore for the whole local dataset.

A backup is a ZIP archive containing the SQLite database, the evidence images
and the generated documents, plus a manifest describing the contents. The
SQLite file is snapshotted with the ``sqlite3`` backup API so it stays
consistent even while the application is running.
"""

from __future__ import annotations

import json
import logging
import shutil
import sqlite3
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

from app.config.settings import Settings
from app.database import Database
from app.services.base_service import BaseService
from app.utils.dates import utcnow
from app.utils.exceptions import StorageError, ValidationError

logger = logging.getLogger(__name__)

_DB_MEMBER = "database/fielddesk.db"
_MANIFEST_MEMBER = "manifest.json"
_REQUIRED_TABLES = {"client", "service", "equipment"}


@dataclass
class BackupManifest:
    """Metadata stored inside a backup archive."""

    app_name: str
    app_version: str
    created_at: str
    database_file: str
    images: int
    documents: int

    @classmethod
    def from_dict(cls, data: dict) -> "BackupManifest":
        """Build a manifest from its JSON representation."""
        return cls(
            app_name=str(data.get("app_name", "FieldDesk")),
            app_version=str(data.get("app_version", "")),
            created_at=str(data.get("created_at", "")),
            database_file=str(data.get("database_file", _DB_MEMBER)),
            images=int(data.get("images", 0)),
            documents=int(data.get("documents", 0)),
        )

    def to_dict(self) -> dict:
        """Return the JSON-serialisable representation."""
        return asdict(self)


class BackupService(BaseService):
    """Creates, validates and restores FieldDesk backups."""

    def __init__(self, database: Database, settings: Settings) -> None:
        super().__init__(database)
        self._settings = settings

    # ------------------------------------------------------------------
    # Backup
    # ------------------------------------------------------------------
    def create_backup(self, destination_dir: Path | None = None) -> Path:
        """Create a backup archive.

        Args:
            destination_dir: Directory for the archive; defaults to the
                configured backups directory.

        Returns:
            The path of the created ZIP archive.
        """
        directory = destination_dir or self._settings.backups_dir
        directory.mkdir(parents=True, exist_ok=True)
        archive = directory / f"FieldDesk_Backup_{self._stamp()}.zip"
        return self._build_archive(archive)

    def _create_safety_backup(self) -> Path:
        archive = self._settings.backups_dir / (
            f"FieldDesk_Backup_pre_restore_{self._stamp()}.zip"
        )
        return self._build_archive(archive)

    def _build_archive(self, archive: Path) -> Path:
        archive.parent.mkdir(parents=True, exist_ok=True)
        manifest = self._build_manifest()
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            database_copy = temporary_path / "fielddesk.db"
            if self._settings.database_path.is_file():
                self._copy_database(
                    self._settings.database_path, database_copy
                )

            with zipfile.ZipFile(
                archive, "w", zipfile.ZIP_DEFLATED
            ) as archive_file:
                archive_file.writestr(
                    _MANIFEST_MEMBER,
                    json.dumps(
                        manifest.to_dict(), indent=2, ensure_ascii=False
                    ),
                )
                if database_copy.is_file():
                    archive_file.write(database_copy, _DB_MEMBER)
                self._write_directory(
                    archive_file, self._settings.images_dir, "images"
                )
                self._write_directory(
                    archive_file, self._settings.documents_dir, "documents"
                )
        logger.info("Backup created: %s", archive.name)
        return archive

    def _build_manifest(self) -> BackupManifest:
        return BackupManifest(
            app_name=self._settings.app_name,
            app_version=self._settings.app_version,
            created_at=utcnow().isoformat(timespec="seconds"),
            database_file=_DB_MEMBER,
            images=self._count_files(self._settings.images_dir),
            documents=self._count_files(self._settings.documents_dir),
        )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_backup(self, archive: str | Path) -> BackupManifest:
        """Validate a backup archive and return its manifest.

        Raises:
            ValidationError: If the file is missing, is not a ZIP or does not
                contain the expected structure.
        """
        path = Path(archive)
        if not path.is_file():
            raise ValidationError("El archivo de copia de seguridad no existe.")
        if not zipfile.is_zipfile(path):
            raise ValidationError(
                "El archivo seleccionado no es una copia de seguridad válida."
            )

        with zipfile.ZipFile(path) as archive_file:
            names = set(archive_file.namelist())
            if _MANIFEST_MEMBER not in names:
                raise ValidationError(
                    "La copia de seguridad no contiene el manifiesto esperado."
                )
            if _DB_MEMBER not in names:
                raise ValidationError(
                    "La copia de seguridad no contiene la base de datos."
                )
            try:
                data = json.loads(archive_file.read(_MANIFEST_MEMBER))
            except (json.JSONDecodeError, UnicodeDecodeError) as error:
                raise ValidationError(
                    "El manifiesto de la copia de seguridad está dañado."
                ) from error
        return BackupManifest.from_dict(data)

    # ------------------------------------------------------------------
    # Restore
    # ------------------------------------------------------------------
    def restore_backup(self, archive: str | Path) -> BackupManifest:
        """Restore a backup over the current data.

        A safety backup of the current data is created first. If anything
        fails during the restore, the safety backup is applied again.

        Returns:
            The manifest of the restored backup.

        Raises:
            ValidationError: If the archive is invalid.
            StorageError: If the restore cannot be completed.
        """
        manifest = self.validate_backup(archive)
        source = Path(archive)
        safety = self._create_safety_backup()
        logger.info("Restoring backup %s", source.name)

        try:
            self._apply_archive(source)
            self._validate_database()
        except Exception as error:  # noqa: BLE001 - attempt a rollback
            logger.exception("Restore failed; rolling back to safety backup")
            try:
                self._apply_archive(safety)
            except Exception:  # noqa: BLE001 - report the original failure
                logger.exception("Could not roll back to the safety backup")
            raise StorageError(
                "No se pudo restaurar la copia de seguridad."
            ) from error

        logger.info("Backup restored from %s", source.name)
        return manifest

    def _apply_archive(self, archive: Path) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            with zipfile.ZipFile(archive) as archive_file:
                self._safe_extract(archive_file, temporary_path)
            self._database.engine.dispose()
            self._replace_data(temporary_path)
        self._database.engine.dispose()

    def _replace_data(self, source: Path) -> None:
        database_source = source / _DB_MEMBER
        if database_source.is_file():
            shutil.copy2(database_source, self._settings.database_path)
        self._replace_directory(source / "images", self._settings.images_dir)
        self._replace_directory(
            source / "documents", self._settings.documents_dir
        )

    def _validate_database(self) -> None:
        database_path = self._settings.database_path
        if not database_path.is_file():
            raise StorageError("La base de datos restaurada no existe.")

        connection = sqlite3.connect(str(database_path))
        try:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise StorageError(
                    "La base de datos restaurada está dañada."
                )
            tables = {
                row[0]
                for row in connection.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
        finally:
            connection.close()

        if not _REQUIRED_TABLES.issubset(tables):
            raise StorageError(
                "La base de datos restaurada no tiene la estructura esperada."
            )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _copy_database(source_path: Path, destination_path: Path) -> None:
        source = sqlite3.connect(str(source_path))
        try:
            destination = sqlite3.connect(str(destination_path))
            try:
                source.backup(destination)
            finally:
                destination.close()
        finally:
            source.close()

    @staticmethod
    def _write_directory(
        archive: zipfile.ZipFile,
        directory: Path,
        arc_root: str,
    ) -> None:
        if not directory.exists():
            return
        for path in sorted(directory.rglob("*")):
            if path.is_file():
                arcname = f"{arc_root}/{path.relative_to(directory).as_posix()}"
                archive.write(path, arcname)

    @staticmethod
    def _replace_directory(source: Path, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        for child in destination.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
            else:
                child.unlink(missing_ok=True)
        if source.exists():
            for child in source.iterdir():
                target = destination / child.name
                if child.is_dir():
                    shutil.copytree(child, target)
                else:
                    shutil.copy2(child, target)

    @staticmethod
    def _safe_extract(
        archive: zipfile.ZipFile,
        destination: Path,
    ) -> None:
        root = destination.resolve()
        for member in archive.infolist():
            member_path = (root / member.filename).resolve()
            if not member_path.is_relative_to(root):
                raise ValidationError(
                    "La copia de seguridad contiene rutas no seguras."
                )
        archive.extractall(root)

    @staticmethod
    def _count_files(directory: Path) -> int:
        if not directory.exists():
            return 0
        return sum(1 for path in directory.rglob("*") if path.is_file())

    @staticmethod
    def _stamp() -> str:
        return utcnow().strftime("%Y-%m-%d_%H%M%S")
