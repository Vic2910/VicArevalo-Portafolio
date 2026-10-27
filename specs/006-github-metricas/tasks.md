# Tasks: Sincronización GitHub y dashboard administrativo

**Input**: plan.md, spec.md, data-model.md, research.md, contracts/dashboard-http.md, contracts/github-sync.md y quickstart.md de `specs/006-github-metricas/`; constitución 1.0.0 y diseños 002–004.
**Organización**: Setup → fundamentos → US1 (P1) → US2 (P1) → US3 (P2) → cierre. Las advertencias de integridad de US3 son obligatorias desde P1, no una mejora opcional.
**Pruebas**: Pytest solicitado por spec/diseño/constitución, HTTPX MockTransport y reloj controlado; DB/roles reales aislados para permisos y carreras. Escribir suites primero y comprobar fallos pertinentes; mocks/skips no acreditan RLS. No sincronizar la cuenta real durante planificación ni pruebas predeterminadas.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas desde raíz; [P] solo después de prerrequisitos y en archivos distintos. Cuenta objetivo canónica `Vic2910` según spec.md; las apariciones `Vic 2910` en diseño son espaciado tipográfico, nunca login con espacios en requests.
**Alcance**: Mismo monolito/PostgreSQL, worker de solicitudes manuales sin broker/cron/SaaS. Sin privados, importación editorial, CV, IA o activación de contacto 004 RET-001.

## Phase 1: Setup — base compartida

- [ ] T001 Inspeccionar código disponible y registrar en specs/006-github-metricas/implementation-notes.md factory/configuración, guard/sesiones/CSRF/auditoría/pools/recibos 002 y fuentes locales de proyectos 003/mensajes 004; completar prerrequisitos de seguridad faltantes antes de integración, sin asumir que documentos son implementación. Adaptador de mensajes ausente devuelve not_configured, sin forzar habilitación de 004 ni dependencia de 005.
- [ ] T002 Consolidar HTTPX estable compatible con Python 3.12 y stack 002 en pyproject.toml y requirements.lock sin duplicar cliente transitivo; verificar documentación primaria/API version vigente, licencias exactas/transitivas y gratuidad en specs/006-github-metricas/dependencies.md. Revalidar el header inicial propuesto 2026-03-10 al implementar, sin usar valores obsoletos por inferencia.
- [ ] T003 [P] Añadir METRICS_DATABASE_URL, GITHUB_SYNC_DATABASE_URL y GITHUB_READ_TOKEN opcional vacíos en .env.example, secretos excluidos en .gitignore; configurar app/config.py con TLS verificado, cuenta Vic2910 fija, API version/contexto no secreto y presupuestos de diseño, nunca endpoints/login/token aportados por formulario ni token real en fixtures.
- [ ] T004 [P] Preparar tests/fixtures/github/ y tests/conftest.py con cuenta ID100/ajena200, source R1/fork R2, SHA propia compartida entre repos, own/other/unknown/committer objetivo/fecha futura, catálogo/commits multipágina y 304/cuotas/errores/reescrituras; oráculo explícito repo/SHA independiente del algoritmo, transporte sin red por defecto, reloj controlado y configuración TEST_* aislada con marca security.

## Phase 2: Foundational — persistencia y permisos bloqueantes

- [ ] T005 Crear mediante CLI descubierta con --help migraciones en supabase/migrations/ para todos los campos de github_identity, github_repositories y github_commits del modelo: ID numérico estable, requested_login Vic2910, atributos públicos mínimos, «PK(repo_id,sha)», authored_at/content_fingerprint y SHA hexadecimal validada. Sin email/nombre/mensaje/parche/avatar ni raw payload. Registrar rutas reales CLI en specs/006-github-metricas/implementation-notes.md, sin inventar timestamps.
- [ ] T006 Crear mediante CLI migraciones en supabase/migrations/ para github_runs con todos los campos del modelo y «account_id nullable hasta verificación», «last_success_at nullable», «result_count nullable», run_version/política/corte fijos; github_run_repositories con «PK(run_id,repo_id)», «pinned_head_sha nullable» y contexto/cursor propio; github_run_commits con «PK(run_id,repo_id,sha)», observed_author_id/login nullable, «attribution own/other/unknown» y eligible_date. FKs e índices run/repo/atribución; count null distinto de cero confirmado.
- [ ] T007 Crear mediante CLI migraciones de supabase/migrations/ para github_attempts con request_operation_id único, sesión/epoch iniciadores, started_at nullable y campos completos del modelo; github_sync_control singleton con active_attempt_id nullable, fence/lease/heartbeat/cooldown/proveedor/backoff; github_complete_results por scope_definition_hash con previous_complete_run_id nullable; github_operations con «action start/resume» y operation_id PK. No tokens/cookies en jobs y stage separado de punteros completos.
- [ ] T008 Crear mediante CLI migración de github_page_cache en supabase/migrations/ con todos los campos de modelo, clave canónica endpoint/parámetros/page/per_page/sha/API version/contexto no secreto, representación mínima validada/Link/validadores/byte_size. Aplicar RLS privada y grants mínimos: backend_metrics_read bajo guard solo 006 y columnas mínimas proyectos/mensajes, backend_github_sync escribe solo 006/auditoría y bookkeeping acotado; anon/authenticated/JWT admin sin métricas/control/cache/mutaciones. Sin propiedad/BYPASSRLS/service_role/SECURITY DEFINER y sin ampliar escritura a 003/004/005.
- [ ] T009 Implementar bases de app/metrics/repository.py y app/github_sync/repository.py con SQL parametrizado, TLS/contexto local limpio y reloj DB; lectura independiente por familia/mismo snapshot dentro de cada una, recibos/locks/control para intentos, sin HTTP/sleep bajo transacción. Registrar blueprints en app/__init__.py reutilizando guard/cabeceras no-store/CSRF/origen de 002.

**Checkpoint**: Datos parciales/último completo separados por esquema; GET solo tiene dependencias locales. Pruebas pueden usar resultados persistidos sintéticos sin worker todavía.

## Phase 3: US1 — Consultar métricas locales (P1)

**Objetivo**: Dashboard privado útil sin GitHub, con estados independientes y cero solo cuando está comprobado.
**Prueba independiente**: Proyectos/mensajes/runs sintéticos, GitHub desconectado y veinte GET; cantidades correctas, cero requests externos y fallo de tarjeta sin afectar otras.

### Pruebas primero

- [ ] T010 [P] [US1] Crear tests/unit/metrics/test_local_metrics.py para published con borrador contado una vez, draft nunca publicado, retired separado y deleted fuera; mensajes id/state/expires_at vivos sin leer textos ni stored_count, fuentes ausentes/fallidas no son cero y RET-001 separado. Commits sin completo, completo cero, completo viejo y parcial diferenciados con as_of por familia.
- [ ] T011 [P] [US1] Crear tests/contract/metrics/test_dashboard_http.py para guard en dashboard/detalle/recibos, sin sesión/permiso/verificación y no-store; ejecutar 20 GET con transporte que falla si GitHub se invoca, sin enqueue ni cambio de fuente/cooldown, incluyendo refresh/polling local. Explicación textual de alcance/fechas/forks/dedupe y parcial sin reemplazar completo.
- [ ] T012 [P] [US1] Crear tests/integration/metrics/test_metrics_permissions.py con roles reales anon/authenticated/JWT admin/backend_metrics_read y contexto ausente/viejo: cantidades privadas denegadas a no autorizados, reader solo columnas mínimas sin remitente/texto/draft completo/bytes/tokens; mismos snapshots por familia y fallo independiente. Verificar DB tras intentos, security skip explícito sin entorno.

### Implementación

- [ ] T013 [US1] Implementar métricas locales en app/metrics/repository.py y app/metrics/service.py con MetricResult(value|null,state ready/empty/unavailable/not_configured,as_of,explanation), categorías de proyectos del modelo y mensajes vivos con misma referencia temporal de familia. Fuente ausente/fallo no devuelve 0, conteo correcto vacío sí puede ser 0 con recepción bloqueada explicada; nunca cachear cantidades tras eliminación/vencimiento ni copiar mensajes.
- [ ] T014 [US1] Implementar GET /admin/metricas, detalle local run y operaciones propias en app/metrics/routes.py y app/templates/metrics/dashboard.html, app/templates/metrics/sync_detail.html; guard actual, sin cliente GitHub/encolar/renovar intentos desde GET. Mostrar completo/parcial separados con alcance/corte/fecha/antigüedad y «Sin resultado completo confirmado» si procede, sin sumarlos ni afirmar historial global/experiencia profesional.
- [ ] T015 [US1] Aplicar HTML español semántico/h1/skip link/labels/foco y estados textuales sin hover/color obligatorio en plantillas de app/templates/metrics/ y app/static/css/site.css, 200 %/320 px/contraste/espaciado/orientación/movimiento reducido/sin JS; ejecutar T010–T012 y registrar specs/006-github-metricas/validation.md y specs/006-github-metricas/accessibility.md con advertencia SHA repetida entre repos/forks y completitud «para este alcance».

**Checkpoint**: MVP lectura local con fixtures, sin sincronización; advertencias esenciales presentes desde este incremento.

## Phase 4: US2 — Sincronizar repositorios y commits (P1)

**Objetivo**: Solicitud manual autorizada duradera y recorrido correcto del alcance público sin duplicaciones ni publicación editorial.
**Prueba independiente**: MockTransport multipágina y autores distintos, iniciar/consumir solicitud, guardar resultado y repetir tras 60 min simulados; count idéntico por parejas y cero escritura editorial.

### Pruebas primero

- [ ] T016 [P] [US2] Crear tests/unit/metrics/test_github_client.py para host/endpoints/headers/TLS/redirects/Link seguros, owner/public/forks/rename/ACCOUNT_MISMATCH, historial por cabeza fija multipágina sin since/until/author ni corte anticipado por fechas; top-level author.id, authored_at/cutoff y dedupe repo/SHA, datos esenciales inválidos/incompatibles parcial y repo vacío comprobado frente a 404/409 genérico.
- [ ] T017 [P] [US2] Crear tests/contract/metrics/test_sync_requests.py para POST start/resume con guard/CSRF/origen/operation_id/version, 202 solo queued persistido, 409 activo/versión, 429 Retry-After y 503 worker/recursos/guard; doble envío mismo cuerpo/otro cuerpo, commit incierto y ausencia de replay tras login, sin cooldown/HTTP por solicitudes no autorizadas.
- [ ] T018 [P] [US2] Crear tests/integration/metrics/test_worker_transactions.py con DB/roles reales y MockTransport para dos POST/workers, lease90s/fence, heartbeat/pausa/reinicio/respuesta tardía, pérdida de autoridad/epoch/sesión antes HTTP/escritura/promoción, persistencia página+cursor atómica y rollback por paso; queued bloquea duplicados, commit incierto resuelto por recibo y ningún permiso de sync sobre proyectos/mensajes/CV.

### Implementación

- [ ] T019 [US2] Implementar app/github_sync/client.py HTTPX síncrono secuencial con host fijo api.github.com, GET públicos permitidos y headers API version verificada/Accept/User-Agent; anónimo por defecto y token opcional backend solo si acredita alcance público mínimo sin privados/escritura. Validar máximo3 redirects y Link HTTPS/mismo host/ruta/params/manifest sin userinfo, ciclos o endpoints arbitrarios, sin reenviar credencial fuera de origen ni guardar raw payload.
- [ ] T020 [US2] Implementar descubrimiento/atribución en app/github_sync/service.py: resolver Vic2910 por ID estable, catálogo owner per_page100 completo incluyendo forks, owner.id/private=false, rama/head fija y cutoff; commits sha fijo sin since/until/author ni parar por fecha o SHA de otro repo. «attribution own solo si author.id de cuenta GitHub de nivel superior coincide con account_id; null=unknown, otroID=other», fecha autoría<=cutoff y pareja repo/SHA. Sin nombre/email/committer/coautoría como prueba, sin importar privados ni proyectos.
- [ ] T021 [US2] Implementar start/resume duraderos en app/github_sync/repository.py y app/metrics/routes.py con operación/attempt queued/control/auditoría atómicos, expected_run_version y worker operativo verificado; mismo operation_id/actor/digest devuelve recibo sin otro inicio/cooldown, distinto409. Inicio efectivo del worker fija started_at y mínimo60min para nuevo intento incluidas continuaciones; reserva provisional también bloquea duplicados, 202 nunca éxito de sincronización.
- [ ] T022 [US2] Implementar app/github_sync/worker.py y app/github_sync/cli.py con comando Flask github-worker del mismo monolito que solo consume solicitudes autorizadas persistidas, sin scheduler ni inicio por reloj/GET. Lease90s/owner aleatorio/fence monotónico, renovar/verificar antes de HTTP y escritura, Auth/guard002 de sesión iniciadora sin copiar tokens al job; timeoutHTTP10s, secuencial, segmento<=5min/200requests o cuota menor. Perder permiso/lease detiene HTTP y promoción; viejo worker/respuesta tardía no persiste y reinicio marca interrupted sin reanudar HTTP silenciosamente.
- [ ] T023 [US2] Implementar stage/páginas/membresía y promoción en app/github_sync/repository.py y app/github_sync/service.py: página/datos mínimos/cursor juntos, UNIQUE run/repo/SHA y representaciones incompatibles parciales; revalidar catálogo/owner/default_branch/head al final, completar solo todo el manifiesto. Promover count/puntero/checked_at/last_success_at/control/auditoría en un commit con guard/fence; rollback conserva último válido/fecha, desconexión se consulta antes de afirmar éxito. Nuevo run reconstruye membresía alcanzable tras force-push, nunca acumulado histórico como actual.
- [ ] T024 [US2] Integrar start/continuar y consultas propias en app/templates/metrics/dashboard.html y app/templates/metrics/sync_detail.html con estados queued/running/partial/interrupted/complete, espera/motivo sin botón falso y refreshGET local sin JS; ejecutar T016–T018 y regresión US1. Registrar specs/006-github-metricas/validation.md con oráculo explícito y cero escritura editorial/privada fuera de 006; detener trabajo por límite como parcial, nunca total truncado.

**Checkpoint**: Sincronización P1 demostrable con respuestas controladas. US3 completa endurecimiento de caché/cuotas/continuaciones y aceptación de todos los fallos; P1 no se activa ignorando restricciones del proveedor.

## Phase 5: US3 — Interpretar límites, alcance y antigüedad (P2)

**Objetivo**: Reutilizar representaciones válidas, respetar esperas y recuperar progreso sin mezclar ni esconder resultados incompletos.
**Prueba independiente**: Tras completo controlado, interrumpir página/cuota/DB, conservar resultado, mostrar parcial con contexto propio y continuar explícitamente cuando permitido; 304 no implica completo por sí mismo.

### Pruebas primero

- [ ] T025 [P] [US3] Crear tests/unit/metrics/test_cache_and_limits.py para 200/304 por cada página, Link validado, caché miss/incompleta/contexto cambiado, head estable con autoría nueva; Retry-After segundos/fecha, remaining0/reset, secundario sin instrucciones>=60s/exponencial/3 consecutivos suspensión24h, 401/403 permisos sin retry como cuota y max de todas las esperas. Reloj controlado, sin sleeps largos.
- [ ] T026 [P] [US3] Crear tests/integration/metrics/test_resume_and_history.py para segmento agotado/lease interrumpida, intento manual siguiente>=60min y proveedor, mismo corte/heads solo si compatibles, cambio catálogo/owner/head/default_branch parcial sin fusión; completo anterior/parcial inicial y 304 sin cambios, rollback/recursos sin adelantar fecha ni borrar válido. Validar preservación por limpieza y no duplicaciones al reanudar.
- [ ] T027 [P] [US3] Crear tests/contract/metrics/test_scope_states.py para perfil/repo inaccesible vs vacío probado, error independiente, alcance/período/cutoff/cabezas/ventana/atribución/forks/dedupe/exclusiones/fechas propios de completo y parcial; esperas con fecha/zona, cero GET externo/polling sin prolongar sesión y ausencia de raw JSON/secreto/email/texto de commit en HTML/logs/errores.

### Implementación y verificación

- [ ] T028 [US3] Implementar caché condicional normalizada en app/github_sync/client.py y app/github_sync/repository.py con clave de endpoint/parámetros/página/sha/APIversion/contexto no secreto, ETag/Last-Modified y Link; 200 validado actualiza caché/stage/cursor atómicos, 304 solo reutiliza representación completa compatible de esa página. Miss obliga GET no condicional dentro de presupuesto o parcial; head estable no omite páginas/autoría y caché jamás almacena token/Authorization/raw payload.
- [ ] T029 [US3] Implementar cuotas/backoff persistidos en app/github_sync/client.py y app/github_sync/service.py: headers de respuestas sin /rate_limit por página, espera más conservadora Retry-After/reset/instrucciones, secundario sin espera mínimo60s con crecimiento exponencial y suspensión24h tras3 consecutivos propuesta; 401/403 permisos detienen por configuración. next_allowed_at=max(started_at+60min,provider_blocked_until,backoff_until); persistir y salir sin largas esperas, eludir cuotas ni HTTP desde GET.
- [ ] T030 [US3] Completar segmentación/reanudación en app/github_sync/worker.py y app/github_sync/service.py manteniendo cutoff/manifiesto originales y ventana explícita; revalidar compatibilidad antes de seguir, parcial/incompatible exige nuevo run explícito. Reservar presupuesto para validación final, detener HTTP si DB no persiste progreso y conservar último completo separado de parcial; nuevas verificaciones completas sin cambios avanzan fecha solo tras commit, no por 304 aislado.
- [ ] T031 [US3] Implementar limpieza/recursos en app/github_sync/repository.py y documentar specs/006-github-metricas/operations.md: «dos resultados completos más reciente parcial, historial de attempts 30 días», preservar punteros/reanudables y borrar solo runs/commits/caché sin referencias; «Caché LRU<=16 MiB y presupuesto lógico 006<=64 MiB más margen físico compartido 350 MiB». Medir índices/TOAST/otros módulos, limpiar seguro o parcial/rechazo sin borrar último válido para ocultar error ni activar cargos; no cron remoto requerido.
- [ ] T032 [US3] Completar explicaciones/estados/fechas con zona visible en app/metrics/service.py y plantillas app/templates/metrics/dashboard.html, app/templates/metrics/sync_detail.html: completo para alcance observado, no snapshot global simultáneo; mismo SHA cuenta por repo incluso fork, no trabajo profesional. PerfilID cambiado ACCOUNT_MISMATCH sin fusionar y repos ausentes solo fuera del catálogo observado sin inferir privados/eliminados. Ejecutar T025–T027 y registrar specs/006-github-metricas/validation.md con completo/parcial separados.
- [ ] T033 [US3] Revisar todos los estados con axe gratuito y teclado/lector, foco/labels/status opcional sin robo de foco, 200 %/320 px/contraste/espaciado/orientación/movimiento reducido/sin JS en specs/006-github-metricas/accessibility.md; corregir app/static/css/site.css y plantillas. Medir SC-008 con Victor <1min para pendientes/última fecha válida/completitud; si falta participante registrar pendiente, sin inventar medición.

**Checkpoint**: Restricciones y recuperación acreditadas sin sustituir último resultado válido por cero o parcial silencioso.

## Phase 6: Polish — evidencia y aceptación

- [ ] T034 [P] Actualizar specs/006-github-metricas/quickstart.md con comandos PowerShell implementados, HTTPS/origen, worker local/CLI, fixtures MockTransport antes de ejecución, TEST_* y proyecto aislado verificado para limpieza; roles/migraciones/advisors descubiertos por --help, operación sin token y límites. Sin calendario, sincronización real de Vic2910 ni valores secretos en documentación.
- [ ] T035 Ejecutar tests/unit/metrics, tests/contract/metrics y tests/integration/metrics -m security más regresión 002–004 aplicable; consolidar specs/006-github-metricas/validation.md con commit/lock/licencias/APIheader, roles/grants/RLS, HTTP sanitizado/oráculos, 20GET cero egress, paginación/304/carreras/cuota/fencing/rollback/recursos y trazabilidad FR-001–012/SC-001–008. Skips de DB son aceptación incompleta y 004 permanece bloqueado.
- [ ] T036 Completar matriz de todos los criterios WCAG2.1 A/AA aplicables y justificación de no aplicables en specs/006-github-metricas/accessibility.md, revisar medición de Victor y evidencia funcional/seguridad en specs/006-github-metricas/validation.md; cerrar defectos obligatorios y revisión específica de secretos/permisos/cuotas antes de aceptar. Diferenciar algoritmo validado con fixtures de comprobación operativa real posterior, sin exigir token ni modificar datos reales para esta entrega.

## Dependencies & Execution Order

```text
Seguridad002 + adaptadores locales003/004 controlados
 → Setup T001–T004 → Fundamentos T005–T009
   → US1 T010–T015 (P1, MVP lectura local)
     → US2 T016–T024 (P1, sincronización manual)
       → US3 T025–T033 (P2, endurecimiento/interpretación)
         → Polish T034–T036 → aceptación
```

T002 precede T003/T004. Fundamentos secuenciales T005→T006→T007→T008→T009. Suites por historia se escriben primero; implementación US1 T013→T014→T015, US2 T019→T020→T021→T022→T023→T024 y US3 T028→T029→T030→T031→T032→T033. GET jamás adquiere trabajo ni cliente GitHub, tampoco para recuperar worker interrumpido.

US1 se prueba sin sincronización con resultados locales persistidos; US2 sin API real mediante MockTransport y sesión002; US3 parte de fixtures completas/parciales y clock controlado para cada transición. Adaptadores003/004 pueden usar esquemas/filas aislados; esquema ausente y RET-001 se representan con estado real, nunca cero inferido/activación. Archivos client.py/service.py/repository.py/worker.py y plantillas compartidos se editan secuencialmente entre tareas.

No abrir sincronización P1 real antes de completar protecciones US3 de cuota/caché/alcance requeridas por FR; la prioridad P2 no exime advertencias/esperas obligatorias. Capturar ramas/cabezas fijas no afirma snapshot global simultáneo.

## Parallel Examples

- Setup: T003 (config/env) y T004 (fixtures/tests) tras T002.
- US1: T010 (lógica), T011 (HTTP/no-egress) y T012 (roles reales) en archivos distintos tras fundamentos.
- US2: T016 (cliente), T017 (rutas), T018 (DB/worker) preparan suites juntas con interfaces acordadas; ejecución integrada espera aplicación y roles.
- US3: T025 (cache/cuotas), T026 (historia/DB), T027 (presentación) tras US2; fixtures aisladas por caso/worker salvo carreras deliberadas.
- Cierre: T034 documentación desde resultados existentes; T035/T036 actualizan evidencia compartida secuencialmente. No paralelizar workers reales fuera de tests deliberados de exclusión.

## Implementation Strategy

1. Reutilizar seguridad y preparar modelo privado con completo/stage/attempt separados, permisos mínimos y cliente mock por defecto en pruebas.
2. MVP técnico US1: dashboard sin red externa con estados honestos y alcance/fechas; veinte recargas sin egress.
3. US2 añade solicitud manual duradera, atribución por cuenta y paginación completa por cabeza, worker serial/lease/fence y promoción atómica sin importación editorial.
4. US3 completa caché/esperas/continuaciones/retención y comprensión, conservando el último válido ante fallos; todas las advertencias y protecciones requeridas deben estar presentes antes de activación de P1.
5. Cerrar seguridad real, accesibilidad y SC-008; demostrar algoritmo con fixtures sin consultar cuenta real ni crear token/calendario. Aceptación total requiere todas las historias y evidencia, no solo 202 de cola.

## Trazabilidad

US1: FR-002/004/005/008/009/010, SC-003/004/005/006/007. US2: FR-001/002/003/007/009/011/012, SC-001/002/004/005/006. US3: FR-005/006/007/008/010/012, SC-001/003/004/005/007/008. T035/T036 consolidan todos los FR/SC.

Las tareas de esquema incorporan todos los campos de las tablas del modelo y citan enum/nullabilidad/invariantes; nombres de migración se obtienen por CLI. No datos de mensajes/commits privados en logs; datos públicos GitHub no convierten métricas en información pública.
