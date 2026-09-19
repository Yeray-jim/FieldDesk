# Guía de desarrollo

## Requisitos

- Python 3.13 o superior.
- Git.

## Entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## Dependencias

```bash
pip install -r requirements.txt        # runtime
pip install -r requirements-dev.txt    # runtime + testing
```

Las versiones están fijadas para garantizar compilaciones reproducibles.

## Configuración

Toda la configuración se centraliza en `app/config/settings.py`
(clase `Settings`). Las rutas se derivan del directorio raíz del proyecto y
pueden sobrescribirse con variables de entorno:

| Variable | Descripción |
| -------- | ----------- |
| `FIELDDESK_PROJECT_ROOT` | Raíz del proyecto. |
| `FIELDDESK_STORAGE_DIR` | Directorio base de datos de usuario. |
| `FIELDDESK_DATABASE_PATH` | Ruta del archivo SQLite. |
| `FIELDDESK_IMAGES_DIR` | Directorio de evidencias. |
| `FIELDDESK_DOCUMENTS_DIR` | Directorio de documentos. |
| `FIELDDESK_BACKUPS_DIR` | Directorio de backups. |
| `FIELDDESK_LOGS_DIR` | Directorio de logs. |
| `FIELDDESK_ENVIRONMENT` | Entorno (`development`, `testing`, `production`). |
| `FIELDDESK_DEBUG` | `1` para activar el modo depuración. |
| `FIELDDESK_LOG_LEVEL` | Nivel de logging (`DEBUG`, `INFO`, ...). |

## Ejecución

```bash
python -m app.main
```

Al arrancar se configuran el logging y las carpetas de `storage/`
automáticamente.

## Testing

```bash
pytest                      # suite completa
pytest -m unit              # pruebas unitarias
pytest -m integration       # pruebas de integración
pytest --cov=app            # cobertura (si se instala pytest-cov)
```

Los tests usan rutas temporales (`tmp_path`) para no tocar los datos reales.

## Migraciones

```bash
alembic upgrade head                              # aplicar migraciones
alembic revision --autogenerate -m "mensaje"      # crear una migración
alembic downgrade -1                              # revertir la última
```

La URL de base de datos refleja `settings.database_url`.

## Debugging

- Activa `FIELDDESK_DEBUG=1` y `FIELDDESK_LOG_LEVEL=DEBUG`.
- Los logs se escriben en `storage/logs/fielddesk.log` con rotación.
- No se permite `print` como mecanismo de diagnóstico; usa `logging`.

## Build y distribución

Flet permite empaquetar la aplicación para escritorio y web:

```bash
flet build linux     # o windows / macos / apk / web
```

El empaquetado se abordará en una fase de distribución posterior.

## Convenciones de código

- PEP 8, nombres descriptivos y type hints en todo el código.
- Docstrings en clases y funciones públicas.
- Sin lógica de negocio en los callbacks de la interfaz.
- Sin SQL crudo fuera de los repositorios.
