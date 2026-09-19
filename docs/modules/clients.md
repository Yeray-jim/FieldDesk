# Módulo: Clientes

> Estado: **implementado** (servicio en Fase 4, interfaz integrada en Fase 6).

## Propósito

Gestionar la información de las empresas o personas a las que el técnico
presta servicio. Es el punto de partida del flujo funcional.

## Responsabilidades

- Crear, consultar, editar y eliminar clientes.
- Buscar y filtrar por nombre, empresa, teléfono o email.
- Verificar relaciones antes de eliminar para evitar pérdida de información.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `Client` | `database/models` | Entidad ORM. |
| `ClientRepository` | `database/repositories` | Persistencia y consultas. |
| `ClientCreate` / `ClientUpdate` | `schemas` | Validación Pydantic. |
| `ClientService` | `services` | Reglas de negocio. |
| `ClientsView` / `ClientForm` | `views` / `components` | Interfaz. |

## Flujo

```text
ClientForm → ClientCreate (Pydantic) → ClientService → ClientRepository → SQLite
```

## Dependencias

- `ClientService` → `ClientRepository`, `schemas`, `utils`.
- `ClientsView` → `ClientService`.

## Ejemplo de uso

```python
service = ClientService(repository)
client = service.create_client(
    ClientCreate(name="Empresa XYZ", company="XYZ S.A.", phone="555-0101")
)
```
