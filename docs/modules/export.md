# Módulo: Exportación CSV

> Estado: **completo**.

## Propósito

Permitir que el técnico extraiga los datos principales a hojas de cálculo para
compartirlos o analizarlos fuera de la aplicación.

## Responsabilidades

- Exportar clientes, equipos, servicios, incidencias y materiales a CSV.
- Generar archivos compatibles con Excel y LibreOffice.

## Clases principales

| Clase | Capa | Responsabilidad |
| ----- | ---- | --------------- |
| `ExportService` | `services` | Consulta los repositorios y escribe los CSV. |
| `SettingsView` | `views` | Acción «Exportar a CSV». |

## Formato

- Codificación **UTF-8 con BOM** y separador `;`, de modo que Excel en
  configuraciones regionales españolas detecte bien acentos y columnas.
- Un archivo por conjunto de datos, con marca de tiempo:
  `Clientes_20260919_110530.csv`, `Equipos_...`, `Servicios_...`,
  `Incidencias_...`, `Materiales_...`.
- Se escriben en `storage/documents/`.
- La exportación de materiales incluye una columna `existencias`.

## Dependencias

- Repositorios de cada agregado y `Settings` para el directorio de salida.

## Ejemplo de uso

```python
paths = services.exports.export_all()
```
