# Tasks: Perfil público y experiencia académica

**Input**: `specs/001-perfil-publico/`: plan.md, spec.md, research.md, data-model.md, contracts/public-data.md, contracts/public-page.md y quickstart.md; constitución 1.0.0.
**Organización**: Setup → fundamentos → US1 (P1) → US3 (P1) → US2 (P2) → validación transversal. Los identificadores US conservan su correspondencia con spec.md.
**Pruebas**: Pytest solicitado por spec y constitución; escribir las pruebas de cada historia primero y comprobar su fallo antes de implementar. RLS requiere un entorno real aislado; mocks y skips no acreditan permisos.
**Formato**: `- [ ] Tnnn [P?] [USn?] descripción con ruta`. Rutas relativas a la raíz del repositorio. [P] permite trabajo simultáneo únicamente tras satisfacer las dependencias indicadas y sin editar archivos compartidos.
**Alcance**: Generación de tareas; no acredita implementación ni conformidad. Sin panel, publicación automática, proyectos, formulario, generación de CV, GitHub o IA de 002–007. Fixtures sintéticos exclusivamente de prueba, nunca fallback público.

## Phase 1: Setup — infraestructura compartida

**Propósito**: Preparar el monolito Flask/Jinja y herramientas locales gratuitas.

- [X] T001 Inicializar Python 3.12, Flask 3.1, Jinja 3.1, supabase-py 2 y Pytest en pyproject.toml y requirements.lock; fijar versiones exactas y transitivas compatibles, registrar licencias, gratuidad y alternativa ante indisponibilidad en specs/001-perfil-publico/dependencies.md.
- [X] T002 [P] Preparar .env.example sin valores reales y .gitignore para excluir .env, tokens, .venv, cachés y evidencias sensibles; documentar únicamente nombres de variables de aplicación y pruebas.
- [X] T003 [P] Crear app/__init__.py con factory create_app y puntos de inyección del repositorio/reloj; preparar app/public/__init__.py y tests/conftest.py con cliente Flask y fixtures sintéticos sin red por defecto.
- [X] T004 Inicializar configuración CLI local en supabase/config.toml y documentar en specs/001-perfil-publico/quickstart.md creación/aplicación de migraciones en entorno aislado gratuito, provisión/limpieza por operador autorizado y prohibición de usar producción.

## Phase 2: Foundational — prerrequisitos bloqueantes

**Propósito**: Contratos internos, configuración segura y superficie de datos mínima; completar antes de las historias.

- [X] T005 [P] Implementar en app/config.py SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY y plazo global configurable de 6 segundos; rechazar credenciales privilegiadas para lectura pública, permitir renderizar indisponibilidad con configuración ausente/inválida y excluir secretos/payloads de registros y errores.
- [X] T006 [P] Definir en app/public/service.py ResourceResult con «state ready/empty/unavailable; data solo para ready; error interno categorizado sin payload privado», PublicPage y Destination con «key projects/contact/cv; available/unavailable; URL solo cuando disponible, derivada del router y configuración del servidor»; una excepción nunca será empty.
- [X] T007 [P] Crear mediante CLI supabase/migrations/202610270001_public_profiles.sql con public_profiles: «id UUID PK; full_name y degree texto requeridos; summary texto nullable; public_contacts JSON array; published_at timestamptz nullable» y «Perfil único mediante restricción singleton; identidad confirmada; resumen pendiente se omite; contactos solo autorizados.»; aplicar «Texto plano con trim; rechazar cadenas vacías y marcadores pendientes al publicar.» y «nombre/carrera/actividad/institución 200 caracteres; resumen 2000; descripción 4000; valor de contacto 2048; máximo 10 contactos» a los campos correspondientes.
- [X] T008 Ampliar supabase/migrations/202610270001_public_profiles.sql con RLS y grants SELECT explícitos anon/authenticated solo para published_at no nulo; impedir INSERT/UPDATE/DELETE, sin service_role, vistas ni SECURITY DEFINER; mantener borradores/contactos privados fuera de tablas públicas y sin USAGE/SELECT de estos roles en esquema privado, sin implementar edición de 002.
- [ ] T009 Crear en app/public/repository.py adaptador inyectable y presupuesto monotónico compartido entre operaciones, timeout limitado al tiempo restante, sin llamadas tras agotarlo ni reintentos; proyecciones explícitas sin select=*, filtros published_at/profile_id y clasificación sanitizada de timeout, 429, pausa, HTTP y estructura inválida como unavailable.

**Checkpoint**: Factory y configuración toleran ausencia de Supabase; contratos permiten aislar historias; superficie pública solo contiene instantáneas aprobadas.

## Phase 3: US1 — Conocer el perfil de Victor (P1)

**Objetivo**: Identidad aprobada y navegación honesta, sin requerir otras features.
**Prueba independiente**: Con fixtures del perfil y endpoints controlados, GET / presenta identidad exacta, omite pendientes y privados; perfil vacío responde 200 y fallo 503; destinos solo enlazan cuando están registrados y habilitados.

### Pruebas antes de implementación

- [X] T010 [P] [US1] Crear tests/unit/test_profile_repository.py para get_profile con cero/uno/duplicados, estructura inválida, configuración ausente, timeout, 429 y HTTP; comprobar columnas explícitas, filtro publicado, ausencia de escritura/reintentos y presupuesto compartido.
- [X] T011 [P] [US1] Crear tests/contract/test_public_profile.py para identidad/carrera/resumen/contactos aprobados, omisión de pendientes y centinelas privados, escape editorial y ausencia de fallback; verificar HTTP 200/503, mensajes exactos del contrato, UTF-8 y Cache-Control no-store en todos los estados.
- [X] T012 [P] [US1] Crear tests/unit/test_destinations.py con matriz endpoint registrado/capacidad habilitada para projects/contact/cv; usar endpoints de prueba para verificar destino anunciado y CV con variante aprobada; indisponibles sin href, tabindex ni botón falso y sin consultas externas por visitante.
- [ ] T013 [P] [US1] Crear tests/integration/test_profile_rls.py y tests/integration/fixtures/profile.sql con instantánea, retirada, borrador y contacto privado centinela; probar anon y autenticado no administrador mediante select=*, UUID y esquema privado, mutaciones y comprobación posterior de DB; edición privada no cambia instantánea. Usar variables TEST_* de quickstart, marca rls y skip explícito sin entorno; provisión/limpieza externa autorizada sin secretos en archivos.

### Implementación

- [X] T014 [US1] Implementar get_profile en app/public/repository.py: cero = empty, uno validado = ready, duplicado/inválido = unavailable; validar «public_contacts: objetos {kind, label, value}; kind email/https/phone, etiqueta comprensible requerida», «Validar correo, URL HTTPS o teléfono; construir mailto/tel en servidor. No aceptar HTML, javascript ni data. Ausencia = array vacío.» y límites de T007; datos privados/evidencia de aprobación nunca forman parte del resultado.
- [X] T015 [US1] Implementar composición del perfil y destinos en app/public/service.py: sin perfil publicado no consultar ni mostrar hijos; fallo del perfil conserva unavailable; resolver URL por router únicamente con endpoint y capacidad disponible, por defecto los tres destinos deshabilitados y CV condicionado a variante aprobada.
- [X] T016 [US1] Implementar GET / en app/public/routes.py y registrar blueprint en app/__init__.py; devolver text/html UTF-8 y no-store, 200 con perfil ready/empty y 503 con unavailable, sin SDK navegador ni API JSON propia.
- [X] T017 [US1] Crear app/templates/base.html y app/templates/public/index.html con lang=es, título comprensible, un h1 y regiones header/nav/main/footer; perfil vacío «Perfil aún no disponible» y fallo «No podemos mostrar el perfil en este momento. Inténtalo más tarde.»; mostrar solo campos aprobados, escape Jinja sin safe y destinos indisponibles como etiqueta y «No disponible por ahora».
- [X] T018 [US1] Ejecutar tests/unit/test_profile_repository.py, tests/unit/test_destinations.py, tests/contract/test_public_profile.py y tests/integration/test_profile_rls.py; registrar resultados y limitaciones de entorno sanitizados en specs/001-perfil-publico/validation.md, sin declarar RLS aprobado si se omitió.

**Checkpoint**: Perfil demostrable con fixtures y destinos controlados. Antes de aceptar MVP completar también US3 y verificaciones RLS reales.

## Phase 4: US3 — Navegar con distintas capacidades y dispositivos (P1)

**Objetivo**: Acceso equivalente mediante teclado, lector de pantalla y móvil desde el primer incremento.
**Prueba independiente**: Renderizar estados completos, parciales, vacíos y fallidos con repositorio inyectado; recorrer teclado/lector, texto al 200 %, ancho 320 px, ambas orientaciones y movimiento reducido sin pérdida.

### Pruebas antes de implementación

- [X] T019 [P] [US3] Crear tests/contract/test_accessible_page.py para idioma, título, h1 único, jerarquía de encabezados, regiones, skip link a contenido, nombres de enlaces y anclas existentes; parametrizar estados con fixtures y mensajes iniciales comprensibles sin depender de aria-live ni JavaScript.
- [X] T020 [P] [US3] Preparar specs/001-perfil-publico/accessibility.md con matriz de todos los criterios WCAG 2.1 A/AA, escenarios, evidencia, resultado y justificación de no aplicables; incluir procedimientos gratuitos axe, teclado y NVDA, sin presentar verificaciones pendientes como aprobadas.

### Implementación

- [X] T021 [US3] Ajustar app/templates/base.html y app/templates/public/index.html para skip link a main#contenido, ids perfil/conocimientos/experiencia-academica solo cuando procedan, encabezados ordenados y estados por título/encabezado/texto; eliminar controles solo hover y asegurar navegación completa sin JS.
- [X] T022 [US3] Implementar app/static/css/site.css y enlazarlo desde app/templates/base.html con fuentes de sistema, foco visible, orden natural, layout flexible y wrapping de texto/URL, sin alturas que recorten; garantizar texto 200 %, 320 px y orientación flexible, contrastes 4.5:1 normal/3:1 grande/3:1 no textual necesario, señales adicionales al color y prefers-reduced-motion.
- [ ] T023 [US3] Ejecutar tests/contract/test_accessible_page.py y auditoría axe gratuita más revisión manual teclado/NVDA, texto 200 %, 320 px, móvil/escritorio, orientaciones, contrastes, espaciado y movimiento reducido/sin JS; registrar evidencia y corregir defectos en app/templates/base.html, app/templates/public/index.html y app/static/css/site.css; completar specs/001-perfil-publico/accessibility.md para el incremento P1.

**Checkpoint**: US1 + US3 constituyen MVP funcional accesible; contenido real sigue sujeto a aprobación de Victor.

## Phase 5: US2 — Consultar conocimientos y formación (P2)

**Objetivo**: Capacidades verificadas y actividad académica aprobada, diferenciadas de empleo.
**Prueba independiente**: Con perfil controlado y una habilidad/actividad publicadas, comprobar textos, orden y fechas; luego vaciar/fallar cada colección y verificar ocultación o indisponibilidad sin afectar recursos válidos.

### Pruebas antes de implementación

- [X] T024 [P] [US2] Crear tests/unit/test_collections_repository.py para orden display_order/id, páginas de 100 y más de 100 registros hasta última página, vacío confirmado, fallos en páginas posteriores y agotamiento global de 6 s sin truncar ni reintentar; validar recursos independientes y máximo tres operaciones lógicas por petición, diferenciando páginas HTTP.
- [X] T025 [P] [US2] Crear tests/contract/test_public_collections.py para todas las combinaciones ready/empty/unavailable de ambas colecciones, perfil ausente/fallido sin hijos, secciones/anclas omitidas solo en empty y error parcial accesible HTTP 200; fechas pendientes/aisladas/ongoing, orden, escape y ausencia de porcentajes, empleo o contenido ficticio.
- [ ] T026 [P] [US2] Crear tests/integration/test_collections_rls.py y tests/integration/fixtures/collections.sql para anon y autenticado no administrador: publicaciones, retiradas y borradores, select=*, UUID y joins, escritura sin efectos y retirada del padre que oculta hijos en la misma transacción; verificar DB tras mutaciones con operador de pruebas autorizado y registrar skip como seguridad incompleta.

### Implementación

- [X] T027 [US2] Crear mediante CLI supabase/migrations/202610270002_public_collections.sql con public_skills: «id UUID PK; profile_id FK; name requerido; description nullable; display_order entero; published_at nullable» y «Capacidades verificadas, sin porcentajes ni niveles inferidos.»; public_academic_experiences: «id UUID PK; profile_id FK; activity requerida; institution nullable; start_date/end_date date nullable; ongoing boolean; description nullable; display_order entero; published_at nullable» y «end_date >= start_date si ambas existen; ongoing prohíbe end_date. Nunca representa empleo.»; aplicar trim/límites citados en T007, FK con borrado restringido e índices FK/orden.
- [X] T028 [US2] Añadir a supabase/migrations/202610270002_public_collections.sql RLS y grants SELECT mínimos con published_at no nulo y padre publicado, sin escritura anon/authenticated; validar invisibilidad de hijos al retirar padre sin implementar flujo editorial administrativo.
- [X] T029 [US2] Implementar list_skills(profile_id) y list_academic_experiences(profile_id) en app/public/repository.py con validación de campos de T027, proyección explícita, filtros, «Orden de listas: display_order ASC, id ASC.», paginación de 100 completa y plazo compartido; fallo/invalidez produce unavailable sin entregar lista parcial.
- [X] T030 [US2] Ampliar app/public/service.py con resultados independientes de ambas colecciones: empty oculta sección/enlace, unavailable conserva encabezado/explicación/ancla y demás contenido válido; aplicar «Fechas pendientes se omiten sin completar día/mes por inferencia. Si solo se conoce año o mes, conservar null hasta ampliar explícitamente el modelo.» y «Fechas aisladas se etiquetan como inicial/final; «Actualidad» solo si ongoing aprobado.».
- [X] T031 [US2] Integrar conocimientos y experiencia académica en app/templates/public/index.html con ids contractuales, descripciones/fechas aprobadas y orden estable; sin sección laboral ni niveles inferidos, sin mensaje vacío, marcadores o enlaces a secciones omitidas y con error parcial accesible.
- [X] T032 [US2] Ejecutar tests/unit/test_collections_repository.py, tests/contract/test_public_collections.py y tests/integration/test_collections_rls.py y repetir regresión de tests/contract/test_accessible_page.py sobre las secciones finales; actualizar specs/001-perfil-publico/validation.md y specs/001-perfil-publico/accessibility.md con evidencia, corrigiendo defectos antes de cerrar historia.

**Checkpoint**: Las tres historias cubren FR-001–008 y SC-001–004; aceptación aún requiere evidencia transversal completa.

## Phase 6: Polish — verificación transversal y entrega

- [X] T033 [P] Actualizar specs/001-perfil-publico/quickstart.md con comandos PowerShell realmente implementados, variables sin valores, aplicación de migraciones, fixtures aislados, Pytest, pruebas RLS, auditoría gratuita, limpieza y límites; retirar afirmaciones de que aún no existe aplicación solo después de implementarla.
- [ ] T034 Ejecutar suites tests/unit, tests/contract y tests/integration -m rls conforme a specs/001-perfil-publico/quickstart.md; completar specs/001-perfil-publico/validation.md con commit, versiones, entorno y trazabilidad FR/SC, pruebas de fuga en HTML/logs/DB, no-store tras retirada, cuotas/timeouts, paginación y destinos; no aceptar si falta evidencia RLS real o hay fallos abiertos.
- [ ] T035 Repetir revisión visual y automática/manual de todos los estados finales y todos los criterios WCAG aplicables en specs/001-perfil-publico/accessibility.md; cerrar defectos de app/templates/base.html, app/templates/public/index.html y app/static/css/site.css y documentar pendientes de aprobación de contenido real antes de activación en specs/001-perfil-publico/validation.md.

## Dependencies & Execution Order

```text
Setup T001–T004
  → Fundamentos T005–T009
    → US1 T010–T018 (P1)
      → US3 T019–T023 (P1) → MVP accesible
        → US2 T024–T032 (P2)
          → Polish T033–T035 → aceptación completa
```

T002/T003 parten tras T001; T004 requiere herramientas locales preparadas. T005/T006/T007 son independientes tras Setup; T008 depende de T007 y T009 de T005/T006. Pruebas de cada historia se escriben primero; fixtures de T003 están disponibles para todas. T014–T017 son secuenciales; T018 exige implementación y suite. T021/T022 preceden T023. T027 precede T028; T029 requiere migraciones y adaptador; T030 requiere T029 y T031 requiere T030; T032 integra y valida.

US1 se verifica sin US2/003–007. US3 usa fixtures para colecciones antes de US2; su integración visual requiere US1 y se revalida tras US2. US2 usa perfil inyectado para pruebas aisladas; su integración reutiliza US1 y US3. La independencia de pruebas no significa ausencia de dependencias de integración. Los archivos compartidos repository.py, service.py e index.html se modifican secuencialmente entre historias.

## Parallel Examples

- Setup: T002 (.env.example/.gitignore) y T003 (factory/fixtures) tras T001.
- Fundamentos: T005 (config), T006 (resultados) y T007 (esquema) tras Setup.
- US1: T010, T011, T012 y T013 escriben suites distintas con fixtures acordados; luego implementación secuencial. RLS se ejecuta tras aplicar migración y preparar entorno.
- US3: T019 (contrato HTML) y T020 (matriz manual) tras US1; implementar y validar después.
- US2: T024, T025 y T026 escriben suites distintas tras US3; migraciones y aplicación avanzan después sin modificar archivos compartidos simultáneamente.
- Polish: T033 puede prepararse con los resultados existentes; T034/T035 esperan todas las historias y consolidan evidencia en orden, sin escrituras simultáneas a documentos compartidos.

## Implementation Strategy

1. Completar Setup y fundamentos sin publicar contenido real ni aprovisionar servicios de pago.
2. Implementar US1 con pruebas y datos sintéticos; demostrar perfil, omisiones, indisponibilidad y destinos mediante endpoints controlados.
3. Completar US3 para MVP aceptable: perfil accesible, privacidad y RLS real comprobados. US1 sola es demostración parcial porque US3 también tiene prioridad P1.
4. Añadir US2 y repetir regresiones de perfil, permisos y accesibilidad; conservar funcionalidad sin JavaScript.
5. Completar evidencia de quickstart y matriz WCAG; skips de RLS o revisión manual pendiente bloquean aceptación, sin afirmar PASS. Activación con información real requiere aprobación de Victor; implementación de 002–007 queda fuera.

## Resumen y trazabilidad

35 tareas: Setup 4, fundamentos 5, US1 9, US3 5, US2 9, cierre 3. Hay 15 tareas [P]; los grupos concretos están descritos arriba. US1 cubre FR-001/003/004/007 y SC-001/004; US3 FR-005/006/008 y SC-002/003; US2 FR-002/003/005/007 y SC-001/004. T034/T035 consolidan evidencia de todos los FR/SC.

Los límites de texto se repiten literalmente desde data-model.md; «name requerido» no tiene máximo específico definido allí, por lo que no se inventa uno. No se agrega un flujo de publicación ni se resuelven pendientes personales por inferencia. Aprobación humana de capacidades/contactos se representa mediante instantáneas preparadas por operador autorizado en pruebas.


## Estado de ejecución — 2026-10-27

29/35 tareas marcadas por trabajo ejecutado. Las dos excepciones del checklist se conservaron con autorización explícita de Victor. Los nombres efectivos de migración son 20261028003054_public_profiles.sql y 20261028003106_public_collections.sql, generados por CLI 2.122.0, equivalentes al orden previsto.

- T009 parcialmente implementada: proyecciones, paginación, presupuesto monotónico, timeout restante y reintentos desactivados. Queda validar un límite duro global bajo DNS/respuestas lentas reales; no se afirma corte exacto a 6 s.
- T013/T026: suites SQL reales y fixtures implementados y ejecutados con roles representativos; falta completar acceso por Data API/JWT real Supabase, select=*, UUID/joins y comprobación posterior por esa vía.
- T023/T035: Chrome/axe y revisión visual realizadas; queda recorrido humano completo y NVDA, y cierre de matriz WCAG. No se declara conformidad.
- T034: suite local consolidada y trazabilidad documentadas; aceptación abierta por los puntos anteriores.

T018/T032 registran ejecución y límites, no aceptación de historias sin las verificaciones pendientes. T020 prepara una matriz completa; sus resultados parciales permanecen visibles. Las pruebas se escribieron antes del código correspondiente, pero falta evidencia roja independiente para cada historia; ver validation.md. No se publicaron datos reales ni se modificó producción. No hay hooks registrados en .specify/extensions.yml (archivo ausente).
