# Tasks: Contacto persistente y bandeja privada

**Input**: plan.md, spec.md, data-model.md, research.md, contracts/contact-http.md, contracts/privacy-retention.md y quickstart.md de `specs/004-contacto-privado/`; constitución 1.0.0 y seguridad 002.
**Estado**: Diseño condicionado. RET-001 permanece **ERROR — recepción real bloqueada**. Se pueden implementar controles y ensayar con datos sintéticos; completar tareas funcionales no acredita destrucción física/copia a 90 días ni autoriza activación.
**Organización**: Setup → fundamentos → US1 (P1) → US2 (P1) → US3 (P2) → cierre. Conservación es prerrequisito de activación aunque US3 sea P2; su puerta se construye antes de US1.
**Pruebas**: Pytest requerido por spec/diseño/constitución, con reloj controlado y DB/roles reales aislados para seguridad/transacciones. Escribir suites primero y comprobar fallos pertinentes antes de implementar; mocks/skips no acreditan permisos ni conservación estricta.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas desde raíz; [P] solo tras prerrequisitos y en archivos distintos. Sin mensajes reales, producción, SMTP, IA, adjuntos, exportación o servicios de pago.

## Phase 1: Setup — base compartida

**Propósito**: Reutilizar Flask/Jinja y guard/sesiones/CSRF/auditoría de 002.

- [ ] T001 Revisar base real disponible de 001/002 y registrar en specs/004-contacto-privado/implementation-notes.md factory, configuración, seguridad, pools y plantillas reutilizables; completar prerrequisitos faltantes de specs/001-perfil-publico/tasks.md y specs/002-administracion/tasks.md antes de integración administrativa, sin asumir que planes son código ni depender de implementación completa de 003.
- [ ] T002 Actualizar pyproject.toml y requirements.lock con validador WTForms/email-validator estable compatible sin consultas DNS, conservando Python 3.12 y stack 002; verificar versiones exactas/transitivas, licencias, documentación/changelog vigente y gratuidad en specs/004-contacto-privado/dependencies.md, sin instalar servicios de correo o mantenimiento de pago.
- [ ] T003 [P] Añadir nombres vacíos CONTACT_RECEIVE_DATABASE_URL, CONTACT_ADMIN_DATABASE_URL, CONTACT_RETENTION_DATABASE_URL, CONTACT_TOKEN_SIGNING_KEY y CONTACT_PAYLOAD_HMAC_KEY en .env.example; mantener exclusiones de secretos/certificados/dumps en .gitignore y origen HTTPS exacto protegido, sin valores reales.
- [ ] T004 [P] Preparar tests/conftest.py con sesión técnica HTTPS distinta de admin, reloj inyectable, datos sintéticos, proveedores/repositorios de fallo y configuración TEST_*; simulación de garantía solo en proyecto identificado como aislado, nunca flag de escape en despliegue. Setup/teardown verifican proyecto antes de modificar; integración security sin recursos se omite explícitamente.

## Phase 2: Foundational — persistencia privada y bloqueo de recepción

**Propósito**: Establecer permisos mínimos y puerta fail-closed antes de procesar datos personales.

- [ ] T005 Configurar app/config.py con roles DB separados TLS verify-full, origen exacto, petición contacto <=32 KiB, dependencias <=8 s, statement_timeout 3 s y lock_timeout 1 s; no ampliar grants implícitos auth/editor/media ni usar service_role, roles propietarios, superusuarios o BYPASSRLS. Secretos externos y logs sin parámetros personales, cuerpos ni credenciales, incluso rechazo temprano.
- [ ] T006 Crear mediante CLI descubierta con --help migraciones en supabase/migrations/ para contact_messages con todos los campos del modelo: request_hash único, «state pending/reviewed», «Estado inicial pending; received_at y expires_at inmutables, expires_at=received_at+90*24 h» y lock_version; contact_requests con «payload_hmac nullable», «state received/deleted», «message_id nullable» y todos sus campos; contact_form_sessions con opaque_hash PK/csrf_nonce/created_at/expires_at y «Sesión técnica anónima 24 h, sin IP/email/fingerprint ni payload». Registrar rutas reales generadas en specs/004-contacto-privado/implementation-notes.md sin inventar timestamps.
- [ ] T007 Crear mediante CLI migraciones de supabase/migrations/ para contact_rate_buckets con «scope session/hour/global-hour/global-day», campos técnicos y claves únicas; contact_policy con «retention_days=90», «strict_gate blocked/verified» y evidencia/configuración; contact_retention_health con «status blocked/healthy/failed/stale» y todos los campos del modelo; contact_capacity con stored_count/stored_text_bytes/updated_at singleton. Añadir índices expires_at, received_at DESC/id DESC, state/received_at y hashes/vencimientos; sin índice de correo/texto ni columna IP/user-agent/adjunto/IA.
- [ ] T008 Crear mediante CLI migraciones en supabase/migrations/ para contact_deletion_records exclusivamente «occurred_at, reason manual/expired, result success/failure», sin message_id/digest/referencia recuperable a comunicación; contact_admin_operations con operation_hash PK/action/actor_id/result/completed_at sin contenido ni vínculo recuperable tras eliminar. Aplicar matriz RLS/grants de privacy-retention.md: receive INSERT whitelist pending sin SELECT de mensaje/RETURNING contenido; admin bajo guard SELECT vivo y UPDATE solo state/lock_version, DELETE confirmado; retention solo IDs/fechas/técnicos y DELETE vencido, sin remitente/texto/edición de plazo; Data API incluso JWT admin sin mensajes/recibos/conteos/salud, private no expuesto y sin USAGE público.
- [ ] T009 Implementar app/contact/repository.py con pools separados, SQL parametrizado, contexto SET LOCAL verificado/limpiado y reloj DB; órdenes de locks fijos para política/salud→buckets→capacidad y guard admin heredado de 002. Conservar transacciones cortas, sin llamadas externas/SMTP/IA, reintentos de mutación automáticos ni contenido en auditoría.
- [ ] T010 Implementar puerta en app/contact/retention.py y registrarla en app/__init__.py antes del hook CSRF Flask-WTF y cualquier acceso a request.form/body/parser: exigir plazo 90, evidencia estricta vigente, mecanismo probado, salud, cero incidencias/vencidos y capacidad. Sin todo ello GET 503 sin campos/token y POST 503 antes de consumir datos; ningún booleano aislado ni cron healthy acredita RET-001, sin eximir CSRF cuando puerta permita continuar.

**Checkpoint**: Recepción real cerrada aunque existan tablas/mecanismos candidatos. La evidencia estricta se evalúa separadamente en T033 y el cierre; no puede inventarse para continuar.

## Phase 3: US1 — Enviar un mensaje (P1)

**Objetivo**: Recepción idempotente y accesible en ensayos aislados; estado público real de indisponibilidad mientras RET-001 siga ERROR.
**Prueba independiente**: Con garantía simulada solo en test, enviar datos válidos/doble POST y comprobar exactamente un mensaje pending; sin garantía, cero campos/token/lectura de cuerpo/persistencia.

### Pruebas primero

- [ ] T011 [P] [US1] Crear tests/unit/contact/test_validation.py para trim Unicode exterior, conteo de puntos de código, límites válidos exactos 1/100, correo 254 y cuerpo 10/5000, un carácter fuera y blancos; interior/saltos preservados, correo sin DNS ni lowercase destructivo local, NUL/controles no textuales rechazados y HTML tratado como texto.
- [ ] T012 [P] [US1] Crear tests/unit/contact/test_idempotency.py para token >=256 bits firmado/ligado a sesión 24 h, firma/vínculo/tiempo inválidos, mismo cuerpo/token, otro cuerpo 409, tombstone deleted sin recreación y replay expirado tras limpiar recibos o 90 días; CSRF renovado conserva token original y ningún contenido en cookie/URL.
- [ ] T013 [P] [US1] Crear tests/contract/contact/test_public_http.py para GET/POST/recepcion de contact-http.md: bloqueo antes de parser/CSRF sin campos/token, formulario de tres datos/finalidad/90 días solo en simulación aislada, 422 accesible, 413, 400/403, 409, 410 y 429/Retry-After; commit incierto con texto contractual, 303 solo tras commit y recibo genérico propio sin mensaje/id/conteos.
- [ ] T014 [P] [US1] Crear tests/integration/contact/test_receipt_transactions.py para doble POST/carreras, rollback en cada paso, resultado incierto y mismo token sin duplicado/otra cuota, 3/h sesión/30/h/100/día globales con ventanas UTC, capacidad 1000/20 MiB/margen DB y puerta revalidada; rol receive no puede consultar contenido/cantidades, Data API/JWT admin sin acceso, comprobar DB tras intentos.

### Implementación

- [ ] T015 [US1] Implementar app/contact/forms.py con reglas literales «Nombre 1–100, correo válido hasta 254 y mensaje 10–5000», «medir caracteres como puntos de código Unicode, no bytes» y «Preservar espacios interiores y saltos del cuerpo; no normalizar/eliminar caracteres para satisfacer mínimos»; trim exterior, validador sintáctico sin DNS/existencia, conservar correo trim sin lowercase destructivo y rechazar NUL/controles no textuales. Solo tres datos personales, sin consentimiento adicional inventado, adjunto ni honeypot personal.
- [ ] T016 [US1] Implementar app/contact/idempotency.py con «nonce aleatorio>=256 bits, issued_at, accept_until=issued_at+24 h, versión de firma y vínculo a sesión de formulario», hash de nonce y payload_hmac keyed nunca en logs; sesión técnica cookie Secure/HttpOnly/SameSite=Lax Path=/contacto sin payload/IP/email/fingerprint. Firma/tiempo siempre antes de insertar, expirado 410 aunque falte tombstone; ventana no se amplía por reintento.
- [ ] T017 [US1] Implementar recepción en app/contact/service.py y app/contact/repository.py: resolver recibo previo contextual antes de cuotas, mismo digest confirma sin leer mensaje y otro cuerpo 409; deleted 410 «La recepción anterior ya no está disponible». Para nuevo, lock política/salud/buckets/capacidad y revalidar gate; INSERT único pending con received_at DB y expires_at+2160 horas, recibo/cuotas/capacidad en mismo commit. Límites iniciales «3/h por sesión,30/h y 100/día globales» y «hasta 1000 filas almacenadas/20 MiB», incluidos vencidos no purgados; margen físico DB 350 MiB compartido o más conservador real. Borrar no devuelve cuota y fallo no confirma recepción.
- [ ] T018 [US1] Implementar app/contact/routes.py y app/templates/contact/form.html, app/templates/contact/unavailable.html y app/templates/contact/receipt.html: POST con CSRF/origen sin exenciones, capability de recibo en sesión propia no URL personal y mensaje incierto «No pudimos confirmar la recepción. Puedes reintentar esta misma solicitud»; no token nuevo automático/reenvío al login ni afirmar ausencia tras commit incierto. Aplicar no-store/CSP/cookies/headers también en errores y capacidad contact de 001 solo acreditada/operativa.
- [ ] T019 [US1] Integrar etiquetas autocomplete name/email, resumen enlazado/aria-invalid/describedby, espera/confirmación por texto, navegación/foco y límites visibles en app/templates/contact/form.html y app/static/css/site.css; ejecutar T011–T014 y revisión teclado/lector, 200 %/320 px, contraste/movimiento reducido/sin JS. Registrar specs/004-contacto-privado/validation.md y specs/004-contacto-privado/accessibility.md distinguiendo simulación de habilitación real.

**Checkpoint**: MVP técnico de recepción únicamente sintética. Recepción pública sigue cerrada y no se declara SC-004 acreditado.

## Phase 4: US2 — Consultar y marcar mensajes (P1)

**Objetivo**: Bandeja privada y marcado explícito sin cambiar vencimiento ni exponer comunicaciones/cantidades.
**Prueba independiente**: Con sesión administrativa y filas sintéticas, listar/leer/marcar/reabrir; GET no marca, vencidos no aparecen y error no se presenta como cero.

### Pruebas primero

- [ ] T020 [P] [US2] Crear tests/contract/contact/test_admin_inbox.py para listado/detalle/estado/operaciones, guard en acceso directo, 303 GET sin sesión, 401 POST, 403 y 503, 404 tras guard para eliminado/vencido, 409 versión y 422 state; lectura sin efecto, escape sin autoenlaces/prefetch y no-store, sin cantidades a no autorizados ni repetición tras reautenticar.
- [ ] T021 [P] [US2] Crear tests/integration/contact/test_private_access.py para anon/authenticated/JWT admin y roles receive/admin/retention/previos mediante select=*, UUID, joins/conteos/mutaciones: solo admin con guard/contexto vigente lee mensajes vivos; no fuga de pool, cambios de received_at/expires_at o acceso implícito. Comparar bandeja/conteos en mismo snapshot, marcado concurrente y rollback/recibo incierto sin falso éxito ni contenido en auditoría.

### Implementación

- [ ] T022 [US2] Implementar bandeja/detalle/conteos en app/contact/repository.py y app/contact/service.py con «expires_at>referencia temporal DB», «paginación 25 y orden received_at DESC,id DESC» y total/pending/reviewed del mismo snapshot; lecturas cortas y tiempo comprobado antes de entregar para no exponer vencidos. GET no cambia state/fechas; vacío solo tras consulta correcta, fallo unavailable/503 sin ceros inventados; consumidores privados futuros usan mismo guard/filtro, sin dashboard nuevo.
- [ ] T023 [US2] Implementar marcado pending↔reviewed en app/contact/service.py y app/contact/repository.py comparando lock_version, cambiando solo state/version con recibo operativo sanitizado; revalidar sesión/autoridad vigente en transacción y confirmar solo tras commit. Operation capability propia permite resolver incertidumbre sin payload/referencia recuperable tras borrado; no reejecutar tras login.
- [ ] T024 [US2] Implementar rutas de bandeja/detalle/estado/operaciones en app/contact/admin_routes.py y app/templates/contact/admin/inbox.html, app/templates/contact/admin/detail.html con estado textual y controles explícitos; mostrar nombre/correo/texto/recepción/vencimiento solo tras guard, sin safe/HTML activo/imágenes remotas/autoenlace/prefetch/IA/analytics/SMTP. Integrar alerta de conservación código/fecha en vistas admin aunque falle lectura de bandeja, sin revelar comunicación.
- [ ] T025 [US2] Ejecutar T020–T021 y regresión US1; revisar teclado/lector, estados vacío/error/conflicto/sesión vencida y marcado con 200 %/320 px/sin JS; registrar specs/004-contacto-privado/validation.md y specs/004-contacto-privado/accessibility.md. Medir localizar/leer/marcar con Victor <1 min y envío sintético preparado con visitante <2 min; dejar SC-008 pendiente si falta participante, sin inventar tiempos.

**Checkpoint**: US1/US2 demostrables con fixtures; activación aún depende de conservación estricta, no de prioridad de US3.

## Phase 5: US3 — Eliminar y aplicar la conservación (P2)

**Objetivo**: Eliminación confirmada, caducidad de acceso y controles candidatos de purga, preservando explícito bloqueo RET-001.
**Prueba independiente**: Cancelar/confirmar borrado de fila sintética, probar un microsegundo antes/al/después de 90 días en pending/reviewed; verificar constancias mínimas y alerta/bloqueo ante fallos. Esas pruebas no acreditan copias/físico.

### Pruebas primero

- [ ] T026 [P] [US3] Crear tests/contract/contact/test_admin_delete.py para GET confirmación sin efecto y POST confirmado ligado a sesión/id/versión/acción, cancelar sin cambios, caducidad/CSRF/origen/permiso/versiones y commit incierto sin éxito/replay; mensaje eliminado desaparece de detalle/bandeja/cantidades y recibo no expone comunicación.
- [ ] T027 [P] [US3] Crear tests/integration/contact/test_retention_controls.py con reloj DB controlado: t=90 días−1 microsegundo conserva mensaje salvo borrado manual, al vencer se excluye de lectura/conteos, leer/marcar no cambia fechas; purga de ambos estados y fallos/rollback/carreras, limpieza digest/recibo/capacidad/constancia mínima, replay tras borrar/tombstone expirada y restauración cerrada. Separar resultados TTL/DELETE de SC-004 estricta no acreditada.

### Implementación y evaluación

- [ ] T028 [US3] Implementar borrado manual en app/contact/repository.py y app/contact/service.py: confirmar id/version/acción, eliminar mensaje, limpiar payload_hmac/message_id y dejar tombstone received→deleted solo hasta token_expires_at si sigue vigente, ajustar capacidad y constancia/recibo sanitizados en transacción. «Solo fecha, motivo y resultado; sin remitente, cuerpo, payload hash o ID enlazable a comunicación eliminada»; recibo administrativo tampoco restaura vínculo, cancelar cero cambios y fallo sin confirmación.
- [ ] T029 [US3] Implementar GET/POST eliminar de app/contact/admin_routes.py y app/templates/contact/admin/confirm_delete.html con guard/CSRF/origen, confirmación completa sin modal obligatorio, consecuencias y cancelar/eliminar distinguibles por nombre; PRG solo tras commit y recibo propio para incertidumbre, sin repetición después de reautenticar.
- [ ] T030 [US3] Implementar purga candidata aislada en app/contact/retention.py y SQL revisado en supabase/migrations/ bajo backend_contact_retention: solo vencidos, misma transacción para mensaje/derivados sensibles/capacidad/constancia, sin leer remitente/texto ni extender fechas. Ensayar invocación manual con reloj controlado; documentar candidato pg_cron cada segundo con SQL estático/SECURITY INVOKER privado/EXECUTE revocado a PUBLIC en specs/004-contacto-privado/retention-evidence.md, sin crear job remoto durante generación de tareas ni tratar cadencia como tolerancia aprobada.
- [ ] T031 [US3] Implementar salud y bloqueo en app/contact/retention.py y app/contact/service.py: failed/stale ante fallo/atraso/vencidos/salud no verificable, alerta persistente solo código/fecha/resultado y reintento de purga con espera acotada sin mover expires_at. Retomar exige resolver todos los pendientes y evidencia estricta vigente, nunca un heartbeat healthy; suspensión no sustituye borrado pendiente ni cierra RET-001.
- [ ] T032 [US3] Implementar limpieza acotada de sesiones/recibos/buckets técnicos en app/contact/retention.py con «máximo 24 h desde emisión» y constancias mínimas 90 días como propuesta operativa, sin contenido/correlación al remitente; token expirado nunca inserta tras limpieza. Documentar restauración aislada con recepción/lectura cerradas y reconciliación de vencimientos/borrados/recibos antes de cualquier apertura en specs/004-contacto-privado/operations.md, sin dumps gestionados por aplicación ni PITR/upgrade.
- [ ] T033 [US3] Evaluar en specs/004-contacto-privado/retention-evidence.md evidencia verificable de mecanismo estricto y copias físicas/WAL/respaldos/restauración compatible con gratuidad y exactamente 90 días, usando fuentes primarias vigentes; documentar requisitos acreditados y faltantes. Mantener RET-001 ERROR y recepción deshabilitada si no se demuestra garantía, aunque TTL/DELETE/VACUUM/cron funcionen; no cambiar plazo ni asumir ausencia de copias internas del proveedor.
- [ ] T034 [US3] Ejecutar T026–T027, regresiones US1/US2 y revisión accesible de cancelación/confirmación/fallo/alerta sin JS con teclado/lector; actualizar specs/004-contacto-privado/validation.md y specs/004-contacto-privado/accessibility.md separando caducidad, borrado lógico y garantía física/copia. SC-004 queda pendiente mientras RET-001 no se cierre con evidencia; controles candidatos terminados no equivalen a activación aprobada.

**Checkpoint**: Borrado manual y defensas candidatas comprobables; no prometer que el requisito estricto se puede cumplir sin resolver evidencia de proveedor/mecanismo.

## Phase 6: Polish — seguridad, accesibilidad y cierre condicionado

- [ ] T035 [P] Actualizar specs/004-contacto-privado/quickstart.md con comandos PowerShell realmente implementados, HTTPS/origen, TEST_* y roles aislados, CLI/migraciones/advisors descubiertos por --help y limpieza verificada; documentar estado público 503 obligatorio, pruebas sintéticas con garantía simulada solo aislada y limitación de SC-004, sin escape de producción ni job/automatización remota de planificación.
- [ ] T036 Ejecutar tests/unit/contact, tests/contract/contact y tests/integration/contact -m security más regresiones 001/002; completar specs/004-contacto-privado/validation.md con commit/versiones/licencias, grants/RLS reales, carreras/cuotas/límites exactos/recibos, SQL/SDK/HTML/cookie/URL/logs/caché sin payload ni secretos, sin dependencia de SMTP/IA y trazabilidad FR-001–016/SC-001–008. No acreditar seguridad con mocks/skips ni garantía física por pruebas de purga.
- [ ] T037 Completar specs/004-contacto-privado/accessibility.md con axe gratuito y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables a formulario/422/429/recibo/indisponibilidad, bandeja/detalle/estado/borrado/alerta/conflicto/timeout; teclado/lector/foco/200 %/320 px/contraste/espaciado/orientación/movimiento reducido/sin JS, justificación de no aplicables y SC-008 medido con participantes. Corregir app/static/css/site.css y plantillas de contacto sin romper 001/002.
- [ ] T038 Revisar specs/004-contacto-privado/retention-evidence.md y consolidar en specs/004-contacto-privado/validation.md estado de cada FR/SC, revisión específica de permisos/privacidad/copias y bloqueos de aceptación. Mantener recepción real cerrada mientras RET-001 sea ERROR, falte evidencia obligatoria o haya defectos abiertos; una eventual solución conforme exige revisión documentada antes de apertura, y cualquier cambio del requisito requiere instrucción nueva explícita de Victor, sin volver a pedir plazo ya aprobado ni desplegar en esta tarea.

## Dependencies & Execution Order

```text
001 público + 002 seguridad disponibles
  → Setup T001–T004 → Fundamentos T005–T010 (puerta cerrada)
    → US1 T011–T019 (P1, recepción sintética)
      → US2 T020–T025 (P1, bandeja sintética)
        → US3 T026–T034 (P2, eliminación/ensayos/evidencia)
          → Cierre T035–T038

Activación real: además requiere RET-001 acreditado + mecanismo/salud/capacidad
                + todos los controles y evidencias obligatorios completos.
```

T002 precede T003/T004; fundamentos T005→T006→T007→T008→T009→T010. Ninguna historia procesa datos personales antes de puerta T010; el hook va antes del parser/CSRF, pero no sustituye CSRF para solicitudes permitidas. En cada historia escribir suites antes de implementar y ejecutar integración después de aplicación/migraciones. Implementación US1 T015→T016→T017→T018→T019, US2 T022→T023→T024→T025 y US3 T028→T029→T030→T031→T032→T033→T034.

US1 se evalúa con persistencia/gate simulado solo en pruebas, sin bandeja ni correo saliente. US2 usa mensajes/identidades preparados independientemente de envío público. US3 usa mensajes fechados sintéticos sin esperar 90 días y prueba cada eliminación por separado. Integración comparte repository.py/service.py/retention.py/admin_routes.py y se hace secuencialmente; independencia de prueba no elimina dependencias de seguridad.

T033 puede quedar sin evidencia suficiente: registrar bloqueo concreto y completar controles/evidencia independientes, sin inventar solución ni marcar RET-001 resuelto. T038 informa cierre de tareas implementadas separado de aceptación/activación; el orden P2 de US3 jamás habilita recepción temprana.

## Parallel Examples

- Setup: T003 (.env.example/.gitignore) y T004 (fixtures/configuración de pruebas) después de T002.
- US1: T011 (validación), T012 (tokens), T013 (HTTP) y T014 (transacciones/permisos) pueden escribirse juntos tras fundamentos con interfaces acordadas; ejecuciones reales esperan implementación y fixtures aisladas por caso.
- US2: T020 (contrato de bandeja) y T021 (acceso/DB) pueden prepararse en paralelo tras US1.
- US3: T026 (HTTP eliminación) y T027 (conservación candidata) pueden prepararse en paralelo tras US2; carreras deliberadas se prueban con aislamiento del resto de suites.
- Cierre: T035 documentación puede avanzar con resultados ya disponibles; T036–T038 consolidan archivos de evidencia secuencialmente.

## Implementation Strategy

1. Reutilizar seguridad y preparar esquema/gate fail-closed; conservar el estado público sin campos ni aceptación de datos mientras RET-001 siga ERROR.
2. MVP técnico US1 con datos sintéticos: validación, solicitud única, límites y confirmación honesta, sin SMTP/IA. No es MVP activable.
3. Añadir US2 con mensajes sintéticos: guard vigente, cantidades coherentes, lectura sin marcado y POST explícito; revisar accesibilidad de cada incremento.
4. Añadir US3: borrado confirmado, caducidad de acceso/purga candidata, limpieza/alertas y evaluación estricta independiente. Completar controles posibles aunque evidencia del proveedor permanezca pendiente.
5. Aceptación para activación requiere US1+US2 y conservación efectiva de US3 además de evidencia RET-001, seguridad real y WCAG; jamás abrir por flag, cron exitoso o rebaja implícita del plazo.

## Trazabilidad

US1: FR-001/002/003/004/008/010/012/013, SC-001/003/005/007 y parte SC-008. US2: FR-005/006/011/012/013/014/016, SC-002/006/007/008. US3: FR-003/007/008/009/013/014/015/016, SC-004/005/006/007. T010 cubre gate antes del parser; T033/T038 mantienen explícita aceptación estricta pendiente.

Las tareas citan enum, nullabilidad, límites e invariantes del modelo y exigen incorporar todos los campos de sus tablas; nombres de archivo de migraciones se registran al crearlos con CLI. Datos personales solo viven en contact_messages: recibos/constancias/salud y auditoría nunca duplican comunicaciones.
