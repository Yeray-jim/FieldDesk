# Documentación de FieldDesk

Índice de la documentación del proyecto. La documentación se mantiene
sincronizada con el código real en cada fase del desarrollo.

| Sección | Contenido |
| ------- | --------- |
| [architecture/](architecture/) | Arquitectura general, capas, flujo de datos y decisiones. |
| [database/](database/) | Modelo de datos, tablas, relaciones e integridad. |
| [modules/](modules/) | Documentación funcional de cada módulo. |
| [development/](development/) | Instalación, configuración, testing y migraciones. |
| [user/](user/) | Manual de usuario. |

## Enlaces rápidos

- [Arquitectura](architecture/architecture.md)
- [Decisiones arquitectónicas](architecture/decisions.md)
- [Modelo de datos](database/data_model.md)
- [Guía de desarrollo](development/setup.md)
- [Manual de usuario](user/manual.md)

## Estado del proyecto

Versión **0.1.0** — Fase 9 (Backup). La aplicación permite crear y restaurar
copias de seguridad completas (base de datos + imágenes + documentos) en
formato ZIP, con validación previa, copia de seguridad automática antes de
restaurar y verificación de integridad. Quedan el testing final y la
documentación de cierre (Fases 10 y 11).
