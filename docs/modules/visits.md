# Módulo: Visitas

> Estado: **implementado** (servicio en Fase 4, interfaz integrada en Fase 6).

## Propósito

Registrar cada visita técnica realizada en el marco de un servicio, con su
fecha, horas y trabajo efectuado.

## Responsabilidades

- Añadir visitas a un servicio.
- Registrar fecha, hora de inicio y fin, trabajo realizado y observaciones.
- Aportar información cronológica al historial.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Visit` | `database/models` | Entidad ORM (`service_id` FK). |
| `VisitRepository` | `database/repositories` | Persistencia. |
| `VisitCreate` / `VisitUpdate` | `schemas` | Validación. |
| `VisitService` | `services` | Reglas de negocio. |
| `VisitsView` | `views` | Interfaz. |

## Flujo

```text
Servicio → nueva visita → fecha, horas, trabajo → historial
```

## Dependencias

- Depende de `Service`.

## Ejemplo de uso

```python
service = VisitService(repository)
visit = service.create_visit(
    VisitCreate(service_id=3, visit_date=date.today(), work_performed="Revisión general")
)
```
