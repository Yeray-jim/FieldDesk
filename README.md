# FieldDesk

Aplicación multiplataforma y **100 % offline** para que técnicos de campo
administren clientes, ubicaciones, equipos, servicios, visitas, incidencias,
materiales, evidencias fotográficas y reportes PDF. Todos los datos se
almacenan localmente en **SQLite**; no requiere conexión a Internet.

> Versión actual: **0.1.0** (Fase 1 — Arquitectura).

## Características

- Gestión local de clientes, ubicaciones y equipos.
- Servicios, visitas, incidencias y materiales asociados.
- Evidencias fotográficas almacenadas en disco (solo se guardan metadatos).
- Historial técnico por equipo.
- Generación de reportes PDF profesionales.
- Backup y restauración de la información en formato ZIP.
- Exportación de datos a CSV compatible con Excel y LibreOffice.
- Datos de demostración opcionales para la presentación del proyecto.
- Interfaz con estilo *glassmorphism* moderado y diseño responsivo
  (desktop y móvil).

## Tecnologías

| Área            | Tecnología          |
| --------------- | ------------------- |
| Lenguaje        | Python 3.13+        |
| Interfaz        | Flet                |
| Base de datos   | SQLite              |
| ORM             | SQLAlchemy          |
| Migraciones     | Alembic             |
| Validación      | Pydantic            |
| PDF             | ReportLab           |
| Testing         | Pytest              |

## Arquitectura

FieldDesk usa una **arquitectura por capas** sencilla:

```text
UI (views/components)
        ↓
Services (lógica de negocio)
        ↓
Repositories (acceso a datos)
        ↓
Models / SQLite
```

- **views / components**: interfaz Flet orientada a eventos.
- **services**: reglas de negocio y orquestación.
- **repositories**: operaciones de persistencia por entidad.
- **database / models**: definición del esquema con SQLAlchemy.
- **schemas**: validación de entrada con Pydantic.
- **config / utils**: configuración, logging y utilidades compartidas.

El detalle completo está en [`docs/architecture/`](docs/architecture/).

## Estructura del proyecto

```text
FieldDesk/
├── app/
│   ├── main.py                  # Punto de entrada
│   ├── config/                  # Settings y logging
│   ├── database/                # Modelos y repositorios SQLAlchemy
│   ├── services/                # Lógica de negocio
│   ├── views/                   # Pantallas Flet
│   ├── components/              # Componentes UI reutilizables
│   ├── schemas/                 # Esquemas Pydantic
│   └── utils/                   # Utilidades compartidas
├── migrations/                  # Migraciones Alembic
├── storage/                     # Imágenes, documentos, BD, backups y logs
├── tests/                       # Pruebas unitarias e integración
├── docs/                        # Documentación del proyecto
├── scripts/                     # Scripts auxiliares
├── requirements.txt
├── alembic.ini
├── pytest.ini
└── README.md
```

## Instalación

Requiere Python 3.13 o superior.

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd FieldDesk

# 2. Crear y activar un entorno virtual
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. (Desarrollo) instalar dependencias de testing
pip install -r requirements-dev.txt
```

## Ejecución

```bash
python -m app.main
```

La aplicación creará automáticamente las carpetas de `storage/` necesarias y
arrancará la interfaz Flet.

## Testing

```bash
pytest                 # toda la suite
pytest -m unit         # solo pruebas unitarias
pytest -m integration  # solo pruebas de integración
```

## Migraciones

```bash
alembic upgrade head            # aplicar migraciones
alembic revision --autogenerate -m "descripción"
```

## Backup

La aplicación permite crear y restaurar respaldos (base de datos + imágenes +
documentos) en un archivo ZIP:

```text
FieldDesk_Backup_2026-09-18.zip
```

La restauración valida el archivo y crea un respaldo de seguridad antes de
sobrescribir los datos actuales. Ver [`docs/modules/backup.md`](docs/modules/backup.md).

## Uso

Consulta el manual de usuario en [`docs/user/manual.md`](docs/user/manual.md).

## Documentación

- [`docs/architecture/`](docs/architecture/) — arquitectura y decisiones.
- [`docs/database/`](docs/database/) — modelo de datos.
- [`docs/modules/`](docs/modules/) — documentación por módulo.
- [`docs/development/`](docs/development/) — guía de desarrollo.
- [`docs/user/`](docs/user/) — manual de usuario.

## Roadmap

- [x] Fase 1 — Arquitectura y estructura base.
- [x] Fase 2 — Base de datos (SQLAlchemy + Alembic).
- [x] Fase 3 — Repositorios.
- [x] Fase 4 — Servicios de negocio.
- [x] Fase 5 — Interfaz (tema, componentes, navegación, dashboard).
- [x] Fase 6 — Integración UI ↔ servicios.
- [ ] Fase 7 — Evidencias fotográficas.
- [ ] Fase 8 — Reportes PDF.
- [ ] Fase 9 — Backup y restauración.
- [ ] Fase 10 — Testing completo.
- [ ] Fase 11 — Documentación final.

## Licencia

Distribuido bajo la licencia MIT. Ver [`LICENSE`](LICENSE).
