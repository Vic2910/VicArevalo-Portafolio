# Implementation Plan: CV actualizado en español e inglés

**Branch**: `005-cv-bilingue` (contexto de feature; rama Git actual: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/005-cv-bilingue/spec.md`. La mención de main en la spec es metadato histórico, no la rama actual.

## Summary

Generar PDF textual español/inglés en backend con ReportLab libre, desde una instantánea coherente de contenido publicado. Cada idioma se habilita solo con datos mínimos y textos aprobados vigentes; no hay traducción en descarga ni fallback a idioma/archivo antiguo. Selección y orden de proyectos del CV se confirman en panel y son compartidos por ambos idiomas, independientes de galería.

Reutilizar Flask/Jinja, seguridad administrativa 002 y PostgreSQL Supabase de 001–003. ReportLab Platypus produce una columna con fuentes locales incrustadas y paginación sin recortes. Validar contenido/idioma/extracción con Pytest y pypdf y revisar todas las páginas renderizadas con Poppler. No se genera un PDF real durante esta planificación.

El repositorio contiene diseños y herramientas, sin aplicación implementada. No crear dependencias, migraciones, secretos, datos personales, PDFs, tasks.md o despliegue aquí. El gate RET-001 de 004 permanece intacto: el CV usa contactos públicos aprobados del perfil y no depende del formulario ni de la bandeja privada.

## Technical Context

**Language/Version**: Python 3.12, HTML 5/CSS y catálogo es/en.

**Primary Dependencies**: Stack 002 (Flask 3.1/Jinja 3.1, Psycopg 3, supabase-py 2 para Auth, Flask-WTF, cryptography, Pytest) más ReportLab OSS estable, pypdf y fuente DejaVu Sans TTF regular/negrita local. Poppler como herramienta de QA, no servicio runtime obligatorio. Versiones exactas/transitivas y avisos de licencias se fijarán al implementar, sin usar versiones dev de documentación.

**Storage**: Supabase Free/PostgreSQL. Publicaciones actuales 001/003, selección curricular independiente, traducciones privadas en borrador y proyecciones públicas aprobadas. PDFs en memoria por petición, sin caché persistente, Storage, URLs firmadas ni archivo descargable histórico en servidor. Rol de generación solo SELECT del contenido publicado permitido.

**Testing**: Pytest para mínimo por idioma, vigencia de traducciones, selección/orden, concurrencia y fallos. Integración SQL/RLS con roles reales; pypdf para metadatos/texto/orden/estructura; Poppler y revisión visual de una y varias páginas en ambos idiomas; revisión manual web con teclado/lector/WCAG 2.1 A/AA.

**Target Platform**: Windows/PowerShell en desarrollo, WSGI HTTPS compatible con Python y bibliotecas libres en hosting gratuito por validar al desplegar. Fuentes incluidas localmente con licencia; sin fuentes de sistema o descargas remotas por visitante.

**Project Type**: Monolito Flask con descarga PDF síncrona y formularios administrativos.

**Performance Goals**: SC-008: >=95 % de descargas en <=10 s en condiciones normales. Presupuesto inicial: instantánea <=2 s, generación/validación <=6 s y margen de respuesta 2 s; medir con al menos 100 solicitudes por idioma y contenido representativo. Una generación activa por proceso y espera acotada; saturación devuelve error/reintento. SQL corto, sin bloqueo editorial durante render.

**Constraints**: Una columna A 4, margen 18 mm y texto base 11 pt propuestos; no reducir fuente para forzar una página. Sin imágenes, tablas, barras, empleo ficticio o datos esenciales en encabezados/pies. Texto/URLs largos completos con saltos seguros; tildes/caracteres preservados y cobertura de glifos comprobada. Sin IA/GitHub/SMTP/fetch de recursos durante generación. Cache-Control no-store; no emitir bytes PDF hasta completar render/validación. Presupuesto preventivo 8 MiB de PDF en memoria, sin truncar: si falta recurso, error accesible en vez de documento parcial.

**Scale/Scope**: Un propietario, dos idiomas explícitos, proyectos publicados seleccionados y ordenados por Victor. Mínimo: nombre, correo público autorizado, perfil breve, educación, >=1 habilidad y >=1 proyecto seleccionado publicado o actividad académica pertinente. Campos/editorial reales pendientes se omiten o bloquean idioma según mínimo, sin inventarlos.

## Constitution Check

Gates revisados antes de Phase 0 y después de Phase 1. PASS indica diseño conforme; no prueba funcional, revisión humana de contenido ni conformidad ya ejecutadas.

| Gate | Antes | Después | Evidencia / obligación |
|---|---|---|---|
| I. WCAG 2.1 A/AA | PASS | PASS | Selector, disponibilidad, gestión y errores accesibles; validación manual completa. PDF lineal se comprueba con extracción/selección/lector y revisión visual. |
| II. Honestidad y fuente compartida | PASS | PASS | Instantánea publicada, aprobaciones ligadas a hechos vigentes, selección explícita y sin afirmaciones añadidas. |
| III. Pytest | PASS | PASS | Matriz FR/SC, concurrencia, idioma, texto completo y fallos; RLS real adicional a mocks. |
| IV. Gratuidad y privacidad | PASS | PASS | ReportLab OSS, fuente libre y herramientas locales; sin llamadas de generación a terceros ni acceso a mensajes/secretos. |
| V. Simplicidad | PASS | PASS | Mismo monolito/base, render en memoria y snapshot SQL, sin SaaS PDF, caché distribuida o traductor obligatorio. |
| Integración y permisos | PASS | PASS | Extensiones de modelo explícitas, guard 002, lectura mínima; no activa ni modifica 004. |

No hay violaciones ni enmiendas. Revisión de permisos/traducciones y QA documental requerida antes de aceptar implementación. No se afirma afiliación Harvard/Oxford, compatibilidad universal ATS, PDF/UA o tagging automático por usar ReportLab.

## Project Structure

### Documentation (this feature)

```text
specs/005-cv-bilingue/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── cv-http.md
    └── snapshot-and-pdf.md
```

### Source Code (repository root, propuesto sobre 001–003)

```text
app/
├── __init__.py
├── config.py
├── admin/
├── security/
├── cv/
│   ├── routes.py
│   ├── admin_routes.py
│   ├── forms.py
│   ├── repository.py
│   ├── service.py
│   ├── translations.py
│   └── pdf.py
├── templates/cv/
│   ├── index.html
│   ├── unavailable.html
│   └── admin/
│       ├── projects.html
│       ├── translation_edit.html
│       └── translation_review.html
├── assets/fonts/dejavu/
│   ├── DejaVuSans.ttf
│   ├── DejaVuSans-Bold.ttf
│   └── LICENSE
└── static/css/site.css
tests/
├── fixtures/cv/
├── unit/cv/
├── contract/cv/
└── integration/cv/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: Servicio calcula disponibilidad y manifiesto común; repositorio reúne fuente en transacción de lectura, renderer solo recibe DTO aprobado, nunca cliente DB/sesión. Administrar traducciones/selección aquí reutilizando guard 002. QA genera fixtures en tmp/pdfs y artefactos finales de validación en output/pdf, fuera de documentos reales de Victor.

## Phase 0 — Research

Completada en research.md: instantánea, traducciones, mínimo/educación, selección, PDF/Unicode y QA. Investigación PDF delegada conforme a la habilidad. No quedan clarificaciones técnicas necesarias abiertas. Pendientes de contenido no se rellenan por inferencia.

## Phase 1 — Design & Contracts

Modelo y extensiones a 001/002/003 documentados en data-model.md; interfaces/seguridad/versionado/PDF en contracts/; comandos y escenarios previstos en quickstart.md. No se reescriben los diseños previos: las migraciones futuras deberán consolidar explícitamente estas extensiones y sus pruebas.

## Complexity Tracking

Sin violaciones. Una transacción read-only REPEATABLE READ asegura coherencia sin introducir versión global mutable en todas las features ni mantener locks durante generación.
