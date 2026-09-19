# Módulo: Backup y restauración

> Estado: **completo** (Fase 9).

## Propósito

Proteger la información del técnico permitiendo respaldar y restaurar todos
los datos locales.

## Responsabilidades

- Crear un archivo ZIP con base de datos, imágenes y documentos.
- Validar un backup antes de restaurarlo.
- Crear un respaldo de seguridad antes de sobrescribir datos.
- Restaurar y validar la base de datos resultante.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `BackupService` | `services` | Crear, validar y restaurar backups. |
| `BackupManifest` | `services` | Metadatos del backup (versión, fecha, recuentos). |
| `SettingsView` | `views` | Interfaz de backup/restauración. |

## Formato

```text
FieldDesk_Backup_2026-09-18_110530.zip
├── manifest.json
├── database/fielddesk.db
├── images/
└── documents/
```

La base de datos se copia con la API `sqlite3.backup`, por lo que la copia es
consistente aunque la aplicación esté en uso.

## Flujo de restauración

```text
Seleccionar ZIP → validar estructura/manifest → confirmar
→ copia de seguridad automática de los datos actuales → restaurar
→ validar integridad y tablas → informar resultado
```

Si algo falla durante la restauración, se reaplica automáticamente la copia de
seguridad previa. Las rutas internas del ZIP se validan para evitar
extracciones fuera del destino (*zip slip*).

## Dependencias

- Usa `Settings` para localizar base de datos y almacenamiento.
- Usa `zipfile` y `shutil` de la biblioteca estándar.

## Ejemplo de uso

```python
service = BackupService(settings)
archive = service.create_backup()
service.restore_backup(archive)
```
