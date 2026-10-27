# Contract: privacidad, idempotencia y conservación

## RET-001 — gate obligatorio

Victor confirmó mantener la garantía estricta 90 días y bloquear activación hasta acreditarla. Estado actual ERROR: no existe evidencia suficiente de eliminación física/copia exactamente al vencer con el mecanismo investigado. Las siguientes defensas son diseño verificable, no sustitución ni acreditación de ese requisito.

Puerta de recepción debe exigir conjuntamente: plazo aprobado 90, evidencia técnica vigente de garantía estricta, mecanismo comprobado, salud operativa, cero incidencias/vencidos pendientes y capacidad. Sin cualquiera: GET sin campos y POST rechazado antes de parsear/persistir datos de contacto. No flag secreto para saltar evidencia; modo TESTING solo con proyecto/fixtures aislados, nunca escape de producción. El candidato cron/TTL no puede alimentar por sí solo evidencia verified.

Una eventual apertura requiere revisión específica del mecanismo y copias compatible con gratuidad, alcance y 90 días; no basta un test exitoso ni afirmar que no hay backups accesibles. Si la garantía no es posible con restricciones actuales, se mantiene bloqueado. Solo una instrucción nueva explícita de Victor podría cambiar el requisito, y no se infiere aquí.

## Permisos

Esquema private no expuesto, RLS y grants mínimos. Sin service_role, funciones SECURITY DEFINER o permisos de cliente. Roles runtime no propietarios/superusuarios/BYPASSRLS, conexiones TLS verify-full y SQL parametrizado.

| Rol | Alcance |
|---|---|
| anon/authenticated Data API, incluido JWT admin | Ninguna lectura/inserción/mutación de mensajes, recibos, conteos o salud privada. |
| backend_contact_receive, solo servidor | INSERT columnas de nuevo mensaje pendiente, sin SELECT del contenido/bandeja. Leer/escribir recibo técnico de solicitud contextual y buckets/política/capacidad necesarios. Sin cambiar mensajes existentes, marcar o borrar. |
| backend_contact_admin, solo servidor | Bajo guard 002:SELECT de mensajes vivos, UPDATE solo state/lock_version, DELETE confirmado; recibos/constancia/capacidad mínimos transaccionales. Sin cambiar received_at/expires_at/política ni conceder roles. |
| backend_contact_retention, mantenimiento candidato | DELETE solo de vencidos y limpieza de derivados/recibos técnicos; SELECT solo IDs/fechas/campos técnicos necesarios, no remitente/texto. Escribir salud/constancia mínima. No editar ni extender vencimientos. |
| roles auth/editor/media anteriores | Sin acceso nuevo implícito a mensajes. |

Ingestión usa request_hash/nonce contextual verificado y whitelist de columnas; genera message_id en servidor sin necesitar SELECT/RETURNING del contenido. RLS solo permite INSERT si puerta válida y datos/vencimiento cumplen. Recepción pública no concede una cuenta DB ni capability general. Admin revalida identidad con Auth y autoridad/sesión actuales según 002, incluso en solicitudes directas. Contexto SET LOCAL no se hereda entre conexiones reutilizadas.

Para mantenimiento periódico, ejecutar como rol restringido con SQL estático o función SECURITY INVOKER en esquema no expuesto y EXECUTE revocado a PUBLIC. No job con credencial runtime privilegiada o contenido de mensajes en comando/historial.

## Transacción de recepción

1. Registrar la comprobación de disponibilidad antes del hook CSRF de Flask-WTF y de cualquier parser/formulario. Si está habilitado, continuar con CSRF global sin exenciones. Antes de consumir cuerpo, verificar puerta de disponibilidad; rechazar recepción bloqueada. Limitar request a 32 KiB; proxy/aplicación no registran body ni parámetros personales, incluso en rechazo temprano.
2. Verificar sesión técnica propia, CSRF/origen, firma/token y tiempo 24 h. Token expirado/inválido nunca crea mensaje. Validar nombre/correo/mensaje aunque HTML validation se omita.
3. Con consulta/locks técnicos y UNIQUE(request_hash), resolver recibo previo. Si deleted, devolver anterior no disponible. Si received y digest del cuerpo normalizado coincide, devolver confirmación de esa recepción; distinto=409. No leer mensaje para responder.
4. Para solicitud nueva, bloquear salud/política, buckets compartidos y capacidad en orden fijo. Ventanas configuradas UTC de hora/día, Retry-After calculado hasta reinicio de ventana. No contar otra recepción al reintentar; borrar mensaje no devuelve cuota antispam. Cupos iniciales 3/h sesión,30/h y 100/día globales,1000 mensajes o 20 MiB almacenados y margen físico DB 350 MiB compartido con 003.
5. Revalidar gate/salud/recursos dentro de transacción. Insertar exactamente un mensaje pending con reloj DB, received_at inmutable y expires_at=received_at+interval de 2160 horas; insertar recibo técnico, actualizar cuotas/capacidad, commit. Los datos personales solo en fila del mensaje.
6. Éxito únicamente tras commit/recibo confirmado. Fallo rollback=sin recepción nueva. Desconexión al commit=resultado incierto: permitir repetir mismo token y resolver por recibo, no afirmar existencia/ausencia ni emitir otro token automáticamente. UNIQUE y transacción resuelven doble POST concurrente.

Un mismo texto con token nuevo tras acción explícita del visitante es otra solicitud; no usar fingerprint ni correo para deduplicar. Mientras token vigente, borrado manual elimina digest/message_id y deja tombstone técnica; después de 24 h se limpia. Firma/tiempo impide replay incluso tras desaparición de tombstone, eliminación a 90 días o restauración de recibos antiguos. Restauración debe preservar reglas de firma/vencimiento y permanecer cerrada hasta reconciliar.

## Gestión privada y conteos

Bandeja/detalle/conteos aplican expires_at>referencia temporal DB y guard vigente. Usar una misma referencia/snapshot en listado y cantidades, paginación 25 y orden received_at DESC,id DESC. Leer no marca ni modifica vencimiento. Fallo de lectura no se representa como cero. Contadores de capacidad son técnicos y no se publican; cantidad privada se calcula de mensajes vivos, no incluye recibos ni eliminados.

Marcar compara lock_version y solo cambia estado, con recibo operativo. Eliminar exige token de confirmación ligado a sesión/id/versión/acción, POST/CSRF y confirmación. En transacción quita fila, limpia digest/ligadura del recibo si existe, actualiza capacidad y crea constancia fecha/motivo/resultado. Recibo administrativo solo conserva acción/resultado/capability, sin cuerpo/UUID que permita restaurar comunicación. Cancelar no modifica datos de mensajes.

Tras expiración o reautenticación no ejecutar nuevamente guardado/eliminación. Conflictos 409 conservan estado confirmado. Desconexión al commit se resuelve por recibo protegido; sin falso éxito. Mutaciones/constancia/recibo deben persistir íntegramente o rollback.

## Caducidad y mecanismo candidato de purga

El filtro expires_at impide nuevas lecturas/conteos exactamente desde el vencimiento usando reloj DB; no llamarlo borrado físico. No confiar en reloj del navegador ni en transacción prolongada iniciada antes del vencimiento: lecturas cortas y comprobación de tiempo antes de entregar. No cachear contenido o mantener cursores de bandeja de larga vida.

Para ensayos aislados, pg_cron puede invocar cada segundo una purga acotada por expires_at, sin estado pending/reviewed como excepción. Purga transaccional elimina mensaje y derivados sensibles, ajusta capacidad y registra solo fecha/motivo/resultado. No se aprueba ese segundo como tolerancia de la política estricta. `DELETE`, `VACUUM` y estado healthy no acreditan sobrescritura de todas las copias/WAL.

Salud candidata: último éxito, próximos vencimientos, ejecuciones fallidas y vencidos detectados. Error o atraso detectado pone status failed/stale, bloquea nuevas recepciones y crea alerta persistente de código/fecha en todas las vistas admin. No depende de email/notificación externa; lectura de bandeja puede mostrar alerta aunque falle la consulta de mensajes. No poder comprobar salud también bloquea. Reintentar purga con espera acotada; no ampliar expires_at ni considerar suspensión sustituto de borrar lo pendiente. Retomar no es automático por un solo heartbeat: exige resolver pendientes y volver a acreditar garantía.

Evitar crecimiento de cron.job_run_details: comandos estáticos sin datos personales y limpieza técnica acotada en pruebas; producción requiere diseño conforme antes de habilitar. Ningún job Supabase/Codex se crea durante planificación.

## Copias y constancias

No mensajes en IA, logs de aplicación/SDK/SQL, métricas, dumps gestionados por aplicación, cachés, sesiones/cookies o exportación pública. Mensajes se muestran como texto plano, sin HTML activo, imágenes remotas, autoenlaces/prefetch ni envíos a terceros. Página privada no-store y sin analytics externo.

Constancia de eliminación contiene exclusivamente fecha, motivo manual/vencimiento y resultado; no nombre, email, texto, digest personal ni referencia recuperable del mensaje eliminado. Fallos registran código operativo genérico en salud, sin copiar comunicación. Recibos técnicos aleatorios mínimos tienen expiración propia 24 h y no deben reintroducir contenido borrado.

Tratamiento de respaldos/WAL está explícitamente no acreditado. No asumir que Free carece de copias internas porque no ofrece backups accesibles. Una restauración permanece aislada/cerrada, sin lectura/recepción, aplica vencimientos y reconciliación de recibos/borrados antes de cualquier apertura, que sigue sujeta a RET-001. No habilitar PITR/upgrade ni otro servicio de pago como workaround.
