# Feature Specification: Acceso administrativo y gestión del contenido

**Feature Branch**: `002-administracion` (referencia propuesta; no se ha creado una rama, la actual es `main`).

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Proteger un panel administrativo para que Victor gestione el contenido del portafolio mediante autenticación y autorización verificadas."

## Clarifications

### Session 2026-10-27

- Q: ¿Qué contenido debe actualizarse al confirmar una publicación en el panel? → A: Publicar un elemento por separado: el perfil completo, un conocimiento o una experiencia académica; los demás borradores permanecen sin publicar.
- Q: ¿Cómo debe poder Victor retirar de la vista pública un conocimiento o una experiencia académica ya publicados? → A: Retirar la publicación del sitio y de la fuente del CV, conservando el contenido como borrador.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Acceder y cerrar sesión (Priority: P1)

Como Victor quiero identificarme y cerrar sesión para acceder de forma privada a la administración.

**Why this priority**: Toda operación administrativa depende de un acceso seguro.

**Independent Test**: Con una identidad aprobada y un panel mínimo, iniciar sesión, acceder, cerrar sesión y comprobar que el acceso anterior se rechaza.

**Acceptance Scenarios**:

1. **Given** mi identidad está autorizada, **When** inicio sesión con correo y contraseña válidos, **Then** accedo al panel.
2. **Given** las credenciales son incorrectas, **When** intento acceder, **Then** se rechaza el acceso sin confirmar si el correo existe.
3. **Given** cerré sesión o esta caducó, **When** intento reutilizarla, **Then** se deniega cualquier operación administrativa y se solicita autenticación.
4. **Given** no puede verificarse la identidad, **When** intento acceder, **Then** se informa del fallo sin conceder acceso alternativo.
5. **Given** una identidad acumula cinco intentos fallidos consecutivos en quince minutos, **When** se intenta acceder durante los quince minutos siguientes al quinto fallo, **Then** se limita temporalmente el acceso y se indica cuándo reintentar sin revelar si existe la cuenta.

---

### User Story 2 - Gestionar borradores y publicaciones (Priority: P1)

Como Victor quiero editar perfil, conocimientos y experiencia académica, guardar borradores y publicar información revisada para controlar lo que aparece en el sitio y CV.

**Why this priority**: Permite mantener el contenido actualizado, aprobado y coherente.

**Independent Test**: Con una sesión administrativa y contenido de prueba, guardar un borrador, comprobar la versión pública, publicar y contrastar la fuente aprobada disponible para el sitio y CV.

**Acceptance Scenarios**:

1. **Given** existe contenido publicado, **When** guardo cambios como borrador y vuelvo a abrir la edición, **Then** encuentro los cambios guardados y el sitio y CV conservan el contenido anterior.
2. **Given** revisé un borrador válido de un elemento (el perfil completo, un conocimiento o una experiencia académica), **When** confirmo explícitamente publicar esa versión, **Then** únicamente esa versión del elemento queda disponible como fuente aprobada para el sitio y CV, sin modificar las publicaciones de otros elementos ni publicar sus borradores.
3. **Given** falta información obligatoria o hay afirmaciones sin verificar, **When** intento publicar, **Then** se impide la publicación y se identifican los problemas; se permite conservar un borrador incompleto si su almacenamiento es seguro.
4. **Given** dos ediciones parten de la misma versión, **When** una se guarda y luego se intenta guardar la otra, **Then** se advierte el conflicto sin sobrescribir silenciosamente la primera.
5. **Given** mi sesión caduca durante la edición, **When** intento guardar, **Then** se indica que no se guardó y se permite reautenticar sin publicar automáticamente ni repetir la modificación sin una nueva acción explícita.
6. **Given** falla el almacenamiento, **When** intento guardar o publicar, **Then** se informa del error sin confirmar éxito ni sustituir la última publicación íntegra.
7. **Given** un conocimiento o una experiencia académica están publicados, **When** confirmo retirar su publicación, **Then** el elemento deja de estar disponible en el sitio y en la fuente del CV, se conserva como borrador y los demás elementos permanecen sin cambios.
8. **Given** retiro un elemento que tiene cambios en borrador, **When** se confirma la persistencia de la retirada, **Then** se conservan tanto los cambios del borrador como el contenido de la versión retirada, sin sobrescribirlos ni publicarlos; una nueva publicación requiere revisión y confirmación explícitas.

---

### User Story 3 - Rechazar accesos no autorizados (Priority: P1)

Como propietario quiero impedir que visitantes o personas identificadas sin permiso modifiquen contenido o lean mensajes privados.

**Why this priority**: Identificarse no concede por sí solo permisos administrativos.

**Independent Test**: Evaluar lecturas privadas y modificaciones con visitante, identidad sin permiso e identidad administrativa, incluyendo solicitudes directas fuera del panel.

**Acceptance Scenarios**:

1. **Given** soy visitante o una persona identificada sin permiso, **When** intento leer mensajes, borradores o archivos privados, o modificar contenido, **Then** se deniega la acción sin revelar datos ni modificar contenido.
2. **Given** intento atribuirme permisos o registrar públicamente un administrador, **When** envío la solicitud, **Then** no obtengo permisos ni acceso privado.
3. **Given** tengo una sesión vigente pero se retiró mi autorización, **When** realizo otra operación administrativa, **Then** se deniega.
4. **Given** soy visitante, **When** consulto contenido o imágenes, **Then** solo obtengo elementos publicados y autorizados para difusión pública.
5. **Given** una modificación es inducida desde un origen no autorizado o contiene instrucciones activas maliciosas, **When** se procesa o muestra el contenido, **Then** no provoca modificaciones no autorizadas ni ejecución de esas instrucciones.
6. **Given** se realizan accesos aceptados o rechazados, cierres, denegaciones y publicaciones, **When** reviso los registros y las superficies expuestas, **Then** encuentro tipo, resultado, fecha e identidad disponible de cada evento, sin contraseñas, secretos de sesión ni textos de mensajes privados; los secretos tampoco aparecen en contenido público, documentos, repositorio o errores.

---

### User Story 4 - Administrar con accesibilidad (Priority: P1)

Como Victor quiero completar las tareas administrativas usando teclado y tecnologías de asistencia.

**Why this priority**: La accesibilidad es una condición de aceptación de los flujos completos.

**Independent Test**: Completar acceso, edición, corrección de errores, publicación y cierre mediante teclado y lector de pantalla.

**Acceptance Scenarios**:

1. **Given** uso únicamente teclado, **When** completo los flujos, **Then** todos los controles son alcanzables, el foco es visible y no queda atrapado.
2. **Given** aparecen errores o cambios de estado, **When** uso un lector de pantalla, **Then** identifico los campos afectados y recibo la confirmación o el error correspondiente.
3. **Given** amplío texto al 200 % o uso una anchura de 320 píxeles CSS, **When** completo las tareas, **Then** no pierdo información ni funcionalidad.

### Edge Cases

- Verificación de identidad o autorización indisponible: denegar acciones que no puedan verificarse, sin acceso por defecto.
- Sesión vencida durante edición: indicar que no se guardó; reautenticar no publica ni repite automáticamente la acción.
- Ediciones simultáneas: conservar la versión guardada y advertir antes de reemplazarla.
- Contenido incompleto: conservar únicamente entradas seguras y explicar qué impide publicar.
- Sin versión publicada: no mostrar borradores ni marcadores pendientes en sitio o CV.
- Cuota agotada o fallo al persistir: informar, conservar la última publicación válida y no activar cargos.
- Permiso retirado: impedir nuevas acciones aunque la sesión permanezca vigente.
- Retirada de la última publicación de conocimientos o experiencia académica: conservar el contenido como borrador y ocultar la sección pública vacía y su enlace, conforme a la funcionalidad 001.
- Fallo al retirar una publicación: no confirmar éxito ni efectuar una retirada parcial; conservar el estado publicado anterior e informar del error.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir acceso mediante correo y contraseña únicamente a una identidad administrativa aprobada, sin registro público de administradores (escenarios 1.1, 1.2 y 3.2).
- **FR-002**: El sistema DEBE verificar identidad vigente y autorización actual para cada lectura privada y modificación, incluso fuera del panel; ninguna persona podrá concederse permisos mediante sus propios datos (historia 3).
- **FR-003**: El sistema DEBE permitir editar y conservar borradores de perfil, conocimientos y experiencia académica sin modificar la versión pública (escenario 2.1).
- **FR-004**: Publicar DEBE requerir revisión y confirmación explícita de Victor sobre una versión concreta de un único elemento: el perfil completo, un conocimiento o una experiencia académica. Únicamente esa versión del elemento pasará a ser la fuente aprobada compartida por sitio y CV; las publicaciones y los borradores de otros elementos permanecerán sin cambios (escenario 2.2).
- **FR-005**: El sistema DEBE impedir publicar campos obligatorios incompletos, marcadores pendientes y afirmaciones no verificadas; debe distinguir experiencia académica y profesional y no inventar datos (escenario 2.3).
- **FR-006**: El acceso público DEBE limitarse al contenido publicado y archivos autorizados; mensajes, borradores y archivos privados permanecerán inaccesibles a visitantes y personas sin permiso (escenarios 3.1 y 3.4).
- **FR-007**: El cierre y la caducidad DEBEN impedir reutilizar la sesión anterior; tras reautenticar, cualquier modificación requerirá una nueva acción explícita (escenarios 1.3 y 2.5).
- **FR-008**: El sistema DEBE rechazar acceso si no puede verificar identidad o permisos, limitar intentos según el escenario 1.5 y mostrar errores que no revelen la existencia de cuentas (escenarios 1.2, 1.4 y 1.5).
- **FR-009**: El sistema DEBE proteger credenciales y sesiones durante uso y transferencia, excluir secretos de contenido público, documentos, repositorio, registros y errores, y aplicar permisos mínimos a datos y archivos (escenarios 3.1, 3.4 y 3.6; revisión de protección de información).
- **FR-010**: El sistema DEBE validar entradas, impedir que el contenido editado ejecute instrucciones al mostrarse y rechazar modificaciones inducidas sin autorización del administrador (escenarios 2.3 y 3.5).
- **FR-011**: El sistema DEBE registrar accesos aceptados y rechazados, cierres, denegaciones y publicaciones con tipo, resultado, fecha e identidad disponible, sin credenciales ni contenido privado de mensajes (escenario 3.6).
- **FR-012**: El sistema DEBE detectar ediciones sobre versiones desactualizadas y evitar sobrescrituras silenciosas (escenario 2.4).
- **FR-013**: El sistema DEBE confirmar guardado o publicación solo después de comprobar su persistencia; un fallo conservará la última publicación íntegra e informará que la acción no se completó (escenario 2.6).
- **FR-014**: Los flujos completos del panel DEBEN cumplir WCAG 2.1 AA, incluyendo teclado, foco, lectura asistida, contraste, redistribución y errores vinculados a campos (historia 4 y evaluación de todos los criterios aplicables).
- **FR-015**: El sistema DEBE permitir a Victor retirar explícitamente la publicación de un conocimiento o una experiencia académica por separado, excluyéndolos del sitio y de la fuente del CV y conservando su contenido como borrador. Si ya existen cambios en borrador, DEBE conservarlos junto con el contenido retirado sin sobrescritura. La retirada DEBE confirmarse solo tras persistir íntegramente; un fallo conservará el estado anterior. Volver a publicar requiere la revisión y confirmación de FR-004 (escenarios 2.7 y 2.8).

### Key Entities *(include if feature involves data)*

- **Identidad administrativa**: persona aprobada, correo de acceso y estado actual de autorización, sin credenciales documentadas.
- **Sesión**: relación temporal con una identidad, vigencia y estado de cierre o invalidación.
- **Contenido editorial**: cada elemento (el perfil completo, un conocimiento o una experiencia académica) mantiene su propio borrador, versión publicada, fecha de modificación y aprobación; su publicación es independiente de los demás elementos.
- **Retirada de publicación**: transición de un conocimiento o experiencia académica publicados a contenido conservado como borrador y sin versión pública activa; preserva cualquier borrador previo y requiere nueva aprobación para volver a publicarse.
- **Recurso protegido**: mensaje o archivo con clasificación pública o privada y permisos correspondientes.
- **Evento de seguridad**: tipo, resultado, fecha e identidad disponible, excluyendo secretos y contenido privado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de lecturas privadas y modificaciones evaluadas se deniega a visitantes e identidades sin permiso, incluyendo solicitudes directas, sin revelar datos ni modificar contenido.
- **SC-002**: El 100 % de operaciones evaluadas después de cerrar o caducar la sesión, o retirar el permiso, rechaza el acceso anterior.
- **SC-003**: Guardar borradores modifica cero campos públicos; publicar actualiza únicamente la versión revisada del elemento elegido y produce una fuente coherente para sitio y CV en el 100 % de casos evaluados, sin modificar publicaciones ni borradores de otros elementos.
- **SC-004**: El panel presenta cero incumplimientos aplicables de WCAG 2.1 A y AA tras evaluación automática y revisión manual con teclado y lector de pantalla.
- **SC-005**: Victor completa acceso, edición de un campo, guardado, revisión, publicación y cierre sin ayuda externa en un máximo de cinco minutos con contenido de prueba preparado.
- **SC-006**: El 100 % de conflictos y fallos de persistencia evaluados evita sobrescrituras silenciosas, publicaciones parciales y confirmaciones falsas de éxito.
- **SC-007**: La revisión de registros y superficies expuestas encuentra cero credenciales, secretos de sesión o textos de mensajes privados y evidencia todas las categorías de eventos exigidas por FR-011.
- **SC-008**: El 100 % de casos de indisponibilidad de verificación y exceso de intentos del escenario 1.5 impide conceder acceso y ofrece una indicación comprensible para reintentar.
- **SC-009**: En el 100 % de retiradas evaluadas, el elemento deja de estar disponible para el sitio y la fuente del CV, su contenido y los borradores previos se conservan sin sobrescrituras y los demás elementos no cambian; los fallos no producen retiradas parciales ni confirmaciones falsas.

## Assumptions

- Victor es el único administrador inicial. Delegación de roles, registro de usuarios y recuperación autónoma de cuentas quedan fuera del alcance inicial.
- Victor proporcionará identidad aprobada y correo mediante configuración protegida; no se recopilarán ni escribirán credenciales en esta especificación.
- La limitación del escenario 1.5 es un valor inicial asumido. La duración concreta de las sesiones se definirá en planificación manteniendo caducidad y cierre efectivos.
- El alcance editorial incluye perfil, conocimientos y experiencia académica. Gestión completa de proyectos, imágenes y mensajes, sugerencias de IA, sincronización externa y generación del CV pertenecen a otras funcionalidades; aquí se definen los permisos y la fuente publicada que deberán respetar.
- La retirada de publicación se ofrece para conocimientos y experiencia académica; la eliminación definitiva de estos elementos queda fuera del alcance inicial. Esta aclaración no incorpora una acción de retirada del perfil completo.
- El perfil público de la funcionalidad 001 y los consumidores del CV utilizarán exclusivamente contenido publicado. Esta dependencia puede evaluarse con consumidores controlados sin implementar aquí el generador del CV.
- Para publicar, el perfil requiere nombre, carrera y resumen aprobado; cada conocimiento una denominación verificada; cada experiencia académica un título y descripción aprobados. Los datos opcionales ausentes se omiten. Son reglas iniciales que complementan la especificación del perfil sin inventar información personal.
- La constitución 1.0.0 de `.specify/memory/constitution.md` sigue siendo normativa para arquitectura, servicio de identidad, controles técnicos de seguridad, gratuidad y validación. Esta especificación no modifica esas decisiones; sus detalles se desarrollarán en planificación.
- Los criterios son objetivos de aceptación, no resultados de una aplicación implementada. Las verificaciones usarán identidades y datos aislados, sin mensajes reales ni modificaciones productivas.
