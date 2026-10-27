# Implementation Plan: Galería y administración de proyectos

**Branch**: `003-gestion-proyectos` (contexto solicitado; rama Git actual: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/003-gestion-proyectos/spec.md`. La spec conserva `003-proyectos` como referencia del adjunto y main como metadato histórico; no se renombra la spec ni se cambia la rama Git.

## Summary

Añadir galería y fichas públicas de proyectos reales, y formularios administrativos para crear, revisar, publicar, ordenar, retirar y eliminar. Reutilizar autenticación, sesiones, CSRF, autorización vigente y control de concurrencia de 002. Separar revisiones privadas de instantáneas públicas; compartir estas últimas con futuros consumidores CV. Una imagen inmutable puede tener referencias distintas por proyecto/revisión: reemplazarla modifica solo el borrador seleccionado hasta su publicación.

Para este alcance pequeño, persistir imágenes normalizadas como BYTEA en tablas privadas de PostgreSQL Supabase, con límites estrictos. Servir imágenes mediante Flask con comprobación de publicación por petición, sin URLs públicas permanentes ni firmadas que sobrevivan a la retirada. Imagen, revisión, referencias, recibo y auditoría se confirman en la misma base/transacción; no se usa el producto Storage en esta feature. Alternativas y consecuencias en research.md.

Esta entrega es diseño, no implementación: no crea aplicación, dependencias, migraciones, proyectos reales, archivos de imagen, tasks.md ni despliegue. Los documentos 001/002 son diseños previos, no infraestructura ya existente.

## Technical Context

**Language/Version**: Python 3.12, HTML5 y CSS; JavaScript opcional.

**Primary Dependencies**: Stack previsto en 001/002 (Flask 3.1, Jinja 3.1, supabase-py 2, Psycopg 3, Flask-WTF 1.2, cryptography, Pytest) y Pillow estable compatible para validar/normalizar JPEG, PNG y WebP. Fijar versiones exactas/transitivas y licencias en requirements.lock al implementar; no asumir instalaciones existentes.

**Storage**: PostgreSQL de Supabase Free único almacén de contenido y bytes normalizados. Tablas privadas con RLS y roles backend mínimos; Data API solo instantáneas aprobadas. Rol backend_project_media solo SELECT de bytes con referencias públicas activas. Sin service_role, BYPASSRLS, buckets, CDN ni nuevo servicio.

**Testing**: Pytest para publicación, rutas, validación binaria, control de versiones, permisos, orden, referencias compartidas y fallos transaccionales; pruebas reales de grants/RLS con roles representativos en entorno aislado; evaluación automática y manual WCAG 2.1 A/AA. Consumidor CV controlado, sin PDF aquí.

**Target Platform**: Desarrollo Windows/PowerShell; servidor WSGI con HTTPS y navegadores móvil/escritorio. Hosting gratuito se selecciona/verifica al desplegar, incluyendo límites de petición y memoria para procesamiento de imágenes.

**Project Type**: Monolito Flask renderizado en servidor; extensión modular de 001/002.

**Performance Goals**: SC-007: Victor crea, revisa y publica con textos/imágenes preparados en <=5 min sin ayuda. Galería paginada 12 tarjetas, miniaturas lazy y sin bytes en consulta de listado. Ficha máximo 10 imágenes. Presupuestos propuestos: dependencias de petición <=8 s; SQL statement_timeout 3 s y lock_timeout 1 s; normalización fuera de locks, un procesamiento de imagen simultáneo por proceso. Sin N+1; pool acotado según 002 más máximo 2 conexiones del rol media en un proceso inicial.

**Constraints**: Entrada JPEG/PNG/WebP hasta 5 MiB inclusive (5,242,880 bytes), máximo 12 megapíxeles y lado 6000 px; imagen estática. Derivados WebP: principal hasta 1600 px/lado y 2 MiB, miniatura hasta 480 px/lado y 256 KiB. Hasta 10 imágenes y 20 MiB de derivados únicos por revisión; presupuesto global de bytes 64 MiB, contando imágenes de borradores/revisiones conservados. Umbral físico DB preventivo 350 MiB o cuota real inferior con margen equivalente; medir uso físico además de payload. Valores operativos propuestos para validar antes de implementación, no enmiendas a la spec ni garantías de capacidad.

**Scale/Scope**: Un administrador, portafolio pequeño, múltiples proyectos e imágenes compartidas. Sin buscador, filtros, comentarios, importación automática, historial restaurable, traducción o generación CV. Al superar recursos, rechazar nueva carga y explicar, sin modificar publicación anterior ni activar facturación.

## Constitution Check

Gates evaluados antes de Phase 0 y después de Phase 1. PASS = diseño conforme; no conformidad de software ya ejecutado.

| Gate | Antes | Después | Evidencia y condición de implementación |
|---|---|---|---|
| I. WCAG 2.1 A/AA | PASS | PASS | Alternativas por imagen, orden por campos/botones, confirmaciones accesibles y revisión completa en quickstart. |
| II. Honestidad y UX | PASS | PASS | Campos y autoría revisados, vacío honesto, publicación explícita, sin importación ni logros inventados. |
| III. Pytest | PASS | PASS | Matriz FR/SC, límites exactos, fallos, roles reales, concurrencia y consumidores consistentes. |
| IV. Gratuidad y privacidad | PASS | PASS | Supabase Free y dependencias libres; BYTEA privado acotado, RLS, no caché pública persistente ni claves privilegiadas. |
| V. Simplicidad | PASS | PASS | Mismo monolito y PostgreSQL; normalización local con Pillow, sin servicio de objetos adicional ni saga distribuida. |
| Compatibilidad 001/002 y CV | PASS | PASS | Destino proyectos se registra al implementar; guard de 002; fuente aprobada única y retirada inmediata en nuevas consultas. |

Sin violaciones ni enmiendas propuestas. BYTEA consume cuota DB compartida y transferencia: no ofrece capacidad ilimitada ni sustituye control físico del proyecto. Revisar migraciones, permisos y límites con evidencia antes de aceptar implementación. No aprovisionar credenciales/roles ni publicar datos reales durante planificación.

## Project Structure

### Documentation (this feature)

```text
specs/003-gestion-proyectos/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── projects-http.md
    └── images-and-transactions.md
```

### Source Code (repository root, propuesto sobre 001/002)

```text
app/
├── __init__.py
├── config.py
├── public/
├── admin/
├── security/
├── projects/
│   ├── routes.py
│   ├── admin_routes.py
│   ├── forms.py
│   ├── service.py
│   ├── repository.py
│   └── images.py
├── templates/projects/
│   ├── gallery.html
│   ├── detail.html
│   └── admin/
│       ├── index.html
│       ├── edit.html
│       ├── review.html
│       ├── order.html
│       └── confirm.html
└── static/css/site.css
tests/
├── conftest.py
├── fixtures/projects/
├── unit/projects/
├── contract/projects/
└── integration/projects/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: Blueprint público y administrativo de proyectos, servicio pequeño y repositorio SQL transaccional. Reutilizar seguridad 002 sin alterar sus tipos profile/skill/academic: tablas editoriales específicas de proyecto permiten eliminación definitiva aquí sin conceder DELETE sobre revisiones de 002. No guardar cargas en static ni subir archivos del usuario a Git.

## Phase 0 — Research

Completada en research.md: almacenamiento/revocación, validación, presupuestos, referencias compartidas, orden y eliminación. Investigación independiente delegada conforme a la habilidad. No quedan clarificaciones técnicas necesarias sin resolver.

## Phase 1 — Design & Contracts

Completada en data-model.md, contracts/projects-http.md, contracts/images-and-transactions.md y quickstart.md. Orden público es una operación independiente, con versión de catálogo; no publica borradores. Retirar conserva revisiones; eliminar quita contenido del proyecto y solo limpia imágenes sin referencias de ningún otro proyecto/revisión.

## Complexity Tracking

Sin violaciones. BYTEA exige límite y vigilancia DB explícitos; se elige por atomicidad y bajo volumen. Migrar a Storage por crecimiento sería decisión futura con revisión de privacidad/revocación, fuera del plan actual.
