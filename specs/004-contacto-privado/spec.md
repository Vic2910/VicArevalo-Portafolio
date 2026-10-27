# Feature Specification: Contacto persistente y bandeja privada

**Feature Branch**: `004-contacto` (referencia del adjunto; no se ha creado una rama, la actual es `main`).

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Recibir mensajes de visitantes, persistirlos y permitir a Victor gestionarlos de forma privada."

## Clarifications

### Session 2026-10-27

- Q: ¿Durante cuánto tiempo deben conservarse los mensajes desde su recepción antes de eliminarlos automáticamente? → A: 90 días desde la recepción, estén pendientes o revisados; leerlos o cambiar su estado no amplía el plazo.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Enviar un mensaje (Priority: P1)

Como visitante quiero enviar mi nombre, correo y mensaje y conocer si fue recibido para contactar a Victor.

**Why this priority**: Es la función mínima de contacto y no depende de correo saliente.

**Independent Test**: Con una política de conservación de prueba y datos aislados, enviar un mensaje válido y comprobar que existe una sola recepción persistida.

**Acceptance Scenarios**:

1. **Given** el envío está habilitado y completé datos válidos tras consultar el aviso de finalidad y conservación, **When** envío, **Then** se confirma recepción únicamente después de conservar el mensaje con estado pendiente.
2. **Given** falla la persistencia o se agota la cuota, **When** envío, **Then** recibo un error accesible sin confirmación de éxito y puedo reintentar.
3. **Given** hay campos vacíos, correo inválido o longitudes fuera de los límites, **When** envío, **Then** se indican errores asociados a los campos sin guardar un mensaje inválido.
4. **Given** pulso dos veces o repito la misma solicitud tras perder su confirmación, **When** se procesa de nuevo, **Then** queda un único mensaje y la confirmación corresponde a esa recepción.
5. **Given** no existe un plazo aprobado o no está operativo su mecanismo de eliminación, **When** abro o intento enviar el formulario, **Then** se explica la indisponibilidad y no se habilitan campos ni se aceptan datos de contacto.
6. **Given** alcanzo el límite de frecuencia configurado, **When** vuelvo a enviar antes de poder reintentar, **Then** se informa de la espera sin guardar un nuevo mensaje ni imponer una barrera inaccesible.
7. **Given** uso teclado y lector de pantalla, **When** completo o corrijo el formulario, **Then** puedo operar todos los controles y percibir errores, espera y confirmación.

---

### User Story 2 - Consultar y marcar mensajes (Priority: P1)

Como Victor quiero leer mensajes y marcarlos para distinguir pendientes de revisados sin hacer públicas las comunicaciones.

**Why this priority**: Hace posible atender solicitudes con privacidad.

**Independent Test**: Con una sesión administrativa y mensajes de prueba, consultar uno, cambiar su estado y volver a abrir la bandeja.

**Acceptance Scenarios**:

1. **Given** soy administrador autorizado y existe un mensaje nuevo, **When** abro la bandeja y el mensaje, **Then** veo nombre, correo de respuesta, texto, fecha y estado pendiente; abrirlo no cambia el estado por sí solo.
2. **Given** selecciono un mensaje, **When** lo marco revisado o pendiente y vuelvo a consultar, **Then** se conserva el estado confirmado y las cantidades actuales coinciden con los mensajes conservados.
3. **Given** soy visitante o una persona identificada sin permiso, **When** intento listar, leer, marcar o eliminar mensajes, incluso por dirección directa, **Then** se deniega la operación sin revelar contenido, correos, cantidades privadas ni alterar datos.
4. **Given** caducó mi sesión o falla la persistencia, **When** intento cambiar un estado, **Then** se indica que no se confirmó el cambio y no se muestra falsamente como guardado.
5. **Given** un mensaje contiene instrucciones activas o texto malicioso, **When** lo consulto, **Then** se presenta como contenido sin ejecutar esas instrucciones ni enviar información a terceros o IA.
6. **Given** no hay mensajes o falla la lectura, **When** abro la bandeja, **Then** distingo un estado vacío real de un error, sin interpretar el fallo como cero mensajes.
7. **Given** uso teclado y lector de pantalla, **When** consulto y marco mensajes, **Then** puedo completar las tareas y conocer su resultado.

---

### User Story 3 - Eliminar y aplicar la conservación (Priority: P2)

Como Victor quiero eliminar mensajes y aplicar su plazo de conservación para evitar retener datos innecesarios.

**Why this priority**: Permite gestionar la bandeja; la eliminación por vencimiento es además obligatoria antes de activar la recepción, con independencia de esta prioridad.

**Independent Test**: Con un plazo aprobado de prueba, cancelar y confirmar una eliminación y evaluar mensajes antes y después de vencer.

**Acceptance Scenarios**:

1. **Given** selecciono eliminar un mensaje, **When** cancelo la confirmación, **Then** permanece sin cambios; si confirmo y se completa la eliminación, deja de estar disponible en la bandeja y en cantidades actuales.
2. **Given** un mensaje alcanza los 90 días desde su recepción, **When** vence, **Then** se elimina automáticamente independientemente de su estado y queda solo constancia mínima de fecha, motivo y resultado, sin nombre, correo ni texto.
3. **Given** un mensaje aún no cumple 90 días desde su recepción, **When** se aplica la conservación sin una eliminación manual, **Then** permanece disponible hasta su vencimiento; leerlo o cambiar su estado no reinicia ni amplía el plazo.
4. **Given** falla la eliminación manual, **When** termina el intento, **Then** se informa del fallo sin confirmar éxito y puede reintentarse.
5. **Given** no puede garantizarse la eliminación por vencimiento, **When** se detecta el fallo, **Then** se suspende la recepción de nuevos mensajes, se informa al administrador y se reintenta la eliminación sin extender silenciosamente el plazo.
6. **Given** uso teclado y lector de pantalla, **When** confirmo o cancelo una eliminación, **Then** entiendo la consecuencia, puedo elegir ambas acciones y percibo el resultado.

### Edge Cases

- Campos compuestos solo por espacios: no satisfacen los mínimos tras retirar espacios externos.
- Longitudes exactamente en los límites: se aceptan si el resto del contenido es válido; un carácter fuera del límite se rechaza.
- Interrupción después de guardar pero antes de confirmar: el reintento de la misma solicitud no crea otro mensaje.
- Mensaje eliminado o vencido antes de un reintento: no se recrea por repetición de la misma solicitud; se indica que su recepción anterior ya no está disponible, sin revelar contenido.
- Spam o frecuencia excesiva: comunicar espera con controles accesibles, sin ampliar la recogida de datos personales del formulario.
- Plazo pendiente: no habilitar recepción ni conservar mensajes indefinidamente como alternativa.
- Límite de conservación: antes de cumplir 90 días el mensaje permanece disponible salvo eliminación manual; al cumplirlos vence y se elimina automáticamente, tanto si está pendiente como revisado.
- Sesión administrativa vencida: denegar lectura y cambios; reautenticar no repite automáticamente una eliminación.
- Fallo de conservación: advertir y suspender nuevos envíos; la suspensión no sustituye la obligación de eliminar los datos vencidos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El formulario DEBE recopilar únicamente nombre, correo de respuesta y mensaje, con finalidad de contacto y plazo de conservación visibles antes del envío (escenario 1.1).
- **FR-002**: El sistema DEBE validar todas las solicitudes aunque el visitante omita las validaciones del formulario: nombre de 1 a 100 caracteres, correo válido de hasta 254 y mensaje de 10 a 5000, retirando espacios externos antes de evaluar límites; no guardará entradas inválidas (escenario 1.3 y casos de límites).
- **FR-003**: El sistema DEBE confirmar recepción solo tras persistir exactamente un mensaje pendiente por solicitud; repetir esa misma solicitud no generará duplicados ni recreará mensajes eliminados (escenarios 1.1 y 1.4; casos de reintento).
- **FR-004**: Ante fallo o resultado incierto de persistencia, el sistema DEBE indicar que no confirmó la recepción y permitir reintentar sin afirmar que el mensaje se guardó o que necesariamente no existe (escenario 1.2).
- **FR-005**: Solo el administrador autorizado DEBE poder listar, leer, marcar y eliminar mensajes o consultar cantidades privadas; la recepción pública no concederá capacidad de consulta ni acceso general a la bandeja (escenario 2.3).
- **FR-006**: El sistema DEBE permitir marcar explícitamente pendiente o revisado y conservar el estado; leer no lo modificará automáticamente (escenarios 2.1 y 2.2).
- **FR-007**: Eliminar manualmente DEBE requerir confirmación. Cancelar no alterará datos; completar la eliminación retirará el mensaje de consultas y cantidades actuales (escenario 3.1).
- **FR-008**: El plazo aprobado por Victor es de 90 días desde la recepción. Este plazo DEBE estar configurado y debe existir un mecanismo efectivo documentado de eliminación antes de habilitar la recepción. Sin ellos no se habilitarán campos ni se aceptarán datos de contacto (escenario 1.5).
- **FR-009**: El sistema DEBE eliminar automáticamente los mensajes al cumplir 90 días desde su recepción, cualquiera que sea su estado, sin reiniciar ni ampliar el plazo al leer o marcar; conservará solo fecha, motivo y resultado de la eliminación sin datos del remitente ni contenido (escenarios 3.2 y 3.3).
- **FR-010**: El sistema DEBE aplicar límites de frecuencia configurables, protección antispam accesible y protección frente a envíos inducidos cuando corresponda; al bloquear informará cuándo reintentar sin guardar otro mensaje (escenario 1.6 y revisión de envíos no autorizados).
- **FR-011**: El contenido recibido DEBE mostrarse sin ejecutar instrucciones. Los mensajes no se enviarán a IA, registros de diagnóstico ni exportaciones públicas (escenario 2.5 y revisión de las salidas de datos).
- **FR-012**: Recibir y gestionar mensajes NO DEBE depender de correo saliente o notificaciones externas (historias 1 y 2 verificadas con esas funciones ausentes).
- **FR-013**: Formulario, bandeja y eliminación DEBEN cumplir WCAG 2.1 AA, incluyendo teclado, foco visible, etiquetas, errores asociados y anuncios accesibles de estado (escenarios 1.7, 2.7 y 3.6; revisión de todos los criterios aplicables).
- **FR-014**: Cambios y eliminaciones DEBEN confirmar éxito solo tras persistir; caducidad de sesión o fallos mostrarán el estado no confirmado sin repetir automáticamente acciones al reautenticar (escenarios 2.4 y 3.4).
- **FR-015**: Si falla el cumplimiento de conservación, el sistema DEBE informar al administrador, suspender nuevas recepciones y reintentar la eliminación pendiente sin ampliar tácitamente el plazo aprobado (escenario 3.5).
- **FR-016**: La bandeja DEBE distinguir ausencia de mensajes e indisponibilidad de lectura, y sus cantidades actuales excluirán mensajes eliminados (escenarios 2.2, 2.6 y 3.1).

### Key Entities

- **Mensaje**: identificador, nombre, correo de respuesta, contenido, fecha de recepción, vencimiento y estado pendiente o revisado.
- **Política de conservación**: plazo de 90 días desde la recepción aprobado por Victor, fecha de vigencia, criterio de vencimiento y condición de habilitación de la recepción.
- **Solicitud de contacto**: identidad de un envío y resultado, suficiente para reconocer sus reintentos sin crear mensajes duplicados; no añade campos personales al formulario.
- **Constancia de eliminación**: fecha, motivo manual o por vencimiento y resultado, sin nombre, correo ni texto del mensaje.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de confirmaciones evaluadas corresponde a exactamente un mensaje persistido por solicitud, incluso con doble pulsación y pérdida de confirmación.
- **SC-002**: Cero visitantes e identidades sin permiso evaluados pueden consultar contenido, remitentes o cantidades privadas, ni modificar mensajes.
- **SC-003**: El 100 % de entradas inválidas definidas se rechaza sin persistencia y con indicación accesible; se aceptan los límites válidos exactos.
- **SC-004**: El 100 % de mensajes evaluados que no se hayan eliminado manualmente se elimina automáticamente al cumplir 90 días desde su recepción, sin depender de estar pendientes o revisados; leer o marcar no altera su vencimiento y las constancias contienen cero datos de remitentes o textos.
- **SC-005**: Sin plazo aprobado o mecanismo efectivo, el 100 % de intentos de recepción se bloquea sin aceptar datos de contacto. Los fallos de conservación evaluados suspenden nuevos envíos y generan aviso al administrador.
- **SC-006**: El 100 % de cambios de estado y eliminaciones confirmados se refleja al reabrir la bandeja; cancelar produce cero cambios y los fallos no producen confirmaciones falsas.
- **SC-007**: Los flujos completos presentan cero incumplimientos aplicables de WCAG 2.1 A y AA tras evaluación automática y revisión manual con teclado y lector de pantalla.
- **SC-008**: Con datos preparados, un visitante completa un envío válido sin ayuda en menos de dos minutos y Victor puede localizar, leer y marcar el mensaje en menos de un minuto.

## Assumptions

- La bandeja depende de `002-administracion`; recepción y conservación pueden evaluarse con persistencia e identidades aisladas.
- Victor aprobó un plazo de conservación de 90 días desde la recepción en la sesión de aclaración de 2026-10-27. La activación pública sigue condicionada a configurar ese plazo y verificar el mecanismo efectivo de eliminación. Las pruebas usarán datos aislados y tiempo controlado para evaluar los límites sin esperar 90 días reales.
- Los límites de longitud son propuestas iniciales del adjunto. Para evaluar caracteres se considerarán caracteres Unicode, no bytes; se conservarán espacios interiores y saltos de línea del mensaje.
- El umbral y la ventana antispam se definirán durante planificación según la cuota gratuita y se comprobarán antes de habilitar recepción. También se documentarán la cobertura de reintentos, el período mínimo de reconocimiento de una misma solicitud y el tratamiento de copias de respaldo para cumplir la conservación sin duplicar contenido privado.
- El vencimiento se calcula desde la recepción; leer o cambiar de estado no lo extiende. El plazo aprobado debe incluir las garantías efectivas de eliminación, sin retención indefinida ni tolerancias ocultas.
- La bandeja muestra primero los mensajes más recientes y distingue pendientes y revisados. No se incluyen respuestas desde el panel, adjuntos, exportación, correo saliente ni análisis de mensajes con IA.
- Los indicadores consumidos por otras funcionalidades deben usar únicamente mensajes todavía conservados. La construcción de un dashboard independiente queda fuera de esta entrega.
- La constitución 1.0.0 de `.specify/memory/constitution.md` conserva su autoridad sobre persistencia, arquitectura, seguridad, gratuidad y validación. Las decisiones técnicas del adjunto siguen sujetas a ella y se concretarán en planificación.
- Los criterios son objetivos de aceptación, no resultados ya verificados. La evaluación usará datos aislados y roles representativos, sin mensajes reales ni cambios sobre información productiva.
