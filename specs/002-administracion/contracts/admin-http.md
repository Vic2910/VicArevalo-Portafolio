# Contract: HTTP administrativo

HTML español UTF-8 renderizado con Jinja, sin JS obligatorio. Todas las respuestas /admin: Cache-Control no-store, Referrer-Policy same-origin, X-Content-Type-Options nosniff, CSP sin scripts inline ni framing (frame-ancestors none). HTTPS obligatorio en despliegue; cookies Secure/HttpOnly/SameSite=Lax, sin Domain, Path=/admin. Nunca llevar tokens o contenido privado en URL. Formularios POST con CSRF, origen validado y tamaño máximo 64 KiB; GET nunca modifica contenido editorial.

## Rutas propuestas

| Método y ruta | Entrada / resultado |
|---|---|
| GET /admin/login | Formulario correo/contraseña, etiquetas y autocomplete username/current-password; CSRF de preautenticación sin secretos Auth. |
| POST /admin/login | Correo, contraseña e idle_timeout_minutes permitido (30–300); verificar limitador, Auth y autorización; éxito persiste sesión/auditoría y 303 a /admin/. Sin signup, roles ni JWT suministrables por cliente. |
| POST /admin/session/extend | Interacción explícita con CSRF y guard vigente; renovar actividad dentro del plazo absoluto, sin publicar ni cambiar contenido. |
| POST /admin/logout | Revocar sesión propia antes de confirmar y borrar cookie; 303 a login tras revocación persistida. Intentar signout del proveedor sin depender de él para bloquear replay local. |
| GET /admin/ | Identidad autorizada y listado de perfil/conocimientos/experiencia con estado borrador/publicado; sin dashboard de métricas fuera de alcance. |
| GET /admin/items/new?kind=skill o academic | Formulario nuevo; perfil singleton se edita por su id. |
| POST /admin/items | Crear borrador seguro con kind permitido, payload y operation_id. Nunca crea otro perfil ni publica. |
| GET /admin/items/<uuid>/edit | Borrador actual, lock_version y estado de publicación; contenido escapado. |
| POST /admin/items/<uuid>/draft | payload, expected_version, operation_id y CSRF; guardado privado, luego 303 a editor con confirmación persistida. |
| GET /admin/items/<uuid>/review | revision_id y expected_version; versión exacta, errores o vista previa y confirmación explícita. |
| POST /admin/items/<uuid>/publish | revision_id, expected_version, review_token, confirmed=true, operation_id y CSRF. Publica solo lo revisado, 303 tras commit. |
| GET /admin/items/<uuid>/withdraw | Solo skill/academic: vista de versión publicada y explicación de conservación de borrador. |
| POST /admin/items/<uuid>/withdraw | published_revision_id, expected_version, confirmation_token, confirmed=true, operation_id y CSRF; retirada individual, 303 tras commit. |
| GET /admin/operations/<uuid> | Resultado del recibo solo para sesión autorizada y actor correspondiente; confirma resultado tras incertidumbre de red. |

Sin rutas públicas para crear administradores, alterar permisos, eliminar elementos o retirar perfil. Validar kind y UUID; no usar nombres de tabla ni destinos de redirect suministrados por cliente. next, si existe, solo ruta relativa /admin permitida sin esquema/host externo.

## Estados HTTP y mensajes

- GET privado sin sesión: 303 a login sin incorporar contenido privado; POST sin sesión/caducada: 401 con «No se guardó esta solicitud. Inicia sesión y vuelve a revisar antes de enviarla». No guardar payload para reejecutarlo tras login.
- Identidad válida no autorizada o permiso retirado: 403 genérico, sin contenido ni efecto. Verificación/DB/Auth indisponible: 503 genérico, denegar.
- Credenciales erróneas o identidad no aprobada: mismo 401 y mensaje genérico sin confirmar existencia. Bloqueo: 429 con Retry-After y hora/plazo accesible, para cualquier identidad normalizada. Intento concurrente reservado: 429 breve sin eludir contador.
- Validación de campos: 422 con resumen enlazado a campos, aria-invalid y aria-describedby; conservar entradas seguras únicamente mientras sesión esté autorizada, nunca password.
- CSRF inválido: 400; origen ajeno: 403. Rechazar antes de mutar. No imprimir token ni razón interna sensible.
- Conflicto de expected_version/revisión: 409, explicar que no se sobrescribió la versión guardada; ofrecer recargar y comparar, sin reemplazo automático.
- Recurso no encontrado o ajeno al tipo permitido: 404 tras guard, sin revelar existencia a no autorizados.
- Persistencia fallida con rollback comprobado: 503, sin éxito. Commit incierto por desconexión: «No se pudo confirmar el resultado; consulta su estado antes de volver a enviarlo», nunca afirmar que se perdió ni repetir automáticamente. Consultar recibo con misma operación autorizada.

## Presentación accesible y reautenticación

Un h1, regiones semánticas, skip link y foco visible. Etiquetas persistentes, requisitos previos claros, navegación consistente y botones de acción con nombre específico. Confirmar publicación/retirada en páginas completas, sin modal obligatorio. Diferenciar visual y textualmente versión pública y borrador, nunca solo color.

Mensajes iniciales por título/encabezado y texto; si se añaden actualizaciones dinámicas usar status apropiado. Tras error, resumen con enlaces a campos; no mover foco de forma inesperada. Contraste 4.5:1 texto normal, 3:1 grande y componentes necesarios; 200 % de texto, 320 px CSS, espaciado ampliado y movimiento reducido.

Avisar antes de timeout de inactividad si el panel permanece abierto mediante mejora progresiva opcional, ofreciendo extensión explícita dentro de 24 h; la extensión es POST protegido y requiere guard actual. La inactividad se puede ajustar antes del login de 30 hasta 300 minutos y el límite absoluto de 24 h se explica al iniciar. No autosave, publicación ni repetición automática al reautenticar; no localStorage/cookies/URLs para recuperar contenido. Una pestaña antigua puede conservar texto en su DOM local, pero servidor no lo reexpone en respuesta no autorizada. El usuario puede volver a introducirlo tras autenticarse y realizar acción nueva.
