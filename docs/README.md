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

Versión **0.1.0** — Fase 10 (Testing). La suite cuenta con 141 pruebas y una
cobertura del 87 % sobre el código de `app/`. Se han corregido los errores
detectados (entre ellos, que `migrations/env.py` ignoraba una URL de base de
datos pasada programáticamente). Queda la documentación de cierre (Fase 11).
