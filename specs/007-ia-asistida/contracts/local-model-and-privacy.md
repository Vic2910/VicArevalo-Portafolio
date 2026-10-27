# Contract: modelo local, privacidad y aceptación como borrador

## Modalidad inicial

Qwen/Qwen2.5-1.5B-Instruct-GGUF Q4_K_M oficial y llama.cpp. Manifiesto fija revisión/hash/licencia de pesos/runtime, plantilla y límites. Binarios/modelo por ruta local previamente aprovisionada, nunca URL introducida por cliente ni descarga durante solicitud. Runtime MIT y pesos Apache-2.0 con avisos conservados. No proveedor remoto/telemetría/inferencia de terceros ni autorización implícita por formato OpenAI-compatible.

Local significa mismo host backend; no llamar loopback del navegador ni abrir túnel desde hosting al escritorio. Si host gratuito no tiene memoria, asistencia unavailable, no fallback. Umbral conservador 4 GiB libres y prueba de CPU/memoria antes de habilitar, sin afirmar que sea requisito oficial. Recursos para editor manual/WSGI reservados; inferencia nunca monopoliza todos los handlers de cancelación/edición.

## Aislamiento del runtime

Proceso llama-server por generación, host 127.0.0.1 y puerto efímero, una solicitud, sin proxy/servidor público. Clave efímera de transporte local por entorno dedicado LLAMA_API_KEY (no argv/log/DB), jamás incluida en prompt. Navegador no conoce puerto/clave ni llama al modelo directamente. Parent solo permite rutas locales necesarias; no fetch de endpoints arbitrarios del usuario/modelo.

Crear subprocess con lista de argumentos y shell=False, ejecutable/modelo de manifiesto verificado; oculto en Windows. Entorno allowlist de variables de sistema estrictamente necesarias y clave efímera, sin SUPABASE/DB/GITHUB/SECRET_KEY/HF_TOKEN, home de aplicación con secretos o credenciales heredadas. Modelo no recibe herramientas, servicios, DB, configuración, archivos de proyecto, roles administrativos o callbacks.

Configuración debe desactivar logs, cache de prompts/slots, webUI, autoload/download/model router, métricas detalladas y guardado de KV. Documentación actual soporta --offline, --log-disable, --no-cache-prompt, --no-webui y --no-slots; comprobar --help del build fijado, no adivinar flags. No slot-save-path, prompt files, media-path/file URLs o tools/MCP. Offline y aislamiento de salida de red verificables; si no pueden verificarse, no habilitar.

Prompt solo por request HTTP loopback en memoria tras gate de privacidad/límites; no comandos/archivos temporales con texto. stdout/stderr se descartan o reducen a códigos internos seguros, nunca se guardan payloads. Terminar proceso/grupo al final; sin KV/caché compartida entre revisiones. Gestionar job/process group para que cancelación/muerte del padre no deje proceso huérfano; si no puede confirmarse capacidad liberada, IA queda indisponible antes de lanzar otra.

## Fuente mínima y validación

Allowlist:profile.summary y project.description para improve; campos textuales publicados aprobados 005 y destinos de borrador permitidos para translate es/en. Sin mensajes 004, contacto/visitor data, métricas 006, credenciales, imágenes o contexto automático. Backend construye DTO de selección y contexto explícitos mostrados por Victor; no una consulta libre de DB.

Validar source 1–1500/context 0–500 caracteres Unicode y prompt serializado completo<=3072 bytes UTF-8 antes de iniciar/transmitir a runtime. Esta cota conservadora se acredita para tokenizer/plantilla fijados, contexto 4096 y reserva 768 salida+256 control; no usar endpoint modelo para contar tokens de una entrada ya fuera de límites. Si cambia tokenizer/template, revalidar cota; no recortar silenciosamente. Request<=64 KiB. Usuario ve límites y puede seleccionar fragmento menor.

Bloquear source_kind/field no permitido y patrones de credenciales identificados (claves API/JWT/PEM/configuración sensible) o contactos pegados no pertinentes, sin registrar/eco del valor. Revisar texto/contexto antes de envío y exigir confirmación de contenido editorial. No comparar contra secretos reales leyéndolos para construir prompt ni cargar tabla de mensajes como filtro. No prometer detección infalible de datos personales en texto libre; prevención principal es frontera de fuentes/permiso y revisión visible.

Prompt de sistema fijo pide mantener hechos/nombres/nivel académico, no crear logros/empleos/certificaciones y devolver needs_information si falta base. Fuente/contexto tratados como datos, no instrucciones de herramientas. Prompt no garantiza veracidad; salida siempre no aprobada y revisión humana obligatoria. No ejecutar razonamiento/instrucciones que aparezcan en fuente o respuesta.

## Generación y límites

Una reserva global en DB y una por revisión, rate 6 inicios/10 min por admin y 20/h global; lease/fencing evita duplicados entre procesos. Cuota se consume al admitir inferencia; validación fallida no inicia modelo. Inicio solo con guard 002 vigente, CSRF y preview_token ligado a texto/contexto/idioma/source/target/instancia.

Deadline total 60 s incluye arranque/carga/generación/lectura; memoria/CPU acotadas por process manager y benchmark previo, con prioridad de tareas manuales. Una inferencia lenta no bloquea guardado/publicación/CV; runtime no se carga al importar app ni al visitar una página.

Respuesta acotada 768 tokens,4000 caracteres/16 KiB y JSON estructurado con status suggestion/needs_information, language y texto/campos faltantes. finish_reason length, JSON incompleto, exceso o formato inválido=no propuesta aceptable, sin aplicar substring. Etiqueta de idioma no prueba traducción correcta. No procesar tool_calls, funciones, HTML o URLs como acciones; texto en textarea/textContent o escape Jinja, nunca innerHTML/eval/subprocess del modelo.

Fallo/ausencia/recursos insuficientes:estado útil y trabajo manual disponible. No reintentos automáticos con otro modelo/proveedor, descargas, billing o entrenamiento con solicitudes.

## Ciclo efímero, cancelación y recarga

Textos solo en memoria del padre/hijo durante petición y DOM de revisión actual. Controles DB guardan nonce/estado/fechas/cuota, no entrada/salida/digest de propuesta. No jobs persistentes con payload, tabla de sugerencias, historial, URL, session cookie o almacenamiento de navegador para recuperarlas.

Frontend al abrir obtiene nuevo editor_nonce y generation_epoch del campo; invalida anteriores. Al generar conserva request_id/proof enRAM y compara nonce/epoch/digest al recibir. Una respuesta vieja o fuente/campo editado no se inserta ni guarda; se anuncia desactualización y se requiere nueva revisión explícita. Cada entrega revalida permiso/sesión en servidor.

Cancelar primero marca request cancelado/epoch inválido y limpia resultado; AbortController corta espera del cliente. Proceso se termina al observar cancelación/control, con gracia acotada y kill si no finaliza. Descartar limpia DOM/control, sin tocar revisión guardada. Cerrar/pagehide intenta cerrar revisión; heartbeat técnico 5 s/lease 15 s acota abandono si el evento no llega. No se supone que cerrarHTTP cancela físicamente el modelo.

Reapertura/recarga crea nonce nuevo e invalida todo request anterior del mismo campo, independientemente de avisos perdidos. BFCache/pageshow borra estado IA antes de mostrar revisión y reabre instancia nueva; no rehidratar textarea de propuesta ni reenvío automático. Respuesta pendiente solo tiene canal de petición original, no ruta GET recuperable ni destino a editor nuevo. Borradores ya guardados quedan intactos.

Si DB/permiso/lease no verificables, terminar generación/descartar salida y fallar cerrado. Polling/heartbeat no prolongan sesión 002 ni autoriza lectura después de revocación. Metadatos de coordinación expiran y se limpian sin conservar texto; no se promete borrado forense de RAM, sino ausencia de persistencia y recuperación de propuestas.

## Aceptación y autoridad editorial

Generación jamás llama repositorio de escritura editorial. Accept es otra acción explícita de Victor con final_value revisado, confirmación de comprobar hechos, source proof y expected_revision/version; no puede elegir una acción del modelo como endpoint o target.

Revalidar fuente (aprobación/hash vigente al traducir), target/campo permitido, instancia activa, estado delivered, sesión/autoridad y versión. Comprobar que cliente no cambió campo sin nueva revisión. Si desactualizado 409, no overwrites ni herencia de aprobación. Validar final_value con reglas normales de campo, conservar resto de revisión guardada y persistir solo ese campo en borrador. Otras ediciones no guardadas permanecen cliente y no se guardan implícitamente.

Transacción compartida del servicio editorial guarda revisión, consume nonce, crea recibo y auditoría mínima. Extender grants técnicos de roles existentes para esto, sin permiso nuevo de publicación/approval en 007. Rollback mantiene último estado; commit incierto consulta recibo sin recuperar sugerencia original. operation_id igual/cuerpo idéntico no duplica; distinto 409. Identificar origen asistido en revisión es opcional, sin guardar prompt/propuesta descartada.

Aprobar/publicar sigue en 002/003/005, con revisión humana de hechos/nivel e idioma. Traducción aceptada no habilita CV por sí sola. Propuesta que inventa logro, mezcla idiomas o eleva capacidad se corrige/descarta antes de aprobación; no se presume que modelo nunca falle.

## Permisos y superficie pública

Tablas técnicas privadas/RLS, sin acceso anon/authenticated Data API. Coordinador IA lee solo campos editoriales explícitos y controles necesarios bajo guard; no recibe grants de bandeja/configuración/archivos. Proceso modelo tiene cero credenciales DB y sin red externa, a diferencia del backend que verifica permisos. Ningún endpoint 007 puede aprobar/publicar o alterar fuente CV pública.

Logs de app/runtime/proxy solo tipo/resultado/fecha/actor/request/código/duración, sin textos/secretos/fingerprints de propuesta. Headers no-store, sin analytics o reportes de errores que capturen formulario. Ninguna salida a IA remota, repositorio, PDF o métricas públicas; texto final aceptado sigue privacidad editorial normal.

Gate RET-001004 se conserva; no entrenar, resumir ni responder mensajes. Datos 006 no se autoañaden. CV aprobado y publicación manual no consultan disponibilidad/runtime 007.
