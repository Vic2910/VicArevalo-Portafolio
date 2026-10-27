# Contract: dashboard y control administrativo

Todas las rutas requieren guard 002 (identidad verificada, autorización/epoch/sesión actuales), HTTPS, no-store y headers de seguridad. Sin dashboard público, token GitHub en cliente ni nueva autenticación. GET no consulta GitHub, no encola trabajo, no renueva intentos y no modifica datos de fuente.

## Rutas

| Ruta | Contrato |
|---|---|
| GET /admin/metricas | Leer Supabase:proyectos publicados/borradores, mensajes actuales totales/pendientes y commits con último completo/último parcial. Cada tarjeta tiene estado/fecha propios. |
| POST /admin/github/sincronizaciones | Solicitud explícita start con operation_id y CSRF. Reservar solo si permiso, cooldown, proveedor, recursos y worker operativo lo permiten;202 después de persistir queued. |
| POST /admin/github/sincronizaciones/<run_id>/continuar | Acción explícita resume con expected_run_version, operation_id y CSRF; mismo corte/manifiesto solo si compatible y nueva ventana permitida. No replay automático después de login. |
| GET /admin/github/sincronizaciones/<run_id> | Estado local:alcance, páginas/repos procesados, timestamps, razones de parcialidad, restricciones y próximo intento; no requests GitHub. |
| GET /admin/github/operaciones/<operation_id> | Recibo de start/resume propio para resolver doble POST/resultado incierto; solo admin vigente. |

GET sin sesión 303 a login; POST sin sesión/caducada 401; identificado sin permiso 403; verificación indisponible 503. CSRF 400/origen ajeno 403; run inexistente 404; conflicto activo/version 409; espera local/proveedor 429 con Retry-After y momento accesible. Worker ausente/salud no verificable/cupo 503 sin confirmar inicio. Mismo operation_id/cuerpo retorna mismo recibo, distinto cuerpo 409. Fallo/commit incierto no produce éxito ficticio; reintentar misma operación para resolver.

202 significa solicitud persistida; no afirmar «Sincronización completada» ni actualizar fecha satisfactoria. Worker interrumpido se muestra como tal sin borrar último válido. Inicio/continuación no autorizado no cambia cooldown/control ni hace llamadas externas. No rutas para publicar repositorios como proyectos, cambiar cuenta objetivo desde formulario o introducir endpoints arbitrarios.

## Métricas

Proyectos publicados y borradores son categorías de proyectos, no de revisiones. Publicado con cambios pendientes sigue published; retired no pertenece a ninguna de esas dos categorías, puede mostrarse separado. Eliminados no suman. Mensajes solo actuales según 004, sin vencidos/recibos/eliminados; no mostrar contenido ni remitentes. Fallo de lectura de una tarjeta produce indisponibilidad solo allí, sin ceros inventados.

RET-001004 permanece visible como estado de contacto bloqueado si corresponde;006 no lo levanta. Ausencia de esquema/lectura de mensajes no equivale a 0. Un cero consultado correctamente puede coexistir con recepción bloqueada y se explica así.

Commits sin éxito anterior:«Sin resultado completo confirmado», nunca 0 supuesto. Parcial inicial muestra datos observados expresamente parciales y fecha/corte propios. Con completo anterior, ese conteo sigue identificado con su manifiesto y antigüedad; parcial al lado, nunca se suma ni reemplaza silenciosamente. Perfil/repo inaccesible tiene explicación, no conteo 0 de ese error.

Cada conteo muestra corte/período de autoría, repos y forks incluidos, rama/cabeza observadas, exclusiones, dedupe repo/SHA, atribución por cuenta, ventana de observación y fecha de comprobación satisfactoria. Advertencia explícita:SHA idéntica puede contar una vez por repositorio, incluidas bifurcaciones; no es historial global ni medida de experiencia laboral. «Completo» siempre va seguido de «para este alcance».

## Interacción y accesibilidad

HTML español, h 1/encabezados, regiones y skip link; nombres de acción claros y foco visible. Totales con etiquetas textuales, no gráficos necesarios. Espera, sin datos, parcial, error y completitud no dependen solo de color. Explicaciones se pueden leer con teclado/lector sin hover.

Refrescar estado local mediante link/botón GET funciona sin JS; polling opcional solo Supabase, acotado y sin prolongar sesión por tráfico de fondo. No dispara requests GitHub ni recrea attempts. Controles de start/continuar no aparentan estar disponibles durante espera:mostrar motivo y fecha/plazo de reintento, no botón falso.

Errores iniciales por título/encabezado/texto; actualizaciones dinámicas opcionales en región status sin robar foco. Texto 200 %,320 px CSS, orientación/espaciado, contraste WCAG y movimiento reducido. Evaluar todos los criterios A/AA aplicables y comprensión de alcance/fechas; objetivo manual SC-008 en<1 min.

Sin logs de Authorization/Cookie, token opcional, cuerpos REST, emails/mensajes de commit o datos de contacto. Errores usan códigos seguros/correlación; HTML no incorpora JSON bruto del proveedor.
