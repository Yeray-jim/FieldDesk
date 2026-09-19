# Manual de usuario

FieldDesk es una aplicación offline para técnicos de campo. Toda la
información que registres se guarda en tu propio equipo; no necesitas
conexión a Internet.

## Primer inicio

Al abrir la aplicación, la base de datos y las carpetas de almacenamiento se
crean automáticamente. Puedes empezar a registrar información de inmediato.

## Crear un cliente

1. Entra en la sección **Clientes**.
2. Pulsa **Nuevo cliente**.
3. Completa los campos (los marcados con `*` son obligatorios).
4. Pulsa **Guardar**.

## Registrar una ubicación

1. Abre un cliente y entra en **Ubicaciones**.
2. Pulsa **Nueva ubicación** y completa la información.

## Registrar un equipo

1. Abre una ubicación y entra en **Equipos**.
2. Pulsa **Nuevo equipo** e indica nombre, tipo, marca, modelo y estado.

## Crear un servicio

1. Entra en **Servicios** y pulsa **Nuevo servicio**.
2. Selecciona cliente y equipo, describe el trabajo, la prioridad y la fecha.
3. Guarda el servicio.

## Registrar una visita

1. Abre un servicio y pulsa **Añadir visita**.
2. Indica la fecha, las horas y el trabajo realizado.

## Gestionar incidencias

1. Dentro de un servicio o equipo, pulsa **Nueva incidencia**.
2. Describe el problema, la prioridad y su estado.
3. Al resolverla, registra la resolución aplicada.

## Materiales

1. Abre un servicio y pulsa **Añadir material**.
2. Elige un material del catálogo e indica la cantidad utilizada.

## Evidencias fotográficas

1. Dentro de un servicio, pulsa **Añadir evidencia**.
2. Selecciona una imagen; se copiará al almacenamiento local y se asociará al
   servicio.

## Historial de un equipo

Abre un equipo y consulta la pestaña **Historial** para ver, en orden
cronológico, sus servicios, visitas, incidencias, materiales y evidencias.

## Reportes PDF

1. Abre un servicio y pulsa **Generar reporte**.
2. El PDF se guarda en `storage/documents/` y puedes abrirlo o compartirlo.

## Backup y restauración

- **Crear backup**: genera un archivo
  `FieldDesk_Backup_AAAA-MM-DD.zip` con la base de datos, las imágenes y los
  documentos.
- **Restaurar backup**: selecciona un archivo válido. La aplicación crea antes
  un respaldo de seguridad y, al terminar, te informa del resultado.

## Exportar datos

Desde **Configuración** puedes exportar clientes, equipos, servicios,
incidencias y materiales a CSV, compatible con Excel y LibreOffice.

## Consejos

- Comprueba siempre las acciones de eliminación: se te pedirá confirmación.
- Realiza backups con frecuencia para proteger tu información.
