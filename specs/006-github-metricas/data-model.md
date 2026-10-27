# Data model: 006-github-metricas

Diseño lógico, sin migraciones ni datos reales. Esquema private no expuesto; RLS, UTC en persistencia y fechas localizadas con zona visible en UI. ID GitHub numérico estable, SHA hexadecimal validado como representación del proveedor. No commits/emails/textos de mensajes en logs.

## Entidades

| Tabla propuesta | Campos principales | Invariantes |
|---|---|---|
| github_identity | account_id PK, requested_login=Vic 2910, verified_login, html_url, verified_at | Cambio de ID bajo mismo login no se acepta como misma persona. No importar email/avatar/texto del perfil. |
| github_repositories | repository_id PK, owner_id, full_name, html_url, fork, default_branch, last_public_observed_at, availability | Solo observaciones públicas verificadas; rename conserva ID. No convertir metadatos actuales en alcance histórico de otro run. |
| github_commits | repository_id FK, sha, authored_at, content_fingerprint | PK(repo_id,sha). Fecha del objeto Git, sin email/nombre/mensaje/parches. Misma SHA en otro repo es otra pareja. |
| github_runs | id UUID PK, run_version entero, account_id nullable hasta verificación, scope_definition_hash, policy_version, cutoff_at, created_at, finished_at, status, catalog_complete, manifest_hash, last_success_at nullable, result_count nullable, error_code | Run lógico con política/corte fijos; cuenta y definición completas obligatorias antes de declarar éxito. run_version cambia al reservar/reanudar/finalizar estado, para detectar formularios obsoletos; stage nunca es último resultado completo. Count solo se confirma al promover, cero válido distinto de null. |
| github_run_repositories | run_id, repository_id, observed_name/owner/fork, default_branch, pinned_head_sha nullable, observed_at, state, page_count, next_cursor, finished_at | PK(run_id,repo_id). Guarda contexto propio del run, incluido empty confirmado, completo o fallo. No acumular otra cabeza en mismo manifiesto. |
| github_run_commits | run_id, repository_id, sha, observed_author_id nullable, observed_author_login nullable, attribution own/other/unknown, eligible_date boolean, observed_at | PK(run_id,repo_id,sha), FK a commit y run_repo. Autoría observada por run para que cambio de asociación no reescriba resultados antiguos. |
| github_attempts | id UUID PK, run_id, request_operation_id único, requested_by, initiating_session_id, authorization_epoch, requested_at, started_at nullable, ended_at, status, requests_done, pages_done, stop_reason | Segmento manual de run; nuevo intento o continuación requiere>=60 min desde inicio anterior y proveedor. Sin tokens ni cookie opaca persistidos aquí. |
| github_sync_control | singleton PK, active_attempt_id nullable, fence_counter, lease_owner, lease_until, worker_heartbeat_at, last_started_at, next_local_allowed_at, provider_blocked_until, backoff_until, secondary_failure_count | Una reserva activa global. Reloj DB y fencing; no exclusión solo por memoria/worker. Cola aún no ejecutada también bloquea duplicados. |
| github_complete_results | scope_definition_hash PK, latest_complete_run_id, previous_complete_run_id nullable, checked_at | Punteros solo se actualizan tras completar/persistir todos los requisitos en misma transacción. |
| github_page_cache | cache_key PK, canonical_url, params/API_version, credential_context_id no secreto, etag/last_modified, normalized_page, next_link, checked_at, byte_size | Solo representación mínima de página validada completa; no raw payload, Authorization o token.304 no existe como representación vacía. |
| github_operations | operation_id PK, actor_id, action start/resume, request_digest, attempt_id, committed_at | Idempotencia del POST; doble envío no reserva dos intentos ni reinicia cooldown. |

Índices: FKs run/repo/attempt, PK de dedupe, account/owner, run/status y eligible attribution, lease/control singleton, cache_key único. No índice por email o texto de commit. Auditoría 006 reutiliza security_events 002 con tipo/resultado/fecha/actor/run y códigos, sin contenido privado.

## Alcance y conteo

scope_definition_hash identifica regla (ID cuenta, solo públicos propios+forks, default branches, fecha de autoría y dedupe). manifest_hash agrega corte/IDs observados/ramas/cabezas de ese run. Mantener ambos: dos cortes/resultados no se suman por compartir regla ni se declaran idénticos por tener mismo total.

Período: desde primer commit accesible en cada cabeza fijada, sin límite inferior arbitrario, hasta authored_at<=cutoff_at. No filtrar servidor por since/until/author ni interrumpir recorrido por fecha. IDs/SHAs/datos de fuente con estructura inválida producen parcial/error, no exclusión silenciosa de contribución potencial. Fecha futura queda excluida del período y se explica.

attribution own solo si author.id de cuenta GitHub de nivel superior coincide con account_id; null=unknown, otroID=other. commit.author.name/email, committer, firmas o coautores textuales no cambian esto. result_count cuenta miembros own con eligible_date y únicos por repo/SHA. La misma SHA puede aportar en dos repositorios, incluidos forks; no es total global de SHA únicos ni medida de experiencia profesional.

run_repositories permite distinguir cero comprobado por repo de recurso sin datos/fallido. Catálogo público vacío verificado permite resultado completo de alcance vacío; perfil 404 o repo del manifiesto inaccesible no se convierten en cero. Repos antiguos ausentes del catálogo nuevo se etiquetan «fuera del catálogo público observado», sin inventar si fueron privados/eliminados/transferidos; el resultado anterior conserva su manifiesto.

## Estados y transiciones

1. POST autorizado reserva operación/attempt queued y puntero activo en transacción; devuelve 202, no éxito de sincronización. Cooldown provisional protege reserva; started_at real del worker establece al menos 60 min desde inicio efectivo para siguientes intentos.
2. Worker verifica guard/autoridad actual 002 y toma lease 90 s/fence. Renueva antes de cada HTTP y escritura; timeout HTTP 10 s. No mantiene transacción durante red. Worker viejo no persiste ni hace nuevas llamadas tras perder permiso/lease; respuestas tardías no promueven.
3. Discovery registra cuenta/catálogo completo y fija ramas/cabezas+corte. Persistir página/membresía+cursor juntos; página repetida no duplica. Metadatos incompatibles para misma pareja generan parcial.
4. Segmento termina por cuota/tiempo/límite/sesión:awaiting_resume si hay progreso compatible, failed si no; último válido intacto. Lease expirado/reinicio:interrupted, sin nuevo HTTP desde GET; continuación manual cuando esté permitida crea otro attempt.
5. Continuar mantiene corte/IDs/cabezas del mismo run solo tras revalidación. Cambio de propietario, catálogo, default_branch/head incompatible:run parcial/incompatible; nueva ejecución explícita reconstruye membresía. No mezclar stage con otro manifiesto.
6. Completar requiere páginas agotadas/representación validada, autoría/fechas, repos vacíos probados y revalidación final de catálogo/cabezas, además de guard/persistencia. Promover count/puntero/last_success_at atómicamente. Resultado sin cambios puede tener conteo igual y checked_at nuevo; no duplicar miembros.

No existe snapshot global simultáneo GitHub: registrar ventana de observación created_at→finished_at y cabezas. Completitud significa alcance observado y validado, no todo historial de la cuenta. Sin completo previo, mostrar parcial propio con fecha/corte sin total completo confirmado.

## Resumen local no persistido

- MetricResult(value|null, state ready/empty/unavailable/not_configured, as_of, explanation). Cero solo después de consulta correcta o sincronización completa que lo confirme.
- Proyectos: published si publicación vigente; draft si nunca publicado; retired si tuvo publicación y ahora no. Proyecto publicado con borrador de corrección se cuenta una vez como published; retirados no suman draft/published; eliminados excluidos. Inconsistencia de fuentes se presenta como error.
- Mensajes: count(id) y count pending sobre filas con expires_at futuro, excluyendo eliminadas; SELECT solo columnas id/state/expires_at por rol mínimo y guard vigente. No usar stored_count 004 ni leer nombre/correo/cuerpo. Si esquema no existe o lectura falla:unavailable/not_configured, nunca 0 inferido. Si consulta vacía correcta:0 con estado de contacto RET-001 separado.
- Commits: último completo compatible con manifiesto/corte/fecha propios, más intento parcial separado. Estado antiguo/completo son dimensiones diferentes; siempre mostrar fecha/antigüedad y eventual bloqueo externo.

Cada familia local se consulta de forma independiente con su as_of; un fallo no invalida ni convierte las otras en cero. Dentro de una familia, totales/desglose usan misma referencia temporal/snapshot. No prometer una instantánea global de todas las fuentes independientes.

## Retención técnica y recursos

Preservar al menos último completo, anterior necesario para comparar y último parcial/progreso reanudable. Propuesta:dos resultados completos más reciente parcial, historial de attempts 30 días; limpiar solo runs no referidos y commits/cache sin referencias. Nunca borrar último válido para ocultar error. Contextos incompatibles se etiquetan; no fusionar ni usar purga para declararlos completos.

Caché LRU<=16 MiB y presupuesto lógico 006<=64 MiB más margen físico compartido 350 MiB. Contar índices/TOAST/otros módulos al medir uso real, no garantizar espacio con payload. Si limpieza segura no basta, parcial/rechazo hasta recursos disponibles, sin trucos de cuota o cargos.
