# Módulo: Evidencias

> Estado: **completo** (servicio en Fase 4, selección y visualización en
> Fase 7).

## Propósito

Asociar fotografías a los servicios como respaldo visual del trabajo
realizado.

## Responsabilidades

- Seleccionar imágenes desde el sistema de archivos.
- Copiarlas a `storage/images/` con un nombre único.
- Registrar en SQLite únicamente los metadatos y la ruta.
- Visualizar y eliminar evidencias.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Evidence` | `database/models` | Metadatos de la evidencia. |
| `EvidenceRepository` | `database/repositories` | Persistencia. |
| `EvidenceCreate` | `schemas` | Validación. |
| `EvidenceService` | `services` | Copia de archivos y reglas. |
| `image_thumbnail` | `components/gallery` | Miniatura JPEG con Pillow. |
| `ImagePreviewDialog` | `components/gallery` | Visor a tamaño completo. |
| `ServiceEvidenceDialog` | `views` | Galería, selección con `FilePicker` y borrado. |

## Flujo

```text
ServiceEvidenceDialog → FilePicker (async, múltiple) → EvidenceService.add_evidence
→ validar imagen → copiar a storage/images/ → guardar metadatos → refrescar galería
```

## Interfaz

La acción **Evidencias** de cada servicio abre una galería modal con
miniaturas generadas por Pillow. Permite seleccionar varias imágenes, verlas a
tamaño completo, eliminarlas (con confirmación, borrando también el archivo) y
resume el recuento de evidencias.

## Dependencias

- Depende de `Service` y de `utils/files` para el manejo de rutas.

## Regla clave

Las imágenes **nunca** se almacenan como BLOB en SQLite (ver
[ADR-003](../architecture/decisions.md)).

## Ejemplo de uso

```python
service = EvidenceService(repository, settings)
evidence = service.add_evidence(
    EvidenceCreate(service_id=3, description="Estado final del equipo"),
    source_path="/ruta/foto.jpg",
)
```
