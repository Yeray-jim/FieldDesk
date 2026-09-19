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

## 10. Decisiones arquitectónicas

Las decisiones relevantes y su justificación se registran en
[`decisions.md`](decisions.md).
