# Feature Specification: Perfil público y experiencia académica

**Feature Branch**: `001-perfil-publico`

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Presentar a Victor Rafael Arévalo Sierra, sus conocimientos y su experiencia académica mediante un portafolio honesto, moderno y accesible."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Conocer el perfil de Victor (Priority: P1)

Como visitante quiero identificar quién es Victor, qué estudia y cuál es su perfil para valorar su trabajo.

**Why this priority**: Es el contenido mínimo que da identidad y valor al portafolio.

**Independent Test**: Abrir el sitio con contenido aprobado de prueba, sin proyectos ni integraciones activas.

**Acceptance Scenarios**:

1. **Given** existe un perfil aprobado, **When** abro el inicio, **Then** veo el nombre completo, Ingeniería en Desarrollo de Software y el perfil breve.
2. **Given** el perfil breve está pendiente, **When** abro el inicio, **Then** veo los datos confirmados sin marcadores ni textos inventados.
3. **Given** existen borradores o datos privados junto al contenido publicado, **When** consulto el sitio como visitante, **Then** solo accedo a los datos publicados y aprobados, incluidos únicamente los contactos autorizados.
4. **Given** proyectos, contacto o CV están disponibles, **When** utilizo su navegación, **Then** llego al destino anunciado; si alguno no está disponible, veo un estado comprensible sin enlaces que aparenten funcionar.
5. **Given** falla la lectura del perfil, **When** abro el inicio, **Then** recibo un mensaje accesible de indisponibilidad sin datos inventados ni información privada del fallo.

---

### User Story 2 - Consultar conocimientos y formación (Priority: P2)

Como visitante quiero consultar habilidades verificadas y experiencia académica para entender su preparación.

**Why this priority**: Permite evaluar capacidades sin atribuir experiencia laboral inexistente.

**Independent Test**: Publicar una habilidad y una actividad académica de prueba y consultar ambas.

**Acceptance Scenarios**:

1. **Given** hay conocimientos y formación publicados, **When** consulto sus secciones, **Then** veo descripciones y fechas aprobadas diferenciadas de experiencia laboral.
2. **Given** no existe experiencia profesional, **When** consulto el perfil, **Then** no se presentan empleos, logros ni certificaciones ficticios.
3. **Given** una sección no tiene contenido publicado, **When** consulto el sitio, **Then** esa sección se omite o presenta un estado vacío útil, sin ejemplos ficticios ni marcadores pendientes.
4. **Given** hay conocimientos publicados, **When** los consulto, **Then** veo capacidades verificadas sin porcentajes arbitrarios de dominio.

---

### User Story 3 - Navegar con distintas capacidades y dispositivos (Priority: P1)

Como visitante quiero recorrer el contenido con teclado o lector de pantalla y desde móvil para acceder a la misma información.

**Why this priority**: La accesibilidad es obligatoria para cualquier primera versión.

**Independent Test**: Recorrer los contenidos y navegación con teclado, lector de pantalla y ampliación.

**Acceptance Scenarios**:

1. **Given** uso solo teclado, **When** recorro enlaces y controles, **Then** el foco es visible, sigue un orden lógico y no queda atrapado.
2. **Given** amplío texto al 200 % o uso 320 píxeles CSS de ancho, **When** consulto las secciones, **Then** el contenido se redistribuye sin pérdida de información ni controles, salvo excepciones normativas justificadas.
3. **Given** uso lector de pantalla, **When** recorro el contenido y sus estados, **Then** reconozco encabezados, destinos y controles por nombres comprensibles y recibo los mensajes de estado pertinentes.
4. **Given** consulto el sitio en cualquier estado disponible, **When** reviso texto, controles y gráficos necesarios, **Then** cumplen el contraste aplicable y ninguna información depende solo del color.
5. **Given** he solicitado movimiento reducido, **When** navego por el sitio, **Then** se respeta esa preferencia y ningún movimiento impide leer o utilizar controles.

### Edge Cases

- Sin contenido en una sección: ocultarla o mostrar un estado vacío útil sin ejemplos ficticios.
- Fallo de lectura o agotamiento de cuota gratuita: mostrar indisponibilidad de la función afectada, sin activar cargos ni sustituir datos por afirmaciones inventadas.
- Texto extenso o enlaces largos: mantener lectura y redistribución sin recortes.
- Resumen, institución, fechas o contactos pendientes: no publicar marcadores ni completar datos por inferencia.
- Destinos de proyectos, contacto o CV no disponibles: comunicar el estado sin ofrecer una acción que aparente estar operativa.
- Borradores y datos privados existentes: impedir su consulta pública, incluso mediante acceso directo a los datos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE mostrar la identidad confirmada y únicamente contenido publicado y aprobado por Victor.
- **FR-002**: El sistema DEBE separar educación y actividades académicas de experiencia profesional; omitir empleos mientras no existan.
- **FR-003**: El sistema DEBE leer de Supabase el perfil, conocimientos y experiencia académica; nunca exponer borradores o datos privados.
- **FR-004**: El sistema DEBE ofrecer navegación coherente a proyectos, contacto y CV cuando estén disponibles, con estados claros cuando no lo estén y sin acciones que aparenten estar operativas.
- **FR-005**: El sistema DEBE mantener jerarquía semántica, etiquetas comprensibles, mensajes de estado accesibles y diseño consistente; no usar porcentajes arbitrarios de dominio.
- **FR-006**: El sistema DEBE cumplir todos los criterios aplicables de WCAG 2.1 A y AA: contraste 4.5:1 en texto normal, 3:1 en texto grande y 3:1 en componentes y gráficos necesarios según el contraste no textual aplicable; no transmitir información solo mediante color; respetar movimiento reducido.
- **FR-007**: El sistema DEBE omitir campos pendientes y gestionar secciones vacías y fallos de lectura con estados útiles y accesibles, sin contenido ficticio, marcadores ni detalles privados de errores.
- **FR-008**: El sistema DEBE permitir navegación completa por teclado, con foco visible y orden lógico, lectura asistida y uso con texto al 200 % y ancho de 320 píxeles CSS, sin pérdidas de información o controles, salvo excepciones normativas justificadas.

### Key Entities

- **Perfil público**: nombre, carrera, resumen aprobado y datos de contacto autorizados; solo su contenido publicado y aprobado es visible.
- **Conocimiento**: nombre, descripción verificable, orden y estado editorial.
- **Experiencia académica**: institución, actividad, período, descripción y estado editorial; se distingue de experiencia profesional.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % del contenido visible coincide con datos aprobados y no contiene marcadores pendientes; ningún borrador ni dato privado es accesible al visitante.
- **SC-002**: Todas las secciones y controles son recorribles por teclado y comprensibles con lector de pantalla, sin incumplimientos aplicables de WCAG 2.1 AA.
- **SC-003**: El perfil conserva contenido y controles al 200 % de texto y 320 píxeles CSS, con las excepciones normativas justificadas.
- **SC-004**: En todos los escenarios de aceptación de secciones vacías, fallos de lectura y destinos no disponibles, el visitante encuentra el estado previsto sin afirmaciones inventadas ni acciones que aparenten funcionar; todos los destinos disponibles llevan al contenido anunciado.

## Assumptions

- Depende de la funcionalidad 002 para edición; se puede evaluar con contenido aprobado de prueba sin implementar el panel.
- Pendientes de Victor: perfil breve, institución, fechas y conocimientos verificados; la ubicación es opcional. Estos pendientes de contenido no impiden planificar y nunca se mostrarán como marcadores al público.
- La interfaz pública tendrá español como idioma inicial; esta decisión no limita el CV bilingüe.
- Fuente normativa: constitución del proyecto 1.0.0, disponible en `.specify/memory/constitution.md`, identificada en la entrada como «Markdown pegado.md». Los criterios de esta spec son objetivos de aceptación, no resultados ya verificados.
- Se mantienen Python, Flask, Jinja, Supabase gratuito y recursos exclusivamente gratuitos. Las propuestas iniciales aquí señaladas no enmiendan la constitución y requieren validación de Victor antes de implementarse.
- La futura verificación funcional utilizará Pytest con mocks o datos aislados. La autorización y las políticas de acceso se comprobarán con roles representativos en un entorno de prueba; los mocks no acreditan por sí solos las políticas de acceso. La revisión manual de accesibilidad complementará las verificaciones automáticas.
- Prioridad P1 identifica obligaciones necesarias para aceptar esta funcionalidad; las dependencias declaradas pueden sustituirse por datos o servicios controlados para su evaluación aislada. Los identificadores FR y SC son locales a este archivo.
- Esta funcionalidad cubre presentación pública y navegación hacia proyectos, contacto y CV. La edición, gestión de proyectos, recepción de mensajes, generación del CV e integraciones adicionales corresponden a otras funcionalidades.
- La rama indicada es metadato solicitado; su creación depende de un hook de Git. El directorio de esta spec se resuelve independientemente como `specs/001-perfil-publico` por numeración secuencial.
