# Research: 002-administracion

Fecha: 2026-10-27. Fuentes locales: spec, constitución 1.0.0 y diseño 001. Se delegó una revisión independiente de sesiones, revocación, Data API y atomicidad conforme a speckit-plan; hallazgos consolidados aquí.

## 1. Identidad y sesiones gratuitas

- **Decision**: Supabase Auth correo/contraseña, cuenta aprovisionada por operador y UUID autorizado en tabla protegida. Sin signup en aplicación; deshabilitar registro público en configuración Auth. get_user verifica identidad con proveedor en cada operación privada; fallo de verificación deniega. Tokens solo backend, cifrados con Fernet; cookie opaca aleatoria, hash en DB. Sesión propia: 30 min inactividad ajustables hasta 300 min, 24 h absolutas, revocación inmediata persistida.
- **Rationale**: No depender de límites de sesión Pro. Un JWT válido puede sobrevivir a signout: cookie, estado actual y frontera DB deben invalidar el acceso administrativo aunque persista el token. El cliente nunca obtiene tokens Auth.
- **Alternatives considered**: JWT en cookie firmada Flask (legible y difícil de revocar); límites Pro; expiración JWT como único cierre; memoria de un worker (incoherente entre procesos).
- **Sources**: [sessions](https://supabase.com/docs/guides/auth/sessions), [signout](https://supabase.com/docs/guides/auth/signout), [Fernet](https://cryptography.io/en/latest/fernet/).

## 2. Autorización y acceso directo

- **Decision**: admin_authorizations actual y sesión vigentes en cada transacción privada. API pública niega toda lectura privada y escritura, incluso a JWT de administrador. Backend usa conexión PostgreSQL dedicada con roles de autenticación y edición separados, sin BYPASSRLS ni propiedad de tablas. Esquema privado sin exposición Data API. Políticas editoriales exigen contexto de sesión verificado establecido localmente solo por backend y autoridad actual.
- **Rationale**: user_metadata es editable y claims app_metadata pueden quedar obsoletos. Decorador Flask no protege Data API; la denegación de permisos directos sí evita replay de JWT. No hacen falta claves service_role ni funciones SECURITY DEFINER.
- **Alternatives considered**: Políticas TO authenticated generales; service_role (excesivo); RPC públicas que duplican el guard y elevan superficie de ataque.
- **Sources**: [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Data API](https://supabase.com/docs/guides/api/securing-your-api), [functions](https://supabase.com/docs/guides/database/functions).

## 3. Atomicidad, revisión y retirada

- **Decision**: Revisiones inmutables y punteros draft/published por elemento. Comparación de lock_version y revisión exacta confirmada. Publicar o retirar actualiza punteros, instantánea y auditoría en una sola transacción; guardar solo crea revisión privada. Mantener versión retirada y borrador independiente.
- **Rationale**: Evita publicaciones parciales, revisión obsoleta y pérdida de borradores. Tres llamadas REST separadas no forman una transacción. Locks breves con orden fijo; no esperar Auth dentro del bloqueo editorial.
- **Alternatives considered**: Última escritura gana; editar fila publicada directamente; publicar todos los borradores; sobrescribir borrador al retirar.
- **Sources**: [Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html), [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html).

## 4. Limitación y auditoría

- **Decision**: Estado compartido en Supabase por HMAC de correo normalizado, incluyendo cuentas inexistentes, cinco fallos consecutivos en 15 min y bloqueo 15 min desde quinto; éxito reinicia contador. Reserva atómica por identidad para serializar intentos concurrentes sin mantener transacción durante Auth. Errores de dependencia no cuentan como contraseña errónea ni permiten acceso. Eventos estructurados mínimos y transaccionales para publicaciones/retiros; sink seguro de servidor para fallos si DB cae.
- **Rationale**: Cumple umbral exacto en varios workers sin enumeración ni contador solo por IP. Registro de fallos no debe filtrar secretos ni mensajes. Una operación no recibe éxito antes de commit.
- **Alternatives considered**: Memoria local; limitar solo por IP; registrar formularios/tokens; confirmar antes de persistir.

## 5. Formularios, CSRF y accesibilidad

- **Decision**: Flask-WTF con CSRF global, comprobación de origen mismo sitio, POST para mutaciones y PRG tras éxito; error conserva valores seguros de la petición mientras siga autorizado. Jinja con autoescape, texto plano, URLs tipadas. Revisión y retirada mediante páginas de confirmación accesibles sin diálogo JS obligatorio. Sesión vencida no guarda ni reejecuta; nueva acción explícita tras autenticar.
- **Rationale**: SameSite no sustituye CSRF. HTML semántico y mensajes vinculados a campos permiten teclado y lector. No guardar borradores privados en localStorage, URLs o cookies para recuperar formularios vencidos.
- **Alternatives considered**: Mutación GET, HTML confiable, autosave/publicación al reautenticar y CAPTCHA obligatorio.
- **Sources**: [CSRF](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/), [Flask security](https://flask.palletsprojects.com/en/stable/web-security/), [WCAG 2.1](https://www.w3.org/TR/WCAG21/).

## 6. Dependencias y gratuidad

- **Decision**: Mantener stack 001; añadir Psycopg 3 (LGPL con excepciones documentadas), Flask-WTF (BSD-3-Clause), cryptography (Apache-2.0 o BSD). Conservar avisos, verificar versión estable compatible y licencias transitivas al bloquear dependencias. Supabase Free sin upgrades; no SaaS nuevo ni función Pro para seguridad.
- **Rationale**: Necesidades concretas de transacción, CSRF y protección de tokens. Conexión PostgreSQL/pooler configurada según entorno, TLS y cuotas reales; despliegue no forma parte de este trabajo. Si falla Auth/DB, denegar acciones sin afirmar éxito ni activar cargos.
- **Alternatives considered**: Redis, almacén externo de sesiones, servicios de auditoría de pago, criptografía artesanal.
- **Sources**: [Psycopg licencia](https://www.psycopg.org/license/), [Flask-WTF licencia](https://flask-wtf.readthedocs.io/en/1.2.x/license/), [cryptography](https://cryptography.io/en/latest/), [Supabase pricing](https://supabase.com/pricing).

Se revisó el [changelog](https://supabase.com/changelog) actual; el lector web no admite el índice .md y se usó HTML. No se detectó cambio que obligue a alterar esta arquitectura; verificar APIs de nuevo al fijar versiones. Identidad real, claves y contenido no son incógnitas de diseño: se aportan por configuración protegida y revisión humana. No quedan clarificaciones técnicas necesarias abiertas.
