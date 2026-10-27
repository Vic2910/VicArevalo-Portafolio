# Implementation Plan: Perfil público y experiencia académica

**Branch**: `001-perfil-publico` (contexto de feature; rama Git actual: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/001-perfil-publico/spec.md`

## Summary

Diseñar el inicio público en español de Victor con Flask/Jinja y lectura de Supabase. Mostrar solo identidad, conocimientos y experiencia académica aprobados; ocultar campos pendientes y secciones opcionales vacías con sus enlaces. Distinguir fallos de lectura de ausencia de publicaciones. Proyectos, contacto y CV se integran por disponibilidad explícita, sin implementar 002–007.

El repositorio contiene únicamente especificaciones y herramientas Spec Kit. La estructura y comandos siguientes son propuestas para implementación, no archivos ni pruebas ya existentes.

## Technical Context

**Language/Version**: Python 3.12 como base de compatibilidad propuesta, HTML5 y CSS.

**Primary Dependencies**: Flask 3.1, Jinja 3.1, supabase-py 2 y Pytest; fijar versiones exactas compatibles y transitivas en requirements.lock durante implementación. Sin JavaScript obligatorio.

**Storage**: PostgreSQL en Supabase Free. Instantáneas públicas separadas de borradores privados; sin otra base, Realtime ni Storage en esta feature.

**Testing**: Pytest para rutas, servicio, adaptador y contratos HTML; integración RLS en entorno aislado con anon y autenticado no administrador; auditoría automática y revisión manual WCAG.

**Target Platform**: Desarrollo Windows/PowerShell; servidor WSGI Python y navegadores móvil/escritorio. Hosting gratuito por elegir al desplegar, no requerido para validar localmente.

**Project Type**: Monolito web modular renderizado en servidor.

**Performance Goals**: Presupuestos de diseño propuestos: tres operaciones de lectura por petición, sin N+1, paginación de 100 registros hasta completar colecciones, plazo global de dependencias de 6 segundos sin reintentos automáticos. Sin truncamiento silencioso: agotamiento produce indisponibilidad de la sección.

**Constraints**: WCAG 2.1 A/AA; texto 200 %, ancho 320 px CSS; gratuidad exclusiva; lectura sin claves privilegiadas; escape Jinja. No servir contenido retirado desde caché: Cache-Control: no-store. No logs de secretos ni datos privados.

**Scale/Scope**: Un propietario, una página `/`, tres entidades de contenido y tres destinos futuros. No asumir tráfico ni disponibilidad ilimitada.

## Constitution Check

Gates revisados antes de investigación y después del diseño. PASS indica conformidad del diseño, no aceptación de una implementación todavía inexistente.

| Gate | Antes | Después | Evidencia / obligación |
|---|---|---|---|
| I. WCAG 2.1 A/AA | PASS | PASS | Contrato HTML, estados accesibles y matriz manual completa en quickstart. |
| II. Honestidad y UX | PASS | PASS | Solo instantáneas aprobadas, pendientes omitidos, vacío distinto de error, sin experiencia ficticia. |
| III. Pytest | PASS | PASS | Matriz FR/SC, fallos externos, pruebas RLS reales separadas de mocks. |
| IV. Gratuidad y privacidad | PASS | PASS | Bibliotecas libres, Supabase Free, separación física de privados, RLS y permisos mínimos. |
| V. Simplicidad | PASS | PASS | Flask/Jinja, blueprint, servicio y adaptador pequeño; sin SPA ni infraestructura adicional. |
| Alcance y revisión humana | PASS | PASS | Contenido real requiere aprobación de Victor; edición y autorización de publicaciones corresponden a 002. |

No hay violaciones ni enmiendas propuestas. Hosting y contenido real se resuelven antes de activación, sin bloquear este diseño local. Versiones exactas, licencias transitivas y permisos deberán verificarse al implementar.

## Project Structure

### Documentation (this feature)

```text
specs/001-perfil-publico/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── public-page.md
    └── public-data.md
```

tasks.md pertenece a la fase posterior speckit-tasks y no se crea aquí.

### Source Code (repository root, propuesto)

```text
app/
├── __init__.py
├── config.py
├── public/
│   ├── routes.py
│   ├── service.py
│   └── repository.py
├── templates/
│   ├── base.html
│   └── public/index.html
└── static/css/site.css
tests/
├── conftest.py
├── unit/
├── contract/
└── integration/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: Application factory y blueprint público. Servicio construye estados/destinos; adaptador concentra consultas Supabase y es inyectable. Sin repositorios genéricos, ORM ni módulos administrativos anticipados. Migraciones se crearán con CLI durante implementación.

## Phase 0 — Research

Completada en research.md: stack, publicación segura, estados, navegación, cuotas y verificación. No quedan incógnitas técnicas necesarias sin resolver. Las propuestas respetan la constitución y no sustituyen aprobación de cambios técnicos futuros.

## Phase 1 — Design & Contracts

Completada en data-model.md, contracts/public-data.md, contracts/public-page.md y quickstart.md. Compartir fuente de publicación con futuro CV. Fixtures aislados permiten evaluar sin implementar panel.

## Complexity Tracking

Sin violaciones que justificar.
