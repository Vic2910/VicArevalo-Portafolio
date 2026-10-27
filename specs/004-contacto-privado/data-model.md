# Data model: 004-contacto-privado

Diseño condicionado a RET-001 de plan.md. No se acredita eliminación estricta por definir tablas/purga. No hay mensajes reales ni migraciones ejecutadas. Esquema private no expuesto y RLS; timestamptz UTC y reloj DB como autoridad.

## Entidades

| Tabla propuesta | Campos | Invariantes |
|---|---|---|
| contact_messages | id UUID PK, request_hash único, sender_name, reply_email, body, received_at, expires_at, state pending/reviewed, lock_version | Estado inicial pending; received_at y expires_at inmutables, expires_at=received_at+90*24 h. Solo admin vigente lee contenido vivo; marcar no toca fechas. |
| contact_requests | request_hash PK, form_session_hash, payload_hmac nullable, accepted_at, token_expires_at, state received/deleted, message_id nullable | Recibo técnico de una solicitud, sin nombre/correo/cuerpo. Hash de nonce aleatorio, no del remitente. Único por token. Eliminación limpia payload_hmac y message_id; token expirado nunca vuelve a insertar. |
| contact_form_sessions | opaque_hash PK, csrf_nonce, created_at, expires_at | Sesión técnica anónima 24 h, sin IP/email/fingerprint ni payload. Cookie Secure/HttpOnly/SameSite=Lax y Path=/contacto; no confundir con sesión administrativa. |
| contact_rate_buckets | scope session/hour/global-hour/global-day, bucket_key, window_start, accepted_count, expires_at | Sin datos personales; sesión por hash aleatorio. Límites compartidos configurables, inicial 3/h por sesión,30/h y 100/día globales. Reintentos no consumen otra recepción. |
| contact_policy | singleton PK, retention_days=90, approved_at, evidence_reference, strict_gate blocked/verified, configured_at |90 días aprobado por spec; evidencia strict_gate no acreditada. Sin UI pública que lo modifique; booleano aislado no basta para habilitar. |
| contact_retention_health | singleton PK, status blocked/healthy/failed/stale, last_attempt_at, last_success_at, next_due_at, due_count, failure_code | Estado operativo sin mensajes; salud reciente no acredita RET-001. Retomar requiere evidencia válida y resolver todos los vencidos/fallos. |
| contact_deletion_records | occurred_at, reason manual/expired, result success/failure | Solo fecha, motivo y resultado; sin remitente, cuerpo, payload hash o ID enlazable a comunicación eliminada. ID interno técnico de fila si necesario, no message_id. |
| contact_admin_operations | operation_hash PK, action, actor_id, result, completed_at | Recibo de mutación administrativa sin contenido; tras eliminación no retener referencia recuperable al mensaje. Permite resolver resultado incierto mediante capability ligada a sesión. |
| contact_capacity | singleton PK, stored_count, stored_text_bytes, updated_at | Control transaccional de hasta 1000 filas almacenadas/20 MiB, incluidos vencidos aún no purgados y margen DB compartido; contador no reemplaza conteo autoritativo de bandeja. |

Índices: request_hash único; expires_at para purga/lectura; received_at DESC,id DESC para bandeja; state/received_at para pendientes; hashes y vencimientos de recibos/sesiones; claves únicas de buckets. No índice de correo ni texto completo del mensaje. Sin columna IP, user-agent, adjunto o resultado de análisis IA.

## Validación de datos personales

Aplicar trim Unicode exterior antes de límites; medir caracteres como puntos de código Unicode, no bytes. Nombre 1–100, correo válido hasta 254 y mensaje 10–5000. Preservar espacios interiores y saltos del cuerpo; no normalizar/eliminar caracteres para satisfacer mínimos. Correo sintáctico con validador establecido, sin DNS ni comprobar existencia; conservar entrada trim para mostrar al admin, sin lowercase destructivo de parte local. NUL/controles no textuales inválidos; HTML textual se almacena/muestra escapado, no se interpreta.

Formularios solo solicitan esos tres datos personales. CSRF, token de solicitud y sesión son controles técnicos, no nuevos campos personales. Aviso de finalidad y 90 días visible antes de ingreso; no checkbox de consentimiento adicional inventado. No valores reales en fixtures/documentos/logs.

## Solicitud e idempotencia

Token servidor firmado: nonce aleatorio>=256 bits, issued_at, accept_until=issued_at+24 h, versión de firma y vínculo a sesión de formulario. No datos personales en token/cookie/URL. Ventana de reconocimiento operativo:24 h desde emisión, nunca se amplía por reintento. Antes de insertar, validar firma/vínculo/tiempo; expired=410 sin nueva recepción.

Mientras token vigente: request_hash único y mensaje pendiente se insertan atómicamente; payload_hmac keyed permite detectar otro cuerpo bajo mismo token sin guardar copia del texto. Mismo token/cuerpo devuelve confirmación de misma recepción; otro cuerpo=409, no otro mensaje. El HMAC sigue siendo derivado sensible: nunca logs y se elimina con recibo o borrado del mensaje.

Eliminación manual temprana cambia recibo a deleted, elimina digest/message_id y mantiene solo tombstone técnica hasta token_expires_at. Reintento válido recibe «La recepción anterior ya no está disponible», sin recrear ni revelar contenido. Después de 24 h se limpia recibo/sesión/buckets vencidos; token expirado se rechaza incluso sin tombstone. A 90 días no se necesita un recibo con datos de remitente para impedir replay. Nuevo token emitido para un nuevo envío explícito es otra solicitud, aunque el texto coincida.

## Estados y transiciones

- Mensaje nuevo→pending; abrir GET no cambia state ni fechas. POST explícito pasa pending↔reviewed con comparación de lock_version. Dos pestañas desactualizadas=409.
- Eliminación manual: confirmación explícita de id/version; transacción quita mensaje, actualiza recibo si aún existe, capacidad, constancia mínima y recibo administrativo sanitizado. Cancelar no modifica mensaje/conteos.
- Al clock>=expires_at, todos los lectores/conteos excluyen el mensaje; esta es caducidad de acceso, no prueba de destrucción. Purga candidata borra registros vencidos y derivados sensibles con constancia mínima. La garantía estricta sigue en ERROR hasta acreditarse también copias/físico.
- Fallos no confirman cambio/eliminación. Resultado de commit incierto se consulta mediante recibo; reautenticar nunca repite acción. Estado vacío solo después de consulta correcta, no como conversión de excepción.

Bandeja y cantidades se calculan en un mismo snapshot/referencia temporal de lectura con expires_at futuro, orden más reciente primero; paginación 25 y conteos total/pending/reviewed coherentes. Ningún consumidor público accede a esas cantidades. Dashboard futuro usa mismo filtro/guard, no una copia desactualizada.

## Retención técnica y copias

Sesiones/recibos técnicos viven máximo 24 h desde emisión; no contienen comunicación. Constancias mínimas pueden conservarse 90 días como propuesta operativa, sin contenido o correlación al remitente. No duplicar borrados en security_events con mensaje/correo/ID que reconstituya comunicación. Alertas solo código/fecha/resultado operativo.

No exportaciones/dumps de mensajes gestionados por aplicación ni caché de contenido. Copias físicas/WAL del proveedor requieren evidencia específica de cumplimiento: ausencia de backup accesible en Free no demuestra ausencia de copias. No se seleccionó mecanismo conforme de destrucción estricta; recepción real continúa bloqueada.
