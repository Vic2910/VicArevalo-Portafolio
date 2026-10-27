# Tasks: Galería y administración de proyectos

**Input**: `specs/003-gestion-proyectos/`: plan.md, spec.md, data-model.md, research.md, contracts/projects-http.md, contracts/images-and-transactions.md y quickstart.md; constitución 1.0.0 y diseños 001/002.
**Organización**: Setup → fundamentos → US1 (P1) → US2 (P1) → US3 (P2) → cierre. Se conserva el directorio solicitado 003-gestion-proyectos; 003-proyectos en spec.md es metadato histórico.
**Pruebas**: Pytest exigido por diseño/spec/constitución. Escribir pruebas de cada historia primero y comprobar fallos relevantes antes de implementar. Seguridad y atomicidad requieren roles/DB reales aislados; mocks y skips no acreditan aceptación. Accesibilidad se verifica en cada incremento.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas relativas a raíz; [P] significa archivos independientes tras cumplir prerrequisitos, no escrituras concurrentes sobre mismos fixtures.
**Alcance**: Tareas futuras, sin aplicación ni datos publicados en esta entrega. Sin Storage/CDN, service_role, importación GitHub, IA, buscador, filtros, historial restaurable ni PDF. BYTEA privado de imágenes normalizadas, nunca originales en static/Git.

## Phase 1: Setup — infraestructura compartida

**Propósito**: Reutilizar monolito 001 y seguridad 002 sin asumir que sus documentos son código existente.

- [ ] T001 Inspeccionar base disponible y registrar en specs/003-gestion-proyectos/implementation-notes.md factory, configuración, plantillas/CSS, guard/sesiones/CSRF, auditoría/recibos, pools y tablas públicas de 001/002; completar prerrequisitos faltantes de specs/001-perfil-publico/tasks.md y specs/002-administracion/tasks.md antes de integrar administración, sin rehacer archivos existentes ni declarar implementadas otras features por inferencia.
- [ ] T002 Añadir Pillow estable compatible con Python 3.12 al stack existente de pyproject.toml y requirements.lock, fijando versiones exactas/transitivas; verificar codecs JPEG/PNG/WebP, documentación/changelog vigentes y licencias Pillow/codecs en specs/003-gestion-proyectos/dependencies.md. Si falta codec requerido, bloquear habilitación de cargas con diagnóstico interno.
- [ ] T003 [P] Añadir PROJECT_MEDIA_DATABASE_URL vacío en .env.example y exclusiones de originales, temporales, secretos y certificados privados en .gitignore; configurar credenciales separadas de rol media mediante entorno protegido, sin valores reales en documentos.
- [ ] T004 [P] Preparar tests/conftest.py y tests/fixtures/projects/ con A/B publicados compartiendo asset, C solo borrador, revisión pendiente en A y bytes exclusivos privados; crear archivos raster sintéticos válidos JPEG/PNG/WebP, uno válido de exactamente 5 MiB y casos maliciosos/límites. Nunca usar buffer arbitrario como evidencia de imagen válida ni presentar fixtures como proyectos reales.

## Phase 2: Foundational — persistencia y permisos bloqueantes

**Propósito**: Modelo específico de proyectos, sin ampliar tipos ni DELETE de revisiones de 002.

- [ ] T005 Configurar app/config.py con PROJECT_MEDIA_DATABASE_URL TLS verify-full, máximo 2 conexiones media por proceso y un proceso inicial; mantener presupuesto dependencias <=8 s, statement_timeout 3 s y lock_timeout 1 s; separar multipart <=6 MiB de formularios sin archivo <=64 KiB, evitando que el límite global de 002 bloquee cargas válidas. Exponer límites claros sin secretos.
- [ ] T006 Crear mediante CLI descubierta con --help migración en supabase/migrations/ para private.projects con todos los campos del modelo y «published_revision_id nullable», punteros del mismo proyecto/UUID estable; private.project_revisions con «repository_url nullable, demo_url nullable», «UNIQUE(project_id, revision_number)» y «Inmutables mientras exista proyecto; solo eliminación explícita del proyecto permite borrar sus revisiones»; private.project_revision_images con «alt_text nullable en borrador», «PK(revision_id, association_id); orden único por revisión», position/representative/use_authorized contextuales. Registrar ruta real creada en specs/003-gestion-proyectos/implementation-notes.md, sin inventar timestamp de migración.
- [ ] T007 Crear mediante CLI migración en supabase/migrations/ para private.project_image_assets con main_bytes/thumbnail_bytes BYTEA, «mime=image/webp», width/height/main_size/thumbnail_size/sha256/created_at, «Tamaños congruentes con octet_length» y «No UPDATE de contenido»; project_catalog singleton/version, project_media_budget singleton/stored_bytes/updated_at, project_operations con «project_id nullable», «result_revision_id nullable», operation_id PK y todos los campos del modelo; project_publication_events con «operation_id único» y evidencia mínima sin textos/bytes tras eliminar. Recibos/auditoría no tendrán FK que impida eliminación del proyecto.
- [ ] T008 Crear mediante CLI migración de instantáneas en supabase/migrations/ con todos los campos de public.public_projects y public.public_project_images de data-model.md, enlaces opcionales «repository_url/demo_url nullable», FK/restricciones que impidan mezclar revisiones y asociaciones; índices FK, asset_id, display_order/id, revision_id/association_id y operaciones únicos; sin índices BYTEA/payload. URLs se construyen por router, no se persisten firmadas.
- [ ] T009 Aplicar en migraciones de supabase/migrations/ RLS/grants explícitos de contracts/images-and-transactions.md: anon/authenticated incluso JWT admin solo SELECT público vigente; backend_auth sin nuevos grants; backend_editor con guard/autoridad actual y DELETE limitado a proyectos; backend_project_media no propietario/BYPASSRLS solo SELECT de variantes/metadata de assets con asociación pública activa mediante EXISTS y permisos mínimos sobre asociaciones. Sin acceso media a sesiones/auditoría/revisiones privadas ni escritura; esquema private no expuesto y sin USAGE público, sin SECURITY DEFINER.
- [ ] T010 Implementar base transaccional de app/projects/repository.py y registro de blueprints en app/__init__.py: reutilizar guard/SQL parametrizado/contexto local/pools de 002 y orden de locks autorización→sesión→catálogo→proyecto→presupuesto→assets UUID ordenados cuando correspondan; sin Auth/normalización/render bajo locks. Integrar auditoría/operation_id y contexto limpiado al devolver conexión; estados ready/empty/unavailable sin confundir caída con vacío.

**Checkpoint**: Superficie pública mínima y tabla de bytes protegida; los tres incrementos pueden probarse con publicaciones/sesiones aisladas.

## Phase 3: US1 — Explorar proyectos publicados (P1)

**Objetivo**: Galería/ficha con contenido aprobado y alternativas pertinentes, sin depender de editor ni sincronización externa.
**Prueba independiente**: Con publicaciones de prueba, consultar listado/ficha/imágenes y estados vacío/error; URLs de borradores/revisiones no vigentes nunca entregan contenido.

### Pruebas primero

- [ ] T011 [P] [US1] Crear tests/contract/projects/test_public_http.py para galería 12 tarjetas, orden display_order/id, enlaces anterior/siguiente, page inválida 400 y fuera de rango 404 salvo página 1 vacía 200; ficha publicada/404 genérica y fallo 503, enlaces opcionales omitidos, escape, alt/leyenda con imagen rota y destino projects disponible aunque galería vacía.
- [ ] T012 [P] [US1] Crear tests/contract/projects/test_public_media.py para GET/HEAD principal/miniatura con project_id/revision_id/association_id exactos, variante inválida/privada/antigua 404, proveedor fallido 503 sin bytes; headers no-store/nosniff/image-webp/longitud y comprobación vigente incluso con Range/condicionales/querystring, sin ETag/304/redirect, original ni autorización por asset_id global.
- [ ] T013 [P] [US1] Crear tests/integration/projects/test_public_permissions.py para anon/autenticado no admin/JWT admin/rol media: select=*, UUID y joins no revelan privados, bytes ni borradores; rol media solo lee asset públicamente referenciado y no escribe/ve sesiones. Verificar DB tras intentos y consultas públicas consistentes en una instantánea, sin BYTEA en listado ni N+1; integración security se omite explícitamente sin entorno.

### Implementación

- [ ] T014 [US1] Implementar lecturas públicas en app/projects/repository.py y composición en app/projects/service.py con metadatos/asociaciones de misma revisión en una instantánea SQL/transacción de lectura, sin bytes en listado/ficha ni N+1; paginar 12 por display_order/id y distinguir empty de unavailable. No prometer foto histórica entre peticiones de páginas diferentes.
- [ ] T015 [US1] Implementar app/projects/routes.py para /proyectos, ficha por UUID y GET/HEAD /proyectos/<project_id>/versiones/<revision_id>/imagenes/<association_id>/<variant>; consultar asociación vigente y bytes de variante en misma instantánea bajo rol media, sin asset global. Ignorar Range con respuesta completa si procede, nunca saltar control; no-store también en errores y sin ETag/304/caché retirada.
- [ ] T016 [US1] Crear app/templates/projects/gallery.html y app/templates/projects/detail.html con HTML español semántico, título/h1, navegación/skip link y paginación accesible, miniaturas lazy, alt y leyenda textual, orden de imágenes y enlaces HTTP/HTTPS reales en misma pestaña por defecto; vacío honesto y error útil sin tarjetas ficticias, carrusel obligatorio ni acciones vacías. Registrar capacidad projects/endpoint mediante integración con app/public/service.py de 001 cuando módulo operativo.
- [ ] T017 [US1] Ajustar app/static/css/site.css para galería/ficha flexibles, foco visible, contrastes 4.5:1 normal/3:1 grande/no textual necesario, URLs largas, 200 % y 320 px, orientación/espaciado/movimiento reducido y funcionamiento sin JS; ejecutar T011–T013 y revisión teclado/lector/imagen rota, registrando evidencia en specs/003-gestion-proyectos/accessibility.md y specs/003-gestion-proyectos/validation.md.

**Checkpoint**: US1 es MVP de lectura con publicaciones aisladas, sin afirmar editor completo ni seguridad real si suites omitidas.

## Phase 4: US2 — Crear y publicar un proyecto (P1)

**Objetivo**: Guardado privado, carga segura y publicación explícita de revisión exacta con autoría/derechos confirmados.
**Prueba independiente**: Administrador sintético crea/reabre borrador incompleto, adjunta imagen válida, completa/revisa y publica; público solo recibe versión aprobada y fallos no dejan registros parciales.

### Pruebas primero

- [ ] T018 [P] [US2] Crear tests/unit/projects/test_validation.py para límites de título/descripción/tecnologías/alt/URLs/referencias, campos obligatorios de publicación, borrador incompleto seguro, deduplicación trim/casefold, marcadores y confirmación humana; HTTP/HTTPS sin fetch servidor, esquemas/credenciales/controles rechazados y salida escapada.
- [ ] T019 [P] [US2] Crear tests/unit/projects/test_image_pipeline.py para JPEG/PNG/WebP reales, exactamente 5,242,880 bytes aceptados por tamaño y exceso rechazado, 12 MP/lado6000, coherencia MIME/extensión/decoder, nombre Unicode/peligroso, ejecutable/corrupto/truncado/animado/bomba, codec ausente, orientación y eliminación de metadatos; verificar derivados/hash/tamaños y originales descartados sin persistencia parcial.
- [ ] T020 [P] [US2] Crear tests/contract/projects/test_admin_creation.py para listado/nuevo/crear/editar/borrador/cargar/asociar/preview/revisar/publicar/operaciones del contrato, guard/CSRF/origen/herencia 002, 401/403/404/409/413/422/503 y 303 solo tras commit; token exacto expirado/ajeno, confirmaciones ausentes y sesión vencida sin replay. Rechazo conserva estado confirmado y exige seleccionar archivo de nuevo.
- [ ] T021 [P] [US2] Crear tests/integration/projects/test_creation_transactions.py para guard/RLS editor sin contexto o contexto viejo, publicación individual y consumidores galería/ficha/CV controlado, carga concurrente junto a cupo, medición física ausente/fallida, rollback en cada paso y auditoría fallida, doble envío/commit incierto por recibo. Verificar asset/revisión/referencias/punteros/presupuesto íntegros, ningún huérfano y cero publicación privada.

### Implementación

- [ ] T022 [US2] Implementar app/projects/forms.py con reglas literales: «Título hasta 200 caracteres; descripción hasta 10000; tecnologías máximo 20, cada una hasta 80, sin duplicados tras trim/casefold», «Publicar exige título/descripción y >=1 tecnología, sin marcadores ni afirmaciones no revisadas» y «Borrador seguro permite campos faltantes, normalizados a vacío/null según tipo»; «URLs opcionales hasta 2048, HTTP/HTTPS con host y puerto válidos, sin credenciales ni controles» y «No aceptar javascript/data, protocolo relativo o atributos HTML. No realizar fetch servidor para comprobar el enlace.».
- [ ] T023 [US2] Ampliar app/projects/forms.py con «máximo 10 referencias por revisión; exactamente una representativa al publicar; toda referencia informativa requiere alt no vacío hasta 300 y autorización explícita de uso»; alt/use_authorized/representative/position pertenecen a cada asociación contextual. Revisión exige autoría/veracidad/derechos, no inferidos de repositorios ni IA; conservar entradas seguras solo mientras sesión autorizada.
- [ ] T024 [US2] Implementar app/projects/images.py leyendo máximo 5 MiB+1 sin confiar en Content-Length, un archivo por multipart <=6 MiB y campos acotados; «Entrada por archivo <=5,242,880 bytes inclusive; formato JPEG/PNG/WebP, estático, <=12 MP y lado<=6000». Rechazar nombre vacío/rutas/traversal/controles/NUL/reservados/extensión incoherente tras normalización Unicode, sin sanear silenciosamente para aceptar; firma/decoder/MIME coherentes y MIME ausente solo inferido por decoder validado.
- [ ] T025 [US2] Completar app/projects/images.py con verify/reabrir/decodificar completo, avisos de bomba como error y rechazo truncado/multiframe; aplicar orientación, RGB/RGBA y reencodificar «Derivados principal<=2 MiB/1600 px y thumbnail<=256 KiB/480 px, WebP sin metadatos»; excluir EXIF/ICC/comentarios, calcular hash/bytes en backend y descartar originales/temporales privados al terminar/error. Normalización fuera de locks y máximo un procesamiento por proceso, sin servicios externos.
- [ ] T026 [US2] Implementar presupuesto en app/projects/repository.py y app/projects/service.py: «Por revisión <=20 MiB de derivados únicos, global<=64 MiB de assets de todos los borradores/revisiones», «límite preventivo inicial 350 MiB» físico o umbral más conservador de cuota vigente; medir tamaño DB/margen y bloquear presupuesto bajo lock. Insertar bytes/revisión/referencias/contador/auditoría/recibo en un commit tras revalidar guard/version; si falta medición/cupo devolver estado útil sin guardar parcialmente, borrar referenciados ni activar cargos.
- [ ] T027 [US2] Implementar creación/guardado/asociación en app/projects/service.py y app/projects/repository.py: expected_version, revisión inmutable y lock_version, punteros del mismo proyecto, publicación intacta; asset existente solo por selección explícita del admin autorizado y nueva referencia con alt/derechos contextuales propios. Recibos project_operations con id/actor/acción/digest idénticos idempotentes, otro cuerpo 409, hash de derivados incluido; commit incierto se consulta sin retry automático.
- [ ] T028 [US2] Implementar revisión/publicación en app/projects/service.py y app/projects/repository.py con token de sesión/acción/proyecto/revisión/digest/version de 10 min, borrador actual y confirmaciones explícitas; revalidar campos, bytes y referencias, materializar solo esa revisión/asociaciones y actualizar puntero/version/catálogo/aprobación/auditoría/recibo en transacción. Primera publicación al final; no importar ni publicar repositorios automáticamente.
- [ ] T029 [US2] Implementar rutas administrativas de creación/edición/carga/asociación/preview/revisión/publicación/operaciones en app/projects/admin_routes.py reutilizando 002, con sus códigos/headers y resultado solo tras commit; preview privada por proyecto/revisión/asociación/variante y guard actual sin prolongar sesión por assets. Implementar app/templates/projects/admin/index.html, app/templates/projects/admin/edit.html y app/templates/projects/admin/review.html con límites antes de input file nativo, errores vinculados y confirmación de versión normalizada, sin secretos ni bytes privados públicos.
- [ ] T030 [US2] Ejecutar T018–T021, regresión US1 y revisión automática/manual de acceso→crear→adjuntar→corregir→revisar→publicar sin JS, teclado/NVDA, 200 %/320 px y demás WCAG aplicables; completar specs/003-gestion-proyectos/accessibility.md y specs/003-gestion-proyectos/validation.md. Medir SC-007 con Victor y material preparado <=5 min, incluyendo explicación borrador/publicación; si falta participante registrar pendiente sin inventar resultado.

**Checkpoint**: US1 + US2 permiten MVP de lectura y creación/publicación. US3 P2 completa mantenimiento, retirada y eliminación; no declarar feature completa antes.

## Phase 5: US3 — Actualizar, ordenar o retirar proyectos (P2)

**Objetivo**: Correcciones aisladas, orden independiente, retirada y eliminación seguras con imágenes compartidas.
**Prueba independiente**: Con A/B compartiendo imagen y C borrador, corregir/reemplazar A, confirmar orden, publicar/retirar/eliminar y verificar consumidores, bytes y referencias de los demás antes/después; cancelar no muta.

### Pruebas primero

- [ ] T031 [P] [US3] Crear tests/integration/projects/test_shared_images.py para reemplazo de A solo en borrador, publicaciones A/B sin cambios hasta confirmación, publicación cambia solo A y revoca URL vieja de A, B conserva bytes/alt/derechos/URL; retirada conserva revisiones y eliminación nunca borra referencias de cualquier revisión/borrador ajeno, incluidas carreras con nueva asociación.
- [ ] T032 [P] [US3] Crear tests/contract/projects/test_admin_maintenance.py para orden por campos numéricos/lista completa/catalog_version, duplicados/omisiones 422 y catálogo obsoleto 409; confirmar/cancelar retirada/eliminación separadas, versiones/tokens erróneos y sesión vencida sin efectos/replay; corrección conserva posición y republicación al final.
- [ ] T033 [P] [US3] Crear tests/integration/projects/test_maintenance_transactions.py para guardado/publicación/orden/retiro/borrado concurrentes, fallos en cada paso y commit incierto/doble POST; comparar galería/ficha/fuente CV controlada y GET/HEAD media con Range/condicionales después del commit. Verificar catálogo/punteros/contador/auditoría/recibos, borrado sin FK residual y evidencia mínima sin textos/bytes.

### Implementación

- [ ] T034 [US3] Implementar reemplazo target_association_id y correcciones en app/projects/service.py y app/projects/repository.py: nuevo asset inmutable o elección explícita existente y nueva revisión/referencia local, nunca UPDATE binario global; guardar cambia cero publicaciones y publicar actualiza solo proyecto elegido, conserva posición y referencias ajenas. Revalidar versiones y confirmar revisión exacta nueva.
- [ ] T035 [US3] Implementar orden en app/projects/repository.py y app/projects/service.py con lock catálogo, expected_catalog_version y lista exacta de IDs vigentes sin duplicados/omisiones; persistir posiciones 1..N y versión catálogo atómicamente con recibo/auditoría, sin tocar revisiones, borradores ni versiones de contenido. Cualquier cambio concurrente de membresía/publicación invalida formulario viejo con 409.
- [ ] T036 [US3] Implementar retirada en app/projects/service.py y app/projects/repository.py ligada a publicación/lock_version y token confirmado: eliminar instantánea/asociaciones, limpiar puntero publicado y actualizar catálogo/versión/recibo/auditoría en mismo commit, conservando borrador y todas las revisiones/bytes. Republicar exige revisión/confirmación nuevas y vuelve al final; rutas antiguas de ese proyecto ya no entregan aunque otro siga compartiendo asset.
- [ ] T037 [US3] Implementar eliminación en app/projects/repository.py y app/projects/service.py con confirmación separada proyecto/version, borrando publicación/proyecto/revisiones/referencias solo de ese proyecto; comprobar ausencia de cualquier referencia antes de borrar assets bajo locks y FKs restrictivas, contar borradores/revisiones ajenos y decrementar presupuesto solo por bytes realmente eliminados. Mantener recibo/auditoría UUID/digest sin contenido y consultables por actor autorizado tras eliminación; cancelar no ejecuta mutación editorial.
- [ ] T038 [US3] Completar rutas GET/POST orden/retirar/eliminar de app/projects/admin_routes.py y plantillas app/templates/projects/admin/order.html y app/templates/projects/admin/confirm.html, con acciones/proyecto claramente nombrados, campos numéricos sin drag obligatorio y confirmación destructiva distinta de retirada; cancelación vuelve sin POST destructivo y errores/conflictos no sobrescriben datos.
- [ ] T039 [US3] Ejecutar T031–T033 y regresiones US1/US2; verificar ciclo corregir→ordenar→publicar→retirar→republicar→eliminar y cancelaciones con teclado/lector, imagen rota, sin JS/gestos/hover/color obligatorio. Actualizar specs/003-gestion-proyectos/validation.md y specs/003-gestion-proyectos/accessibility.md con evidencia sanitizada de referencias compartidas, revocación y estado íntegro ante fallos.

**Checkpoint**: Todas las historias completas si permisos reales, transacciones, consumidores y revisión manual están acreditados; cierre consolida aceptación.

## Phase 6: Polish — recursos, operación y aceptación

- [ ] T040 [P] Documentar en specs/003-gestion-proyectos/operations.md reconciliación de project_media_budget con sumas de variantes y tamaño físico DB, alertas/margen compartido y limpieza acotada por operador o backend autorizado solo de assets realmente sin referencias, bajo locks/FK; jamás eliminar por antigüedad/recuento obsoleto ni liberar cuota borrando referenciados. Revisar conservación de evidencia mínima y exclusión de originales/secretos.
- [ ] T041 Medir y registrar en specs/003-gestion-proyectos/resources.md memoria/tiempo del máximo de archivo/píxeles, codec normalizador, derivados, consultas sin N+1, paginación 12, concurrencia de carga y límites físicos/payload reales con margen de 001/002; validar presupuestos propuestos antes de habilitar cargas y ajustar configuración de app/config.py si recursos gratuitos no bastan, sin reducir controles ni activar facturación.
- [ ] T042 Actualizar specs/003-gestion-proyectos/quickstart.md con comandos PowerShell implementados, HTTPS/origen, variables protegidas, CLI/migraciones/advisors descubiertos por --help, TEST_* y fixtures/limpieza con verificación de proyecto aislado; documentar codecs, límites exactos y omisiones como aceptación incompleta, sin desactivar Secure/CSRF ni publicar datos reales.
- [ ] T043 Ejecutar tests/unit/projects, tests/contract/projects y tests/integration/projects -m security más regresiones 001/002; consolidar specs/003-gestion-proyectos/validation.md con commit/versiones/licencias, roles/grants/RLS revisados, evidencia de límites exactos, atomicidad/concurrencia, recursos y trazabilidad FR-001–015/SC-001–009; inspeccionar logs/headers/HTML/errores para cero secretos/originales/bytes privados/URLs persistentes.
- [ ] T044 Completar matriz WCAG 2.1 A/AA de todos los flujos/estados en specs/003-gestion-proyectos/accessibility.md mediante axe gratuito y revisión manual teclado/lector, contraste, espaciado, 200 %/320 px/orientación y movimiento reducido; revisar evidencia SC-007 con Victor y registrar revisión de permisos/presupuestos e imagen/autoría reales antes de activación en specs/003-gestion-proyectos/validation.md. No aceptar con skips de seguridad, medición pendiente o defectos obligatorios abiertos; no desplegar como parte de estas tareas.

## Dependencies & Execution Order

```text
Base pública 001 + seguridad 002 disponibles
  → Setup T001–T004 → Fundamentos T005–T010
    → US1 T011–T017 (P1, MVP lectura)
      → US2 T018–T030 (P1, MVP creación/publicación)
        → US3 T031–T039 (P2, mantenimiento completo)
          → Polish T040–T044 → aceptación completa
```

T002 precede T003/T004. Fundamentos secuenciales T005→T006→T007→T008→T009→T010; migraciones con CLI y nombres reales anotados, no ejecutar escrituras sobre producción. Pruebas de cada historia primero, implementación en orden y cierre tras suites completas. T014→T015→T016→T017; T022→T023→T024→T025→T026→T027→T028→T029→T030; T034→T035→T036→T037→T038→T039. Cierre espera historias.

US1 puede evaluarse sin editor mediante publicaciones aisladas. US2 usa sesión de 002 y consumidores controlados, sin GitHub/IA/CV PDF. US3 usa proyectos/revisiones preparadas para probar cada transición independientemente, pero integra sobre repositorio/editor US2. La independencia de prueba no permite editar repository.py/service.py/admin_routes.py en paralelo ni omitir prerrequisitos de seguridad. Accesibilidad es condición de cada incremento, no una mejora opcional final.

## Parallel Examples

- Setup: T003 (.env.example/.gitignore) junto a T004 (fixtures/tests) después de T002.
- US1: T011 (HTML), T012 (media HTTP) y T013 (permisos reales) preparan suites en archivos distintos tras fundamentos; su ejecución integrada espera aplicación y DB.
- US2: T018 (validación), T019 (imágenes), T020 (HTTP admin) y T021 (transacciones) pueden escribirse simultáneamente con interfaces/fixtures acordados; integración paralela requiere datos aislados por caso/worker.
- US3: T031 (compartidas), T032 (HTTP mantenimiento) y T033 (transacciones) pueden prepararse juntas tras US2; nunca mutar el mismo catálogo/asset de fixture simultáneamente fuera de pruebas de carreras deliberadas.
- Polish: T040 puede redactarse tras historias sin competir con medidas T041; T042–T044 actualizan evidencias compartidas secuencialmente.

## Implementation Strategy

1. Completar prerrequisitos reales 001/002, fijar dependencias/codecs y revisar permisos/migraciones en entorno aislado.
2. US1 ofrece primer MVP de lectura con proyectos sintéticos publicados solo para evaluación local; validar galería, fichas y privacidad antes de editor.
3. US2 añade MVP P1 de creación/publicación: borrador privado, carga segura, revisión de versión concreta y autoría/derechos explícitos; probar rollback, cuotas y accesibilidad, medir SC-007 con Victor.
4. US3 incorpora orden separado, correcciones y reemplazos locales, retirada y eliminación con referencias compartidas preservadas; repetir consumidores y controles de entrega posterior a commit.
5. Consolidar suites reales, recursos y matriz WCAG; no confundir demostración P1 con cumplimiento de todos los FR/SC de feature. Aprobación de proyectos/imágenes reales es humana; no inferirla de fixtures o validación sintáctica.

## Trazabilidad

US1: FR-006/009/010 y SC-002/006. US2: FR-001/002/003/007/008/009/010/011/013 y SC-001/002/003/006/007/008. US3: FR-003/004/005/010/012/013/014/015 y SC-004/005/006/008/009. T041–T044 consolidan aceptación transversal; T013/T021/T033 acreditan DB real, no mocks.

Las tareas de migración usan supabase/migrations/ como destino obligatorio y registran el archivo exacto generado por CLI, evitando inventar timestamps. Reglas/enum/nullabilidad y límites citados provienen del modelo; los campos completos se incluyen según sus tablas. No garantizar revocación de copias previamente descargadas ni de respuestas ya iniciadas antes del commit.
