# Feature Specification: Asistencia editorial mediante IA gratuita o local

**Feature Branch**: `007-ia-asistida` (referencia del adjunto; no se ha creado una rama, la actual es `main`).

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Ayudar a Victor a redactar y traducir información del portafolio mediante sugerencias revisables, sin inventar hechos ni depender de servicios de pago."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obtener y revisar una sugerencia (Priority: P1)

Como Victor quiero pedir una mejora del texto que selecciono para redactar mi perfil o un proyecto con claridad y mantener el control de los hechos.

**Why this priority**: Proporciona asistencia acotada sin automatizar decisiones editoriales.

**Independent Test**: Desde un campo editorial autorizado de prueba, seleccionar un texto, solicitar una mejora, revisarla y aceptarla como borrador sin modificar publicaciones.

**Acceptance Scenarios**:

1. **Given** selecciono un texto académico real, **When** solicito una mejora, **Then** recibo una propuesta identificada como no aprobada junto al texto fuente, sin modificar el borrador ni la publicación.
2. **Given** faltan datos para afirmar un logro, **When** solicito completarlo, **Then** se indica qué información falta o se pide aportarla sin incorporar un hecho inventado como válido.
3. **Given** revisé una propuesta, **When** la edito y acepto como borrador, **Then** se incorpora solo al campo elegido, permanece editable y no queda publicada ni aprobada automáticamente.
4. **Given** he cambiado el campo desde que solicité la sugerencia, **When** llega la respuesta o intento aceptarla, **Then** se avisa que corresponde a una versión anterior y no se sobrescribe el texto actual sin una nueva decisión explícita.
5. **Given** intento incluir credenciales, mensajes de contacto o datos de visitantes, **When** preparo la solicitud, **Then** no se transmiten al modelo y se explica que debo utilizar solo contenido editorial permitido.
6. **Given** soy visitante o una identidad sin permiso, **When** intento solicitar o consultar sugerencias mediante una solicitud directa, **Then** se deniega sin transmitir texto al modelo ni revelar borradores.

---

### User Story 2 - Revisar una traducción (Priority: P2)

Como Victor quiero obtener una propuesta en español o inglés para preparar variantes del portafolio y CV sin cambiar sus hechos.

**Why this priority**: Reduce trabajo editorial preservando la revisión humana; sigue siendo parte del alcance completo.

**Independent Test**: Con un texto fuente aprobado de prueba, solicitar el otro idioma, revisar la propuesta y aceptarla como borrador comprobando que no habilita por sí sola una descarga del CV.

**Acceptance Scenarios**:

1. **Given** selecciono una fuente aprobada y español o inglés como destino, **When** solicito traducir, **Then** recibo una propuesta no aprobada en ese idioma que conserva hechos, nombres y nivel de experiencia de la fuente.
2. **Given** acepto una traducción como borrador, **When** consulto el sitio o la disponibilidad de CV, **Then** no se ofrece como variante publicada hasta completar la revisión y aprobación editorial independiente.
3. **Given** la propuesta cambia hechos, contiene otro idioma o aumenta el nivel de una capacidad, **When** la reviso, **Then** puedo corregirla o descartarla sin cambiar el contenido aprobado.
4. **Given** la fuente cambia después de generar una traducción, **When** intento incorporarla, **Then** se advierte su desactualización y no hereda aprobación para los hechos nuevos.

---

### User Story 3 - Descartar, cancelar y continuar manualmente (Priority: P1)

Como Victor quiero descartar sugerencias o trabajar sin IA para mantener control y continuar las tareas esenciales.

**Why this priority**: La disponibilidad del modelo no puede bloquear edición, publicación o CV aprobado.

**Independent Test**: Deshabilitar el modelo y completar edición, guardado, publicación y descarga de CV con contenido aislado ya aprobado.

**Acceptance Scenarios**:

1. **Given** no quiero utilizar una sugerencia, **When** la descarto, **Then** el texto editorial previo y la publicación permanecen intactos.
2. **Given** hay una generación en curso, **When** cancelo, **Then** se comunica la cancelación, puedo seguir editando y una respuesta tardía no se aplica automáticamente.
3. **Given** el modelo está ausente, sin memoria suficiente o falla, **When** continúo manualmente, **Then** puedo editar, guardar, publicar y descargar un CV ya aprobado sin IA ni cambio automático de proveedor.
4. **Given** se alcanza el tiempo o frecuencia permitidos, **When** termina o se rechaza la solicitud, **Then** se informa del límite y de cómo reintentar sin perder texto ni activar costes.
5. **Given** la respuesta contiene instrucciones maliciosas, **When** se muestra, **Then** se trata como texto sin ejecutar acciones, consultar secretos o modificar datos por instrucciones del modelo.
6. **Given** uso teclado y lector de pantalla, **When** genero, reviso, edito, acepto, descarto o cancelo, **Then** puedo completar las acciones y percibir generación, resultado, cancelación y error.

### Edge Cases

- Entrada vacía o insuficiente: explicar qué aportar sin completar hechos imaginarios.
- Propuesta incorrecta o que convierte trabajo académico en empleo: conservarla como salida no confiable, permitir corrección o descarte y no otorgarle aprobación.
- Texto o contexto excedido: rechazar con explicación antes de transmitir; no recortar silenciosamente información necesaria.
- Respuesta excesiva o incompleta: indicar que no constituye una propuesta completa lista para aceptar, sin aplicarla automáticamente.
- Edición concurrente, cancelación o sesión vencida antes de recibir respuesta: no sobrescribir el campo ni revelar la propuesta sin autorización vigente.
- Recursos insuficientes o cuota agotada: mantener funciones manuales, sin contratar servicios ni activar facturación.
- Datos privados incluidos accidentalmente: bloquear entradas identificadas como no permitidas; el modelo no tiene acceso a la bandeja, credenciales ni contexto privado automático.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: La administración DEBE ofrecer sugerencias de perfil, descripciones de proyectos y traducciones español/inglés basadas únicamente en el texto seleccionado y contexto editorial mínimo proporcionado o aprobado por Victor (historias 1 y 2).
- **FR-002**: La modalidad inicial DEBE utilizar un modelo local gratuito con licencia compatible. Cualquier proveedor remoto requerirá aprobación explícita previa de Victor sobre gratuidad y privacidad, sin activar facturación; no habrá sustitución automática (escenario 3.3 y revisión previa de habilitación).
- **FR-003**: Antes de solicitar generación se DEBE mostrar el texto y contexto que se utilizarán, permitiendo corregirlos. No se incorporarán automáticamente mensajes de contacto, datos de visitantes, secretos ni otras fuentes privadas; se bloquearán entradas identificadas como no permitidas antes de transmitirlas (escenario 1.5 y revisión de límites de información).
- **FR-004**: Toda salida DEBE identificarse como sugerencia no aprobada y permitir compararla con su fuente, revisarla, editarla, aceptarla como borrador o descartarla; ninguna solicitud modificará por sí sola contenido editorial (escenarios 1.1, 1.3 y 3.1).
- **FR-005**: El sistema NO DEBE aprobar ni publicar automáticamente, inventar datos para cubrir carencias o tratar afirmaciones generadas como hechos verificados. Victor deberá verificar hechos y nivel de experiencia antes de aprobar (escenarios 1.2 y 2.3).
- **FR-006**: Aceptar una sugerencia DEBE afectar solo al borrador seleccionado. Publicar y aprobar traducciones del CV serán acciones editoriales separadas, explícitas y autorizadas (escenarios 1.3 y 2.2).
- **FR-007**: La propuesta DEBE conservar la referencia al texto fuente usado y advertir diferencias si este cambia, evitando sobrescritura silenciosa o transferencia automática de aprobación a hechos nuevos (escenarios 1.4 y 2.4).
- **FR-008**: Las entradas y respuestas DEBEN tratarse como texto no confiable, sin ejecutar instrucciones ni conceder al modelo acceso a secretos, mensajes privados o acciones administrativas (escenario 3.5).
- **FR-009**: El sistema DEBE aplicar límites explícitos de longitud, duración y frecuencia, comunicarlos antes de solicitar y explicar su incumplimiento sin perder texto; debe permitir cancelar y evitar aplicar respuestas tardías (escenarios 3.2 y 3.4; casos de longitud).
- **FR-010**: Ausencia o fallo del modelo NO DEBE impedir editar, guardar, publicar manualmente ni descargar CV con información ya aprobada, ni activar servicios de pago (escenario 3.3).
- **FR-011**: Solicitar, consultar y aceptar sugerencias DEBE exigir identidad y autorización administrativas vigentes, incluso mediante solicitudes directas o tras caducar una sesión (escenario 1.6 y caso de sesión vencida).
- **FR-012**: Los flujos completos DEBEN cumplir WCAG 2.1 AA, incluidos teclado, foco, identificación de controles y anuncios accesibles de generación, cancelación y error (escenario 3.6 y evaluación de criterios aplicables).

### Key Entities

- **Solicitud editorial**: propósito de redacción o traducción, texto seleccionado, contexto editorial mínimo autorizado, versión fuente, idioma destino y estado de generación.
- **Sugerencia**: texto propuesto, fuente de referencia, idioma y estado no aprobado, editable, aceptado como borrador o descartado.
- **Decisión editorial**: aceptación como borrador o descarte por Victor, separada de la aprobación y publicación posteriores.
- **Modalidad de asistencia**: funcionamiento local inicial, disponibilidad, límites y eventual aprobación explícita de una alternativa remota gratuita y compatible con la privacidad.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cero solicitudes evaluadas aprueban o publican automáticamente; aceptar una propuesta cambia únicamente el borrador seleccionado.
- **SC-002**: En el 100 % de descartes, cancelaciones y respuestas tardías evaluados permanece intacto el contenido editorial previo salvo cambios manuales explícitos de Victor.
- **SC-003**: Con el modelo deshabilitado se completan edición, guardado, publicación y descarga de CV aprobado en el 100 % de escenarios esenciales definidos, sin servicios de pago.
- **SC-004**: Ninguna solicitud evaluada transmite credenciales, mensajes de visitantes ni datos de estos al modelo; ninguna salida evaluada ejecuta acciones o accede a información privada.
- **SC-005**: Todas las propuestas evaluadas muestran su condición no aprobada y todas las diferencias de versión fuente detectadas se advierten antes de incorporarlas sin sobrescritura silenciosa.
- **SC-006**: En el conjunto de textos de aceptación en español e inglés, toda propuesta que llegue a aprobación humana conserva el 100 % de los hechos verificados de su fuente, sin logros inventados ni capacidades elevadas.
- **SC-007**: El 100 % de accesos sin permiso, entradas fuera de límites y fallos de generación evaluados se rechaza o finaliza con indicación comprensible sin perder la edición manual.
- **SC-008**: Los flujos completos presentan cero incumplimientos aplicables de WCAG 2.1 A y AA tras revisión automática y manual con teclado y lector de pantalla.
- **SC-009**: Con una propuesta de prueba preparada, Victor identifica sin ayuda su estado no aprobado y puede aceptarla como borrador o descartarla en menos de un minuto, distinguiendo ambas acciones de publicar.

## Assumptions

- Depende de `002-administracion` y se integra con perfil de `001-perfil-publico`, proyectos de `003-gestion-proyectos` y variantes de `005-cv-bilingue`. Puede validarse aisladamente con un campo editorial y respuestas controladas.
- Modelo, licencia compatible, requisitos de hardware y límites concretos se seleccionarán y documentarán antes de implementar. No se presume cómputo gratuito ilimitado ni disponibilidad permanente.
- El proveedor remoto no forma parte de la modalidad inicial; su eventual aprobación no se presume por esta especificación. Si no se cumplen gratuidad y privacidad, la asistencia queda indisponible y continúa el trabajo manual.
- La protección de datos se basa en limitar las fuentes y el contexto autorizado, además de bloquear entradas identificadas como privadas; no se promete detección infalible de cualquier secreto pegado en texto libre. Victor revisará el contenido mostrado antes de enviarlo.
- La veracidad de una salida generada no se presume: la revisión humana corrige o descarta errores antes de aprobar; no se garantiza que un modelo nunca produzca una afirmación incorrecta.
- Las sugerencias se mantienen durante la revisión activa; aceptar como borrador reutiliza la conservación editorial existente. No se exige historial permanente de conversaciones ni se reutilizarán solicitudes para entrenamiento. Cualquier conservación adicional deberá definirse y justificarse en planificación.
- Quedan fuera chatbot público, respuestas automáticas a visitantes, entrenamiento con mensajes y generación automática de experiencia o logros.
- La constitución 1.0.0 en `.specify/memory/constitution.md` conserva su autoridad sobre arquitectura, IA, seguridad, gratuidad, revisión humana y validación. Sus decisiones técnicas se concretarán durante planificación sin enmendarlas aquí.
- Los criterios son objetivos de aceptación, no resultados ya verificados. Las pruebas usarán textos aislados sin datos privados reales, incluyendo salidas incorrectas, fallos, conflictos y revisión manual de accesibilidad.
