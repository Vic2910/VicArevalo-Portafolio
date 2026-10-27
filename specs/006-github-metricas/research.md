# Research: 006-github-metricas

Fecha:2026-10-27. Base: spec 006, constitución 1.0.0 y diseños 002–005. Investigación delegada independiente de API oficial consolidada aquí. No se consultaron repositorios reales de Vic 2910.

## 1. Recursos y cuenta

- **Decision**: Resolver /users/Vic 2910, persistir account.id y descubrir /users/{login}/repos?type=owner&per_page=100, siguiendo todas las páginas. Verificar private=false y owner.id antes de aceptar; incluir fork=true. Nombres/URLs son atributos, repository.id es identidad.
- **Rationale**: Listas de repos autenticados pueden incluir privados/ajenos; no corresponden al alcance. Un username reasignado a otro account.id no se fusiona con identidad previa: error de identidad, revisión administrativa necesaria.
- **Alternatives considered**: /user/repos, excluir forks, nombres de repo como PK, consultar perfil real para rellenar fixtures.
- **Source**: [repositorios REST](https://docs.github.com/en/rest/repos/repos#list-repositories-for-a-user).

## 2. Autoría y fecha

- **Decision**: Contar solo top-level author.id igual al ID verificado; author=null es desconocido y otro ID es ajeno. Fecha de período=commit.author.date UTC. No nombres/emails/committer/coautoría textual ni firma como sustitutos.
- **Rationale**: Dueño de repo o integrador no acredita autoría. Fecha de autoría no debe confundirse con filtros de última actualización de endpoint. Persistir SHA/ID/fecha mínimos, sin emails/mensajes de commit/respuestas crudas.
- **Alternatives considered**: Coincidencia de correo/nombre, author=login como única prueba, contar commits de todos los autores en repo propio.
- **Source**: [commits REST](https://docs.github.com/en/rest/commits/commits#list-commits).

## 3. Recorrido y reescritura

- **Decision**: Fijar default_branch/head SHA por repo y cutoff UTC del run; listar toda historia alcanzable con sha=<SHA fijo>, per_page 100 y Link. Sin since/until/author como atajos; filtrar autoría/fecha localmente después de recorrer, sin detener por fechas no monótonas. Deduplicar repo_id/SHA.
- **Rationale**: Evita saltos por cambios de rama y pérdida de commits antiguos accesibles. Force-push/default branch nuevo requiere reconstruir membresía, no acumular histórico como actual. Revalidar catálogo/cabezas al finalizar; cambios incompatibles=parcial. No se afirma snapshot global simultáneo del proveedor.
- **Alternatives considered**: Append-only incremental; parar al ver fecha antigua; usar SHA sin repo como dedupe global; contar solo primera página.
- **Sources**: [branches](https://docs.github.com/en/rest/branches/branches#get-a-branch), [paginación](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api).

## 4. Caché y comprobación sin cambios

- **Decision**: Caché por URL/parámetros/API version/contexto de credencial no secreto, ETag/Last-Modified, páginas normalizadas y Link.304 reutiliza solo representación completa de esa página; caché ausente/inválida obliga GET no condicional. Nuevo run valida todas las páginas aunque head no cambie.
- **Rationale**:304 de una página no acredita historial completo ni otras páginas. Asociaciones de autor pueden cambiar aun con SHA estable. Sin cambios solo se declara tras recorrer/verificar alcance y persistir fecha, sin duplicar miembros.
- **Alternatives considered**:304→run completo; head igual→omitir autoría; guardar ETag sin representación; caché que mezcle parámetros/token contexts.
- **Source**: [buenas prácticas/condicionales](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api).

## 5. Cuotas y ejecución duradera

- **Decision**: Requests secuenciales, headers vigentes y token opcional backend de lectura pública; API version inicial 2026-03-10, revalidar al implementar. Respeto de Retry-After, reset cuando remaining=0 y espera mínima 1 min ante límite secundario sin instrucciones, luego exponencial. next_allowed=max(último inicio+60 min, proveedor, backoff). No sleeps largos/retry continuo ni cambiar IP/token para evadir cuotas.
- **Rationale**: Cuota real depende de contexto/proveedor y prevalece sobre configuración local. Runs largos se segmentan con progreso duradero y continuación manual permitida; sin generar requests desde dashboardGET. Worker no declara éxito al encolar.
- **Alternatives considered**: Varias sincronizaciones paralelas; polling de GitHub por página admin; cola/SaaS nuevo; esperar en transacción SQL; reintentar 403 indefinidamente.
- **Sources**: [rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), [HTTPX](https://www.python-httpx.org/).

## 6. Métricas locales y privacidad

- **Decision**: Proyectos publicados si tienen publicación vigente (aunque haya edición pendiente); borradores si nunca publicados; retirados si tuvieron publicación y hoy no, sin contarlos dos veces. Mensajes=count de filas vivas según 004, no recibos ni vencidos. Consultas/códigos de estado independientes; cantidades privadas sin contenido de mensajes.
- **Rationale**: Un error no es cero. Contacto sin esquema/garantía muestra no disponible/bloqueado, no habilita recepción. Tabla existente consultada correctamente vacía sí permite cero con contexto del bloqueo. No copiar mensajes o hacer métricas históricas de remitentes.
- **Alternatives considered**: Contar borrador de corrección como otro proyecto; retired dentro de drafts; usar contador técnico de capacidad 004; almacenar conteo de mensajes sin expiración o exposición pública.

## 7. Persistencia y promoción

- **Decision**: Run con manifiesto/corte fijos, intentos segmentados, stage y último completo separados. UNIQUE(run_id,repo_id,SHA) y promoción atómica de membresía/summary/puntero/fecha solo tras recorrido validado. Reanudar mantiene manifiesto solo si sigue compatible; si no, parcial y nueva ejecución explícita. Conservar último resultado válido y último parcial etiquetados, sin sumarlos.
- **Rationale**: Fallo de persistencia no puede adelantar fecha satisfactoria. Fencing rechaza escrituras de worker antiguo. No mezclar cambios de alcance o history rewritten en un acumulado.
- **Alternatives considered**: Actualizar total por página en vivo; sobrescribir último bueno al fallar; marcar exitoso antes de commit.
- **Sources**: [PostgreSQL transacciones](https://www.postgresql.org/docs/current/tutorial-transactions.html), [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).

## 8. Recursos y licencias

- **Decision**: HTTPX MIT y stack 002 con avisos/licencias/transitivas verificados al bloquear versiones; Supabase Free y API pública sin cargo. Presupuesto de 006:64 MiB lógico, caché 16 MiB, margen físico DB compartido 350 MiB; limpiar caché no referida y runs antiguos sin eliminar último válido/partial requerido. Si no hay capacidad, parcial/rechazo sin truncar total.
- **Rationale**: La cuota es restricción, no garantía ilimitada. No crear calendario automático, token real ni conexión a datos del usuario en planificación.
- **Sources**: [HTTPX licencia](https://github.com/encode/httpx/blob/master/LICENSE.md), [Supabase pricing](https://supabase.com/pricing).

[Changelog Supabase](https://supabase.com/changelog) revisado; usar TLS/clientes soportados y no desactivar verificación. No se identificó cambio que altere el diseño de RLS/SQL. Fuentes y comportamiento de GitHub se revalidarán al fijar versión/API. No quedan preguntas técnicas necesarias sin resolver.
