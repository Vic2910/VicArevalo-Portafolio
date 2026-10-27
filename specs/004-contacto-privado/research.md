# Research: 004-contacto-privado

Fecha:2026-10-27. Fuentes locales: spec 004, constitución 1.0.0 y diseño 002. Investigación delegada de conservación, copias e idempotencia consolidada aquí.

## 1. Garantía estricta y decisión de Victor

- **Decision**: Mantener 90 días desde recepción sin ampliar por lectura/marcado; bloquear activación hasta acreditar cumplimiento estricto, incluidas las cuestiones de copias planteadas. Victor eligió expresamente esta opción durante planificación. No cambiar spec ni plazo por inferencia.
- **Rationale**: Cron programa ejecuciones, pero no garantiza instante exacto. DELETE no significa sobreescritura física inmediata y la documentación del proveedor no acredita destrucción individual exacta en copias/WAL. TTL puede impedir consulta al vencer, pero no demuestra eliminación del contenido.
- **Alternatives considered**: Purga periódica presentada como cumplimiento exacto (rechazada); asumir que Free implica ausencia de copias internas (sin evidencia); ampliar tolerancia/definir borrado operativo (opción no elegida); cifrado con clave permanente (no destruye datos si clave sigue disponible).
- **Sources**: [Cron](https://supabase.com/docs/guides/cron), [vacuum/MVCC](https://www.postgresql.org/docs/current/routine-vacuuming.html), [backups](https://supabase.com/docs/guides/platform/backups).
- **Resultado**: RET-001 ERROR. Documentar controles candidatos no cierra este gate; ninguna prueba aislada acredita la garantía del proveedor. No se ha seleccionado un mecanismo como solución conforme de borrado estricto.

## 2. Persistencia privada y permisos

- **Decision**: Tablas privadas no expuestas, RLS y roles backend separados de ingestión/administración/purga. Visitante no recibe Supabase JWT ni permisos SQL. Lectura administrativa usa identidad/autoridad/sesión actuales de 002; lectura no marca revisado.
- **Rationale**: INSERT público general o service_role innecesario ampliarían superficie. Ingestión solo ve recibo técnico de solicitud propia, nunca bandeja, remitentes, texto o cantidades.
- **Alternatives considered**: Tabla public con filtro UI; clave privilegiada; notificación por email como persistencia; analizar contenido con IA.
- **Source**: [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security).

## 3. Reintentos sin recreación

- **Decision**: Token firmado con nonce aleatorio>=256 bits, issued_at y accept_until 24 h, ligado a sesión anónima. UNIQUE(request_hash), inserción de mensaje pendiente y recibo en una transacción. Reintento con mismo token vuelve al mismo resultado; cuerpo distinto=409 mientras exista digest. Token vencido siempre se rechaza antes de insertar.
- **Rationale**: Una tombstone técnica temporal tras eliminación evita recrear durante ventana válida; después la firma/expiración impide replay sin guardar mensajes o hashes personales indefinidamente. No deduplicar por correo/texto: otro envío explícito con nuevo token es otra solicitud.
- **Alternatives considered**: Deshabilitar botón JS; buscar cuerpo idéntico; idempotencia solo en memoria; tombstones con correo o payload permanente.
- **Source**: [PostgreSQL INSERT/ON CONFLICT](https://www.postgresql.org/docs/current/sql-insert.html).

## 4. Validación y abuso

- **Decision**: Trim exterior, longitudes por caracteres Unicode (puntos de código, no bytes), preservar interior/saltos; correo sintáctico sin DNS ni verificar existencia de buzón. Tres campos personales, sin adjuntos. CSRF y origen; límites por sesión aleatoria y globales, sin CAPTCHA visual, timers mínimos o fingerprint/IP/email persistidos.
- **Rationale**: Evita barreras y recogida adicional, con límite global para contener rotación de cookies. Nuevos recibos consumen cuota; reintentos idempotentes no crean ni cuentan otro mensaje. Estos límites mitigan abuso, no garantizan disponibilidad ante ataque.
- **Alternatives considered**: CAPTCHA obligatorio, rastreo por correo/IP, honeypot con contenido adicional, validación solo navegador, consultas DNS o fetch de enlaces del mensaje.
- **Sources**: [Flask-WTF CSRF](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/), [email-validator](https://github.com/JoshData/python-email-validator), [WCAG2.1](https://www.w3.org/TR/WCAG21/).

## 5. Mecanismos de conservación que pueden probarse

- **Decision**: Como defensa candidata, expires_at fijo=received_at+90*24 h UTC y ningún lector/conteo devuelve vencidos. Purga transaccional por rol limitado, heartbeat, alerta persistente admin y puerta de recepción fail-closed. Cron puede ensayarse cada segundo con datos sintéticos, pero su cadencia no se aprueba como tolerancia.
- **Rationale**: Evita acceso tardío y permite detectar fallos/reintentar sin extensión tácita. No confundir ejecución de mantenimiento con garantía de borrado físico. No habilitar solo porque último job salió bien.
- **Alternatives considered**: Purga al visitar bandeja únicamente; borrar revisados y conservar pendientes; reiniciar plazo al leer; fallback indefinido si DB cae.
- **Sources**: [Cron quickstart](https://supabase.com/docs/guides/cron/quickstart), [backups](https://supabase.com/docs/guides/platform/backups).

## 6. Copias, restauración y logs

- **Decision**: No crear dumps/exportaciones/cachés de mensajes. Logs sin nombre/correo/texto ni parámetros SQL; constancia de eliminación solo fecha/motivo/resultado. Una restauración se hace aislada y con recepción/lectura cerradas, aplica vencimientos y vuelve a acreditar garantía antes de abrir.
- **Rationale**: No reintroducir mensajes eliminados por restauración. Exclusión de dumps gestionados por aplicación no demuestra ausencia de copias internas del proveedor; ese límite permanece explícito en RET-001.
- **Alternatives considered**: Copiar mensajes a auditoría; backups privados indefinidos; borrar solo pantalla; restaurar y abrir antes de aplicar conservación.

## 7. Dependencias y cuotas

- **Decision**: Reutilizar stack gratuito 002; validador de correo estable Unlicense con dependencias/licencias verificadas al bloquear versiones. Sin correo saliente, IA, SMTP o cron SaaS de pago. Contener almacenamiento de mensajes 20 MiB/1000 filas y margen DB compartido con imágenes 003; paginar bandeja 25.
- **Rationale**: No depender de notificación externa ni trasladar el problema de conservación a otro proveedor. Si cuota o salud no verificables, bloquear recepción y mostrar fallo, sin falso éxito.
- **Alternatives considered**: Servicios de formulario externos; upgrades automáticos; cola con copia adicional de mensajes.
- **Sources**: [email-validator](https://github.com/JoshData/python-email-validator), [Supabase pricing](https://supabase.com/pricing).

[Changelog](https://supabase.com/changelog) revisado: deprecación de cifrados TLS antiguos afecta APIs HTTP a partir de noviembre2026; usar clientes Python/OS soportados, nunca desactivar verificación TLS. No se halló evidencia que cierre RET-001. No se cambia arquitectura constitucional ni requisito de gratuidad para resolverlo.
