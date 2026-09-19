# Módulo: Ubicaciones

> Estado: **implementado** (servicio en Fase 4, interfaz integrada en Fase 6).

## Propósito

Representar las sedes o instalaciones físicas de un cliente donde residen los
equipos.

## Responsabilidades

- Administrar las ubicaciones asociadas a un cliente.
- Servir de contexto para localizar equipos.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Location` | `database/models` | Entidad ORM (`client_id` FK). |
| `LocationRepository` | `database/repositories` | Persistencia. |
| `LocationCreate` / `LocationUpdate` | `schemas` | Validación. |
| `LocationService` | `services` | Reglas de negocio. |
| `LocationsView` | `views` | Interfaz. |

## Flujo

```text
Cliente seleccionado → listar sus ubicaciones → crear/editar → refrescar
```

## Dependencias

- Depende de `Client`.
- Es dependencia de `Equipment`.

## Ejemplo de uso

```python
service = LocationService(repository)
location = service.create_location(
    LocationCreate(client_id=1, name="Sucursal Centro", address="Av. Central 123")
)
```
