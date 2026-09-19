# Decisiones arquitectónicas (ADR)

Registro breve de las decisiones que afectan a la arquitectura de FieldDesk.
Cada entrada indica contexto, decisión y consecuencias.

## ADR-001 — Arquitectura por capas sencilla

- **Contexto**: se necesita una base mantenible y escalable sin caer en
  sobreingeniería.
- **Decisión**: usar cuatro capas conceptuales (UI, servicios, repositorios,
  modelos/SQLite) con dependencias unidireccionales.
- **Consecuencias**: código fácil de probar y entender; los servicios pueden
  probarse sin interfaz; se evita el acoplamiento con Flet.

## ADR-002 — SQLite + SQLAlchemy + Alembic

- **Contexto**: la aplicación es offline y monopuesto.
- **Decisión**: SQLite como motor, SQLAlchemy como ORM y Alembic para
  migraciones versionadas. Prohibido SQL crudo en la aplicación.
- **Consecuencias**: portabilidad total del archivo de base de datos y
  evolución controlada del esquema.

## ADR-003 — Evidencias en sistema de archivos, no como BLOB

- **Contexto**: las fotografías pueden ser grandes.
- **Decisión**: guardar las imágenes en `storage/images/` y almacenar en
  SQLite únicamente metadatos y la ruta al archivo.
- **Consecuencias**: base de datos ligera; los backups deben incluir el
  directorio de almacenamiento.

## ADR-004 — Flet 1.0 como framework de interfaz

- **Contexto**: se requiere una única base de código para escritorio y móvil.
- **Decisión**: usar Flet 1.0 (API `ft.run(main)` con modelo de controles y
  eventos) y componentes reutilizables propios.
- **Consecuencias**: la capa de UI queda aislada del resto; cualquier cambio
  de framework no afecta a servicios ni repositorios.

## ADR-005 — Configuración centralizada

- **Contexto**: no deben existir rutas "hardcodeadas".
- **Decisión**: una única clase `Settings` (`app/config/settings.py`) deriva
  todas las rutas del proyecto y admite sobrescritura por variables de
  entorno.
- **Consecuencias**: pruebas aisladas mediante rutas temporales y despliegues
  portables.

## ADR-006 — Validación con Pydantic en la frontera

- **Contexto**: la UI no debe enviar datos inválidos a la lógica de negocio.
- **Decisión**: definir esquemas Pydantic (`Create`, `Update`) en
  `app/schemas` y validarlos antes de llamar a los servicios.
- **Consecuencias**: errores detectados pronto y mensajes claros para el
  usuario.

## ADR-007 — Glassmorphism moderado

- **Contexto**: se busca una estética moderna sin sacrificar usabilidad.
- **Decisión**: aplicar glassmorphism de forma contenida (transparencias y
  desenfoques suaves) sobre un sistema de componentes reutilizables y un tema
  visual único.
- **Consecuencias**: prioridad a legibilidad, jerarquía y consistencia por
  encima del efecto visual.

## ADR-008 — Estructura de almacenamiento bajo `storage/`

- **Contexto**: el enunciado sugiere `storage/images` y `storage/documents`;
  bases de datos, backups y logs también necesitan ubicación.
- **Decisión**: centralizar todo en `storage/` con subcarpetas
  `images/`, `documents/`, `database/`, `backups/` y `logs/`.
- **Consecuencias**: un único directorio de datos fácil de respaldar o
  portar; las carpetas generadas se excluyen del control de versiones salvo
  su marca `.gitkeep`.

## ADR-009 — Política de borrado segura

- **Contexto**: eliminar datos con histórico (servicios, incidencias,
  equipos) puede provocar pérdida irreversible.
- **Decisión**: usar `ON DELETE RESTRICT` para las relaciones de negocio
  (cliente→ubicación/servicio, ubicación→equipo, equipo→servicio/incidencia,
  material→consumo), `CASCADE` solo para hijos compuestos sin vida propia
  (servicio→visitas/evidencias/consumos) y `SET NULL` para
  servicio→incidencia. La capa de servicios validará antes de borrar.
- **Consecuencias**: la base de datos actúa como red de seguridad ante
  borrados accidentales; el usuario recibe un bloqueo explícito en lugar de
  una pérdida silenciosa. Detalle en
  [`../database/data_model.md`](../database/data_model.md).

## ADR-010 — Timestamps en UTC sin zona

- **Contexto**: SQLite no conserva la zona horaria de los `DateTime`.
- **Decisión**: almacenar `created_at`/`updated_at` como UTC "naive"
  mediante el helper `app.utils.dates.utcnow`.
- **Consecuencias**: orden y comparación consistentes independientemente de
  la zona del equipo. La conversión a hora local se hará en la capa de
  presentación cuando sea necesaria.
