# Módulo: Reportes (PDF)

## Propósito

Generar un reporte PDF profesional de un servicio que reúna toda la
información relevante del trabajo de campo.

## Responsabilidades

- Recolectar cliente, ubicación, equipo, servicio, visitas, incidencias,
  materiales y evidencias.
- Componer el documento con ReportLab.
- Guardar el PDF en `storage/documents/`.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `ReportService` | `services` | Recolecta datos y orquesta la generación. |
| `ReportBuilder` | `services` | Composición del documento ReportLab. |
| `ReportView` | `views` | Disparador y descarga. |

## Contenido del reporte

```text
FieldDesk
Información del cliente
Información de ubicación
Información del equipo
Información del servicio
Fecha
Trabajo realizado
Observaciones
Incidencias
Materiales
Evidencias fotográficas
```

## Dependencias

- Consume `ServiceService`, `IncidentService`, `MaterialService`,
  `EvidenceService` y `VisitService`.
- Usa ReportLab y Pillow.

## Ejemplo de uso

```python
service = ReportService(...)
pdf_path = service.generate_service_report(service_id=3)
```
