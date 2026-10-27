# Contract: GitHub REST, worker y persistencia

## Acceso y cliente

Cliente HTTPX síncrono, serial y TLS verificado; host fijo https://api.github.com y únicamente GET de perfil público, catálogo owner, metadatos públicos, rama predeterminada y commits. Accept application/vnd.github+json, User-Agent identificable y X-GitHub-Api-Version2026-03-10 como versión inicial verificada en docs; revalidar al implementar. Token opcional solo en header backend y nunca URL/log/error/DB.

Por defecto usar acceso anónimo público. Si se configura token, debe acreditarse que no concede acceso privado ni escritura y es adecuado para lectura pública; no aceptar token de permisos amplios como atajo. No consultar /user/repos ni otros recursos privados. No alternar credenciales/IP para eludir cuota. Cambio de contexto de credencial invalida caché correspondiente, sin almacenar token o su hash como ID público.

Redirecciones/Link se validan antes de seguir:max 3 redirects, HTTPS/api.github.com, sin userinfo/host alterno, rutas de endpoints públicos permitidos y repo/sha del manifiesto. No reenviar Authorization a otro origen. No aceptar URL, login objetivo o repo arbitrario desde formulario. Link repetido/cíclico, parámetros fuera de scope o estructura inválida producen parcial/error, nunca completitud supuesta.

## Descubrimiento y manifiesto

1. GET /users/Vic 2910:resolver ID estable.404/perfil inválido=error y último resultado preservado, no cero. ID distinto de identidad ya verificada=ACCOUNT_MISMATCH sin fusionar actividad.
2. GET /users/{verified_login}/repos?type=owner&per_page=100 y seguir Link hasta agotarlo. Verificar owner.id y private=false; incluir forks. Descartar contenido privado inesperado sin almacenarlo; credencial de alcance indebido falla cerrada. No usar visibilidad inferida de nombre.
3. Para cada repo, fijar repository.id, nombre observado, fork, default_branch y head SHA. Si hay rename verificado del mismo ID, actualizar atributos/ruta manteniendo identidad. Default_branch inexistente/404 no significa vacío; cero requiere respuesta semánticamente comprobada de repositorio sin commits. Un 409 genérico no basta.
4. Fijar cutoff_at del run y heads. Listar commits sha=<SHA fijo>&per_page=100, sin since/until/author, siguiendo todas las páginas. No detener por fecha de autoría, por tener ya visto SHA en otro repo o por alcanzar un número local de páginas. Límite de recurso conduce a parcial, no total truncado.
5. Comparar author.id top-level con account.id; null desconocido, ajeno otroID. commit.author.date válida determina <=cutoff; no usar committer/name/email/verified signature para atribuir. No guardar mensajes/parches/emails/nombres crudos.
6. Persistir miembros por run/repo/SHA. Igualdad repetida se deduplica; representaciones incompatibles de la misma pareja en run impiden declarar completo. Una SHA en dos repos cuenta dos parejas y debe advertirse.
7. Finalizar solo tras paginación completa y revalidar catálogo/propiedad/default_branch/head. Cambios que invalidan manifiesto=parcial/incompatible, no mezclar cabezas. Catálogo vacío 200 recorrido completo admite alcance vacío; recurso del manifiesto que ahora responde 404/403 no se vuelve 0. Repos previos ausentes del catálogo nuevo quedan fuera del alcance observado, sin inferir motivo; histórico anterior conserva su etiqueta.

La completitud no es snapshot global simultáneo:describe recursos/cabezas y período observados en ventana del run. Todos los commits accesibles hasta corte de autoría pertenecientes a esas cabezas y atribuibles se cuentan, incluidas bifurcaciones. No otras ramas, repos ajenos, privados, commits futuros de autoría o actividad como integrador.

## Caché condicional

Clave canónica incluye endpoint/parámetros/page/per_page/sha, API version y contexto de autenticación no secreto. Guardar ETag o Last-Modified, representación mínima normalizada validada y Link de próxima página. Respuesta 200 completa actualiza caché+stage+cursor transaccionalmente.

En 304, reutilizar exclusivamente esa representación y enlaces validados (cabeceras actuales cuando existan); cache miss/incompleta/incompatible requiere GET no condicional dentro del presupuesto o resultado parcial. No crear página vacía por 304 ni actualizar fecha satisfactoria del run aún incompleto. Un head estable no autoriza saltarse todas las páginas:autoría asociada puede haber cambiado. Nuevo run valida cada representación necesaria; continuación de mismo run conserva páginas ya observadas y documenta ventana temporal.

## Cuotas, espera y segmentación

Consultar headers reales de cuota, no /rate_limit por cada página. Un solo request a la vez, timeout total 10 s y máximo inicial 200 requests/5 min por segmento, reducido por remaining/reserva de validación final y recursos. Sin presupuesto suficiente, guardar progreso y liberar worker; no insistir ni marcar completo.

En 403/429:identificar restricción por headers/código de proveedor; respetar Retry-After (segundos/fecha), X-RateLimit-Reset cuando remaining=0 y cualquier instrucción más conservadora. Sin espera explícita ante secundario, al menos 60 s y crecimiento exponencial en repeticiones; tras 3 restricciones secundarias consecutivas, suspensión local 24 h propuesta.403 de permisos o 401 de token inválido no se reintentan como cuota:detener/error de configuración.

next_allowed_at=max(último started_at real+60 min, provider_blocked_until, backoff_until). Reservar queued impide duplicados antes de inicio; al iniciar worker fijar started_at y cooldown definitivo. Todo nuevo attempt, incluida continuación manual, respeta ventana. No esperar horas dentro de request/worker ni nuevo HTTP por refreshGET; persistir bloqueo y salir. Respetar instrucciones más largas, nunca reducirlas al mínimo local.

Un run puede abarcar varios intentos, manteniendo corte/manifiesto originales y páginas observadas, con inicio/final y antigüedad explícitos. Continuación manual solo si alcance sigue compatible; en caso contrario conservar parcial y requerir nuevo run explícito. No prometer completar historiales arbitrarios con presupuesto gratuito.

## Worker, sesión y carreras

POST con guard 002 crea reserva/attempt/operación/auditoría en transacción y devuelve 202. Worker del monolito solo consume solicitudes ya autorizadas; no inicia sincronizaciones por reloj/visita. Hilo local o CLI del mismo código, sin Redis/broker/cron externo. Detectar heartbeat ausente antes de aceptar solicitud; reinicio conserva cola/estado en DB.

Un singleton de control y lease 90 s, owner aleatorio y fencing monotónico aseguran único intento activo. Adquisición/renovación/finalización por comparación atómica de lease/fence. Guardar páginas/promover exige fence vigente y autoridad/epoch/sesión iniciadora actuales. Antes de cada HTTP comprobar de nuevo lease/permiso; timeout 10 s es menor que lease y no se permite takeover mientras haya reserva/lease válidos. Worker antiguo no hace nuevas llamadas ni acepta respuestas tardías tras perder lease. Testear pausa/reinicio/latencia y dos procesos.

Auth se verifica mediante componente 002 para sesión iniciadora, con tokens gestionados allí, sin copiarlos a job. Expiración/revocación detiene nuevos HTTP y promoción; conservar parcial/estado seguro. Bookkeeping terminal/interrupted por mantenimiento tiene grants de columnas limitados a control/estado, no acceso a mensajes ni permiso para promover resultados sin guard. Nunca reejecutar automáticamente tras login.

Cada página guarda datos mínimos/cursor/avance en transacción corta, sin HTTP o sleep bajo locks. Lease vencido se marca interrupted de forma condicionada, no nuevo inicio silencioso; siguiente intento requiere acción y tiempo permitidos. Fallo DB no permite seguir gastando cuota sin persistir avance. Idempotencia operation_id evita dos starts por doble POST/commit incierto.

## Promoción y cambios de historia

Stage separado de último completo. Para promover, verificar manifest/páginas/cero probado/atribución/corte, revalidación final, recursos, guard/fence y persistencia de filas/count. Actualizar run completo, puntero, checked_at/last_success_at, control y auditoría en una transacción. Fallo rollback conserva último completo y fecha anterior; commit incierto se consulta por run/operación antes de afirmar éxito.

Nuevo resultado reconstruye membresía alcanzable; no sumar filas históricas como actuales tras force-push/default branch change. Resultado sin cambios también requiere verificación completa y commit, mantiene count y avanza checked_at. Parcial jamás reemplaza puntero ni suma con total viejo; sin anterior, no hay total completo confirmado.

## Roles, métricas y privacidad

Tablas 006 privadas con RLS. Rol backend_metrics_read puede SELECT de resultados 006 bajo guard y columnas mínimas para count de proyectos/mensajes; no textos de contacto, drafts editoriales completos, imágenes o tokens. Proyectos publicados/borradores/retirados se resuelven por puntero/publicación previa, sin leer descriptions. Mensajes usan id/state/expires_at y guard 004; counts ejecutados con referencia temporal común y sin cachear cantidades que sobrevivan a eliminación/vencimiento.

Rol backend_github_sync escribe solo tablas 006/control/recibos/auditoría con sesión/lease actual y bookkeeping terminal acotado. No INSERT/UPDATE de proyectos 003, fuente CV 005 o mensajes 004. Roles sin ownership/BYPASSRLS/superusuario/service_role, SQL parametrizado y TLS verify-full. anon/authenticated, incluso JWT cliente de admin, no leen dashboard/cache/control ni disparan trabajo directo por Data API. Datos públicos GitHub no vuelven públicas las métricas privadas.

Limpiar solo caché/runs no referidos bajo presupuesto, preservando último completo y parcial requerido. Sin contenido de commits/remitentes en logs, raw REST o exportaciones públicas; token solo entorno protegido. No activar 004, no copiar sus mensajes ni usar GitHub como fuente automática de proyectos/CV.
