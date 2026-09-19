# Módulo: Reportes (PDF)

> Estado: **completo** (Fase 8).

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
| `ServiceReportData` | `services/report_builder` | Objeto de valor con todos los datos del reporte. |
| `ReportBuilder` | `services/report_builder` | Compone el documento con ReportLab (platypus). |
| `ReportService` | `services` | Recolecta el grafo del servicio y orquesta la generación. |
| `ServicesView` | `views` | Acción «Reporte PDF» por servicio. |

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

- Accede a los repositorios para recolectar cliente, ubicación, equipo,
  servicio, visitas, incidencias, materiales y evidencias.
- Usa ReportLab (composición) y Pillow (dimensiones de las imágenes).

## Generación

El PDF se guarda en `storage/documents/` con el nombre
`Reporte_servicio_<id>_<fecha>.pdf` y se abre con el visor predeterminado del
sistema a través de `UrlLauncher`.

## Ejemplo de uso

```python
service = ReportService(database, settings)
pdf_path = service.generate_service_report(service_id=3)
```
