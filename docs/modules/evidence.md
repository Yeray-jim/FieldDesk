# Módulo: Evidencias

> Estado: **servicio implementado** (Fase 4); la interfaz de selección y
> visualización llega en la Fase 7.

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
| `EvidenceGallery` | `components` | Visualización. |

## Flujo

```text
FilePicker → validar imagen → copiar a storage/images/ → guardar metadatos → galería
```

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
