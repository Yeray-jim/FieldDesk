# Arquitectura de FieldDesk

## 1. Visión general

FieldDesk es una aplicación **multiplataforma y completamente offline**
construida con Python y Flet. Toda la información se almacena localmente en
una base de datos **SQLite**; no existen servidores, APIs ni servicios en la
nube.

La arquitectura sigue un enfoque **por capas** deliberadamente sencillo, sin
sobreingeniería, que separa la interfaz, la lógica de negocio y el acceso a
datos.

## 2. Diagrama de capas

```text
┌──────────────────────────────────────────────┐
│  UI — Views / Components (Flet)              │
│  Eventos: click, submit, change, navigate... │
└───────────────────────┬──────────────────────┘
                        │ schemas Pydantic (entrada)
┌───────────────────────▼──────────────────────┐
│  Services — lógica de negocio                │
│  Reglas, validación de dominio, orquestación │
└───────────────────────┬──────────────────────┘
                        │ entidades del dominio
┌───────────────────────▼──────────────────────┐
│  Repositories — acceso a datos               │
│  Operaciones CRUD por agregado               │
└───────────────────────┬──────────────────────┘
                        │ SQLAlchemy ORM
┌───────────────────────▼──────────────────────┐
│  Models + SQLite                             │
│  storage/database/fielddesk.db               │
└──────────────────────────────────────────────┘
```

Las dependencias siempre apuntan hacia abajo: la UI no conoce SQL, y los
repositorios no conocen la UI.

## 3. Responsabilidad de cada capa

| Capa | Ubicación | Responsabilidad |
| ---- | --------- | --------------- |
| Interfaz | `app/views`, `app/components` | Renderizar pantallas, capturar eventos y delegar en los servicios. Sin lógica de negocio. |
| Servicios | `app/services` | Reglas de negocio, validación, coordinación de repositorios y manejo de errores de dominio. |
| Esquemas | `app/schemas` | Validación de entrada con Pydantic antes de llegar a los servicios. |
| Repositorios | `app/database/repositories` | Operaciones de persistencia sobre un agregado. Aíslan SQLAlchemy del resto. |
| Modelos | `app/database/models` | Definición del esquema ORM y de las relaciones. |
| Base de datos | `app/database` | Motor, sesión y configuración de conexión SQLite. |
| Configuración | `app/config` | `Settings` centralizado, URL de base de datos y logging. |
| Utilidades | `app/utils` | Constantes, validadores, fechas y manejo de archivos. |

### Convenciones de los repositorios

- Cada repositorio hereda de `BaseRepository` y declara el atributo `model`.
- Reciben una `Session` abierta y **nunca** hacen `commit`: el límite
  transaccional pertenece a `Database.session`.
- Las escrituras hacen `flush` para exponer de inmediato las claves primarias
  y los errores de integridad.
- Las consultas específicas (búsquedas, filtros, conteos) viven en el
  repositorio del agregado correspondiente, no en los servicios ni en la UI.

### Convenciones de los servicios

- Cada servicio hereda de `BaseService` y recibe un `Database`.
- Cada método abre su propia unidad de trabajo con `_repositories()`, que
  crea una sesión y un bundle `Repositories`; la sesión confirma o revierte
  automáticamente al salir del bloque.
- La validación de entrada se realiza con esquemas Pydantic antes de tocar la
  base de datos.
- Las reglas de negocio lanzan excepciones de dominio
  (`ValidationError`, `NotFoundError`, `ConflictError`, `StorageError`) con
  mensajes comprensibles para el usuario.
- Los servicios comprueban las relaciones antes de eliminar y explican el
  motivo del bloqueo.

## 4. Flujo de datos

Ejemplo: registrar un cliente.

```text
1. El usuario completa el formulario en ClientForm (components)
2. on_submit construye ClientCreate (schemas, Pydantic valida)
3. ClientService.create_client(data) aplica reglas de negocio
4. ClientRepository.add(entity) persiste con SQLAlchemy
5. SQLite guarda el registro
6. El servicio devuelve el Client creado
7. La vista refresca la tabla y muestra feedback al usuario
```

El callback de la interfaz es un punto de entrada fino: extrae datos, llama al
servicio y presenta el resultado. Nunca contiene lógica de negocio extensa.

## 5. Dependencias entre módulos

- `views` y `components` dependen de `services` y `schemas`.
- `services` dependen de `database/repositories`, `schemas` y `utils`.
- `repositories` dependen de `database/models` y de la sesión.
- `config` y `utils` son transversales y no dependen de capas superiores.
- No se permiten dependencias inversas (por ejemplo, un repositorio que
  importe una vista).

## 6. Flujo principal del dominio

```text
Cliente → Ubicación → Equipo → Servicio → Visita
                                   ├── Incidencias
                                   ├── Materiales
                                   └── Evidencias
                                             ↓
                                    Historial → Reporte PDF
```

## 7. Estrategia offline

- SQLite como única fuente de datos.
- Evidencias fotográficas en `storage/images/`; SQLite solo guarda metadatos
  y rutas.
- Backups en ZIP con base de datos + imágenes + documentos.
- Exportación a CSV para intercambio manual de información.
- No existe ningún requisito de red para las funciones principales.

## 8. Programación orientada a eventos

La UI de Flet es inherentemente orientada a eventos. Para evitar callbacks
gigantes, cada evento actúa como entrada a la capa de servicios:

```python
def on_save_click(self, event: ft.ControlEvent) -> None:
    self.service_controller.create_service(self._collect_form_data())
```

## 9. Manejo de errores y logging

- Los servicios lanzan excepciones de dominio comprensibles.
- La UI las traduce a mensajes claros para el usuario (nunca tracebacks).
- El logging es centralizado (`app/config/logging_config.py`) con niveles
  `DEBUG`, `INFO`, `WARNING`, `ERROR` y `CRITICAL`, y rotación de archivos en
  `storage/logs/`.
- No se utiliza `print` como mecanismo de diagnóstico.

## 10. Interfaz y sistema de diseño

La capa de interfaz vive en `app/views` (pantallas) y `app/components`
(componentes reutilizables). Se apoya en un sistema visual único:

- **Tema**: tokens de color, espaciado, radios y efectos en
  `app/components/theme.py` (glassmorphism moderado: superficies blancas
  translúcidas, desenfoque suave y sombra ligera).
- **Componentes**: `GlassCard`, `StatCard`, `StatusBadge`,
  `GlassTextField`, `GlassDropdown`, `GlassTable`, `GlassDialog`,
  `FormDialog` (formulario validado), botones consistentes y navegación
  responsiva.
- **CRUD reutilizable**: `app/views/crud_view.py` implementa una vez el
  listado, la búsqueda, el alta, la edición, el borrado con confirmación y el
  manejo de errores. Cada pantalla de entidad solo declara sus columnas,
  campos y llamadas al servicio (DRY).
- **Estado y color**: los estados se comunican siempre con texto además de
  color (`StatusBadge`), por accesibilidad.
- **Shell responsivo**: `app/views/app_shell.py` usa un `NavigationRail` en
  escritorio y una `NavigationBar` inferior en móvil, conmutando según el
  ancho de la página.
- **Eventos finos**: los callbacks de los controles delegan en los servicios;
  no contienen lógica de negocio.
- **Feedback**: los errores de dominio se muestran como avisos claros
  (`notify`), nunca como tracebacks, y las acciones destructivas piden
  confirmación (`confirm_dialog`).

Las pantallas de clientes, ubicaciones, equipos, servicios, visitas,
incidencias y materiales están conectadas de extremo a extremo
(UI → servicios → repositorios → SQLite). El panel de control, la gestión de
materiales por servicio y la galería de evidencias (con `FilePicker` y
miniaturas Pillow) también consumen los servicios reales.

## 11. Decisiones arquitectónicas

Las decisiones relevantes y su justificación se registran en
[`decisions.md`](decisions.md).
