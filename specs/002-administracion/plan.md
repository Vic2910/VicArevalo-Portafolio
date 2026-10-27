# Implementation Plan: Acceso administrativo y gestión del contenido

**Branch**: `002-administracion` (identificador de feature; rama Git observada: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/002-administracion/spec.md`. La mención de main en la spec es metadato histórico, no la rama actual.

## Summary

Panel Flask/Jinja en español para el único administrador aprobado, identificado mediante Supabase Auth. Sesión opaca revocable en servidor; autorización vigente por operación. Edición con revisiones inmutables y control optimista; publicación explícita de una revisión de un solo elemento; retirada individual de conocimientos/experiencia sin perder el borrador ni la versión retirada. La fuente pública sigue las tablas de 001 y será compartida por el futuro CV.

El repositorio contiene documentos y herramientas Spec Kit, sin aplicación implementada. El diseño termina en Phase 1; no crea código, migraciones, cuentas, secretos, tasks.md ni despliegues. Gestión completa de proyectos, archivos y mensajes, IA, métricas y generación del CV pertenecen a otras features.

## Technical Context

**Language/Version**: Python 3.12, HTML5 y CSS; coherente con 001.

**Primary Dependencies**: Flask 3.1/Jinja 3.1, supabase-py 2 para Auth, Psycopg 3 para transacciones PostgreSQL, Flask-WTF 1.2 para formularios/CSRF, cryptography (Fernet) para tokens cifrados en servidor y Pytest. Fijar versiones estables exactas compatibles y transitivas en requirements.lock al implementar; no instalar versiones dev de las páginas de documentación.

**Storage**: Supabase Free único almacén: Auth, sesiones, autorización, limitador compartido, revisiones, auditoría e instantáneas públicas. Esquema privado no expuesto; conexión PostgreSQL backend TLS con roles dedicados mínimos, sin service_role, BYPASSRLS ni superusuario. Lectura pública mantiene Data API y RLS de 001.

**Testing**: Pytest para rutas, autenticación, permisos, validación, transacciones, carreras y estados; integración Supabase/PostgreSQL con identidades aisladas y roles reales; revisión automática y manual WCAG 2.1 A/AA. Reloj inyectable, sin esperar minutos reales en tests.

**Target Platform**: Desarrollo Windows/PowerShell, servidor WSGI con HTTPS y navegadores móvil/escritorio. Hosting gratuito se validará al desplegar, incluyendo conexión segura a PostgreSQL; no es necesario para diseño o validación aislada.

**Project Type**: Monolito modular con formularios renderizados, sin SPA ni JavaScript necesario.

**Performance Goals**: SC-005: flujo preparado acceso→edición→borrador→revisión→publicación→cierre en <=5 minutos sin ayuda. Presupuestos técnicos: dependencias con timeout total 8 s por operación; transacciones DB cortas con statement_timeout 3 s y lock_timeout 1 s; llamadas Auth fuera de bloqueos editoriales. Pool máximo inicial 2 conexiones por rol/proceso, un proceso inicial; sin N+1 ni reintentos automáticos de mutaciones.

**Constraints**: Gratuidad exclusiva; sesión 30 min de inactividad ajustables hasta 300 min y 24 h absolutas; limitador exacto cinco fallos consecutivos en ventana de 15 min→bloqueo 15 min desde quinto; cierre/revocación efectivos; cookies Secure/HttpOnly/SameSite=Lax; CSRF; mínimo privilegio; cero secretos en cliente, logs o documentos; Cache-Control no-store para todo /admin.

**Scale/Scope**: Un administrador inicial; tres tipos de elemento editorial. Sin delegación, registro público, recuperación autónoma, retirada del perfil ni eliminación definitiva de elementos.

## Constitution Check

Gates evaluados antes de Phase 0 y después de Phase 1. PASS refleja diseño conforme; la aceptación exige evidencia posterior.

| Gate | Antes | Después | Evidencia y condición de implementación |
|---|---|---|---|
| I. Accesibilidad verificable | PASS | PASS | Flujos completos, errores asociados, foco, confirmación accesible y matriz WCAG en quickstart. |
| II. Honestidad y UX | PASS | PASS | Revisión explícita por versión, afirmaciones verificadas, borradores incompletos privados; sin publicación automática. |
| III. Pytest | PASS | PASS | Matriz FR/SC, replay, concurrencia, rollback y roles reales; mocks no acreditan RLS. |
| IV. Gratuidad y datos protegidos | PASS | PASS | Límites de sesión propios sin función Pro; RLS, roles DB mínimos y sesiones cifradas; sin claves que eludan RLS. |
| V. Monolito mantenible | PASS | PASS | Flask/Jinja y mismo PostgreSQL; Psycopg justificado para atomicidad sin microservicios ni nueva base. |
| Permisos y cambios de datos | PASS | PASS | Revocación actual y frontera de acceso directo especificadas; revisión de migraciones/privilegios obligatoria antes de aceptar implementación. |

No hay violaciones ni enmiendas. Los roles DB usan credenciales backend sensibles, con grants explícitos y revisión específica; no son cuentas de propietario ni claves privilegiadas de Supabase. Esta planificación no aprovisiona esos roles ni modifica datos. Contenido e identidad real serán proporcionados por Victor por configuración protegida.

## Project Structure

### Documentation (this feature)

```text
specs/002-administracion/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── admin-http.md
    └── security-and-transactions.md
```

### Source Code (repository root, propuesto sobre 001)

```text
app/
├── __init__.py
├── config.py
├── public/                    # módulos propuestos en 001
├── admin/
│   ├── routes.py
│   ├── forms.py
│   ├── auth.py                # proveedor Auth, sesión y guard
│   ├── service.py             # borrador, revisión, publicación, retirada
│   └── repository.py          # SQL parametrizado y transacciones
├── security/
│   ├── csrf.py
│   ├── sessions.py
│   ├── rate_limit.py
│   └── audit.py
├── templates/admin/
│   ├── login.html
│   ├── index.html
│   ├── edit.html
│   ├── review.html
│   ├── withdraw.html
│   └── error.html
└── static/css/site.css
tests/
├── conftest.py
├── unit/admin/
├── contract/admin/
└── integration/admin/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: Reutilizar application factory, estilos y publicación de 001. Blueprint admin y módulos de seguridad pequeños. Repositorio editorial transaccional separado del adaptador público; sin ORM ni jerarquías genéricas. Preparación de roles/cuentas por operador de prueba no forma parte de rutas web.

## Phase 0 — Research

Consolidada en research.md con investigación independiente delegada por la habilidad. Resueltos duración/cierre, permisos actuales, acceso directo, limitador, transacciones y compatibilidad con 001. No quedan decisiones técnicas necesarias sin resolver.

## Phase 1 — Design & Contracts

Modelo y transiciones en data-model.md; contratos HTTP y seguridad/transacciones en contracts/; escenarios ejecutables previstos en quickstart.md. La spec 002 exige resumen para nuevas publicaciones de perfil y descripción para experiencias; 001 puede seguir leyendo publicaciones históricas parciales. No se añade retirada de perfil aunque 001 contemple su invisibilidad como defensa.

## Complexity Tracking

Sin violaciones. Psycopg y roles backend son mecanismos dentro de la misma base para transacciones y aislamiento del acceso público, no infraestructura adicional.
