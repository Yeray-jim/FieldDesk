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

El único campo obligatorio es el **nombre**. El teléfono, el email y la
dirección son opcionales, ya que hay clientes que no disponen de ellos.

## Registrar una ubicación

1. Entra en **Ubicaciones** (o pulsa **Nueva ubicación**).
2. Selecciona el cliente y completa, además del nombre: **estado**,
   **municipio**, **colonia o fraccionamiento**, **calle y número**, **lote**,
   **manzana** y **referencias**.

También puedes crear una ubicación sin salir del alta de un equipo: en el
desplegable **Ubicación** elige **«+ Crear nueva ubicación…»**.

## Registrar un equipo

1. Abre una ubicación y entra en **Equipos**.
2. Pulsa **Nuevo equipo** e indica nombre, tipo, marca, modelo y estado.
3. La **fecha de instalación** y el **fin de garantía** se eligen tocando el
   campo y seleccionando el día en el calendario.

## Crear un servicio

1. Entra en **Servicios** y pulsa **Nuevo servicio**.
2. Selecciona cliente y equipo, describe el trabajo y la prioridad.
3. Elige la **fecha y la hora programadas** con el calendario y el reloj.
4. Guarda el servicio.

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

## Apariencia

En **Ajustes → Apariencia** puedes elegir el tema **Sistema**, **Claro** u
**Oscuro**. El cambio se aplica al instante.

## Datos de demostración

Si quieres explorar la aplicación con información de ejemplo, abre
**Ajustes → Datos de demostración → Cargar datos de demostración**. La opción
solo está disponible cuando la base de datos está vacía.

## Consejos

- Comprueba siempre las acciones de eliminación: se te pedirá confirmación.
- Realiza backups con frecuencia para proteger tu información.
