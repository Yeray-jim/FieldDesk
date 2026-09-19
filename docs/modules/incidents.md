# Módulo: Incidencias

> Estado: **implementado** (servicio en Fase 4, interfaz integrada en Fase 6).

## Propósito

Documentar problemas o fallos detectados en un equipo, opcionalmente ligados a
un servicio concreto.

## Responsabilidades

- Registrar incidencias con prioridad y estado.
- Gestionar estados (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CANCELLED`).
- Guardar la resolución aplicada.
- Alimentar el dashboard con incidencias prioritarias.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Incident` | `database/models` | Entidad ORM. |
| `IncidentRepository` | `database/repositories` | Persistencia. |
| `IncidentCreate` / `IncidentUpdate` | `schemas` | Validación. |
| `IncidentService` | `services` | Reglas de negocio. |
| `IncidentsView` | `views` | Interfaz. |

## Flujo

```text
Equipo (y servicio opcional) → incidencia → estado → resolución → historial
```

## Dependencias

- Depende de `Equipment` y, opcionalmente, de `Service`.

## Ejemplo de uso

```python
service = IncidentService(repository)
incident = service.create_incident(
    IncidentCreate(equipment_id=2, title="Fuga de aceite", priority="HIGH")
)
```
