# Implementation Plan: Sincronización GitHub y dashboard administrativo

**Branch**: `006-github-metricas` (contexto solicitado; rama Git actual: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/006-github-metricas/spec.md`. main en la spec es metadato histórico; no se cambia de rama.

## Summary

Dashboard privado que consulta solo Supabase para proyectos, mensajes actuales y resultados de GitHub persistidos. Sincronización manual autorizada del perfil público Vic 2910 y repositorios públicos propios, incluidos forks, en ramas predeterminadas fijadas por SHA. Contar autoría por cuenta GitHub verificable y deduplicar por repository_id/SHA. El resultado completo y el intento parcial tienen identidad, alcance y fechas separados; jamás convertir un fallo en cero ni publicar proyectos editoriales desde repositorios.

Reutilizar Flask/Jinja y guard 002; fuentes locales 003/004. Worker del mismo monolito procesa una solicitud duradera en PostgreSQL, sin broker/cron/SaaS y sin consultas externas al abrir o recargar dashboard. Caché condicional normalizada, cuotas/esperas persistidas y promoción atómica solo tras completar y guardar el alcance.

El repositorio contiene documentos y herramientas, no aplicación. Esta entrega no implementa código, jobs, token, sincronización real, migraciones, tasks.md o despliegue. RET-001 de 004 queda intacto: mostrar estado de contacto bloqueado o métrica no disponible según fuente, sin habilitar recepción ni asumir mensajes inexistentes como cero.

## Technical Context

**Language/Version**: Python 3.12, HTML 5/CSS y JavaScript opcional solo para consultar estado local.

**Primary Dependencies**: Stack 002 (Flask 3.1/Jinja 3.1, Psycopg 3, supabase-py 2 para Auth, Flask-WTF, cryptography, Pytest) y HTTPX estable para cliente REST con timeout/transport mock. Puede consolidarse con HTTPX transitivo existente, sin duplicar clientes. Fijar versiones/licencias/transitivas al implementar.

**Storage**: Supabase Free/PostgreSQL único almacén: runs/attempts, repositorios, commits mínimos, membresía por resultado, caché de páginas, cursores, lease/fencing, cuotas y último resultado válido. Tablas privadas/RLS, roles de lectura métricas y escritura sync mínimos; sin service_role/BYPASSRLS. No mensajes ni payloads editoriales duplicados en tablas de métricas.

**Testing**: Pytest y HTTPX MockTransport con respuestas controladas multipágina,403/429/304/errores, autoría/forks, reescritura y carreras. Integración SQL/RLS real aislada, reloj inyectado y pruebas de no-egress al consultar dashboard; revisión WCAG 2.1 A/AA con teclado/lector.

**Target Platform**: Desarrollo Windows/PowerShell; WSGI HTTPS con worker local del mismo código. Hosting gratuito debe permitir ejecución/persistencia duradera mediante DB y recuperación tras pausa/reinicio. Si worker no operativo, no aceptar inicio como si ya estuviera sincronizando.

**Project Type**: Monolito modular renderizado, con tarea acotada y duradera en misma base, sin programación automática requerida.

**Performance Goals**: SC-008: Victor identifica pendientes, fecha válida y completitud en <1 min. Veinte GET consecutivos del dashboard generan cero requests GitHub. Presupuesto local propuesto: <=2 s por consulta de métrica en condiciones de prueba; estado independiente ante fallo. HTTP externo timeout total 10 s, secuencial; segmento de worker<=5 min/200 requests o cuota disponible menos reserva, lo que ocurra antes. Sin prometer completar un historial arbitrario en una ejecución.

**Constraints**: Inicios/continuaciones de intentos separados >=60 min, ampliados por proveedor/backoff; un intento activo con lease 90 s renovable y fencing. Repo/autor por ID estable, autoría de fecha<=cutoff fijo y recorrido completo sin filtros temporales de servidor. Caché hasta 16 MiB y presupuesto 006 hasta 64 MiB lógicos con umbral DB compartido 350 MiB; agotamiento=parcial/error, nunca total truncado ni upgrade. Conservar último completo y parcial identificado.

**Scale/Scope**: Un administrador, una cuenta pública y ramas predeterminadas de repositorios propios/forks públicos. Excluir privados, repos ajenos, otras ramas y commits posteriores al corte; autor desconocido/ajeno aporta cero. No incluye todo GitHub, coautoría textual, trabajo profesional ni SHA únicos globales.

## Constitution Check

Gates antes de Phase 0 y después de Phase 1. PASS de diseño, no evidencia de implementación ya ejecutada.

| Gate | Antes | Después | Evidencia / obligación |
|---|---|---|---|
| I. WCAG 2.1 A/AA | PASS | PASS | Métricas/estado/espera/alcance textuales, teclado y matriz manual completa. |
| II. Honestidad | PASS | PASS | Cuenta autor verificable, forks sin atribuir herencia ajena, período/ramas/dedupe explícitos; sin empleo o proyectos inventados. |
| III. Pytest | PASS | PASS | Matriz FR/SC, paginación/304/reescritura/carreras, RLS real y fallo independiente por métrica. |
| IV. Gratuidad y privacidad | PASS | PASS | Solo API pública y Free, cuotas/backoff, token opcional backend, sin mensajes copiados ni nuevos servicios de pago. |
| V. Simplicidad | PASS | PASS | Mismo Flask/PostgreSQL y worker local, sin SPA/broker/scheduler externo. |
| Integridad local / gate 004 | PASS | PASS | Conteos privados actuales, retirados separados; contacto bloqueado sigue bloqueado y no genera métricas cero ficticias. |

Sin violaciones/enmiendas. Revisar secretos, permisos y cuota del despliegue antes de aceptar. No se requiere conocer ni consultar datos reales de Vic 2910 para planificar; no se aprovisiona token.

## Project Structure

### Documentation (this feature)

```text
specs/006-github-metricas/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── dashboard-http.md
    └── github-sync.md
```

### Source Code (repository root, propuesto)

```text
app/
├── __init__.py
├── config.py
├── admin/
├── security/
├── metrics/
│   ├── routes.py
│   ├── service.py
│   └── repository.py
├── github_sync/
│   ├── client.py
│   ├── service.py
│   ├── repository.py
│   ├── worker.py
│   └── cli.py
├── templates/metrics/
│   ├── dashboard.html
│   └── sync_detail.html
└── static/css/site.css
tests/
├── fixtures/github/
├── unit/metrics/
├── contract/metrics/
└── integration/metrics/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: GET metrics depende únicamente de repositorios Supabase; cliente GitHub solo importado/ejecutado por worker tras solicitud autorizada. Worker puede ejecutarse como hilo del proceso del monolito o comando del mismo código para pruebas/operación; exclusión se decide en DB, no por memoria del proceso. Recepción 202 significa solicitud persistida, nunca sincronización satisfactoria.

## Phase 0 — Research

Consolidada en research.md con investigación delegada de API oficial. Resueltos autoría, fecha/corte, forks, snapshot observado, paginación/304, límites, reanudación, métricas y permisos. No quedan clarificaciones técnicas necesarias pendientes.

## Phase 1 — Design & Contracts

Modelo/estados en data-model.md, contratos de dashboard/worker/API en contracts/ y guía runnable prevista en quickstart.md. No se amplía alcance a privados, importación de proyectos o dashboard público; no se modifica 005 ni gate 004.

## Complexity Tracking

Sin violaciones. Worker duradero y caché de páginas responden a recorrido multipágina y cuota; permanecen en el monolito/base existentes. No se mantiene una transacción SQL abierta durante HTTP.
