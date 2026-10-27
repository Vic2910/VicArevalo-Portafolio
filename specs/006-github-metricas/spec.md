# Feature Specification: Sincronización de GitHub y dashboard administrativo

**Feature Branch**: `006-github-metricas` (referencia del adjunto; no se ha creado una rama, la actual es `main`).

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Leer datos públicos de Vic2910, incluidos commits atribuibles, persistirlos y mostrar métricas de proyectos, commits y mensajes."

## Clarifications

### Session 2026-10-27

- Q: ¿Deben incluirse en el conteo los commits atribuibles a Vic2910 dentro de repositorios propios que sean bifurcaciones de otros proyectos? → A: Incluir bifurcaciones propias, contar únicamente commits atribuibles a Vic2910 y advertir posibles repeticiones entre repositorios.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Consultar métricas locales (Priority: P1)

Como Victor quiero ver cantidades de proyectos, commits y mensajes para conocer el estado del portafolio sin depender de una consulta externa al abrir el panel.

**Why this priority**: El dashboard ofrece valor incluso cuando GitHub no está disponible.

**Independent Test**: Abrir el dashboard con proyectos, mensajes y actividad previamente sincronizada de prueba, sin conexión a GitHub.

**Acceptance Scenarios**:

1. **Given** soy administrador y hay datos conservados, **When** abro el dashboard, **Then** veo proyectos publicados y borradores, mensajes actuales totales y pendientes, y commits sincronizados con su alcance y fecha.
2. **Given** falla la lectura de una métrica, **When** consulto el panel, **Then** esa métrica indica indisponibilidad sin sustituirla por cero; otras métricas válidas siguen siendo interpretables.
3. **Given** nunca hubo sincronización satisfactoria, **When** consulto commits, **Then** aparece ausencia de datos, no un total cero confirmado.
4. **Given** soy visitante o una identidad sin permiso, **When** intento consultar el dashboard o iniciar sincronización, incluso mediante solicitud directa, **Then** se deniega sin revelar cantidades privadas ni modificar datos.
5. **Given** retiro un proyecto o elimino un mensaje, **When** vuelvo a consultar, **Then** las cantidades actuales excluyen el mensaje eliminado y distinguen el proyecto retirado de publicados y borradores.

---

### User Story 2 - Sincronizar repositorios y commits (Priority: P1)

Como Victor quiero incorporar actividad pública atribuible a Vic2910 para consultar evidencia de trabajo real.

**Why this priority**: Completa las métricas sin atribuir actividad ajena ni fabricar proyectos editoriales.

**Independent Test**: Con respuestas controladas de varias páginas y autores distintos, iniciar una sincronización y repetirla una vez permitido el siguiente intento.

**Acceptance Scenarios**:

1. **Given** hay varias páginas de repositorios y commits públicos propios y ajenos, **When** sincronizo el alcance inicial, **Then** se recorren las páginas necesarias y solo los commits cuyo autor está vinculado de forma verificable a Vic2910 integran su conteo.
2. **Given** repito páginas o una sincronización sin cambios, **When** consulto el resultado, **Then** un mismo par repositorio/SHA se cuenta una vez, aunque se haya observado en varias ramas.
3. **Given** el autor no tiene vínculo verificable, **When** proceso el commit, **Then** se identifica atribución desconocida y aporta cero al conteo propio, aunque el repositorio sea de Victor.
4. **Given** inicio una actualización permitida, **When** se completa y se guarda, **Then** se conserva el resultado y su fecha satisfactoria; abrir o recargar el dashboard no inicia otra consulta a GitHub.
5. **Given** la siguiente actualización aún no está permitida o hay una en curso, **When** solicito otra, **Then** no se abre una sincronización duplicada y veo el estado y cuándo puedo reintentar.
6. **Given** se sincroniza un repositorio, **When** finaliza la operación, **Then** no aparece automáticamente como proyecto publicado del portafolio ni como experiencia profesional.
7. **Given** una bifurcación pública propiedad de Vic2910 contiene commits propios verificables y commits ajenos, **When** sincronizo su rama predeterminada, **Then** solo los atribuibles a Vic2910 integran el conteo; si su SHA aparece también en otro repositorio del alcance, cuenta una vez por repositorio y la explicación advierte esa posible repetición.

---

### User Story 3 - Interpretar límites, alcance y antigüedad (Priority: P2)

Como Victor quiero conocer qué representan los datos, cuándo se comprobaron y qué quedó pendiente para interpretar correctamente métricas parciales.

**Why this priority**: Evita presentar actividad parcial o antigua como un historial completo. Las advertencias de integridad siguen siendo obligatorias para aceptar las historias P1.

**Independent Test**: Tras una sincronización válida, simular interrupción de paginación, restricciones de consulta y recuperación sin cambios.

**Acceptance Scenarios**:

1. **Given** GitHub indica una restricción de consultas, **When** se intenta actualizar, **Then** se respeta la espera comunicada y se suspenden nuevos intentos durante ella, conservando los últimos datos válidos.
2. **Given** se interrumpe la lectura de páginas, **When** consulto el panel, **Then** distingo el último resultado válido del intento parcial, veo alcance, advertencia y fecha de ambos, sin presentar el parcial como total completo.
3. **Given** hay un conteo de commits, **When** consulto su explicación, **Then** conozco período, repositorios, ramas, reglas de atribución y deduplicación, exclusiones y completitud para ese alcance, sin una afirmación de historial global.
4. **Given** una comprobación satisfactoria no encuentra cambios, **When** consulto el panel, **Then** se conserva el conteo y se actualiza la fecha de comprobación sin duplicaciones.
5. **Given** un perfil o repositorio deja de ser accesible, **When** se intenta actualizar, **Then** se muestra su estado sin inventar actividad ni transformar el error en cero; el histórico retenido se identifica con su alcance anterior.
6. **Given** uso teclado y lector de pantalla, **When** reviso métricas, explicaciones e inicio una actualización, **Then** puedo completar las tareas y percibir espera, éxito, parcialidad y error sin depender del color.

### Edge Cases

- Perfil o repositorio vacío, renombrado, eliminado o inaccesible: distinguir ausencia real comprobada de fallo de consulta; conservar referencias por identidad estable cuando sea verificable.
- Autor desconocido o solo coincidencia de nombre o correo no verificada: no atribuir el commit a Vic2910.
- Mismo SHA en varias ramas: una contribución por repositorio; en repositorios distintos puede contar una vez por cada repositorio y debe explicarse.
- Bifurcaciones públicas propias: incluirlas con las mismas reglas de atribución; no atribuir a Vic2910 los commits heredados de otros autores ni presentar el conteo por repositorio como un total de SHA únicos globales.
- Paginación interrumpida o persistencia fallida: no adelantar la fecha satisfactoria ni reemplazar el resultado válido por un parcial silencioso.
- Repositorio sin commits comprobado: cero real para ese repositorio, sin convertir otros errores en cero.
- Cambio de rama predeterminada o historial reescrito: el siguiente resultado completo debe representar lo accesible en el alcance vigente, sin acumular como actuales commits que ya no pertenecen a él.
- Restricción sin espera explícita: aplicar espera progresiva y suspensión temporal conforme a las reglas vigentes del proveedor, sin insistencia continua.
- No hay resultado anterior y el primer intento es parcial: mostrar solo datos parciales etiquetados y ausencia de un total completo confirmado.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE consultar únicamente recursos públicos del perfil Vic2910 y sus repositorios propios, incluidas sus bifurcaciones públicas, dentro del alcance definido, incluyendo todas las páginas de repositorios y commits necesarias para declarar ese alcance completo. Las bifurcaciones se someterán a las mismas reglas de atribución y deduplicación de FR-003 (escenarios 2.1 y 2.7).
- **FR-002**: Resultados, alcance y estado de sincronización DEBEN conservarse para consultas posteriores; abrir el dashboard no generará consultas a GitHub por visitante o por recarga (escenarios 1.1 y 2.4).
- **FR-003**: El conteo DEBE deduplicar por identidad de repositorio y SHA, y atribuir solo commits con vínculo de autor verificable a Vic2910; pertenencia del repositorio, coincidencia nominal o actividad como integrador no bastan por sí solas (escenarios 2.1–2.3).
- **FR-004**: El dashboard DEBE diferenciar proyectos publicados y borradores, mensajes totales actuales y pendientes; mensajes eliminados quedan excluidos y proyectos retirados no se suman a publicados ni borradores (escenarios 1.1 y 1.5).
- **FR-005**: Cada conteo de commits DEBE indicar período, repositorios, ramas, reglas de atribución y deduplicación, exclusiones, completitud y fecha de última comprobación satisfactoria. DEBE explicar que incluye bifurcaciones públicas propias y que un mismo SHA atribuible puede contar una vez en cada repositorio del alcance; no representa SHA únicos globales ni equivaldrá automáticamente a experiencia laboral o historial global (escenarios 3.3 y 2.7).
- **FR-006**: Las actualizaciones DEBEN respetar restricciones primarias y secundarias del proveedor, sus instrucciones de espera, comprobaciones sin cambios cuando procedan, espera progresiva y suspensión temporal sin eludir cuotas (escenarios 3.1 y 3.4).
- **FR-007**: El administrador DEBE poder solicitar actualización explícita, con un intervalo local inicial mínimo de 60 minutos entre inicios de intentos, ampliado cuando las restricciones lo exijan. No se permitirán sincronizaciones simultáneas duplicadas (escenarios 2.4 y 2.5).
- **FR-008**: Ante fallos o parcialidad se DEBEN conservar e identificar los últimos datos válidos, distinguir cero comprobado, dato ausente y error, y mostrar por separado el intento parcial sin declararlo completo ni adelantar la fecha satisfactoria (escenarios 1.2, 1.3, 3.2 y 3.5).
- **FR-009**: Dashboard y sincronización DEBEN restringirse al administrador autorizado, incluso en solicitudes directas. Cualquier credencial opcional de lectura permanecerá en configuración protegida y no aparecerá en navegador, registros, repositorio o errores (escenario 1.4 y revisión de secretos).
- **FR-010**: Los flujos completos DEBEN cumplir WCAG 2.1 AA, con teclado, foco visible, explicaciones textuales y cambios de estado perceptibles con tecnologías de asistencia (escenario 3.6 y evaluación de criterios aplicables).
- **FR-011**: La sincronización NO DEBE acceder a repositorios privados ni crear o publicar automáticamente proyectos editoriales (escenarios 2.1 y 2.6; revisión del alcance consultado).
- **FR-012**: Un resultado solo DEBE declararse satisfactorio tras completar y conservar su alcance; repeticiones sin cambios no duplicarán contribuciones y los cambios de alcance no mezclarán resultados incompatibles (escenarios 2.2, 2.4 y 3.4; casos de cambio de rama e historial).

### Key Entities

- **Repositorio sincronizado**: identidad pública estable, nombre, dirección, propiedad, condición de bifurcación, rama observada y estado de disponibilidad.
- **Commit sincronizado**: repositorio, SHA, fecha de autoría, vínculo verificable del autor o atribución desconocida y ramas observadas.
- **Sincronización**: alcance, período, estado, páginas procesadas, inicio y finalización, fecha satisfactoria, restricciones y próximo intento permitido.
- **Resumen administrativo**: cantidades actuales de proyectos y mensajes, conteo de commits de un alcance identificado, fecha de consulta y estado independiente de cada métrica.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Repetir el 100 % de sincronizaciones de prueba sin cambios mantiene idéntico conteo de contribuciones, sin duplicar pares repositorio/SHA.
- **SC-002**: Todos los commits ajenos o de autoría desconocida evaluados aportan cero al conteo propio, incluidos los heredados en bifurcaciones propias; todos los atribuibles dentro del alcance completo se cuentan una vez por repositorio, incluidas las bifurcaciones públicas propias. Los casos con un mismo SHA en varios repositorios muestran la explicación exigida por FR-005.
- **SC-003**: En el 100 % de fallos y restricciones evaluados se preserva el último resultado válido y se muestra su antigüedad sin sustituirlo por cero ni por un parcial presentado como completo.
- **SC-004**: Todos los conteos evaluados coinciden con los registros correspondientes al alcance y fecha mostrados; todos los resultados parciales se identifican y explican.
- **SC-005**: Abrir o recargar el dashboard en veinte consultas consecutivas produce cero nuevas consultas a GitHub. Los intentos dentro de una espera activa o durante otra sincronización producen cero sincronizaciones adicionales.
- **SC-006**: El 100 % de accesos no autorizados evaluados se rechaza sin revelar métricas privadas y la revisión de superficies expuestas encuentra cero credenciales de lectura.
- **SC-007**: Los flujos completos presentan cero incumplimientos aplicables de WCAG 2.1 A y AA tras evaluación automática y revisión manual con teclado y lector de pantalla.
- **SC-008**: Con datos de prueba, Victor identifica sin ayuda en menos de un minuto la cantidad de mensajes pendientes, la fecha del último resultado válido y si el conteo de commits es parcial o completo para su alcance.

## Assumptions

- Depende de `002-administracion` para acceso; integra proyectos de `003-gestion-proyectos` y mensajes de `004-contacto-privado`. Puede evaluarse con datos y respuestas controladas, sin modificar datos productivos.
- Alcance inicial: repositorios públicos propiedad de Vic2910 y sus ramas predeterminadas; Victor confirmó incluir las bifurcaciones públicas propias en la sesión de aclaración de 2026-10-27. Se cuentan commits atribuibles accesibles desde el primero hasta el corte de cada sincronización; se excluyen repositorios ajenos y otras ramas. No representa toda la actividad de GitHub ni un conteo de SHA únicos entre repositorios.
- Se utiliza la fecha de autoría para el período de actividad. La atribución requiere la asociación verificable del autor con la identidad del perfil; no se deduce únicamente de nombres o correos coincidentes.
- Un resultado completo describe el alcance observado en esa ejecución, no una instantánea global simultánea del proveedor. Los cambios detectados durante el recorrido se advertirán si impiden acreditar su completitud.
- El intervalo de 60 minutos es una propuesta local del adjunto, sujeta a validación antes de implementación; no promete disponibilidad ni cuota externa. Los límites del proveedor prevalecen.
- La actualización inicial será manual y explícita desde administración; una programación automática no es necesaria para aceptar esta funcionalidad.
- Los proyectos retirados pueden mostrarse por separado, pero no son una métrica obligatoria. Mensajes totales significa registros actualmente conservados, sin eliminados por acción manual o conservación.
- Los intentos parciales pueden conservar progreso para reanudar, pero no reemplazan el último resumen completo compatible. Si cambia el alcance, ambos se etiquetan por separado hasta disponer de un resultado completo del nuevo alcance.
- La constitución 1.0.0 en `.specify/memory/constitution.md` sigue siendo normativa para arquitectura, integración con GitHub, persistencia, seguridad, gratuidad y validación. Sus decisiones técnicas se concretarán durante planificación sin enmendarlas aquí.
- Los criterios son objetivos de aceptación, no resultados ya verificados. Se comprobarán paginación, atribución, deduplicación, permisos y restricciones con datos aislados, complementados por revisión manual de accesibilidad.
