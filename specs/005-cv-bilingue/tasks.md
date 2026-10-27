# Tasks: CV actualizado en español e inglés

**Input**: plan.md, spec.md, data-model.md, research.md, contracts/cv-http.md, contracts/snapshot-and-pdf.md y quickstart.md de `specs/005-cv-bilingue/`; constitución 1.0.0 y diseños 001–003.
**Organización**: Setup → fundamentos → US1 → US2 → US3 → cierre. Las tres historias son P1; US1/US2 usan selección y publicaciones sintéticas para pruebas independientes, US3 completa gestión de selección/coherencia y QA exhaustiva.
**Pruebas**: Pytest solicitado por diseño/spec/constitución. Escribir suites antes de implementar y verificar fallos pertinentes. Roles/DB reales para RLS/concurrencia; extracción pypdf/Poppler y revisión de todas las páginas complementarias, nunca sustitutas. No generar PDFs reales de Victor en planificación.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas desde raíz; [P] solo tras prerrequisitos y sin modificar archivos compartidos. Solo fixtures sintéticas, sin publicación de contenido real, deploy, IA, GitHub, SMTP o acceso a mensajes/imágenes binarias.

## Phase 1: Setup — infraestructura compartida

**Propósito**: Preparar generación local gratuita sobre el monolito existente.

- [ ] T001 Inspeccionar implementación real de 001–003 y documentar en specs/005-cv-bilingue/implementation-notes.md factory, configuración, guard/sesión/CSRF/auditoría/recibos de 002 y publicaciones de perfil/habilidades/académicos/proyectos disponibles; completar sus prerrequisitos faltantes antes de integración, sin asumir que documentos son código. Mantener 004 RET-001 intacto: correo autorizado del perfil basta y recepción/bandeja no son dependencia.
- [ ] T002 Ampliar pyproject.toml y requirements.lock con ReportLab OSS y pypdf estables compatibles con Python 3.12 y stack 002; localizar Poppler para QA y verificar documentación vigente/versiones exactas/transitivas/licencias en specs/005-cv-bilingue/dependencies.md, sin ReportLab Plus/SaaS PDF. Incorporar TTF regular/negrita y LICENSE en app/assets/fonts/dejavu/ con origen/licencia verificados, sin depender de fuentes del equipo o descarga runtime.
- [ ] T003 [P] Añadir CV_READ_DATABASE_URL y CV_ADMIN_DATABASE_URL vacíos en .env.example, mantener secretos ignorados en .gitignore y configurar roles externos con TLS verificado en app/config.py; presupuesto snapshot<=2 s, render/validación<=6 s y margen 2 s, buffer 8 MiB, una generación activa por proceso y espera acotada; ninguna reducción/truncamiento de contenido para cumplir límites.
- [ ] T004 [P] Preparar tests/fixtures/cv/ y tests/conftest.py con nombre/tildes/correo autorizado, education explícita, habilidades/actividad y A/B/C publicados, galería A,B,C y selección CV B,A, C sin traducción, traducciones sintéticas aprobadas y privadas centinela; casos mínimos faltantes/inglés obsoleto/URLs y textos mono-multipágina. Configurar TEST_* aislados y marcas security/pdf_visual, omisiones explícitas sin PASS.

## Phase 2: Foundational — fuentes, hashes y permisos bloqueantes

**Propósito**: Consolidar extensiones explícitas sin inventar hechos ni alterar galería.

- [ ] T005 Crear mediante CLI descubierta con --help migraciones en supabase/migrations/ que añadan «record_kind education/academic» a revisión/payload/public_academic_experiences de 001/002, backfill conservador academic y clasificación confirmada por Victor al revisar en app/admin/forms.py y app/admin/service.py; «Educación aprobada requiere actividad/programa y descripción aprobados según 002; institución/fechas opcionales se omiten si pendientes». Una education no cuenta también como actividad; no inferir educación del perfil/texto.
- [ ] T006 Añadir mediante migraciones en supabase/migrations/ «publication_epoch UUID por ciclo de publicación» en private.projects/public_projects y adaptar app/projects/repository.py: primera publicación/republicación genera nuevo epoch, corrección mientras publicado lo conserva; retirada/eliminación excluye vigente. Añadir cv_projection_hash a las cuatro fuentes públicas mediante helper/trigger puro SECURITY INVOKER de proyección canónica versionada, con backfill solo de datos aprobados, nunca hash aportado por cliente. Registrar archivos exactos CLI en specs/005-cv-bilingue/implementation-notes.md sin inventar timestamps.
- [ ] T007 Crear mediante CLI migraciones de supabase/migrations/ para public.cv_project_selection con singleton/selection_version entero/confirmed_at y public.cv_project_selection_items con project_id/selected_epoch/position/selection_version, «posición única», sin selección inicial implícita y una configuración es/en. FK a private.projects limpia referencias al eliminar sin conceder acceso público al padre; RLS solo muestra selección con id+epoch publicado vigente, sin referencias retiradas, sin alterar display_order de galería.
- [ ] T008 Crear mediante CLI migraciones en supabase/migrations/ para todos los campos de private.cv_translation_revisions («source_kind profile/skill/education/academic/project», «language=en», «Revisión inmutable», texts JSON/invariant_fields/source_projection_hash/lock_version/autor/fechas), private.cv_translation_approvals, public.cv_approved_translations («source_kind/source_id/language PK») y private.cv_operations («operation_id PK»). Añadir PK/FKs/índices source_kind/source_id/hash/operaciones y RLS que solo exponga traducción de fuente publicada con hash curricular coincidente; evidencia/identidad revisor privadas.
- [ ] T009 Aplicar matriz de permisos en supabase/migrations/: backend_cv_read solo SELECT fuentes/selección/traducciones vigentes, sin borradores/mensajes/archivos/sesiones/escritura; backend_cv_admin dedicado bajo guard 002 para tablas 005 y lectura de fuentes públicas, sin modificar hechos de 001/003; anon/authenticated incluso JWT admin sin mutación ni revisiones privadas. Roles no propietarios/superusuarios/BYPASSRLS, sin service_role/vistas privilegiadas/SECURITY DEFINER, esquema privado no expuesto y contexto SQL local limpio.
- [ ] T010 Implementar lectura base en app/cv/repository.py: conexión limpia y nueva transacción READ ONLY REPEATABLE READ por petición, primer SELECT establece snapshot, todas las fuentes/selección por id+epoch/traducciones/hashes del mismo snapshot sin N+1; cerrar antes de render. Definir DTO inmutable/manifiesto CvFactsSnapshot/CvLanguageAvailability/CvDocumentModel/GeneratedCv en app/cv/service.py, facts_version común y document_version con idioma/aprobaciones/catálogo/layout/fuentes; renderer sin cliente DB ni sesión.

**Checkpoint**: Fuentes coherentes y selección confirmada pueden prepararse con operador aislado para probar descargas sin UI de selección todavía; no selección automática en operación.

## Phase 3: US1 — Descargar el CV en español (P1)

**Objetivo**: PDF textual español solo desde publicaciones con mínimos aprobados, sin depender de otro idioma o servicios externos.
**Prueba independiente**: Con fuente/selección sintéticas completas elegir español, descargar y comparar texto con manifiesto; mínimos ausentes bloquean ruta directa, borradores no aparecen.

### Pruebas primero

- [ ] T011 [P] [US1] Crear tests/unit/cv/test_spanish_availability.py para cada mínimo ausente, educación distinta de actividad, proyectos seleccionados o actividad pertinente, contacto autorizado y omisión opcionales; fuente fallida no es vacío. Verificar cero borradores/centinelas/empleo/porcentajes inventados y que 004/IA/GitHub/SMTP ausentes no bloquean descarga.
- [ ] T012 [P] [US1] Crear tests/contract/cv/test_spanish_http.py para GET /cv y /cv/es.pdf, idioma desconocido 400 sin fallback, mínimo ausente 409, fuente/render/glifo/recurso fallido 503 con reintento; revalidación por descarga, headers no-store/nosniff/attachment/Content-Language/longitud/X-CV-Source-Version, sin ETag/304/streaming temprano ni caché antigua.
- [ ] T013 [P] [US1] Crear tests/unit/cv/test_spanish_pdf.py para buffer reabrible y texto esperado/orden pypdf, nombre/tildes/URLs exactos, metadatos, fuentes incrustadas y ausencia de imágenes/JS/Launch/adjuntos/formularios/restricciones de copia; markup editorial escapado, glifo faltante provoca error, no sustitución silenciosa. Usar manifiesto de fixtures como oráculo independiente.

### Implementación

- [ ] T014 [US1] Implementar mínimos/manifiesto español en app/cv/service.py: «nombre publicado, correo público autorizado, perfil breve, >=1 educación publicada clasificada, >=1 habilidad verificada y >=1 proyecto seleccionado vigente o actividad académica pertinente publicada»; incluir todas las educaciones/habilidades/actividades publicadas y solo selección CV vigente ordenada, sin doble contar education. Sin mínimo devuelve motivo genérico; error fuente separado de incompleto, sin datos privados ni fallback.
- [ ] T015 [US1] Implementar app/cv/pdf.py ReportLab OSS Platypus con un frame/columna A4, márgenes 18 mm, DejaVu Sans local 11 pt/negrita, Paragraph/Spacer y paginación automática; identidad/contacto en cuerpo, luego perfil/educación/habilidades/proyectos/actividades, secciones vacías omitidas. Registrar familia una vez por proceso y comprobar glifos; XML escape editorial, URLs texto con wrapping sin guiones añadidos, títulos junto a primera línea y entradas largas divisibles, sin KeepTogether gigante/tablas/imágenes/cuerpo reducido para forzar página.
- [ ] T016 [US1] Completar generación/validación runtime en app/cv/pdf.py y app/cv/service.py: buffer privado íntegro <=8 MiB y generación acotada, reabrir con pypdf, páginas/metadatos/idioma e identidad/encabezados esperados antes de entregar; saturación/timeout/error 503 sin bytes ni archivo viejo. Metadata localizada sin paths/secretos/acciones PDF activas; renderer solo DTO aprobado, sin fetch/IA/DB ni persistencia PDF/caché/Storage.
- [ ] T017 [US1] Implementar app/cv/routes.py, app/templates/cv/index.html y app/templates/cv/unavailable.html para selector y español: nombres explícitos, enlaces solo disponibles y motivos independientes, ruta directa validada y filename Victor_Rafael_Arevalo_Sierra_CV_es.pdf; integrar blueprint en app/__init__.py y capacidad cv de 001 al menos un idioma disponible. Etiquetas/h1/skip/foco/error/reintento sin JS; ejecutar T011–T013 y registrar evidencia en specs/005-cv-bilingue/validation.md, sin afirmar bilingüismo completo.

**Checkpoint**: US1 es MVP técnico español con fixtures; aceptación de feature exige también inglés y actualización/selección de US3.

## Phase 4: US2 — Descargar el CV en inglés (P1)

**Objetivo**: Mismos hechos y orden con textos ingleses revisados para hashes vigentes; indisponibilidad independiente por idioma.
**Prueba independiente**: Con traducciones aprobadas del mismo facts_version descargar inglés y comparar hechos/encabezados/texto; faltar una necesaria bloquea solo inglés, C no seleccionado no bloquea.

### Pruebas primero

- [ ] T018 [P] [US2] Crear tests/unit/cv/test_translations.py para hash curricular vigente/obsoleto, todos los campos necesarios e invariantes explícitas, fuentes retiradas y proyectos no seleccionados, límites de expansión/estructura/markup y hechos inalterables; cambiar imagen/orden galería no invalida traducción, cambio curricular sí. Español completo sigue disponible cuando falta inglés, sin omitir elementos para evitar traducción.
- [ ] T019 [P] [US2] Crear tests/contract/cv/test_english_and_admin_http.py para /cv/en.pdf y rutas traducciones listar/editar/borrador/revisar/aprobar/operaciones de cv-http.md, guard/CSRF/origen y estados contractuales; review token ligado a sesión/revisión/digest/version, fuente cambiada 409, draft privado no habilita inglés y commit incierto sin replay. Probar nombres/idioma de archivo/documento y selector teclado/lector.
- [ ] T020 [P] [US2] Crear tests/integration/cv/test_translation_approval.py para aprobación con roles/DB reales, carreras source/revisión/sesión, idempotencia/recibos/rollback/auditoría y proyección RLS vigente por hash; anon/authenticated/JWT admin sin escritura/privados, reader sin fuentes retiradas/borradores/mensajes/archivos. Verificar DB tras intentos y contexto ausente/viejo; security skip explícito sin entorno.

### Implementación

- [ ] T021 [US2] Implementar app/cv/translations.py y app/cv/forms.py con allowlist de textos traducibles por tipo y campos invariantes revisados; «No puede sustituir IDs, fechas, contactos, URLs o lista de hechos», «títulos 400, resumen 4000, descripción académica 8000 y proyecto 20000» y demás límites hasta doble del campo fuente sin truncar; rechazar estructuras desconocidas/marcadores/atributos/markup activos. Nombres propios/técnicos no se declaran invariantes por heurística; equivalencia semántica requiere revisión humana.
- [ ] T022 [US2] Implementar guardar/revisar/aprobar traducción en app/cv/repository.py y app/cv/translations.py con revisiones inmutables/expected_version/hash fuente autoritativo, confirmación y review_token exactos ligados a sesión de 10 min conforme a patrón 002; revalidar fuente/revisión/digest en transacción y materializar solo proyección aprobada con auditoría/recibo. Mismo operation_id/actor/cuerpo idempotente, otro cuerpo 409; no publicar fuente española ni reejecutar tras login/incertidumbre.
- [ ] T023 [US2] Implementar catálogo versionado es/en de encabezados/fechas/idioma en app/cv/translations.py y composición inglesa en app/cv/service.py con mismo conjunto/orden/facts_version de español; inglés solo con textos o invariant_fields aprobados/hash vigentes de cada elemento incluido. Sin traducción en descarga/fallback/archivo viejo; un idioma incompleto no bloquea otro, nombres/direcciones legítimos conservados y fechas localizadas sin inventar precisión.
- [ ] T024 [US2] Implementar rutas traducciones/operaciones en app/cv/admin_routes.py y app/templates/cv/admin/translation_edit.html, app/templates/cv/admin/translation_review.html con listado accesible de estados y comparación fuente/traducción, confirmación explícita de hechos y errores enlazados; ampliar app/cv/routes.py y selector para inglés con filename Victor_Rafael_Arevalo_Sierra_CV_en.pdf y metadatos/Content-Language en. Ejecutar T018–T020 y regresión español, registrar specs/005-cv-bilingue/validation.md y revisión semántica pendiente de Victor si aún no realizada.

**Checkpoint**: Ambos idiomas operan desde hechos controlados y aprobaciones vigentes, sin listas/orden divergentes ni traducciones improvisadas.

## Phase 5: US3 — Obtener un documento actualizado y legible (P1)

**Objetivo**: Selección curricular explícita y snapshot vigente coherente, con integridad documental demostrada mono/multipágina.
**Prueba independiente**: Confirmar B,A sin modificar galería, publicar corrección durante render, retirar/republicar y comparar versiones/selección/texto completo de ambos idiomas y todas las páginas.

### Pruebas primero

- [ ] T025 [P] [US3] Crear tests/contract/cv/test_project_selection.py para GET/POST selección con confirmación incluso vacía, expected_selection_version e IDs/epochs/versiones, duplicados/posiciones/proyectos no vigentes 422/409; ambos idiomas comparten orden independiente de galería, retiro excluye sin sustitución y republicación no incluye epoch viejo, guard vigente/CSRF/caducidad/recibos sin replay.
- [ ] T026 [P] [US3] Crear tests/integration/cv/test_snapshot_concurrency.py para publicación antes/durante/después del primer SELECT, conexiones pool limpias, selección/traducción/fuente coherentes y primera petición posterior actualizada; cambios curriculares invalidan inglés, fotos/orden galería no; retiro/eliminación/mínimos/epochs y lectores sin privilegios. Verificar ausencia de consulta DB durante render y ningún PDF/snapshot reutilizado entre peticiones.
- [ ] T027 [P] [US3] Crear tests/integration/cv/test_pdf_visual.py con marca pdf_visual para fixtures de una/varias páginas es/en, manifiestos esperados y extracción pypdf más pdftotext; comparar todos los bloques/orden/caracteres exactos normalizando solo whitespace de layout y recomponiendo URLs partidas sin quitar tildes/puntuación. Renderizar todas las páginas Poppler, comprobar geometría/fuentes/metadata y producir output/pdf/cv-fixture-es.pdf, output/pdf/cv-fixture-en.pdf y PNG/texto en tmp/pdfs; revisión visual humana explícita, no PASS automático por generar PNG.

### Implementación y verificación

- [ ] T028 [US3] Implementar selección confirmada en app/cv/repository.py y app/cv/forms.py: comparar expected_selection_version y conjunto/versiones de publicaciones mostradas, IDs/epochs vigentes sin duplicados y posiciones únicas, lista vacía válida; filas/version/recibo/auditoría atómicos bajo guard 002, sin alterar payload/orden/visibilidad de galería. Resolver elegibilidad por id+epoch y no sustituir retirados; corrección mismo ciclo conserva inclusión y republicación exige inclusión nueva.
- [ ] T029 [US3] Implementar GET/POST /admin/cv/proyectos en app/cv/admin_routes.py y app/templates/cv/admin/projects.html con selección/posiciones numéricas, distinción orden CV/galería, confirmación/errores accesibles y 303 solo tras commit; conflictos 409 recargan sin sobrescritura/publicación de borradores. Recibos propios sin textos resuelven incertidumbre y reautenticar nunca repite operación.
- [ ] T030 [US3] Completar manifiesto/hash y validaciones de app/cv/repository.py y app/cv/service.py para hechos/IDs/tipos/selección/orden/contactos aprobados, document_version con traducciones/catálogo/layout/fuentes y DTO inmutable; ejecutar T025–T026 con DB real y verificar extensiones de app/admin/service.py y app/projects/repository.py de T005/T006 no rompen 001–003. Log de descarga solo idioma/versión pública/duración/código, sin payload privado.
- [ ] T031 [US3] Ejecutar T027 y revisar todas las páginas PNG de mono/multipágina es/en, copiar/seleccionar/leer texto y comparar manifiestos del mismo facts_version; corregir app/cv/pdf.py hasta cero recortes/superposición/glifos perdidos, encabezados huérfanos o URLs alteradas. Registrar specs/005-cv-bilingue/pdf-review.md con versiones/fuentes/evidencia y revisión semántica de Victor, sin prometer afiliación Harvard/Oxford, PDF/UA ni ATS universal.
- [ ] T032 [US3] Medir >=100 descargas por idioma con contenido representativo y conexión normal en specs/005-cv-bilingue/performance.md: >=95 % completas <=10 s, percentiles/memoria/tamaño/consultas, saturación/timeout y contenido largo por separado. Ajustar app/config.py y app/cv/pdf.py sin truncar/reducir legibilidad ni entregar bytes parciales/obsoletos; si se aísla CPU con subproceso local acotado limpiar buffers/temporales, sin cola/copia persistente.
- [ ] T033 [US3] Ejecutar regresión de todas las suites CV y revisar con teclado/lector selector/descarga/409/503/reintento/selección/aprobación; completar specs/005-cv-bilingue/accessibility.md con contraste, foco/labels/errores, 200 %/320 px/espaciado/orientación/movimiento reducido/sin JS y correcciones en app/static/css/site.css/plantillas CV. No deducir WCAG web de extracción PDF ni PDF/UA de una columna.

**Checkpoint**: Tres historias P1 completas solo tras ambas variantes, permisos reales, selección/coherencia, extracción/QA visual y métricas acreditadas.

## Phase 6: Polish — evidencia y aceptación

- [ ] T034 [P] Actualizar specs/005-cv-bilingue/quickstart.md con comandos PowerShell comprobados, HTTPS/origen/variables TEST_* y roles, CLI/migraciones/advisors descubiertos con --help, fuentes/licencias/Poppler y rutas QA; limpieza solo proyecto aislado verificado y artefactos sintéticos. Sin credenciales, contenido real ni activación de 004.
- [ ] T035 Ejecutar tests/unit/cv, tests/contract/cv, tests/integration/cv -m security y -m pdf_visual más regresiones 001–003; consolidar specs/005-cv-bilingue/validation.md con commit/lock/licencias/roles/grants/RLS, manifiestos/facts_version, contenido/idioma/texto/estructura/PNGs todas las páginas, rendimiento y trazabilidad FR-001–013/SC-001–009. Falta de Supabase/fuentes/Poppler/revisión manual es aceptación incompleta, no PASS por skip.
- [ ] T036 Completar revisión automática gratuita axe y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables en specs/005-cv-bilingue/accessibility.md, justificar no aplicables y cerrar defectos; revisar specs/005-cv-bilingue/pdf-review.md y specs/005-cv-bilingue/validation.md con evidencia semántica de ambos idiomas por Victor y revisión específica de permisos/CV. No aceptar feature con una sola variante o datos inventados; no desplegar/publicar contenido real en esta tarea.

## Dependencies & Execution Order

```text
Publicaciones 001/003 + seguridad 002 disponibles
  → Setup T001–T004 → Fundamentos T005–T010
    → US1 T011–T017 (P1, MVP español con fixtures)
      → US2 T018–T024 (P1, inglés aprobado)
        → US3 T025–T033 (P1, selección/coherencia/QA)
          → Polish T034–T036 → aceptación bilingüe
```

T002 precede T003/T004. Fundamentos secuenciales T005→T006→T007→T008→T009→T010; no fuentes privadas al renderer. T011–T013 se escriben antes de T014→T015→T016→T017. T018–T020 antes de T021→T022→T023→T024. T025–T027 antes de T028→T029→T030→T031→T032→T033. Pruebas pueden comenzar con contratos/fixtures y fallar hasta implementación; seguridad/visual requieren dependencias reales y revisiones explícitas.

US1 usa selección y fuentes aprobadas sintéticas sin editor CV ni inglés. US2 usa mismas publicaciones/manifiesto y traducciones aisladas, sin selección UI de US3; no duplicar hechos españoles. US3 prueba cada transición con fixtures independientes pero integra sobre los servicios previos. repository.py/service.py/routes.py/admin_routes.py se editan secuencialmente; independencia de prueba no habilita escrituras simultáneas sobre mismos archivos/DB. 004 no es dependencia y RET-001 permanece bloqueado.

## Parallel Examples

- Setup: T003 (configuración/env) junto a T004 (fixtures/tests) después de T002.
- US1: T011 (mínimos), T012 (HTTP) y T013 (PDF) preparan suites distintas tras fundamentos, con manifiesto/DTO acordados.
- US2: T018 (traducción), T019 (HTTP) y T020 (DB/roles) pueden escribirse juntas tras US1; ejecución real espera esquema y aplicación.
- US3: T025 (selección HTTP), T026 (snapshot DB) y T027 (QA PDF) preparan suites distintas tras US2; fixtures por caso/worker y sin concurrencia accidental sobre selección compartida.
- Cierre: T034 puede redactarse desde resultados existentes; T035/T036 consolidan evidencias compartidas secuencialmente. No paralelizar generaciones de QA sobre mismos filenames.

## Implementation Strategy

1. Reutilizar 001–003 y consolidar clasificación educativa, epochs y hashes sin inferir contenido personal ni publicar nuevas fuentes.
2. MVP técnico US1: descarga española con mínimos y texto íntegro; validar ruta/error y documento con fixtures. Es demostración parcial.
3. US2 incorpora inglés revisado/hash vigente sin fallback; revisar equivalencia de hechos del mismo facts_version y disponibilidad independiente.
4. US3 completa selección independiente, coherencia concurrente, presentación/Unicode y QA visual exhaustiva; medir descargas completas, no solo render local.
5. MVP aceptable de esta feature requiere las tres historias P1 y ambas variantes completas con evidencia real de permisos, semántica, extracción, todas las páginas, accesibilidad web y SC-008. Pendientes de Victor se registran, no se completan por inferencia.

## Trazabilidad

US1: FR-001/003/005/006/007/008/009/010/011, SC-002/003/007 y base SC-008. US2: FR-001/004/005/009, SC-001/003/005/007. US3: FR-002/006/009/010/012/013, SC-001/002/004/006/007/008/009. T035/T036 consolidan todos los FR/SC y QA bilingüe.

Las tareas citan restricciones de campos y reglas del modelo; los restantes campos completos se incorporan según sus tablas. Migraciones se nombran por CLI y su ruta real se registra al crearlas. Documento iniciado antes de publicación puede acabar con snapshot anterior coherente; no se actualizan PDFs ya descargados por terceros.
