# Contract: seguridad, permisos y transacciones

## Frontera de confianza

Supabase Auth identifica; PostgreSQL privado determina autorización actual y vigencia local. Cookie opaca no representa rol. Nunca aceptar user_id, epoch, rol, contexto SQL o JWT enviados en formulario como prueba de autoridad. user_metadata no autoriza; app_metadata no sustituye tabla actual. Cliente Auth aislado por petición/sesión, nunca singleton con estado compartido entre usuarios ni mezclado con cliente público 001.

## Matriz de permisos

| Actor / rol | Publicaciones | Borradores/revisiones | Sesiones/limitador | Autorizar administrador |
|---|---|---|---|---|
| anon / authenticated por Data API, incluso JWT del admin | SELECT publicado por RLS | Sin acceso | Sin acceso | Sin acceso |
| backend_auth (credencial solo servidor) | SELECT público | Sin acceso editorial | Operaciones mínimas de sesión/limitador y append auditoría | Solo leer autorización |
| backend_editor (credencial solo servidor) | SELECT y mutación bajo guard/RLS | SELECT/INSERT revisiones, UPDATE punteros; sin borrado de revisiones | Solo columnas de estado no secretas para guard; append auditoría/recibos | Solo leer autorización |
| operador de aprovisionamiento, fuera de web | Preparación aislada/migraciones | Preparación aislada | Mantenimiento controlado | Aprobar/revocar UUID y epoch |

Los roles runtime no son propietarios, superusuarios, miembros de rol elevado ni BYPASSRLS; no pueden ALTER, otorgar privilegios o cambiar autorización. Tablas expuestas con RLS, privadas con RLS como defensa adicional y sin exposición Data API. Políticas editoriales USING y WITH CHECK comprueban autorización y sesión vigentes mediante contexto local de transacción, establecido solo por backend tras verificación. Consultas de guard usan grants de columnas no secretas, sin vistas privilegiadas, recursión de políticas ni SECURITY DEFINER.

El backend es la frontera de confianza de las credenciales DB: un rol editor puede establecer contexto SQL, pero ningún cliente web/Data API posee esa credencial o permiso. SQL siempre parametrizado, nombres de tabla/columna desde allowlist fija; nunca interpretar payload como SQL. Credenciales separadas por rol, TLS verify-full con CA/host comprobados, secretos fuera de repo. Configuración del pooler compatible con contexto SET LOCAL; rollback/limpieza al devolver conexión. Verificar ausencia de fuga de contexto entre peticiones.

Mensajes y archivos privados de futuras features: negar acceso directo por defecto; aquí no crear pantallas ni permisos genéricos de lectura sobre ellos. Storage sin buckets privados legibles públicamente; uploads/descargas privadas se diseñarán y probarán con sus features. No afirmar validación real de recursos todavía inexistentes; usar recursos aislados representativos para evaluar la frontera.

## Login, límites y sesión

1. Preautenticación: crear sesión de servidor sin identidad y sin permisos, de 10 min, con cookie opaca y nonce CSRF. Usar SessionInterface de Flask sobre ese almacén para Flask-WTF; no almacenar tokens ni payload editorial en la cookie predeterminada firmada de Flask. CSRF y origen válidos; validar tamaño/formato sin revelar cuentas. Normalizar email con trim y casefold conforme al identificador Auth del proyecto. Calcular HMAC con clave backend para cualquier correo, exista o no.
2. Reservar atómicamente intento en login_limits usando reloj DB: si bloqueo vigente, 429 hasta blocked_until; si lease vigente, 429 breve. Lease 10 s, intento Auth con timeout <=8 s y attempt_id único; completar solo si reserva aún vigente. No mantener lock SQL durante llamada Auth.
3. Validar contraseña con Supabase Auth. Fallo de credenciales o identidad sin autorización registra fallo genérico; eliminar timestamps anteriores a 15 min, agregar fallo, quinto fija blocked_until=hora del fallo+15 min. Exactamente al expirar bloqueo, permitir nuevo ciclo. Éxito reinicia fallos y libera lease. Error proveedor/DB no cuenta como contraseña errónea, deniega acceso y libera reserva si posible. Reserva expirada nunca habilita sesión con respuesta tardía.
4. Confirmar UUID y autorización actual; guardar sesión nueva con epoch, tokens cifrados y cookie nueva. No almacenar contraseña. Registro de acceso aceptado debe persistir antes de entregar sesión. Reintentos concurrentes no pueden saltar quinto fallo.
5. Cada lectura privada/mutación: localizar hash de cookie, comprobar revoked_at, plazo absoluto, inactividad y epoch actual; get_user con token Auth válido (refresh solo en backend y dentro de vigencia local); verificar UUID. Si proveedor o guard no verificables, 503 sin acceso. Después, transacción vuelve a comprobar sesión/autoridad con reloj DB antes de consultar datos y aplicar cambios. Actualizar last_seen solo por interacción explícita, no polling/assets. Refresh serializado por lease para no reutilizar refresh tokens en carrera; no renueva expiración local ni autorización.
6. Revocación/salida se serializan con operaciones mediante locks en orden autorización→sesión→elemento. Una petición iniciada después del commit de revocación siempre falla; una ya en curso termina antes de que revocación confirme. Cambiar enabled/epoch impide reutilización aunque JWT o cookie permanezcan.
7. Logout: revocar sesión local en commit y luego eliminar cookie; intentar signout Auth. Si falla proveedor, la sesión local ya no permite nada y JWT directo carece de acceso privado. Si no se confirma revocación DB, no afirmar cierre exitoso; responder error y permitir reintentar. Caducidad falla antes de refresh o mutación. Login nuevo no reproduce ninguna acción anterior.

Duraciones: inactividad predeterminada 30 min, ajustable antes de iniciar sesión hasta 300 min (diez veces) mediante control etiquetado; plazo absoluto 24 h. Persistir elección acotada en sesión, nunca confiar en expiración cliente. Permite ajuste de tiempo conforme a WCAG 2.2.1 sin depender de avisos JavaScript; plazo absoluto supera 20 h. Cualquier aviso posterior es mejora opcional, no control de seguridad. Nueva autenticación tras expiración exige acción nueva para guardar/publicar; nunca reejecución.

## Transacciones editoriales

Validación de proveedor fuera de locks. Cada operación usa autorización y sesión actuales, operación única, lock_version esperado y referencias del mismo elemento. Bloquear autoridad/sesión y fila del elemento en orden fijo; política y servicio comprueban identidad, epoch, plazos y estado. Locks breves: statement_timeout 3 s, lock_timeout 1 s. Sin llamadas HTTP ni renders bajo locks.

- Guardar: validar almacenamiento seguro, comparar versión, insertar revisión inmutable, actualizar solo borrador/version, auditoría y recibo. Datos incompletos seguros se guardan; publicación no cambia.
- Publicar: comprobar token de revisión ligado a sesión/elemento/revisión/digest/version y <=10 min; confirmar casilla explícita, validación semántica y aprobación humana. Si borrador/version cambiaron, 409. Copiar whitelist del payload a una sola tabla pública, actualizar puntero/version, aprobación, auditoría y recibo. Confirmar commit antes de 303.
- Retirar: solo skill/academic, comprobar publicación y versión confirmadas. Borrar instantánea de ese elemento, published_revision_id=null, conservar draft_revision_id y todas las revisiones; registrar retirada/versión/version retirada y recibo. Otras filas intactas. No permitir retirada de perfil desde este flujo.
- Fallo comprobado antes/como rollback: conservar estado anterior íntegro y no éxito. Si conexión se pierde durante commit, resultado incierto: consulta autorizada de operation_receipts con el mismo operation_id. Existencia confirma commit y resultado; ausencia comprobada permite acción nueva explícita, nunca retry silencioso.
- Repetir operation_id con cuerpo/actor/acción idénticos devuelve resultado previo sin mutar otra vez; distinto contenido=409. Guardar/Publicar/Retirar no ejecutan UPSERT ciego sobre otra revisión ni un lote global.

## Auditoría y protección de superficies

Registrar login aceptado/rechazado/limitado, lecturas privadas aceptadas/denegadas, logout, expiración/revocación detectada, guardados, conflictos, publicaciones y retiradas con tipo/resultado/fecha/identidad disponible y correlación. No registrar secretos, cuerpos de petición, textos privados, passwords, Authorization/Cookie ni URLs con claves. Filtrar logs de HTTP/SDK/errores y deshabilitar debug en despliegue.

Mutaciones y su evento/recibo comparten transacción; fallo de auditoría revierte. Denegaciones y fallos externos se emiten a sink estructurado seguro de servidor si DB no está disponible; pruebas comprueban ambos destinos. Si no se puede registrar un acceso aceptado, denegarlo. Exportaciones sanitizadas solo para operador, sin visor público. Cifrado de tokens con Fernet y clave externa rotatable; pérdida/rotación incompatible invalida sesiones y exige login, sin fallback en texto claro.

CSRF en login/logout y toda modificación, comparación de origen con allowlist exacta configurada y sin confiar en cabeceras proxy arbitrarias. Jinja autoescape, sin safe para contenido editorial; previews igualmente escapadas. Cookie y cabeceras según admin-http.md. Conexiones/tokens/errores nunca se incluyen en documentos, HTML, logs ni CV.
