"""File storage helpers.

FieldDesk keeps user files (evidence images and generated documents) on disk
and stores only metadata in SQLite. These helpers centralise the naming and
copying rules so the service layer does not deal with filesystem details.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from uuid import uuid4

from app.utils.dates import utcnow
from app.utils.exceptions import StorageError, ValidationError

IMAGE_EXTENSIONS = frozenset(
    {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
)


def is_supported_image(path: Path) -> bool:
    """Return whether the file has a supported image extension."""
    return path.suffix.lower() in IMAGE_EXTENSIONS


def unique_filename(original_name: str) -> str:
    """Build a collision-free filename preserving the original extension."""
    suffix = Path(original_name).suffix.lower()
    stamp = utcnow().strftime("%Y%m%d_%H%M%S")
    return f"{stamp}_{uuid4().hex[:12]}{suffix}"


def store_image(source: Path, destination_dir: Path) -> Path:
    """Copy an image into the storage directory.

    Args:
        source: Path of the selected image.
        destination_dir: Directory where the image must be stored.

    Returns:
        The path of the stored copy.

    Raises:
        ValidationError: If the source is missing or not a supported image.
        StorageError: If the copy operation fails.
    """
    source = Path(source)
    if not source.is_file():
        raise ValidationError("El archivo seleccionado no existe.")
    if not is_supported_image(source):
        raise ValidationError(
            "El archivo no es una imagen compatible "
            "(jpg, jpeg, png, gif, bmp o webp)."
        )

    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / unique_filename(source.name)
    try:
        shutil.copy2(source, destination)
    except OSError as exc:
        raise StorageError("No se pudo guardar la imagen.") from exc
    return destination


def delete_file(path: Path) -> None:
    """Delete a stored file if it exists.

    Raises:
        StorageError: If the file exists but cannot be removed.
    """
    try:
        Path(path).unlink(missing_ok=True)
    except OSError as exc:
        raise StorageError("No se pudo eliminar el archivo almacenado.") from exc


def read_image_bytes(path: Path) -> bytes | None:
    """Read an image file as raw bytes.

    Returns:
        The file contents, or ``None`` when the file cannot be read.
    """
    try:
        return Path(path).read_bytes()
    except OSError:
        return None


def make_thumbnail(
    path: Path,
    size: tuple[int, int] = (320, 320),
) -> bytes | None:
    """Build a JPEG thumbnail for an image file.

    Args:
        path: Path of the source image.
        size: Maximum bounding box of the thumbnail.

    Returns:
        The encoded JPEG bytes, or ``None`` when the file is not a readable
        image or Pillow is unavailable.
    """
    try:
        from io import BytesIO

        from PIL import Image
    except ImportError:  # pragma: no cover - Pillow is a hard dependency
        return None

    try:
        with Image.open(path) as image:
            converted = image.convert("RGB")
            converted.thumbnail(size)
            buffer = BytesIO()
            converted.save(buffer, format="JPEG", quality=82)
            return buffer.getvalue()
    except Exception:  # noqa: BLE001 - any decoding error yields no preview
        return None
