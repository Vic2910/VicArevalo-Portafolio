# Contract: contacto público y bandeja privada

Condicionado por RET-001: la recepción real sigue bloqueada. Rutas de recepción habilitada describen contrato futuro/ensayos aislados, no permiso para activar. HTML español UTF-8, autoescape, no-store, sin contenido de mensajes en URL, cookies, logs o páginas públicas.

## Disponibilidad y recepción

| Ruta | Contrato |
|---|---|
| GET /contacto | Si falta garantía estricta/política/salud:503 con explicación accesible, sin campos de nombre/correo/mensaje ni emisión de token de envío. Si todo está acreditado:formulario con finalidad y 90 días visibles, tres campos etiquetados, sesión técnica/CSRF y token 24 h. |
| POST /contacto | Comprobar puerta de disponibilidad antes de parsear campos y de persistir; si bloqueada 503, no aceptar/guardar datos. Si habilitada:validación, idempotencia, antispam y transacción;303 a /contacto/recepcion tras commit. |
| GET /contacto/recepcion | Capability de recibo ligada a sesión propia (cookie técnica, no URL con correo/texto) permite solo confirmación genérica de su solicitud, nunca leer contenido, nombre, correo, ID consultable de mensaje o conteos. |

En navegación 001, capacidad contact solo disponible cuando recepción acreditada/operativa; si no, etiqueta de indisponibilidad sin acción aparente. Acceso directo a /contacto mantiene estado útil. Un visitante puede reintentar misma solicitud con mismo token tras incertidumbre mientras siga vigente; el servidor no genera token nuevo automáticamente para reenviar la misma operación.

Datos válidos: nombre 1–100, correo válido<=254 y mensaje 10–5000 caracteres Unicode tras trim. Errores 422 asociados a campos y resumen enlazado, conservar entradas seguras solo en respuesta de esa solicitud no persistida, sin eco de passwords/tokens. Datos no válidos no producen mensaje ni recibo de recepción. Petición máxima 32 KiB y campos técnicos acotados; no archivos ni campos personales adicionales.

Frecuencia:3 recepciones nuevas/h por sesión técnica,30/h y 100/día global, configurables y documentadas. Ventanas UTC compartidas, 429 con Retry-After/espera legible, sin guardar mensaje nuevo. Cookies rotables no evitan tope global; no prometer inmunidad a spam. Reintento de recibo existente se resuelve antes de consumir otra cuota de recepción, tras verificar puerta/CSRF/capability. No CAPTCHA, timer mínimo, JS o gesto necesario.

Firma/token inválido o sesión ajena=400/403 genérico; token expirado=410 sin recrear; mismo token con otro cuerpo=409; recibo de mensaje eliminado=410 «La recepción anterior ya no está disponible». Cuota/DB/salud no verificable=503. Persistencia incierta:«No pudimos confirmar la recepción. Puedes reintentar esta misma solicitud»; no afirmar que existe ni que no existe. Success solo tras commit o recibo técnico confirmado.

## Bandeja y operaciones administrativas

Heredar guard 002 en cada lectura/mutación, incluso solicitudes directas. GET sin sesión redirige a login; POST sin sesión 401; identificado sin permiso 403; verificación indisponible 503. Ningún JWT cliente obtiene Data API de mensajes.

| Ruta | Resultado |
|---|---|
| GET /admin/mensajes?page=N | Paginación 25, newest-first; total y pendientes/revisados actuales, sin vencidos/eliminados. Vacío real 200, fallo 503 sin ceros inventados. |
| GET /admin/mensajes/<id> | Nombre, correo de respuesta, texto, fecha, vencimiento y estado; no cambia pending/reviewed ni plazo. Texto plano escapado, URLs no autoactivadas ni prefetch. |
| POST /admin/mensajes/<id>/estado | state pending/reviewed, expected_version, operation_id y CSRF;303 tras commit. |
| GET /admin/mensajes/<id>/eliminar | Confirmación comprensible con cancelar/eliminar, sin mutación. |
| POST /admin/mensajes/<id>/eliminar | expected_version, confirmation_token ligado a sesión/id/acción, confirmed=true, operation_id y CSRF; eliminación transaccional,303 tras commit. |
| GET /admin/mensajes/operaciones/<operation_id> | Resultado propio de operación, sin mensaje eliminado; solo admin vigente. |

Mensaje vencido/eliminado/no existente=404 tras guard. Conflicto=409 sin sobrescritura; estado inválido 422; CSRF 400/origen ajeno 403. Cancelar vuelve a bandeja sin POST destructivo. Caducidad/fallo no confirma guardado ni reejecuta tras login. No respuestas SMTP, adjuntos, análisis IA, exportación ni enlace mailto que envíe información automáticamente.

## Accesibilidad y superficies

Etiquetas persistentes, autocomplete name/email, instrucciones/longitudes/aviso visibles, h 1/encabezados/regiones, skip link y foco. Resumen de errores enlazado a campos con aria-invalid/aria-describedby. Confirmación y espera mediante texto accesible inicial; si se añaden cambios dinámicos, status adecuado. Confirmar eliminación en página completa, sin modal obligatorio.

Teclado completo y sin trampas, 200 % texto,320 px CSS, espaciado ampliado, contraste WCAG, movimiento reducido y uso sin JS. Envío preparado<2 min y localizar/leer/marcar<1 min a validar manualmente. Auditoría de todos los criterios A/AA aplicables, no solo esta lista.

No-store en todas las respuestas, incluyendo errores y bandeja; CSP/headers y cookies seguras según 002. Ningún script de analytics, tercero o IA recibe contenido. El límite de tokens técnicos 24 h se informa y permite preparar formulario sin barrera breve; si CSRF caduca se ofrece renovar conservando el mismo token de solicitud, nunca reenviar con uno nuevo automáticamente.
