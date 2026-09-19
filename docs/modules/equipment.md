# Módulo: Equipos

> Estado: **implementado** (servicio en Fase 4, interfaz integrada en Fase 6).

## Propósito

Registrar los equipos instalados en cada ubicación y mantener su estado a lo
largo del tiempo.

## Responsabilidades

- Crear, consultar, editar y eliminar equipos.
- Gestionar el estado operativo (`OPERATIONAL`, `MAINTENANCE`,
  `OUT_OF_SERVICE`, `RETIRED`).
- Alimentar el historial técnico por equipo.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Equipment` | `database/models` | Entidad ORM (`location_id` FK). |
| `EquipmentRepository` | `database/repositories` | Persistencia. |
| `EquipmentCreate` / `EquipmentUpdate` | `schemas` | Validación. |
| `EquipmentService` | `services` | Reglas de negocio. |
| `HistoryEntry` / `HistoryService` | `services` | Historial técnico cronológico. |
| `EquipmentView` | `views` | Interfaz. |
| `EquipmentHistoryDialog` | `views` | Historial del equipo en un diálogo. |

## Flujo

```text
Ubicación → equipo → estado → servicios e incidencias → historial
```

## Historial

La acción **Ver historial** (menú de cada equipo) abre
`EquipmentHistoryDialog`, que muestra en orden cronológico inverso los
servicios, visitas, incidencias, materiales y evidencias del equipo.
`HistoryService.get_equipment_history` agrega esos datos en una lista de
`HistoryEntry` (fecha, tipo, título y detalle) sin exponer entidades ORM.

## Dependencias

- Depende de `Location`.
- Es dependencia de `Service` e `Incident`.

## Ejemplo de uso

```python
service = EquipmentService(repository)
equipment = service.create_equipment(
    EquipmentCreate(location_id=1, name="Bomba principal", type="Hidráulica")
)
```
