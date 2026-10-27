# Data model: 002-administracion

Diseño lógico, sin SQL/migraciones ejecutados. UUID para identidades, elementos, revisiones y operaciones; timestamptz UTC para persistencia, fechas/horas accesibles localizadas en UI. Esquema `private` no expuesto a Data API; RLS como defensa adicional. Sin contraseñas propias: Supabase Auth es autoridad de identidad.

## Entidades privadas

| Entidad | Campos principales | Reglas |
|---|---|---|
| admin_authorizations | user_id PK/FK Auth, enabled, authorization_epoch entero, updated_at | Único administrador inicial. Solo operador de confianza puede modificar autorización; nunca formularios ni metadata del cliente. Cada retirada de permiso incrementa epoch para no revivir sesiones antiguas al reactivar. |
| admin_sessions | id PK, opaque_hash único, user_id FK nullable solo en preautenticación, state preauth/active, csrf_nonce, idle_timeout_minutes, authorization_epoch, provider_session_id, encrypted_access_token, encrypted_refresh_token, token_expires_at, created_at, last_seen_at, absolute_expires_at, revoked_at, refresh_lease_until | Cookie aleatoria >=256 bits; solo hash persistido. Preautenticación dura 10 min, carece de permisos y solo conserva nonce CSRF; login rota identificador/nonce y pasa a sesión activa con identidad requerida. Tokens cifrados con clave externa rotatable. Inactividad predeterminada 30 min ajustable hasta 300 min y absoluto 24 h; revocación/epoch inválido no renovables. Ningún token en cookie. |
| login_limits | identity_hmac PK, failure_times (máximo cinco), blocked_until, attempt_id, lease_until, updated_at | HMAC de email normalizado con clave externa, no email crudo. Retener fallos consecutivos de últimos 15 min; quinto bloquea 15 min. Éxito limpia contador. Reserva atómica permite un intento Auth concurrente por identidad. |
| editorial_items | id PK, kind profile/skill/academic, profile_id, draft_revision_id, published_revision_id nullable, lock_version entero, updated_at | Un perfil singleton; cada conocimiento/actividad tiene perfil. Punteros deben referir revisión del mismo elemento. Cada mutación incrementa lock_version; nunca versión en cliente como autoridad. |
| editorial_revisions | id PK, item_id FK, revision_number, payload JSON tipado, created_by, created_at | Inmutables; UNIQUE(item_id, revision_number). Borrador seguro puede ser incompleto. No UPDATE/DELETE del runtime. Publicar exige validación y revisión humana. |
| publication_events | id PK, operation_id único, item_id, revision_id, action publish/withdraw, actor_id, confirmed_at, content_digest | Registro de aprobación/retirada; conserva referencia al contenido retirado aunque exista otro borrador. Sin borrar revisiones por retirada. |
| operation_receipts | operation_id PK, user_id, item_id, action, request_digest, result_version, result_revision, committed_at | Creado junto al cambio en la misma transacción. Resuelve doble envío y resultado de commit incierto; reutilizar id con otro cuerpo se rechaza. |
| security_events | id PK, event_type, outcome, occurred_at, actor_id nullable, identity_hmac nullable, request_id, item_id/revision_id nullable, reason_code | Append-only para runtime. Sin password, correo crudo, IP cruda, cookies, tokens, contenido editorial ni mensajes privados. |

Índices: hashes de sesión/identidad únicos; FKs de revisiones y eventos; item_id+revision_number único; user_id/revoked_at/absolute_expires_at para sesiones; occurred_at para auditoría; operation_id único. No indexar payload editorial por anticipado.

## Payload y relación con 001

- Perfil: full_name, degree, summary, public_contacts. Publicar requiere nombre, carrera y resumen aprobados; no elevar afirmaciones ni inventar datos. Contactos incluidos solo por selección/autorización explícita en revisión.
- Conocimiento: name, description opcional, display_order. Nombre verificado requerido, sin porcentajes arbitrarios.
- Experiencia académica: activity, description, institution opcional, start_date/end_date opcionales, ongoing y display_order. Publicar exige título y descripción aprobados. Fechas coherentes, sin precisión inventada, según 001.
- Compartir límites y formatos de `../001-perfil-publico/data-model.md`: textos cortos 200, resumen 2000, descripción 4000, contactos hasta 10 y valores 2048; validar tipos, tamaño de petición máximo 64 KiB y esquemas URL permitidos. Borrador incompleto admite null/texto vacío normalizado, pero nunca estructura insegura, URL ejecutable o tamaño excesivo.
- Afirmaciones verificadas se acreditan por confirmación explícita registrada de Victor sobre la revisión exacta, no por inferencia automática. Rechazar marcadores conocidos, texto obligatorio vacío y porcentajes de dominio; la validación sintáctica no demuestra veracidad humana.

La publicación materializa solo el payload aprobado en public_profiles/public_skills/public_academic_experiences de 001, con id estable, published_at y relaciones. Metadatos de seguridad, revisiones y contactos no autorizados permanecen privados. El perfil público puede omitir resumen en datos históricos; 002 no permite nuevas publicaciones sin él. No cambiar 001 para inventar contenido.

## Estados y transiciones editoriales

Estado derivado de punteros, no un enum ambiguo: sin publicar, publicado sin cambios, publicado con borrador diferente, retirado. Revisión inmutable es unidad de aprobación.

1. Crear/guardar: comparar expected_version, crear revisión nueva y mover draft_revision_id; mantener publicación. Crear elemento nuevo requiere también operation_id para evitar duplicados.
2. Revisar: GET de draft concreto, comprobar versión; presentar vista escapada e informe de validación. Emitir token de revisión ligado a sesión, elemento, revision_id, digest y lock_version, con vida 10 min. No cambia publicación.
3. Publicar: POST explícito con token, revisión y expected_version; exigir que sigue siendo el borrador actual. Actualizar solo instantánea y published_revision_id de ese elemento, registro de aprobación y recibo en transacción. Otros borradores/publicaciones intactos.
4. Retirar: solo skill/academic publicados. Confirmación ligada a published_revision_id y lock_version. Eliminar esa instantánea pública y poner published_revision_id null, registrar retirada y revisión retirada. Conservar draft_revision_id siempre; si coincide con publicada ya conserva su contenido, y si difiere conservar ambas revisiones.
5. Republicar: nueva revisión/confirmación explícita; nunca reutilizar confirmación previa o reautenticación como orden de publicación.

Sin retirada de perfil ni borrado definitivo en UI. Hijos solo se publican si perfil publicado; si aún no existe, pueden guardarse como borrador. Al retirar último hijo, la sección pública y su ancla desaparecen conforme a 001. Fuente CV solo lee mismas instantáneas.

## Estados de seguridad y retención técnica

Sesión activa→caducada/revocada, sin vuelta automática. Login nuevo crea sesión nueva y rota cookie/CSRF. Revocación de autorización invalida todas las sesiones por epoch. Bloqueo de login expira por reloj DB, no por reinicio de proceso.

Propuestas de operación: eliminar tokens de sesiones revocadas/caducadas tras intentar signout, limpiar filas de sesión a las 24 h y login_limits sin bloqueo/lease activo tras 24 h. Auditoría 90 días con mantenimiento acotado por operador; no afecta conservación de mensajes de 004. Revisiones editoriales se conservan en este alcance sin eliminación automática; monitorizar volumen y denegar nuevas escrituras con estado útil antes de agotar recursos, nunca borrar contenido para liberar cuota silenciosamente.
