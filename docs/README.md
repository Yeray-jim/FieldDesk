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

Versión **0.1.0** — Fase 4 (Servicios de negocio). Están operativos la
estructura, la configuración, el punto de entrada, los modelos ORM, la conexión
SQLite, las migraciones de Alembic, la capa de repositorios y los servicios de
negocio con validación Pydantic y reglas de dominio. La interfaz se implementa
en las fases posteriores.
