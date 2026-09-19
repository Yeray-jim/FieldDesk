# Módulo: Servicios

## Propósito

Representar los trabajos técnicos solicitados para un equipo. Es el eje
central del flujo: agrupa visitas, incidencias, materiales y evidencias.

## Responsabilidades

- Crear, consultar, editar y eliminar servicios.
- Gestionar estado (`PENDING`, `IN_PROGRESS`, `COMPLETED`, `CANCELLED`) y
  prioridad (`LOW`, `MEDIUM`, `HIGH`).
- Relacionar cliente y equipo de forma consistente.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Service` | `database/models` | Entidad ORM. |
| `ServiceRepository` | `database/repositories` | Persistencia. |
| `ServiceCreate` / `ServiceUpdate` | `schemas` | Validación. |
| `ServiceService` | `services` | Reglas de negocio. |
| `ServicesView` | `views` | Interfaz. |

## Flujo

```text
Cliente + Equipo → descripción, fecha, prioridad, estado → visitas/incidencias/materiales/evidencias
```

## Dependencias

- Depende de `Client` y `Equipment`.
- Es dependencia de `Visit`, `Incident`, `ServiceMaterial` y `Evidence`.

## Ejemplo de uso

```python
service = ServiceService(repository)
created = service.create_service(
    ServiceCreate(client_id=1, equipment_id=2, service_type="Mantenimiento")
)
```
