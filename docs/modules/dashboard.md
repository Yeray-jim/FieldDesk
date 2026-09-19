# Módulo: Panel de control

> Estado: **completo** (Fase 5).

## Propósito

Ofrecer una visión rápida de la carga de trabajo del técnico al abrir la
aplicación, sin saturar con gráficas innecesarias.

## Responsabilidades

- Mostrar métricas: clientes, equipos, servicios pendientes, servicios
  completados e incidencias abiertas.
- Listar servicios recientes, próximos servicios e incidencias prioritarias.
- Tolerar fallos parciales: si una consulta falla, el panel sigue mostrándose.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `DashboardView` | `views` | Compone métricas y listas. |
| `StatCard` | `components` | Tarjeta de métrica. |
| `SectionHeader` | `components` | Encabezado de sección. |
| `StatusBadge` | `components` | Estado como color + texto. |

## Flujo

```text
build() → consulta agregados a los servicios → tarjetas y listas
```

## Dependencias

- `ClientService`, `EquipmentService`, `ServiceService` e `IncidentService`.
- Solo accede a atributos escalares; no depende de relaciones ORM cargadas.

## Ejemplo de uso

Se abre automáticamente como primera pantalla de la aplicación.
