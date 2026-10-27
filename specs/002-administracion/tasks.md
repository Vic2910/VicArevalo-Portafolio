# Tasks: Acceso administrativo y gestión del contenido

**Input**: plan.md, spec.md, data-model.md, research.md, contracts/admin-http.md, contracts/security-and-transactions.md y quickstart.md de `specs/002-administracion/`; constitución 1.0.0 y contratos públicos de 001.
**Organización**: Setup → fundamentos → US1 → US3 → US2 → US4 → cierre. Todas las historias son P1; se conserva su ID de la spec, ordenando primero los controles que bloquean edición.
**Pruebas**: Pytest explícito en diseño y constitución. Escribir suites antes de implementar y comprobar fallos relevantes. Reloj inyectable; seguridad y atomicidad se acreditan además con roles/DB reales aislados. Skip no equivale a PASS.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas desde raíz. [P] solo permite paralelismo tras dependencias previas y en archivos distintos.
**Alcance**: Plan de ejecución, sin código ni aprovisionamiento en esta entrega. No implementar proyectos/archivos/mensajes, IA, métricas o PDF; consumidores CV controlados leen la fuente publicada. Sin registro, delegación, recuperación autónoma, retirada de perfil ni eliminación definitiva.

## Phase 1: Setup — infraestructura compartida

**Propósito**: Integrar el panel en el monolito de 001 sin duplicar su base.

- [ ] T001 Revisar implementación disponible de 001 y registrar en specs/002-administracion/implementation-notes.md la disponibilidad de app/__init__.py, app/config.py, app/templates/base.html, app/static/css/site.css, tests/conftest.py y tablas públicas; reutilizarlos si existen y, si solo hay documentos, completar sus prerrequisitos de specs/001-perfil-publico/tasks.md antes de integrar 002, sin marcar 001 completa por inferencia.
- [ ] T002 Ampliar pyproject.toml y requirements.lock con versiones estables exactas compatibles de Psycopg 3, Flask-WTF 1.2, cryptography y soporte de pool usado, manteniendo Python 3.12/Flask/Jinja/supabase-py/Pytest; verificar documentación/changelog vigente antes de implementar y registrar licencias transitivas, avisos, gratuidad y límites en specs/002-administracion/dependencies.md.
- [ ] T003 [P] Añadir nombres vacíos SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, ADMIN_AUTH_DATABASE_URL, ADMIN_EDITOR_DATABASE_URL, SECRET_KEY, SESSION_ENCRYPTION_KEY, LOGIN_HMAC_KEY y ADMIN_ALLOWED_ORIGIN en .env.example; excluir .env, certificados privados y secretos mediante .gitignore, sin credenciales reales.
- [ ] T004 [P] Preparar tests/conftest.py para cliente HTTPS, reloj controlado, proveedor Auth inyectable, identidades sintéticas y configuración TEST_* protegida; distinguir suites sin red de integración marcada security y omitir explícitamente esta última cuando falte entorno aislado.

## Phase 2: Foundational — contratos y persistencia bloqueantes

**Propósito**: Proveer esquema, conexiones y controles transversales antes de cualquier historia.

- [ ] T005 Implementar configuración en app/config.py con origen HTTPS exacto, secretos externos, TLS PostgreSQL verify-full con CA/host, presupuesto total 8 s, statement_timeout 3 s, lock_timeout 1 s y pool máximo inicial 2 conexiones por rol/proceso con un proceso inicial; configuración inválida deniega administración sin divulgar valores.
- [ ] T006 Crear con CLI descubierta mediante --help las migraciones de seguridad en supabase/migrations/; definir private.admin_authorizations con «user_id PK/FK Auth, enabled, authorization_epoch entero, updated_at» y «Cada retirada de permiso incrementa epoch para no revivir sesiones antiguas al reactivar»; private.admin_sessions con todos los campos de data-model.md, «user_id FK nullable solo en preautenticación», «state preauth/active», opaque_hash único y marcas temporales UTC; private.login_limits con «identity_hmac PK, failure_times (máximo cinco), blocked_until, attempt_id, lease_until, updated_at». Usar UUID/timestamptz y los índices de sesión/identidad especificados; no inventar nombres timestamp de migraciones.
- [ ] T007 Crear mediante CLI migración editorial en supabase/migrations/ con editorial_items («kind profile/skill/academic», «published_revision_id nullable», lock_version entero y perfil singleton), editorial_revisions («payload JSON tipado», «Inmutables; UNIQUE(item_id, revision_number)»), publication_events («operation_id único», «action publish/withdraw»), operation_receipts («operation_id PK») y security_events («actor_id nullable, identity_hmac nullable», «item_id/revision_id nullable»); incluir todos los campos de data-model.md, FKs/índices, punteros a revisión del mismo elemento y prohibir UPDATE/DELETE de revisiones al runtime. Registrar ruta real creada en specs/002-administracion/implementation-notes.md.
- [ ] T008 Definir en migraciones de supabase/migrations/ roles backend_auth/backend_editor no propietarios, sin BYPASSRLS, superusuario ni membresías elevadas; aplicar matriz de grants por tabla/columna y RLS privada/pública de contracts/security-and-transactions.md, USING/WITH CHECK y SELECT requerido para UPDATE, sin SECURITY DEFINER ni vistas privilegiadas. anon/authenticated incluso con JWT admin solo leen publicaciones de 001, sin acceso privado ni escritura; runtime solo lee autorización y no puede ALTER/GRANT/cambiarla. Documentar aprovisionamiento externo del operador y signup deshabilitado en specs/002-administracion/quickstart.md.
- [ ] T009 Implementar app/admin/repository.py con SQL parametrizado, allowlists de identificadores, pools separados y contexto SET LOCAL establecido solo por backend verificado; rollback/limpieza al devolver conexión, locks autorización→sesión→elemento y reloj DB; sin HTTP/render bajo lock, sin N+1 ni reintentos de mutaciones.
- [ ] T010 [P] Implementar app/security/audit.py y tabla security_events de T007 como append-only con tipo/resultado/fecha/identidad disponible/correlación; respetar «Sin password, correo crudo, IP cruda, cookies, tokens, contenido editorial ni mensajes privados.»; evento transaccional para cambios, sink estructurado seguro para fallos/denegaciones si DB cae y denegación si no se registra acceso aceptado; filtrar logs SDK/HTTP/errores y debug.
- [ ] T011 [P] Implementar app/security/csrf.py con Flask-WTF y origen exacto configurado para todos los POST incluidos login/logout; rechazo CSRF 400, origen ajeno 403 y petición >64 KiB; no confiar en proxy arbitrario. Registrar blueprint en app/__init__.py con no-store, Referrer-Policy same-origin, nosniff y CSP sin inline ni framing para toda respuesta /admin, incluidos errores; sin secretos/payload en URL ni redirects externos.

**Checkpoint**: Esquema/matriz mínima y repositorio listos. T011 se conecta a SessionInterface de US1 antes de usar formularios; ningún POST puede habilitarse sin ambos.

## Phase 3: US1 — Acceder y cerrar sesión (P1)

**Objetivo**: Acceso privado del administrador aprobado y cierre/caducidad efectivos.
**Prueba independiente**: Con panel mínimo e identidades aisladas, entrar, consultar, cerrar y rechazar replay; probar límites con reloj controlado sin edición.

### Pruebas primero

- [ ] T012 [P] [US1] Crear tests/unit/admin/test_login_limits.py para email trim/casefold y HMAC, cinco fallos consecutivos en ventana 15 min, bloqueo quinto+15 min, bordes exactos, éxito que reinicia y cuentas inexistentes; carreras con lease 10 s, Auth <=8 s, intento tardío y error proveedor/DB que no cuenta como contraseña incorrecta.
- [ ] T013 [P] [US1] Crear tests/unit/admin/test_sessions.py para preauth 10 min, rotación login/nonce, cifrado/rotación/pérdida de clave, cookies sin tokens, inactividad 30–300 min y absoluto 24 h, expiración antes de refresh, epoch/revocación, refresh con lease y last_seen solo en interacción explícita; ninguna reautenticación repite acciones.
- [ ] T014 [P] [US1] Crear tests/contract/admin/test_auth_http.py para GET/POST login, GET /admin/, POST extend/logout: 303, 401 genérico para credenciales/cuenta no aprobada, 429 con Retry-After y 503 fail-closed; verificar atributos cookie/headers, CSRF preauth, logout con fallos DB/Auth y mensaje de POST caducado exacto de admin-http.md sin conservar password/payload.
- [ ] T015 [P] [US1] Crear tests/integration/admin/test_auth_lifecycle.py para limitador/sesiones compartidos entre procesos, login concurrente, refresh serializado, epoch, revocación/logout en carreras y replay local/Data API; usar roles reales y clocks controlados, verificar DB y persistencia de auditoría antes de emitir sesión.

### Implementación

- [ ] T016 [US1] Implementar SessionInterface de Flask en app/security/sessions.py sobre admin_sessions: «Cookie aleatoria >=256 bits; solo hash persistido», preauth 10 min sin permisos, nonce CSRF, tokens Fernet con clave externa rotatable y sin tokens en cookie; identidad obligatoria en active, inactividad predeterminada 30 ajustable 30–300 y absoluto 24 h, eliminación segura e invalidación ante pérdida de clave. Cookie Secure/HttpOnly/SameSite=Lax, sin Domain, Path=/admin.
- [ ] T017 [US1] Implementar app/security/rate_limit.py con reserva atómica por identity_hmac para todo correo normalizado, sin correo crudo; reloj DB, attempt_id y lease 10 s, máximo cinco timestamps de últimos 15 min, quinto bloquea 15 min, éxito limpia, error externo libera si posible y no suma fallo; respuesta tardía no crea sesión y ningún lock permanece durante Auth.
- [ ] T018 [US1] Implementar app/admin/auth.py con cliente Supabase Auth aislado por petición/sesión y separado del público, contraseña solo en llamada, get_user vigente, refresh serializado y autorización actual por UUID/epoch; comprobar vigencia local antes de proveedor y de lectura/mutación DB. Persistir nueva sesión/auditoría antes de entregar cookie; revocar localmente antes de confirmar logout y luego intentar signout, sin depender de signout para bloquear replay.
- [ ] T019 [US1] Implementar rutas login, panel mínimo, session/extend y logout en app/admin/routes.py, formularios en app/admin/forms.py y app/templates/admin/login.html, app/templates/admin/index.html, app/templates/admin/error.html; ajuste etiquetado 30–300 min antes de login, plazo absoluto explicado, autocomplete correcto, redirects relativos /admin y estados exactos del contrato, nunca signup ni JWT/roles aceptados como autoridad.
- [ ] T020 [US1] Ejecutar suites T012–T015 y registrar evidencia sanitizada en specs/002-administracion/validation.md: sesiones revocadas no reviven tras reactivar permiso, error proveedor deniega y cierre sin commit DB no afirma éxito; marcar integración omitida como aceptación incompleta.

**Checkpoint**: US1 demostrable sin edición. US3 endurece y acredita la frontera completa antes de exponer contenido editorial.

## Phase 4: US3 — Rechazar accesos no autorizados (P1)

**Objetivo**: Impedir lecturas privadas/escrituras por panel, solicitudes directas y Data API, con auditoría sanitizada.
**Prueba independiente**: Matriz visitante/no autorizado/admin/revocado contra recursos sintéticos privados y publicaciones; ninguna elevación por datos cliente.

### Pruebas primero

- [ ] T021 [P] [US3] Crear tests/contract/admin/test_security_boundary.py para guard en cada ruta/lectura/modificación, claims/user_metadata/UUID/rol forjados, signup inexistente, POST tras revocación/caducidad, CSRF/origen, GET sin mutación, UUID/kind inválidos y errores sin fuga; registrar rutas editoriales aún pendientes como contratos que deben pasar tras US2, sin deshabilitar guard.
- [ ] T022 [P] [US3] Crear tests/integration/admin/test_permissions.py con roles reales anon/authenticated/JWT admin y backend_auth/backend_editor: select=*, UUID, joins, esquema privado, mutaciones, contexto ausente/viejo y reutilización de pool; verificar estado DB, grants de columnas y ausencia de elevación. Usar fixtures representativas para mensajes/archivos futuros, sin afirmar validadas políticas de features inexistentes.
- [ ] T023 [P] [US3] Crear tests/unit/admin/test_audit_redaction.py para eventos de acceso aceptado/rechazado/limitado, lecturas aceptadas/denegadas, logout, expiración/revocación, guardado/conflicto/publicación/retirada; centinelas secretos en HTML, cookies, URLs, errores y ambos sinks; fallo auditoría revierte mutación o deniega acceso aceptado.

### Implementación

- [ ] T024 [US3] Integrar guard obligatorio en app/admin/auth.py y app/admin/repository.py: proveedor fuera de locks y revalidación de autorización/sesión con reloj DB en transacción antes de datos; serializar revocación con orden de locks, 303 GET sin sesión, 401 POST caducado, 403 sin permiso, 503 sin verificación, 404 solo tras guard; nunca confiar en autoridad del cliente ni metadata.
- [ ] T025 [US3] Revisar y corregir políticas/grants en supabase/migrations/ tras ejecutar matriz T022 y advisors disponibles descubiertos por CLI --help/MCP; registrar roles, grants, frontera backend de credenciales y compatibilidad con 001 en specs/002-administracion/security-review.md, sin exponer secretos ni añadir permisos genéricos sobre recursos futuros.
- [ ] T026 [US3] Integrar eventos de seguridad y redacción de app/security/audit.py en app/admin/auth.py y app/admin/routes.py; verificar headers/cookies/CSRF/origen y no exposición en configuración/errores. Ejecutar T021–T023 para rutas existentes y documentar en specs/002-administracion/validation.md que contratos de rutas US2 se cierran al implementarlas, sin declarar esta cobertura completa prematuramente.

**Checkpoint**: Frontera verificada para acceso mínimo; US2 debe reutilizarla y cerrar la matriz de todas sus rutas.

## Phase 5: US2 — Gestionar borradores y publicaciones (P1)

**Objetivo**: Guardar privado, aprobar una revisión exacta de un solo elemento y retirar publicación conservando todas las revisiones.
**Prueba independiente**: Con sesión/consumidores controlados, guardar A sin cambio público, publicar solo A, retirar con borrador B y comprobar preservación de ambas versiones y demás elementos.

### Pruebas primero

- [ ] T027 [P] [US2] Crear tests/unit/admin/test_editorial_validation.py para payloads tipados, límites y normalización segura, borrador incompleto permitido, publicación obligatoria por tipo, marcadores/porcentajes rechazados, fechas coherentes y contactos expresamente autorizados; aprobación humana ligada a revisión exacta, sin inferir veracidad.
- [ ] T028 [P] [US2] Crear tests/contract/admin/test_editorial_http.py para new/create/edit/draft/review/publish/withdraw/operations de admin-http.md, casos 422/409/404/401/403/503, confirmación ausente/ajena/vencida, revisión A tras guardar B, sesión vencida sin replay y ninguna retirada de perfil/eliminación; preview escapada y éxito solo tras commit.
- [ ] T029 [P] [US2] Crear tests/integration/admin/test_editorial_transactions.py con commits reales para borrador inmutable, publicación individual, dos editores, doble POST, operation_id repetido idéntico/distinto, rollback inyectado en cada paso, auditoría fallida y commit incierto resuelto por recibo del actor autorizado; verificar otras filas/punteros antes/después y ausencia de mutaciones después de revocación confirmada.
- [ ] T030 [P] [US2] Crear tests/integration/admin/test_publication_consumers.py para consumidores sitio 001/CV controlado: guardar no altera público, publicar whitelist e id estable, retirar último skill/academic oculta sección/ancla, conserva borrador distinto y revisión retirada, no afecta otros elementos; republicar exige revisión nueva y no implementar PDF.

### Implementación

- [ ] T031 [US2] Implementar validación y formularios tipados en app/admin/forms.py: «Perfil: full_name, degree, summary, public_contacts», «Publicar requiere nombre, carrera y resumen aprobados»; «Conocimiento: name, description opcional, display_order» y «Nombre verificado requerido, sin porcentajes arbitrarios»; «Experiencia académica: activity, description, institution opcional, start_date/end_date opcionales, ongoing y display_order» y «Publicar exige título y descripción aprobados». Aplicar «textos cortos 200, resumen 2000, descripción 4000, contactos hasta 10 y valores 2048», «tamaño de petición máximo 64 KiB» y «Borrador incompleto admite null/texto vacío normalizado, pero nunca estructura insegura, URL ejecutable o tamaño excesivo.».
- [ ] T032 [US2] Completar app/admin/forms.py con reglas literales de 001: «Texto plano con trim; rechazar cadenas vacías y marcadores pendientes al publicar», contactos «kind email/https/phone, etiqueta comprensible requerida», «No aceptar HTML, javascript ni data. Ausencia = array vacío.» y «end_date >= start_date si ambas existen; ongoing prohíbe end_date»; «Si solo se conoce año o mes, conservar null hasta ampliar explícitamente el modelo». Rechazar marcadores conocidos y porcentajes de dominio sin inventar contenido ni máximo para campos no acotados explícitamente.
- [ ] T033 [US2] Implementar creación/guardado y lectura de revisiones en app/admin/repository.py y app/admin/service.py: comparar expected_version, insertar revisión inmutable, actualizar solo draft_revision_id/lock_version y recibo/auditoría en una transacción, punteros del mismo item y perfil singleton; hijos sin perfil publicado pueden ser borradores. Reabrir último borrador y conservar publicación intacta; no sobrescribir automáticamente ante 409.
- [ ] T034 [US2] Implementar revisión/publicación en app/admin/service.py y app/admin/repository.py: token ligado a sesión/item/revision_id/digest/lock_version con vida 10 min, borrador actual, confirmed=true y autorización humana/contactos explícitos; copiar solo whitelist a una instantánea de 001, published_revision_id/version, publication_events/recibo/auditoría atómicos; hijos solo con perfil publicado. Datos históricos de 001 sin resumen siguen legibles, nuevas publicaciones no.
- [ ] T035 [US2] Implementar retirada en app/admin/service.py y app/admin/repository.py solo skill/academic publicado, confirmación ligada a published_revision_id/version, eliminar instantánea y anular puntero publicado con evento/recibo/auditoría atómicos; conservar draft_revision_id y todas las revisiones, incluida retirada aunque borrador difiera; prohibir perfil y exigir nueva confirmación para republicar.
- [ ] T036 [US2] Implementar idempotencia y resolución de resultado en app/admin/repository.py y app/admin/service.py: operation_id único de creación/guardado/publicación/retirada, mismo actor/acción/digest devuelve recibo sin repetir, distinto cuerpo 409; recibo solo visible al actor con sesión autorizada. Commit incierto muestra mensaje contractual y consulta de estado, ausencia comprobada solo permite nueva acción explícita; ningún retry silencioso ni falso éxito/fracaso.
- [ ] T037 [US2] Implementar rutas editoriales/operations de contracts/admin-http.md en app/admin/routes.py con guard, UUID/kind allowlist, PRG 303 tras commit y códigos/mensajes contractuales; ampliar app/templates/admin/index.html y crear app/templates/admin/edit.html, app/templates/admin/review.html y app/templates/admin/withdraw.html con estados textuales, revisión exacta y confirmación explícita en páginas completas; jamás autosave/replay, safe o recuperación privada en URL/cookie/localStorage.
- [ ] T038 [US2] Ejecutar T027–T030 y matriz completa tests/contract/admin/test_security_boundary.py para todas las rutas implementadas; corregir fallos y completar specs/002-administracion/validation.md con evidencia transaccional y de consumidores, cerrando cobertura diferida de US3 sin declarar integración omitida como aprobada.

**Checkpoint**: Ciclo editorial íntegro, sin publicaciones por lotes ni pérdida de borradores; aceptación final requiere US4 y seguridad real completa.

## Phase 6: US4 — Administrar con accesibilidad (P1)

**Objetivo**: Completar acceso, edición, errores, revisión, publicación, retirada y cierre con teclado/tecnologías de asistencia.
**Prueba independiente**: Recorrer cada flujo con contenido preparado, teclado/NVDA, texto 200 %, 320 px, movimiento reducido y sin JS; Victor completa acceso→edición→borrador→revisión→publicación→cierre sin ayuda en <=5 minutos.

### Pruebas primero

- [ ] T039 [P] [US4] Crear tests/contract/admin/test_accessibility.py para lang/título/h1/regiones/skip link, labels/autocomplete, nombres de acciones, errores 422 con resumen enlazado/aria-invalid/aria-describedby y estados de conflicto/caducidad/fallo; mensajes iniciales comprensibles sin depender de aria-live, sin password reenviado ni controles falsos.
- [ ] T040 [P] [US4] Preparar specs/002-administracion/accessibility.md con matriz de todos los criterios WCAG 2.1 A/AA aplicables por flujo/estado, evidencia y justificación de no aplicables; incluir medición SC-005, ajuste de inactividad previo al login y pruebas automáticas gratuitas/manuales, sin marcar pendientes como PASS.

### Implementación y verificación

- [ ] T041 [US4] Ajustar app/templates/admin/login.html, app/templates/admin/index.html, app/templates/admin/edit.html, app/templates/admin/review.html, app/templates/admin/withdraw.html y app/templates/admin/error.html con jerarquía/regiones/skip link, etiquetas persistentes, requisitos, resumen de errores enlazado, confirmaciones textuales y navegación consistente; mantener foco lógico y flujos completos sin JS ni modales obligatorios, sin indicar estado solo por color.
- [ ] T042 [US4] Ampliar app/static/css/site.css sin romper 001: foco visible, texto normal 4.5:1/grande 3:1/no textual necesario 3:1, wrapping, orientación y espaciado flexible sin recortes a texto 200 %/320 px; respetar movimiento reducido. Ofrecer 30–300 min antes de login y explicar 24 h; si se añade aviso opcional usar POST extend protegido, sin depender de JS para ajuste de tiempo.
- [ ] T043 [US4] Ejecutar T039, axe gratuito y revisión manual teclado/NVDA, errores/corrección/conflicto/timeout, contraste, móvil/escritorio, orientaciones, espaciado, 200 %, 320 px y sin JS; completar specs/002-administracion/accessibility.md y corregir defectos. Registrar SC-005 con Victor, duración y obstáculos reales; si su participación no está disponible, dejar esa aceptación pendiente sin inventar medición.

**Checkpoint**: Cuatro historias P1 completas solo con evidencia funcional, seguridad real y revisión manual; ninguna puntuación automática sustituye WCAG.

## Phase 7: Polish — operación, regresión y aceptación

- [ ] T044 [P] Documentar en specs/002-administracion/operations.md mantenimiento acotado por operador: «eliminar tokens de sesiones revocadas/caducadas tras intentar signout», «limpiar filas de sesión a las 24 h y login_limits sin bloqueo/lease activo tras 24 h», «Auditoría 90 días»; revisiones sin eliminación automática, monitorización de volumen y denegación útil antes de agotar cuota. Incluir rotación protegida de claves, invalidez de sesiones ante rotación incompatible y ningún fallback en texto claro.
- [ ] T045 Actualizar specs/002-administracion/quickstart.md con comandos PowerShell realmente comprobados, HTTPS local/cookie Secure, roles y fixtures aislados, TEST_*, migraciones/advisors descubiertos por --help y limpieza verificada contra identificador de proyecto de prueba; no desactivar Secure/CSRF ni publicar datos reales.
- [ ] T046 Ejecutar tests/unit/admin, tests/contract/admin y tests/integration/admin -m security más regresión pública de 001; consolidar specs/002-administracion/validation.md y specs/002-administracion/security-review.md con commit, versiones/licencias, grants/RLS, pools/TLS, límites/timeout/carreras, rollback/recibos, cero secretos y trazabilidad FR-001–015/SC-001–009; skips o defectos obligatorios abiertos bloquean aceptación.
- [ ] T047 Revisar evidencia final de specs/002-administracion/accessibility.md, specs/002-administracion/validation.md y specs/002-administracion/security-review.md con matriz completa y medición de Victor; registrar revisión específica de autenticación/RLS/secretos/compatibilidad de datos conforme a constitución y aprobación separada de contenido/identidad reales antes de activación, sin desplegar como parte de estas tareas.

## Dependencies & Execution Order

```text
Base 001 disponible → Setup T001–T004 → Fundamentos T005–T011
  → US1 T012–T020 → US3 T021–T026
    → US2 T027–T038 → cierre de matriz de rutas US3
      → US4 T039–T043 → Polish T044–T047
```

T001 decide prerrequisitos existentes y no autoriza rehacerlos. T002 precede T003/T004. Fundamentos: T005→T006→T007→T008→T009; T010/T011 pueden avanzar simultáneamente tras T009 en archivos distintos. No servir formularios hasta enlazar T011 y T016.

En cada historia escribir pruebas primero; ejecutarlas contra contratos faltantes y después implementar secuencialmente. T016→T017→T018→T019→T020; US3 depende de sesión/roles de US1, T024→T025→T026. Suites US3 de rutas futuras se cierran obligatoriamente en T038; no considerar que US3 depende de edición para demostrar su frontera mínima. US2 prueba con sesión/consumidores controlados; T031→T032→T033→T034→T035→T036→T037→T038. US4 verifica componentes aislados con fixtures, pero su recorrido completo espera US2. T041→T042→T043; cierre espera las cuatro historias.

La independencia de prueba se obtiene mediante fixtures y consumidores controlados, no duplicando implementación de autorización/publicación. app/admin/routes.py, forms.py, service.py y repository.py se editan secuencialmente entre tareas; no ejecutar historias simultáneamente sobre esos archivos.

## Parallel Examples

- Setup: T003 (.env.example/.gitignore) junto a T004 (tests/conftest.py) después de T002.
- Fundamentos: T010 (audit.py) y T011 (csrf.py/factory) tras T009, acordando interfaz de auditoría sin modificar el mismo archivo.
- US1: T012, T013, T014 y T015 escriben suites distintas con interfaces/reloj de T004; integración espera esquema y aplicación.
- US3: T021 (contratos), T022 (permisos reales) y T023 (redacción) pueden prepararse juntos tras US1; cambios del guard/políticas son secuenciales.
- US2: T027, T028, T029 y T030 preparan suites distintas tras US3; no lanzar transacciones que alteren el mismo fixture simultáneamente, usar aislamiento por caso/worker.
- US4: T039 (contrato HTML) y T040 (matriz manual) tras US2, antes de ajustes visuales.
- Polish: T044 puede redactarse independientemente tras historias; T045–T047 consolidan evidencia secuencialmente sin competir por documentos compartidos.

## Implementation Strategy

1. Reutilizar 001 y completar fundamentos con entorno aislado gratuito; ninguna cuenta o secreto real dentro del repositorio.
2. MVP de acceso: US1 y controles US3 para panel mínimo, con pruebas reales y accesibilidad básica ya presente. Es demostración parcial, no aceptación de la feature.
3. Incremento editorial US2: borrador → revisión → publicación individual → retirada → republicación, con pruebas de carreras/rollback/recibos y consumidores controlados; preservar fuente pública de 001.
4. Completar US4 y revisión de accesibilidad de cada incremento. Las cuatro historias son P1: MVP aceptable de 002 requiere todas, no solo login.
5. Cerrar evidencia real de seguridad, SC-005 con Victor y revisión de permisos. Sin entorno real o participante disponible, registrar bloqueo de aceptación específico, sin sustituirlo por mocks o mediciones inventadas.

## Trazabilidad y límites

US1: FR-001/007/008/009, SC-002/008. US3: FR-002/006/009/010/011, SC-001/002/007. US2: FR-003/004/005/012/013/015, SC-003/006/009. US4: FR-014, SC-004/005. T046/T047 consolidan todos los requisitos y criterios.

Las reglas/enum/nullabilidad citados en tareas derivan literalmente de data-model.md y 001; los restantes campos completos se enumeran en esas tablas y las tareas de migración los incorporan explícitamente. No añadir experiencia profesional, afirmar capacidades verificadas por sintaxis, generar el CV ni habilitar recursos futuros para demostrar permisos.
