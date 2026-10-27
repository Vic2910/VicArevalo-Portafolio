# Data model: 007-ia-asistida

Diseño lógico sin migraciones/ejecución. Diferenciar metadatos técnicos de texto editorial:ninguna tabla nueva almacena prompt, contexto, salida, fragmentos truncados o embedding de sugerencia. Solo texto final aceptado persiste en revisión habitual 002/003/005.

## Entidades efímeras (RAM, sin tablas)

| Entidad | Campos | Reglas |
|---|---|---|
| EditorialRequest | editor_nonce, request_id, purpose improve/translate, source_ref, source_revision/version, selection_text, context_text, source_language, target_language, target_ref/field, client_field_digest | Preview explícito antes de envío, fuentes allowlist y límites; sin contexto automático de DB/mensajes/secretos. |
| SourceBinding | referencia/versión de fuente y destino, hashes de selección/contexto/campo cliente, rangos opcionales, idioma, nonce de revisión | Proof firmado devuelto al cliente, no historial en DB. Hash es ligadura técnica, nunca aprobación de hechos. |
| Suggestion | request_id, language, text, status unapproved/stale/needs_information/incomplete, missing_information, source_binding | Solo revisión activa en DOM y RAM de petición; editada por Victor, sin autosave, aprobación ni persistencia original. |
| ReviewDecision | accept_as_draft/discard/cancel, edited_value, operation_id | Aceptación explícita pasa validaciones/editorial y crea nueva revisión solo del campo. Descarte/cancelación no cambia contenido. |
| LocalModelProcess | process_handle, loopback_port, transport_capability, deadline, memory/input/output buffers | Entorno mínimo sin credenciales del proyecto, sin red externa/tools; destruido por generación. No KV persistente. |

## Controles técnicos persistidos en private

| Tabla | Campos principales | Reglas |
|---|---|---|
| ai_editor_instances | nonce PK aleatorio, user_id, admin_session_id, target_kind/id/field, generation_epoch, state active/closed, heartbeat_at, lease_until, expires_at | Sin texto. Una revisión activa por admin/campo; nueva instancia invalida anterior y requests ligados. expires_at nunca supera sesión administrativa. |
| ai_request_controls | request_id PK, editor_nonce, user_id, state reserved/running/delivered/cancelled/expired/failed/accepted, runtime_manifest_id, owner/fence, started_at, deadline_at, result_code | Solo coordinación/cuota; no output/selection/context/hash personal. Delivered no permite recuperar output porGET. Request fallido no se reanuda con texto desde DB. |
| ai_capacity | singleton PK, active_request_id nullable, process_owner, fence, lease_until, runtime_health | Una generación global, capacidad no confirmada no permite spawn duplicado. |
| ai_rate_buckets | user_id/global scope, window_start, starts_count, expires_at |6 inicios/10 min por admin y 20/h global; contar cuando se admite inferencia, no preview inválido. Sin payload o datos de visitantes. |
| ai_accept_receipts | operation_id PK, actor_id, request_id, target_kind/id, resulting_revision_id, result, committed_at | Recibo de guardado, sin texto generado original/digest de propuesta; revisión resultante normal contiene texto final aceptado. |

Tablas privadas sin exposición Data API y RLS. Roles editoriales existentes reciben solo permisos técnicos mínimos de validar/consumir nonce al aceptar; la transacción de aceptación debe actualizar revisión/estado/recibo/auditoría de forma íntegra. Generación no obtiene permisos de publicación/aprobación. Logs guardan tipo/resultado/fecha/actor/request/código y tiempos sin payload ni hashes que sirvan de historial textual.

Metadatos vencidos se limpian en mantenimiento acotado (propuesta 24 h); no recuperan sugerencia y no conservan su contenido. Auditoría mínima sigue 002, sin textos. No convertir controles en listado de sugerencias ni reconstruir respuesta desde caché, jobs o modelo.

## Fuentes y destinos permitidos

- improve:profile.summary de 002 o project.description de 003, selección actual editorial mostrada por Victor, incluida edición manual aún no guardada. Solo fragmento seleccionado/contexto explícito llega al modelo.
- translate es→en:fuente publicada aprobada y hash vigente 001/003/005; destino campo de borrador de traducción 005. Traducir un fragmento no completa ni aprueba el resto de la variante.
- translate en→es:fuente inglesa aprobada y vigente 005; destino borrador español de perfil/proyecto mediante 002/003. Publicación española sigue proceso normal e invalida traducciones si hechos/texto cambian.
- Allowlist de rutas/campos fija; no contacts, mensajes 004, métricas 006, archivos, configuración o base arbitraria. No aceptar una URI/SQL/field path introducida por modelo como selector de datos.

Registro/ref de fuente no implica enviar toda entidad. El backend puede leer solo el campo necesario y su versión para verificarlo, no autoañadir perfil/contexto de otros módulos. Preview muestra exactamente selección y contexto a transmitir, idioma y límites; cambios posteriores exigen renovar confirmación.

## Versiones y campos

Base de servidor:revision_id/lock_version del registro destino; base de cliente:digest del campo actual y rango elegido, con índice Unicode por puntos de código. Si se usan selectionStart/selectionEnd del navegador, convertir desde UTF-16 y comprobar substring para no romper caracteres/surrogates. Rango de fuente y destino son distintos al traducir, no se infiere correspondencia entre idiomas.

Respuesta compara instancia/epoch/request y digest del campo cliente actual. Campo o fuente cambiado→stale; no aplicar automáticamente. Aceptación revalida versión fuente/aprobación si traducción y lock_version del destino; conflicto 409 obliga nueva revisión/generación o edición manual explícita, no overwrites. Proof ligado a sesión/editor/target/acción no concede publicación ni sirve tras recarga.

Aceptar persiste solo valor final del campo elegido:el servicio clona última revisión guardada, sustituye ese campo validado y conserva otros campos persistidos. Otras ediciones aún sin guardar en navegador permanecen allí y no se guardan automáticamente. Si se reemplaza solo un rango, cliente muestra fusión/campo completo antes de aceptar y conserva exterior; servidor valida campo final con límites habituales. El texto generado se puede corregir antes de guardar, sin elevar estado aprobado.

## Ciclo de vida

1. Abrir editor→nuevo nonce enRAM/DOM y registro técnico; cerrar/reabrir/recargar nunca recupera resultado anterior.
2. Preview→validar fuente/privacidad/límites y emitir proof; sin modelo ni modificación editorial.
3. Generar→reserva técnica/cuota/fence y proceso local; input/output solo RAM. Respuesta completa válida se entrega una vez a petición original, marcada no aprobada; no endpoint para obtenerla después.
4. Editar propuesta→solo DOM. Aceptar→nueva revisión de borrador y recibo con commit; no aprobación/publicación. Descartar→limpiar propuesta y nonce de generación, datos previos intactos.
5. Cancelar/cerrar/recargar→invalidar request/epoch, abortar fetch y limpiar estado IA; proceso se termina al detectarlo. Heartbeat técnico 5 s/lease 15 s permite acotar abandono si pagehide no llega, sin prolongar sesión por tráfico de fondo. Reapertura invalida previamente por el mismo campo y rechaza toda respuesta vieja.
6. BFCache/pageshow inicializa estado IA vacío y nuevo nonce antes de exponer controles. Sin localStorage/sessionStorage/IndexedDB/ServiceWorker cache ni formulario persistente de propuesta. Borradores previamente guardados continúan por flujo normal.

Cierre abrupto no garantiza notificación instantánea al servidor o borrado forense de RAM; sí ausencia de persistencia/recuperación y descarte al invalidar/expirar. Proceso no tiene ruta de entrega a otra instancia. Cancelación lógica es inmediata aunque terminación física requiera breve cleanup.

## Límites y estado de modelo

source 1–1500 y contexto 0–500 caracteres Unicode; prompt completo<=3072 bytes UTF-8 antes de iniciar proceso, contexto 4096 y salida<=768 tokens+256 reserva. Cota conservadora del tokenizer fijado se valida contra fixtures al implementar; si no puede acreditarse, rechazar antes de transmitir, nunca recortar silenciosamente. Respuesta<=4000 caracteres/16 KiB, completa y estructuralmente válida; length stop/truncada=sin aceptación.

ModelManifest local:ID/revisión/pesoSHA 256/runtimeSHA 256/licencias/chat template/política de red/log/cache, límites y benchmark de hardware. Modelo ausente/mismatch/memoria insuficiente→unavailable; no descarga/cambio de proveedor automático. No nueva configuración remota en este alcance.
