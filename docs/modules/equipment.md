# Módulo: Equipos

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
| `EquipmentView` | `views` | Interfaz. |

## Flujo

```text
Ubicación → equipo → estado → servicios e incidencias → historial
```

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
