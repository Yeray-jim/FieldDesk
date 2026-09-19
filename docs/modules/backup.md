# Módulo: Backup y restauración

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
| `BackupManifest` | `schemas` | Metadatos del backup (versión, fecha). |
| `SettingsView` | `views` | Interfaz de backup/restauración. |

## Formato

```text
FieldDesk_Backup_2026-09-18.zip
├── fielddesk.db
├── images/
├── documents/
└── manifest.json
```

## Flujo de restauración

```text
Validar ZIP → verificar estructura/manifest → backup de seguridad
→ restaurar → validar base de datos → informar resultado
```

## Dependencias

- Usa `Settings` para localizar base de datos y almacenamiento.
- Usa `zipfile` y `shutil` de la biblioteca estándar.

## Ejemplo de uso

```python
service = BackupService(settings)
archive = service.create_backup()
service.restore_backup(archive)
```
