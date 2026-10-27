# Feature Specification: CV actualizado en español e inglés

**Feature Branch**: `005-cv-bilingue` (referencia del adjunto; no se ha creado una rama, la actual es `main`).

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Generar un CV descargable con texto seleccionable, estructura favorable para ATS e idioma elegido por el visitante."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Descargar el CV en español (Priority: P1)

Como visitante quiero descargar el CV en español para conocer la formación y proyectos actuales de Victor.

**Why this priority**: Entrega información publicada sin depender de IA ni sincronización externa.

**Independent Test**: Con contenido español aprobado de prueba, elegir español, descargar y comparar el documento con su versión fuente.

**Acceptance Scenarios**:

1. **Given** el contenido español obligatorio está aprobado, **When** elijo español y descargo, **Then** obtengo un PDF textual en español con identidad, contacto autorizado y contenido curricular coherente con el portafolio publicado.
2. **Given** existen modificaciones únicamente en borrador, **When** descargo, **Then** el documento conserva los datos aprobados anteriores y excluye borradores y marcadores pendientes.
3. **Given** faltan datos mínimos o contacto autorizado, **When** consulto o solicito directamente la descarga, **Then** se explica que el idioma no está disponible y no se entrega un CV incompleto.
4. **Given** no hay experiencia profesional, **When** descargo, **Then** no aparece una sección de empleo ni logros inventados; la experiencia académica se identifica como tal.
5. **Given** no están disponibles la IA o la sincronización externa, **When** descargo desde contenido publicado disponible, **Then** la descarga sigue funcionando sin solicitar esos servicios.

---

### User Story 2 - Descargar el CV en inglés (Priority: P1)

Como visitante quiero elegir inglés para presentar los mismos hechos aprobados a lectores de ese idioma.

**Why this priority**: Ambos idiomas forman parte del alcance obligatorio.

**Independent Test**: Con variantes inglesas revisadas, descargar y comprobar encabezados, hechos y texto extraído frente a la fuente aprobada.

**Acceptance Scenarios**:

1. **Given** todas las variantes inglesas necesarias están aprobadas para la versión vigente, **When** elijo inglés, **Then** recibo encabezados y contenido en inglés con los mismos hechos y alcance del CV español de esa versión.
2. **Given** falta una traducción necesaria o su aprobación no corresponde al contenido vigente, **When** consulto los idiomas o solicito directamente inglés, **Then** se explica su indisponibilidad sin entregar una traducción improvisada, una versión antigua o una mezcla de idiomas.
3. **Given** un idioma está incompleto y el otro está aprobado, **When** consulto las descargas, **Then** puedo descargar el idioma completo sin que la falta del otro lo bloquee.
4. **Given** uso teclado y lector de pantalla, **When** elijo cualquiera de los idiomas, **Then** puedo identificar disponibilidad, seleccionar, descargar y percibir el resultado; el archivo y el documento identifican el idioma elegido.

---

### User Story 3 - Obtener un documento actualizado y legible (Priority: P1)

Como Victor quiero que el CV refleje la última publicación con un orden de lectura claro para lectores y sistemas de seguimiento de candidaturas (ATS).

**Why this priority**: Protege la integridad y legibilidad del documento sin prometer resultados de contratación.

**Independent Test**: Publicar una corrección de prueba, generar ambos idiomas y comparar su presentación y texto extraído con la fuente vigente.

**Acceptance Scenarios**:

1. **Given** publico una corrección completa, **When** solicito el siguiente CV, **Then** incorpora la revisión vigente y no entrega un archivo anterior reutilizado.
2. **Given** retiro un proyecto publicado, **When** solicito el siguiente CV, **Then** no contiene ese proyecto; si la retirada deja incompleto el contenido mínimo, no se ofrece ese idioma hasta resolverlo.
3. **Given** hay una publicación durante la generación, **When** termina la descarga, **Then** todo el documento corresponde a una única versión publicada coherente, sin mezclar revisiones.
4. **Given** selecciono y extraigo el texto de cualquiera de los PDF, **When** lo leo secuencialmente, **Then** conserva nombres, tildes, encabezados, contenido y orden de secciones sin pérdidas ni intercalaciones entre columnas.
5. **Given** hay textos extensos y saltos de página, **When** reviso el documento, **Then** no hay recortes, superposiciones ni pérdida de caracteres y la lectura continúa en orden.
6. **Given** falla la generación o no puede obtenerse la fuente vigente, **When** solicito descargar, **Then** recibo un error accesible con opción de reintento sin PDF corrupto, confirmación falsa o entrega silenciosa de un documento obsoleto.

### Edge Cases

- Sin experiencia laboral: omitir empleo y usar educación, proyectos y experiencia académica reales.
- Datos opcionales ausentes: omitirlos sin marcadores; datos mínimos ausentes: bloquear el idioma afectado.
- Traducción desactualizada por una publicación: no reutilizar su aprobación para hechos nuevos.
- Nombres propios, tecnologías y direcciones: conservar su denominación legítima sin considerarla mezcla indebida de idiomas.
- Tildes, caracteres especiales, enlaces largos y varias páginas: mantener texto completo y orden lineal.
- Publicación simultánea: usar una versión completa vigente al iniciar la generación; una solicitud posterior toma la nueva versión.
- Idioma desconocido en una solicitud directa: indicar selección inválida sin sustituirlo silenciosamente por otro.
- Fallo de fuente o generación: permitir reintento sin ofrecer archivos parciales ni versiones antiguas como actuales.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El visitante DEBE poder elegir explícitamente español o inglés y descargar un PDF en el idioma seleccionado; solicitudes de idiomas no admitidos no producirán un documento en otro idioma (historias 1 y 2; caso de idioma desconocido).
- **FR-002**: Cada generación DEBE usar una única versión coherente de la información publicada vigente al iniciarse. Una solicitud posterior a una publicación no podrá recibir contenido anterior como vigente (escenarios 3.1 y 3.3).
- **FR-003**: El CV DEBE incluir identidad, contacto autorizado, perfil breve, educación, habilidades y proyectos o experiencia académica pertinentes, con hechos verificados y sin empleos, logros ni niveles de dominio inventados (escenarios 1.1 y 1.4).
- **FR-004**: Cada idioma ofrecido DEBE tener revisados y aprobados todos sus textos necesarios para los hechos vigentes. No se mezclarán idiomas salvo nombres propios, direcciones y denominaciones técnicas. Una traducción ausente o desactualizada impedirá entregar ese idioma, sin bloquear otro completo (historia 2).
- **FR-005**: El sistema DEBE excluir borradores, marcadores, mensajes privados, secretos, contactos no autorizados y proyectos retirados o eliminados de toda descarga (escenarios 1.2 y 3.2; revisión del contenido completo).
- **FR-006**: El PDF DEBE contener texto seleccionable y extraíble en una sola columna, con encabezados de significado claro y orden lineal; no contendrá tablas, gráficos, barras de habilidades, imágenes de texto ni información esencial en encabezados o pies (escenarios 3.4 y 3.5; revisión visual).
- **FR-007**: El CV DEBE seguir convenciones sobrias de modelos universitarios como Harvard u Oxford, con fuentes legibles y secciones textuales, sin afirmar afiliación institucional ni compatibilidad garantizada con todos los ATS (revisión visual y de afirmaciones del documento).
- **FR-008**: La generación DEBE utilizar exclusivamente recursos gratuitos, sin servicios PDF de pago ni llamadas obligatorias a IA o sincronización externa; no enviará datos privados a terceros (escenario 1.5 y revisión de dependencias y salidas de datos).
- **FR-009**: El selector, la disponibilidad y los flujos de descarga y reintento DEBEN cumplir WCAG 2.1 AA. Documento y nombre de archivo identificarán el idioma seleccionado (escenario 2.4; evaluación de criterios aplicables).
- **FR-010**: Ante fallo de generación o de acceso a la información vigente, el sistema DEBE informar sin confirmar una descarga exitosa ni entregar un archivo corrupto, parcial o silenciosamente obsoleto y permitirá reintentar (escenario 3.6).
- **FR-011**: Si faltan datos mínimos aprobados, el sistema DEBE explicar la indisponibilidad del idioma y bloquear también su solicitud directa; los datos opcionales ausentes se omitirán (escenario 1.3 y casos de datos faltantes).
- **FR-012**: La presentación DEBE conservar caracteres y contenido completo en textos extensos y saltos de página, sin recortes ni superposiciones que impidan leer o extraer información (escenarios 3.4 y 3.5).

### Key Entities

- **Contenido curricular aprobado**: identidad, contacto autorizado, perfil, educación, habilidades y proyectos o experiencia académica publicados, vinculados a una versión coherente.
- **Variante lingüística**: idioma, textos revisados por sección, hechos de referencia y aprobación correspondiente a la versión vigente.
- **Documento generado**: idioma, versión fuente, fecha de generación y PDF textual con nombre de archivo identificable.
- **Disponibilidad de idioma**: cumplimiento de contenido mínimo, traducciones vigentes y motivo comprensible de indisponibilidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de hechos de cada CV evaluado coincide con una única versión aprobada del portafolio; español e inglés representan los mismos hechos para esa versión.
- **SC-002**: En ambos idiomas, el 100 % del contenido textual esperado se conserva al seleccionarlo y extraerlo, incluidos nombre, tildes, encabezados y orden de secciones.
- **SC-003**: Cero documentos entregados contienen borradores, marcadores, mensajes privados, secretos, proyectos retirados o traducciones no aprobadas para su versión.
- **SC-004**: La primera solicitud iniciada después de cada publicación evaluada incorpora la revisión completa correspondiente; las publicaciones concurrentes nunca producen mezcla de revisiones.
- **SC-005**: En el 100 % de casos con traducción necesaria ausente o desactualizada se bloquea ese idioma con explicación, manteniendo disponible el otro si está completo.
- **SC-006**: La revisión visual de documentos de una y varias páginas en ambos idiomas detecta cero recortes, superposiciones, columnas adicionales o información esencial fuera del cuerpo de lectura.
- **SC-007**: Los flujos completos de elección y descarga presentan cero incumplimientos aplicables de WCAG 2.1 A y AA tras revisión automática y manual con teclado y lector de pantalla.
- **SC-008**: Con contenido aprobado de prueba y condiciones normales de conexión, el 95 % de descargas evaluadas permite obtener el documento en un máximo de diez segundos desde la solicitud; todos los fallos evaluados ofrecen error y reintento sin archivos inválidos.

## Assumptions

- Depende del perfil de `001-perfil-publico`, la aprobación de `002-administracion` y los proyectos de `003-gestion-proyectos`. Puede evaluarse con una versión coherente de prueba sin implementar sincronización externa o asistencia de IA.
- Victor aportará el correo público autorizado, educación, habilidades y textos aprobados de ambos idiomas. Son datos editoriales pendientes y no se inventarán; la aceptación completa exige comprobar las dos variantes.
- El mínimo para ofrecer un idioma incluye nombre público, correo autorizado, perfil breve, educación, al menos una habilidad verificada y al menos un proyecto o experiencia académica pertinente. Los campos opcionales ausentes se omiten y las secciones vacías no se fabrican.
- El orden inicial será identidad y contacto, perfil, educación, habilidades y proyectos o experiencia académica. No se impone una sola página si supone pérdida de información o legibilidad.
- Los proyectos se representan mediante información textual pertinente; no se reproducen las imágenes de la galería. La selección curricular y sus variantes lingüísticas requieren revisión de Victor.
- Se distingue aprobación editorial de publicación técnica: una traducción solo es válida si conserva los hechos vigentes. La gestión de esas aprobaciones reutiliza el flujo administrativo, sin publicar automáticamente traducciones generadas.
- Una descarga iniciada antes de una publicación puede completar la versión anterior coherente; las solicitudes posteriores deben usar la nueva. Los PDF ya descargados por terceros no se actualizan ni retiran retroactivamente.
- No se garantiza clasificación favorable en un ATS concreto, contratación ni afiliación a las universidades citadas. Se evalúan estructura, veracidad, lectura y extracción.
- La constitución 1.0.0 en `.specify/memory/constitution.md` conserva su autoridad sobre arquitectura, generación documental, gratuidad, accesibilidad y validación. Sus decisiones técnicas se concretarán en planificación sin enmendarlas aquí.
- Los criterios anteriores son objetivos de aceptación, no resultados ya verificados. Las comprobaciones usarán contenido aislado e incluirán revisión visual, de idioma, de texto extraído y de accesibilidad de la interfaz.
