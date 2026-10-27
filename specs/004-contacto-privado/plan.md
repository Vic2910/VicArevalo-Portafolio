# Implementation Plan: Contacto persistente y bandeja privada

**Branch**: `004-contacto-privado` (contexto solicitado; rama Git actual: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/004-contacto-privado/spec.md`. `004-contacto` y main en la spec son referencias históricas; no se renombra la feature ni se cambia de rama.

**Estado**: diseño documentado con ERROR de garantía de conservación; activación bloqueada. No presentar como plan listo para habilitar recepción.

## Summary

Diseñar recepción de nombre, correo y mensaje, persistencia idempotente en Supabase y bandeja privada con lectura, marcado explícito y eliminación confirmada. Reutilizar Flask/Jinja, Psycopg y seguridad 002. Ningún correo saliente, IA, adjunto, exportación o servicio de pago.

Victor confirmó en esta planificación: mantener la exigencia estricta de 90 días y bloquear la activación hasta acreditar su cumplimiento. No se rebaja el requisito a ocultación ni a purga periódica. El diseño permite desarrollar y probar controles con datos sintéticos; la recepción real permanece deshabilitada sin campos ni aceptación de datos.

No existen aplicación, migraciones ni pruebas implementadas. No se crean credenciales, mensajes reales, jobs remotos, despliegue ni tasks.md durante esta entrega.

## Technical Context

**Language/Version**: Python 3.12, HTML 5/CSS; funcionamiento sin JavaScript obligatorio.

**Primary Dependencies**: Stack de 002: Flask 3.1/Jinja 3.1, supabase-py 2 para Auth, Psycopg 3, Flask-WTF 1.2, cryptography y Pytest. Validar correo con validador de WTForms/email-validator estable compatible, sin consulta DNS de entregabilidad. Fijar versiones exactas/transitivas/licencias al implementar. pg_cron es candidato de purga en pruebas, no garantía acreditada de borrado estricto.

**Storage**: Supabase Free/PostgreSQL único almacén. Tablas privadas de mensajes, recibos técnicos, limitador, política, salud y constancias mínimas. Roles de recepción, administración y mantenimiento separados, sin service_role, propiedad, superusuario ni BYPASSRLS. Data API no expone mensajes, recibos ni cantidades.

**Testing**: Pytest con reloj controlado, transacciones reales aisladas para carreras y permisos; mocks para fallos; auditoría automática y manual WCAG 2.1 A/AA. Pruebas de mecanismos de borrado no se confunden con acreditación de eliminación física/copia del proveedor.

**Target Platform**: Windows/PowerShell en desarrollo; WSGI HTTPS y navegadores móvil/escritorio. Supabase y hosting gratuitos verificados al desplegar. Contacto público deshabilitado mientras persista gate RET-001.

**Project Type**: Monolito Flask con formulario público y módulo administrativo de bandeja.

**Performance Goals**: SC-008: envío con datos preparados en <2 min; localizar/leer/marcar en <1 min. Bandeja paginada 25, newest-first y conteos del mismo snapshot de lectura. Presupuestos técnicos: dependencias <=8 s; SQL statement_timeout 3 s y lock_timeout 1 s; sin llamadas externas para validar correo o enviar notificaciones.

**Constraints**: Nombre 1–100, correo válido<=254 y mensaje 10–5000 caracteres Unicode tras trim; espacios interiores/saltos conservados. Recepción y expires_at inmutables, vencimiento a 90 días de 24 h UTC. Token de solicitud firmado, aleatorio y ligado a sesión de formulario, vigente 24 h. Antispam inicial configurable:3 recepciones nuevas/hora por sesión anónima,30/hora y 100/día globales, sin IP/email como clave de seguimiento. Cupo preventivo 1000 mensajes o 20 MiB de texto conservado y margen DB compartido. Límites no son garantía de disponibilidad ni sustituyen conservación.

**Scale/Scope**: Un administrador, tres campos personales, sin adjuntos/respuestas/exportaciones. Contadores de mensajes actuales para futuros consumidores privados; no dashboard independiente. Reintentos de misma solicitud válidos 24 h; tokens vencidos no crean mensajes, incluso tras limpiar recibos o 90 días.

## Constitution Check

Antes de investigación se identificó la obligación de acreditar conservación; la investigación confirmó una limitación material. Por decisión explícita de Victor se documenta Phase 1 como diseño condicionado, manteniendo ERROR y bloqueo de activación; no se declara resuelto el gate.

| Gate | Antes | Después del diseño | Evidencia / límite |
|---|---|---|---|
| I. WCAG 2.1 A/AA | PASS de diseño | PASS de diseño | Formulario/bandeja/confirmación con teclado, errores asociados y matriz completa. No es certificación ejecutada. |
| II. UX honesta | PASS de diseño | PASS de diseño | Confirmación solo tras commit; resultado incierto explícito; indisponibilidad sin formulario engañoso. |
| III. Pytest y acceso | PASS de diseño | PASS de diseño | Matriz de entradas, duplicados, fallos, RLS real, expiración y eliminación. |
| IV. Gratuidad y privacidad | Condicionado | Condicionado | Sin acceso público general ni servicios de pago; conservación estricta no acreditada. |
| V. Simplicidad | PASS de diseño | PASS de diseño | Mismo monolito y base; sin cola/SaaS adicional. |
| RET-001: eliminación estricta 90 días, copias incluidas | A verificar | **ERROR — activación bloqueada** | Cron, DELETE y filtro TTL no acreditan destrucción física/respaldos exactamente al vencer. No hay excepción aprobada. |

El plazo 90 días sí está aprobado; no se vuelve a pedir. Falta evidencia de una solución compatible que satisfaga su garantía estricta. No proponer activar por un booleano de configuración ni considerar una prueba de TTL suficiente. Suspender recepción ante fallos tampoco borra los datos existentes ni subsana incumplimiento.

## Project Structure

### Documentation (this feature)

```text
specs/004-contacto-privado/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── contact-http.md
    └── privacy-retention.md
```

### Source Code (repository root, propuesto)

```text
app/
├── __init__.py
├── config.py
├── admin/
├── security/
├── contact/
│   ├── routes.py
│   ├── admin_routes.py
│   ├── forms.py
│   ├── service.py
│   ├── repository.py
│   ├── idempotency.py
│   └── retention.py
├── templates/contact/
│   ├── form.html
│   ├── unavailable.html
│   ├── receipt.html
│   └── admin/
│       ├── inbox.html
│       ├── detail.html
│       └── confirm_delete.html
└── static/css/site.css
tests/
├── conftest.py
├── unit/contact/
├── contract/contact/
└── integration/contact/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: Separar ingestión pública de lectura administrativa. Compartir guard 002 sin ampliar grants de sus roles a mensajes por defecto. Recibos/constancias carecen de payload para no duplicar comunicaciones. Implementación de purga/proveedor no se da por resuelta por añadir retention.py.

## Phase 0 — Research

Documentada en research.md: permisos, validación, idempotencia, límites y garantía de borrado. No quedan preguntas de alcance pendientes: Victor eligió mantener exigencia estricta. RET-001 es un bloqueo técnico acreditado, no una clarificación que se pueda resolver por inferencia.

## Phase 1 — Design & Contracts

Modelo, contratos y guía generados para revisión y validación aislada. No aceptados para activación mientras RET-001 siga en ERROR. La evidencia futura debe cerrar el gate antes de habilitar recepción, o Victor tendría que solicitar una modificación explícita del requisito; no se presume esa modificación.

## Complexity Tracking

Sin excepción constitucional concedida. El bloqueo de conservación no se justifica como deuda aceptable ni se oculta con cron. Artefactos completos no equivalen a conformidad ni a permiso de activación.
