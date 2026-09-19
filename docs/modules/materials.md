# Módulo: Materiales

> Estado: **implementado** (servicio en Fase 4, interfaz integrada en Fase 6).

## Propósito

Mantener un catálogo de materiales y registrar cuáles se consumen en cada
servicio.

## Responsabilidades

- Administrar el catálogo de materiales.
- Asociar materiales a un servicio con una cantidad.
- Reportar los materiales utilizados en el historial y en el PDF.

> No se implementa inventario avanzado (stock, entradas/salidas ni valuación).

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Material` | `database/models` | Catálogo. |
| `ServiceMaterial` | `database/models` | Asociación servicio–material. |
| `MaterialRepository` | `database/repositories` | Persistencia del catálogo y consumos. |
| `MaterialCreate` / `ServiceMaterialCreate` | `schemas` | Validación. |
| `MaterialService` | `services` | Reglas de negocio. |
| `MaterialsView` | `views` | Interfaz. |

## Flujo

```text
Catálogo → seleccionar material + cantidad → asociar al servicio → historial/PDF
```

## Dependencias

- `ServiceMaterial` depende de `Service` y `Material`.

## Ejemplo de uso

```python
service = MaterialService(repository)
service.add_material_to_service(
    ServiceMaterialCreate(service_id=3, material_id=1, quantity=2)
)
```
