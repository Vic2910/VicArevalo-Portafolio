# Contract: galería, fichas y gestión de proyectos

HTML UTF-8, lang=es y Jinja autoescape. Rutas administrativas heredan guard, sesión, CSRF, origen, errores y headers de 002; no crean otra autenticación. Público solo devuelve instantáneas aprobadas. No JS obligatorio.

## Lectura pública

| Ruta | Contrato |
|---|---|
| GET /proyectos?page=<entero> | Galería de 12 tarjetas por página, orden display_order/id; título, descripción, tecnologías e imagen representativa. No consultar bytes en listado. Enlaces anterior/siguiente accesibles. |
| GET /proyectos/<project_id> | Ficha de versión vigente, imágenes ordenadas, alternativas y enlaces opcionales reales. No selector público de revisión privada. |
| GET o HEAD /proyectos/<project_id>/versiones/<revision_id>/imagenes/<association_id>/<variant> | variant principal/miniatura; comprobar relación exacta y publicación todavía activa antes de servir bytes. Sin redirección a Storage ni rutas de asset global. |

Lista sin publicaciones: 200 y estado vacío comprensible, sin tarjetas ficticias. La galería es un destino disponible cuando el módulo está operativo aunque esté vacía; registrar capacidad projects y endpoint para navegación 001. Página inválida=400; página posterior al final=404, salvo página1 vacía. Lectura fallida=503 con explicación accesible, nunca estado vacío falso.

Ficha inexistente/retirada/borrador/eliminada=404 genérico. Imagen/asociación/revisión/variant no vigente=404, sin revelar existencia privada. Dependencia indisponible=503, sin fallback a copia retirada. Estado de proyecto publicado con imagen fallida mantiene descripción, tecnologías, alt y resto de imágenes usables. Renderizar alt en img y leyenda textual pertinente para conservar alternativa incluso si carga/decodificación falla. No carrusel obligatorio ni controles que dependan de la imagen.

Páginas e imágenes usan Cache-Control no-store, sin CDN, ETag/304 ni URLs firmadas; GET y HEAD verifican estado vigente incluso con cabeceras condicionales/Range. Puede responder 200 con imagen completa ignorando Range; nunca servir antes del control de publicación. Content-Type image/webp, nosniff y longitud correcta. No bytes originales ni metadatos privados.

El contrato bloquea solicitudes nuevas posteriores al commit de retirada/eliminación; no promete revocar bytes ya enviados o una descarga iniciada antes. URLs de versiones antiguas dejan de entregar tras una corrección publicada, aunque esa revisión siga privada.

## Administración (además de rutas 002)

| Método y ruta | Entrada / resultado |
|---|---|
| GET /admin/proyectos | Listado privado de proyectos con estado y acciones identificadas. |
| GET /admin/proyectos/nuevo | Formulario incompleto permitido como borrador. |
| POST /admin/proyectos | Campos seguros y operation_id; crear borrador privado, 303 tras commit. |
| GET /admin/proyectos/<id>/editar | Borrador, versión y diferencia clara con publicación. |
| POST /admin/proyectos/<id>/borrador | Campos/referencias + expected_version, operation_id y CSRF; no publica. |
| POST /admin/proyectos/<id>/imagenes | Multipart: un archivo, alt/autorización opcionales en borrador, target_association_id opcional para reemplazo, expected_version, operation_id y CSRF. Valida y crea nueva revisión de borrador atómicamente. |
| POST /admin/proyectos/<id>/imagenes/asociar | Seleccionar asset existente que el admin puede leer; alt/orden/derechos contextuales, expected_version y operation_id. No da acceso a visitantes. |
| GET /admin/proyectos/<id>/versiones/<revision_id>/imagenes/<association_id>/<variant> | Preview solo con identidad y permiso vigentes, no-store; no prolonga sesión por petición de asset. |
| GET /admin/proyectos/<id>/revisar | Revisión/digest/version exactos, informe de validación y confirmación de autoría y derechos. |
| POST /admin/proyectos/<id>/publicar | revision_id, expected_version, review_token, confirmaciones explícitas, operation_id y CSRF; solo versión revisada. |
| GET /admin/proyectos/orden | IDs publicados y catalog_version, posiciones numéricas etiquetadas, sin drag obligatorio. |
| POST /admin/proyectos/orden | Lista completa ordenada + expected_catalog_version, confirmación, operation_id y CSRF; solo orden público. |
| GET /admin/proyectos/<id>/retirar | Confirmación clara de efectos públicos y conservación privada. |
| POST /admin/proyectos/<id>/retirar | Publicación/version confirmadas, confirmation_token, operation_id y CSRF. |
| GET /admin/proyectos/<id>/eliminar | Confirmación destructiva distinta de retirada, proyecto identificado y advertencia de eliminación editorial. |
| POST /admin/proyectos/<id>/eliminar | expected_version, confirmation_token, confirmed=true, operation_id y CSRF. Cancelar vuelve al listado sin POST destructivo. |
| GET /admin/proyectos/operaciones/<operation_id> | Recibo solo para admin vigente y actor; permite resolver commit incierto incluso si proyecto se eliminó. |

Tokens de confirmación/revisión ligados a sesión, acción, proyecto, revisión/digest/version, con vida 10 min. Cambiar borrador invalida confirmación de contenido anterior; republicar requiere nueva confirmación. No aceptar texto/versión del formulario como contenido aprobado sin consultar revisión persistida.

## Errores y accesibilidad

Sin sesión/caducada: GET privado redirige a login; POST=401 sin guardar/repetir acción. Sin permiso=403; CSRF=400/origen ajeno=403; recurso ausente=404; conflicto de versión/membresía=409; campo/archivo inválido=422; tamaño archivo/request excesivo=413; cupo preventivo=409 con explicación y estado intacto; proveedor/DB no verificable=503. Éxito 303 únicamente tras persistencia; commit incierto muestra estado por comprobar, no éxito ni retry automático. No exponer SQL, claves, binarios, filenames peligrosos ni errores internos.

Errores vinculados a campos y resumen enlazado; contraseña nunca repoblada. Rechazo de archivo conserva proyecto/imágenes confirmadas y pide seleccionar archivo otra vez, sin autosubmit tras login. Límite/optimización visibles antes de carga, input file nativo y etiqueta. Orden con campos numéricos/confirmación funciona con teclado y lector; no depender de hover/color/gestos. Botones/links anuncian acción y proyecto.

Un h1, encabezados coherentes, foco visible, skip link, texto 200 %, redistribución a320 px, contraste WCAG y movimiento reducido según 001/002. Alternativas de imágenes son contextuales y revisadas. Links externos HTTP/HTTPS en misma pestaña por defecto, sin acciones vacías; si se usa nueva pestaña, anunciarlo y aplicar noopener. No comprobar disponibilidad externa mediante fetch en servidor. Auditar todos los criterios A/AA aplicables, no solo esta lista.
