# Tasks: Asistencia editorial local y revisable

**Input**: plan.md, spec.md, data-model.md, research.md, contracts/assistance-http.md, contracts/local-model-and-privacy.md y quickstart.md de `specs/007-ia-asistida/`; constitución 1.0.0 y diseños 002/003/005.
**Organización**: Setup → fundamentos → US1 (P1) → US3 (P1) → US2 (P2) → cierre. IDs conservan historias de spec.md; cancelación/independencia manual preceden traducción.
**Pruebas**: Pytest solicitado por diseño/spec/constitución, adaptador/proceso falsos y reloj controlado por defecto. DB/RLS y navegador reales para permisos/lifecycle; ensayo local real separado para hardware/calidad. Escribir suites primero y comprobar fallos pertinentes. Fakes/skips no acreditan modelo real ni navegador.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas desde raíz; [P] tras prerrequisitos y solo archivos distintos. Sin descarga/inferencia/modelo instalado en esta generación de tareas.
**Alcance**: Modelo local mismo host del backend, sin proveedor remoto/túnel, chatbot público, tools, entrenamiento, publicaciones/aprobación automáticas ni mensajes 004. RET-001 permanece intacto y métricas 006 no aportan contexto automático.

## Phase 1: Setup — base compartida

- [ ] T001 Revisar implementación disponible de 002/003/005 y registrar en specs/007-ia-asistida/implementation-notes.md factory/guard/sesión/CSRF/auditoría/pools y servicios de borrador por campo; completar prerrequisitos faltantes antes de integrar aceptación. No asumir documentos como código ni hacer de runtime007 dependencia de edición/publicación/CV manuales.
- [ ] T002 Consolidar Python3.12, stack002 y HTTPX existente en pyproject.toml y requirements.lock con versiones exactas/transitivas; preparar config/ai-model-manifest.json y third_party/ai/NOTICE con opción Qwen/Qwen2.5-1.5B-Instruct-GGUF Q4_K_M oficial Apache-2.0 y llama.cpp MIT. Registrar revisión/SHA256/runtime/template/licencias/política offline y benchmark exigidos como no verificados hasta aprovisionamiento, sin inventar checksum ni descargar pesos/binarios durante planificación.
- [ ] T003 [P] Añadir AI_CONTROL_DATABASE_URL, AI_RUNTIME_PATH y AI_MODEL_PATH vacíos en .env.example, excluir pesos/binarios/temporales/secretos con .gitignore y configurar app/config.py para rutas locales verificadas, límites y asistencia deshabilitada sin requisitos acreditados. Sin URL remota/HF_TOKEN ni clave de inferencia persistida; clave loopback efímera solo memoria por proceso.
- [ ] T004 [P] Preparar tests/conftest.py y tests/fixtures/assistance/ con fuentes académicas/perfil/proyecto/traducciones sintéticas y salidas buenas/needs_information/falso empleo/idioma equivocado/HTML/tool-call/truncada/tardía; adaptador captura bytes enviados, process manager falso y reloj controlado sin red. Configurar TEST_* y marcas security/browser_lifecycle/local_model con omisiones explícitas sin PASS.

## Phase 2: Foundational — controles técnicos y frontera editorial

- [ ] T005 Crear mediante CLI descubierta con --help migraciones en supabase/migrations/ para todos los campos de ai_editor_instances («state active/closed», nonce aleatorio, user/session/target/epoch/heartbeat/lease/expiry), ai_request_controls («state reserved/running/delivered/cancelled/expired/failed/accepted», manifest/owner/fence/deadline/result), ai_capacity («active_request_id nullable») y ai_rate_buckets («user_id/global scope»); una instancia activa por admin/campo, expires_at no supera sesión y ninguna tabla almacena texto/contexto/salida/embedding/hash personal. Registrar rutas reales CLI en specs/007-ia-asistida/implementation-notes.md sin inventar timestamps.
- [ ] T006 Crear mediante CLI migración de ai_accept_receipts en supabase/migrations/ con todos los campos del modelo y operation_id PK, sin texto original/digest de propuesta; RLS privada sin Data API anon/authenticated incluso JWT admin. Coordinador solo lee campos editoriales explícitos y controles bajo guard002, sin bandeja/configuración/archivos ni publicación/aprobación; extender roles editoriales solo para consumir nonce/recibo/auditoría en transacción compartida, sin ampliar autoridad editorial.
- [ ] T007 Implementar app/assistance/repository.py con SQL parametrizado/TLS/contexto local limpio de002, reloj DB, coordinación de instancia/request/lease/fence/capacidad global y cuotas técnicas; tablas no guardan prompt/respuesta/fingerprints ni permiten recuperar output por GET. Auditoría solo tipo/resultado/fecha/actor/request/código/duración, sin captura de formulario en app/proxy/SDK/runtime.
- [ ] T008 Implementar app/assistance/source_policy.py y app/assistance/forms.py con allowlist fija profile.summary/project.description para improve y campos textuales aprobados005 para translate, sin URI/SQL/field path del modelo. Preview de selección/contexto exactos sin autoañadir entidad/otros módulos; «source 1–1500 y contexto 0–500 caracteres Unicode», prompt completo<=3072 bytes UTF-8 antes de proceso/transmisión y request<=64KiB, sin truncar; bloquear fuentes/contactos/visitor data y patrones identificados JWT/PEM/claves antes de modelo sin leer secretos reales ni prometer detector infalible.
- [ ] T009 Definir DTO efímeros EditorialRequest/SourceBinding/Suggestion/ReviewDecision en app/assistance/service.py y prompts fijos en app/assistance/prompts.py: «purpose improve/translate», «status unapproved/stale/needs_information/incomplete», idiomas es/en y decisiones accept_as_draft/discard/cancel. Proof firmado ligado a sesión/editor/source/target/versión/selección/contexto/digest/rangos, sin historial DB; prompt pide conservar hechos/nombres/nivel y needs_information ante faltantes, sin herramientas/acciones.

**Checkpoint**: Fuentes mínimas y controles sin texto persistido; frontend/manual007 no puede llamar publicación/aprobación como efecto de generar.

## Phase 3: US1 — Obtener y revisar una sugerencia (P1)

**Objetivo**: Preview explícita, propuesta no aprobada y aceptación únicamente al campo de borrador seleccionado.
**Prueba independiente**: Campo autorizado sintético, preview→generar fake→comparar/editar→aceptar; generar no cambia datos, aceptar conserva campos vecinos/publicaciones y fuente cambiada impide sobrescritura.

### Pruebas primero

- [ ] T010 [P] [US1] Crear tests/unit/assistance/test_source_policy.py para allowlist/minimización, entradas Unicode/límites exactos y exceso caracteres/bytes antes de proceso, secretos/contactos centinela rechazados con cero bytes al adaptador; selección manual no guardada permitida para improve, preview exacta y cambios posteriores invalidan confirmación. Verificar conversión rangos UTF-16 a puntos de código/substrings y no ruptura de surrogates.
- [ ] T011 [P] [US1] Crear tests/contract/assistance/test_review_http.py para disponibilidad/revisiones/previsualizar/generar/aceptar/operaciones de assistance-http.md, guard actual/CSRF/origen/headers, 401/403/404/409/413/422/429/503 y éxito solo tras commit; salida completa no aprobada o needs_information, sin endpoint GET de propuesta ni autorización por datos del modelo.
- [ ] T012 [P] [US1] Crear tests/integration/assistance/test_acceptance_transactions.py con DB/roles reales y adaptador falso: generación modifica cero borradores/publicaciones, aceptación clona revisión guardada y sustituye solo campo final, otros campos no guardados siguen cliente; versión/source/nonce obsoletos409, rollback/auditoría/nonce/recibo atómicos y doble operation_id/cuerpo idéntico vs distinto. Anon/noadmin/JWT directo sin controles/fuente privada y rol coordinador sin escritura de publicación/mensajes.

### Implementación

- [ ] T013 [US1] Implementar preview/generación de improve en app/assistance/service.py con guard vigente antes de transmitir y entregar, fuente/target/selección/contexto confirmados y proof; validar retorno acotado «status suggestion/needs_information, language es/en, text y missing_information opcional». Límite salida<=768tokens/4000caracteres/16KiB, length stop/JSON incompleto/exceso no aceptable422/502 sin substring; salida siempre no aprobada, sin ejecutar tool_calls/URLs/HTML/instrucciones ni validar veracidad por etiqueta.
- [ ] T014 [US1] Implementar app/assistance/local_adapter.py y app/assistance/process_manager.py con proceso llama-server por generación mediante lista argv/shell=False y ventana oculta Windows; binario/modelo local de manifiesto/checksum verificados, 127.0.0.1/puerto efímero/LLAMA_API_KEY efímera solo entorno hijo mínimo, sin variables DB/Supabase/GitHub/SECRET_KEY/HF_TOKEN ni archivos/herramientas de proyecto. HTTP loopback RAM, sin prompt en argv/archivo, stdout/stderr descartados o códigos seguros; sin acceso navegador ni red externa y sin KV entre generaciones.
- [ ] T015 [US1] Implementar validación de manifiesto/runtime en app/assistance/process_manager.py y app/config.py: descubrir flags del build con --help para offline/log-disable/no-cache-prompt/no-webui/no-slots y desactivar downloads/router/slots/KV/tools, sin adivinar soporte. Si checksum/configuración/aislamiento/recursos no verificables devolver unavailable y no spawn; deadline total60s desde petición incluyendo carga, una generación global, umbral inicial4GiB libres más benchmark real y handlers disponibles para edición/cancelación.
- [ ] T016 [US1] Implementar aceptación en app/assistance/service.py y servicios de borrador app/admin/service.py, app/projects/service.py y app/cv/translations.py según target: revalidar sesión/instancia delivered/proof/source/target/expected_revision/version y final_value con reglas normales; confirmación humana explícita. Clonar última revisión guardada, sustituir solo campo o fusión completa revisada del rango y conservar exterior/campos persistidos; revisión/consumo nonce/recibo/auditoría en un commit. No publicar/aprobar005 ni guardar otras ediciones cliente; resultado incierto consulta recibo sin regenerar/recuperar sugerencia.
- [ ] T017 [US1] Implementar rutas de revisión/preview/generación/aceptación/recibo en app/assistance/routes.py y registro app/__init__.py; crear app/templates/assistance/preview.html, app/templates/assistance/review.html y base de app/static/js/assistance.js con fuente/propuesta editable y «Sugerencia no aprobada», acciones distintas de Publicar, textContent/textarea sin innerHTML/eval y digest/nonce/epoch solo RAM. Nunca aplicar al llegar; fuente/campo cambiado anuncia stale y exige revisión explícita.
- [ ] T018 [US1] Ejecutar T010–T012 con adaptador/proceso falsos y revisar teclado/lector preview/errores/needs_information/comparación/edición/aceptación; registrar specs/007-ia-asistida/validation.md y specs/007-ia-asistida/accessibility.md con pruebas de cero publicación/otros campos y evidencias reales/skips diferenciados. Mantener runtime real deshabilitado hasta validar aislamiento/recursos de T033.

**Checkpoint**: US1 demuestra asistencia revisable con fakes; cancelación/efimeridad de US3 son requisitos antes de habilitar uso real P1.

## Phase 4: US3 — Descartar, cancelar y continuar manualmente (P1)

**Objetivo**: Descartar sin efectos, cancelar respuestas tardías y no recuperar propuestas al cerrar/recargar, con tareas manuales intactas.
**Prueba independiente**: Generación fake lenta→cancelar/cerrar/recargar/BFCache→respuesta tardía; no reaparece ni modifica borradores. Con IA/JS deshabilitados editar/guardar/publicar y descargar CV aprobado.

### Pruebas primero

- [ ] T019 [P] [US3] Crear tests/unit/assistance/test_process_lifecycle.py para deadline60s/OOM/ausencia/checksum/frecuencia6inicios10min por admin/20hora global, una capacidad/lease/fence, cancelación lógica inmediata y terminación/kill/huérfanos; DB/guard no verificables detienen/descartan y no liberación confirmada impide segundo spawn. Ningún fallback/download/coste y validación fallida no consume inferencia.
- [ ] T020 [P] [US3] Crear tests/integration/assistance/test_browser_lifecycle.py con navegador real y marca browser_lifecycle: recarga/cierre/reapertura/pageshow BFCache/pagehide perdido/respuesta tardía/edición mientras genera, nueva instancia vacía invalida anterior; inspeccionar cookie/URL/storage/IndexedDB/cache/DOM restaurado sin output antiguo. Borrador guardado intacto, no historialGET/autoPOST/regeneración, UTF-16 correcto y heartbeat no prolonga sesión.
- [ ] T021 [P] [US3] Crear tests/integration/assistance/test_manual_independence.py para editar/guardar/publicar002/003 y descargar CV005 ya aprobado con runtime ausente/fallido/ocupado/JS deshabilitado; revocación/caducidad durante generación impiden entrega/aceptación y red/proceso fake sin egreso. Probar cancelación/descartar/timeout/rate HTTP y ausencia de payload en DB/logs; mark security cuando corresponda a roles reales.

### Implementación

- [ ] T022 [US3] Implementar cuotas/instancias/cancelación en app/assistance/repository.py y app/assistance/service.py con una activa global y por revisión, 6inicios/10min admin+20/h global contados al admitir, 429 Retry-After; heartbeat5s/lease15s, expiry no supera sesión y polling no la extiende. Nueva instancia del mismo admin/campo invalida anterior, cancel/discard/close consumen epoch/control sin texto, delivered jamás permite GET de output.
- [ ] T023 [US3] Completar app/assistance/process_manager.py con grupo/job de proceso oculto, terminar al completar/cancelar/timeout/lease/permiso/DB fallidos, gracia acotada y kill verificable; proceso viejo/respuesta tardía no entrega, capacidad incierta fail-closed antes de otro spawn. Verificar entorno/red/cache offline y ausencia de huérfanos, sin asumir que AbortController/cerrar HTTP detienen físicamente inferencia.
- [ ] T024 [US3] Completar endpoints latido/cancelar/descartar/cerrar/disponibilidad en app/assistance/routes.py y lifecycle en app/static/js/assistance.js: AbortController, nonce/epoch/digest, limpieza RAM/DOM en pagehide y pageshow/BFCache antes de mostrar controles, nuevo nonce al reabrir aun sin aviso previo. Sin storage/historial/hiddenfield serializado para recuperar ni output recuperable; sin JS asistencia explica indisponibilidad y editor manual sigue completo, no reintento automático tras login.
- [ ] T025 [US3] Integrar estados/límites/alternativa manual accesibles en app/templates/assistance/preview.html, app/templates/assistance/review.html y app/static/css/site.css: generar/comparar/editar/aceptar/descartar/cancelar por teclado/lector, status sin stream intrusivo/robo de foco, errores asociados, foco/200%/320px/contraste/espaciado/orientación/movimiento reducido. Ejecutar T019–T021 y registrar specs/007-ia-asistida/accessibility.md y specs/007-ia-asistida/validation.md.

**Checkpoint**: US1+US3 son MVP P1 con controles de descarte/cancelación y ausencia de dependencia manual; modelo real aún requiere ensayo separado y revisión humana.

## Phase 5: US2 — Revisar una traducción (P2)

**Objetivo**: Propuesta es/en de hechos aprobados que solo pasa a borrador, sin aprobación ni disponibilidad CV automática.
**Prueba independiente**: Fuente aprobada vigente→otro idioma→corregir/aceptar borrador; CV y publicación iguales hasta aprobación separada; fuente cambiada409 sin heredar aprobación.

### Pruebas primero

- [ ] T026 [P] [US2] Crear tests/unit/assistance/test_translation_policy.py para es→en desde fuente aprobada/hash vigente001/003/005 a borrador005, en→es desde inglés aprobado vigente005 a perfil/proyecto002/003, idiomas/ref/campos permitidos e invariantes; fragmento no completa resto de variante y mezcla/empleo/capacidad elevada se corrigen/descartan como no aprobados, nunca hechos verificados.
- [ ] T027 [P] [US2] Crear tests/integration/assistance/test_translation_acceptance.py con fuentes/roles reales controlados: aceptación solo campo de borrador, sin approval005/descarga nueva ni cambio público, sourcehash/targetversion concurrentes409 y no transferencia de aprobación; doblePOST/rollback/recibo incierto no duplica/regenera. Ensayar respuestas malas fake y que revisión humana sigue siendo necesaria, sin certificar calidad por fake.

### Implementación

- [ ] T028 [US2] Implementar bindings y prompts de traducción en app/assistance/source_policy.py, app/assistance/prompts.py y app/assistance/service.py: es→en publicación/hash actuales hacia campo de traducción005 y en→es inglés aprobado/hash vigente hacia borrador español002/003, rutas/campos fijos sin inferir correspondencia de rangos entre idiomas. Preview exacta sin todo el perfil; revalidar fuente/aprobación en aceptación, stale409 si cambia.
- [ ] T029 [US2] Integrar selector destino Español/English y comparación revisable en app/assistance/forms.py, app/assistance/routes.py y plantillas app/templates/assistance/preview.html, app/templates/assistance/review.html; distinguir idioma declarado de idioma revisado, exigir comprobar hechos/nombres/nivel y permitir corrección/descarte. Aceptación reutiliza transacción T016, solo draft sin publicar/aprobar005; ejecutar T026–T027 y registrar specs/007-ia-asistida/validation.md.

**Checkpoint**: Traducciones son borradores hasta revisión editorial independiente; ninguna acción007 habilita CV ni publica.

## Phase 6: Polish — aislamiento, recursos y aceptación

- [ ] T030 [P] Documentar specs/007-ia-asistida/operations.md con limpieza acotada de metadatos técnicos vencidos (propuesta24h), configuración offline/allowlist de entorno/terminación de huérfanos y no persistencia en proxy/app/runtime/navegador; límites de garantía de RAM y hardware, sin modelos compartidos ni recuperación de sugerencias. No cron/job remoto ni entrenamiento/exportación de solicitudes.
- [ ] T031 Actualizar specs/007-ia-asistida/quickstart.md con comandos PowerShell implementados, HTTPS/origen/TEST_* y proyecto aislado verificado para limpieza, CLI/migraciones/advisors mediante --help y marcas security/browser_lifecycle/local_model; documentar aprovisionamiento separado de pesos/binario por fuentes oficiales con revisión/hash/licencias, sin descarga automática/runtime ni fallback remoto.
- [ ] T032 Ejecutar tests/unit/assistance, tests/contract/assistance y tests/integration/assistance -m security/-m browser_lifecycle más regresiones002/003/005; consolidar specs/007-ia-asistida/validation.md con commit/lock/roles/RLS, límites/carreras/recibos y prueba de cero payload en controles/logs/storage/caché. Registrar cada skip como aceptación incompleta y diferenciar fakes de evidencia real de navegador/DB.
- [ ] T033 Preparar y ejecutar ensayo separado tests/integration/assistance/test_local_model.py con marca local_model solo en host apto y datos sintéticos, tras aprovisionamiento local verificado: confirmar modelo/runtimeSHA/plantilla/licencias en config/ai-model-manifest.json y third_party/ai/NOTICE, cota3072bytes frente a tokenizer4096tokens/reserva768+256 con Unicode adverso antes de transmitir, memoria/CPU/deadline60s/cancelación y egreso bloqueado/loopback sin secretos. Registrar specs/007-ia-asistida/model-validation.md; si falta recurso/aislamiento/cota acreditada mantener IA unavailable sin impedir trabajo manual ni afirmar validación del modelo por fake.
- [ ] T034 Completar revisión bilingüe humana de hechos/nombres/nivel, respuestas falsas corregidas/descartadas y SC-009 con Victor identificando no aprobado/aceptar borrador o descartar en<1min; registrar specs/007-ia-asistida/model-validation.md y specs/007-ia-asistida/accessibility.md. Ejecutar axe gratuito y matriz manual de todos los criterios WCAG2.1 A/AA aplicables de todo el ciclo, sin deducir conformidad de puntuación ni afirmar modelo infalible; si falta participante dejar criterio pendiente.
- [ ] T035 Revisar specs/007-ia-asistida/validation.md, specs/007-ia-asistida/model-validation.md y specs/007-ia-asistida/accessibility.md con trazabilidad FR-001–013/SC-001–010, fuentes/permisos/privacidad/procesos/ausencia de recuperación y funciones esenciales sin IA. Cerrar defectos obligatorios antes de aceptar asistencia, sin publicar textos reales, desplegar ni sustituir modelo/proveedor automáticamente; gate004 y aprobaciones005 permanecen fuera de autoridad007.

## Dependencies & Execution Order

```text
Seguridad/borradores002 + proyectos003 + traducciones/CV005 disponibles
 → Setup T001–T004 → Fundamentos T005–T009
   → US1 T010–T018 (P1, propuesta/aceptación)
     → US3 T019–T025 (P1, ciclo efímero/fallback manual)
       → US2 T026–T029 (P2, traducción)
         → Polish T030–T035 → aceptación local acreditada
```

T002 precede T003/T004. Fundamentos secuenciales T005→T006→T007→T008→T009. Cada historia escribe pruebas primero; US1 implementa T013→T014→T015→T016→T017→T018 con adapter fake hasta runtime acreditado; US3 T022→T023→T024→T025; US2 T028→T029. Cierre T031–T035 consolida evidencias secuencialmente, T030 independiente tras historias.

US1 se prueba con campo/adaptador controlados sin modelo real; US3 con generación fake lenta y flujos manuales aprobados, navegador real para lifecycle; US2 con fuentes/variantes sintéticas aprobadas y consumidores005 sin depender del contenido de sugerencias anteriores. Archivos service.py/source_policy.py/process_manager.py/routes.py y JS compartidos se editan secuencialmente entre tareas; independencia de prueba no elimina guard ni versiones.

Pruebas fake pueden pasar antes del aprovisionamiento; esto no habilita runtime ni cierra SC de calidad/hardware. T033 insuficiente mantiene asistencia indisponible mientras trabajo manual continúa. P2 de traducción no rebaja privacidad/cancelación/revisión humana P1.

## Parallel Examples

- Setup: T003 (config/env) y T004 (fixtures/tests) tras T002.
- US1: T010 (fuente/rangos), T011 (HTTP), T012 (DB/aceptación) en archivos distintos tras fundamentos y con interfaces acordadas.
- US3: T019 (procesos), T020 (navegador), T021 (independencia manual/seguridad) pueden prepararse juntas tras US1; DB y navegador integrados esperan implementación y fixtures aisladas.
- US2: T026 (política) y T027 (aceptación DB) en paralelo tras US3; no editar fuentes publicadas del mismo fixture simultáneamente salvo carreras deliberadas.
- Cierre: T030 documentación desde resultados existentes; T031–T035 consolidan manifiesto/evidencias secuencialmente. No ejecutar múltiples modelos reales para ensayar fuera de pruebas explícitas de exclusión.

## Implementation Strategy

1. Reutilizar seguridad/editoriales, controles DB sin texto y preview minimizada. No cargar modelo al importar aplicación o consultar disponibilidad.
2. US1 demuestra sugerencia/revisión/aceptación por campo con fakes, nunca aprobación ni publicación.
3. Completar US3 antes del MVP P1: cierre/recarga/BFCache/cancelación/respuesta tardía y ausencia total de dependencia manual.
4. US2 añade traducciones solo de fuentes vigentes y aceptación como borrador, con aprobación005 separada.
5. Validar runtime real local/recursos/red/privacidad, revisión bilingüe y WCAG. MVP técnico US1+US3; aceptación completa de007 requiere también US2 y evidencias reales de todos los criterios. Si host no es apto, IA unavailable sin contratar recursos ni cambiar proveedor; no declarar cumplido lo no ensayado.

## Trazabilidad

US1: FR-001/002/003/004/005/006/007/008/011/012, SC-001/004/005/006/007. US3: FR-002/004/008/009/010/011/012/013, SC-002/003/004/007/008/009/010. US2: FR-001/005/006/007, SC-001/005/006. T032–T035 consolidan FR/SC, permisos reales, efimeridad navegador, runtime y revisión humana.

Las tareas citan enum/nullabilidad/límites e invariantes del modelo e incorporan todos los campos de tablas técnicas. Migra­ciones se nombran por CLI y se registran al crearlas; modelos/binarios/checksums solo se fijan cuando sean verificados. No prometer borrado forense de RAM ni detección perfecta de secretos/veracidad: se acredita ausencia de persistencia/recuperación y control humano explícito.
