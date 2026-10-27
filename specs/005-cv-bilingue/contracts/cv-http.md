# Contract: selección, disponibilidad y descarga del CV

HTML español para interfaz inicial, nombres explícitos Español/English y etiquetas de idioma. Jinja autoescape, HTTPS, no-store y headers de seguridad 002. Sin dependencias de contacto 004, IA, GitHub o servicios PDF externos.

## Público

| Ruta | Contrato |
|---|---|
| GET /cv | Consultar snapshot actual y presentar disponibilidad independiente es/en. Link de descarga por idioma disponible; idioma no disponible tiene texto comprensible sin href o botón falso. Ningún idioma preseleccionado silenciosamente para descarga directa. |
| GET /cv/<language>.pdf | language estrictamente es o en; snapshot nuevo, validación de mínimo/aprobación y generación completa. Éxito 200 application/pdf como attachment. |

Idioma desconocido=400 con explicación y enlace al selector, nunca fallback. Datos/traducción faltantes=409 con HTML accesible de indisponibilidad, sin PDF parcial/antiguo. Fallo de fuente/render/recurso=503 con explicación y reintento explícito del mismo idioma; no convertir error en lista vacía ni confirmar descarga exitosa. Selector con lectura de fuente fallida=503; con fuente válida pero idiomas incompletos=200 y motivos independientes.

Cada descarga revalida disponibilidad aunque /cv mostrara disponible antes. No servir snapshot/PDF cacheado entre solicitudes. Generación establece su snapshot al iniciar lectura SQL fresca; si publicación termina antes de iniciarlo debe verla. Una publicación posterior puede dejar terminar el PDF de snapshot anterior coherente; siguiente petición toma lo nuevo. No ofrecer URL pública de historial que permita descargar retirados como vigentes.

Éxito: Content-Type application/pdf, Content-Disposition attachment con Victor_Rafael_Arevalo_Sierra_CV_es.pdf o _en.pdf, Content-Language es/en, Cache-Control no-store, nosniff, longitud del buffer completo y X-CV-Source-Version con facts_version público no sensible. No ETag/304, descarga parcial desde archivo antiguo o firma con claves. Fecha/título/autor/idioma del PDF corresponden al modelo, sin paths internos o secretos. No comenzar streaming antes de completar/validar.

Navegación 001 registra capacidad cv cuando al menos un idioma está disponible; apunta al selector. Indisponibilidad del formulario de contacto no bloquea CV si existe correo público autorizado en perfil. Links externos se imprimen como texto aprobado dentro del PDF, no ejecutan fetch del servidor.

## Administración 005

Heredar identidad/autoridad/sesión vigentes, CSRF/origen, protección de secretos, recibos y errores 002 en cada operación, incluso solicitudes directas. No signup ni permisos por metadata del cliente.

| Ruta | Entrada / resultado |
|---|---|
| GET /admin/cv/proyectos | Mostrar proyectos publicados, selección/orden CV y versiones; diferenciar orden de galería. |
| POST /admin/cv/proyectos | IDs/epochs y posiciones, expected_selection_version, versiones de publicaciones mostradas, confirmed=true, operation_id y CSRF. Confirmar lista completa, incluso vacía;303 solo tras commit. |
| GET /admin/cv/traducciones | Fuentes públicas y estado de inglés: pendiente/aprobado/desactualizado, sin publicar sugerencias. |
| GET /admin/cv/traducciones/<kind>/<id>/editar | Fuente pública actual y borrador inglés, hash/version y campos traducibles/invariantes. |
| POST /admin/cv/traducciones/<kind>/<id>/borrador | Textos seguros, invariant_fields revisables, expected_version y operation_id; guarda privado, no habilita idioma. |
| GET /admin/cv/traducciones/<kind>/<id>/revisar | Vista lado fuente/traducción, revisión/digest/version concretos y confirmación de equivalencia de hechos. |
| POST /admin/cv/traducciones/<kind>/<id>/aprobar | revision_id, expected_version, source_hash verificado en servidor, review_token ligado a sesión, confirmed=true, operation_id y CSRF. Revalidar fuente, aprobar/materializar en transacción. |
| GET /admin/cv/operaciones/<operation_id> | Resultado propio de operación solo con permiso vigente, sin texto privado. |

Panel académico 002 deberá exponer record_kind explícito y sujeto a publicación revisada; no inventar educación desde el CV. No crear otra tabla de hechos educativos desconectada de 001.

Lista con duplicados, posiciones inválidas o proyecto no publicado=422/409, sin cambio parcial. Source/selección/revisión obsoleta=409; conservar estado y ofrecer recarga, sin publicar borradores para resolver. Lectura privada sin sesión redirige; POST 401, identificado sin permiso 403, CSRF 400/origen ajeno 403, recurso 404, entrada 422 y dependencia 503. Commit incierto usa recibo y no repite automáticamente tras login.

Retirada/eliminación de 003 excluye del siguiente PDF sin sustitución. Selección/orden 005 no cambia la galería. Corrección del mismo ciclo publicado conserva inclusión; republicación después de retirada exige nueva inclusión por epoch. No hay listas de proyectos diferentes entre es/en.

## Accesibilidad

Selector/gestión completos con teclado, foco visible, etiquetas/lenguaje comprensibles y estados no basados solo en color. Orden por posiciones numéricas y confirmación, sin arrastrar obligatorio. Error inicial por título/encabezado/texto, resumen asociado a campos; cambios dinámicos opcionales anuncian status apropiado. Descargas identificadas por idioma y tipo PDF; no abrir ventanas automáticamente.

Skip link, jerarquía, 200 % texto,320 px CSS, espaciado, contraste WCAG y movimiento reducido. Idioma incompleto explica motivo genérico sin revelar borradores; admin puede ver detalles autorizados. Flujos de fallo y reintento se evalúan junto a éxito; auditoría de todos los criterios A/AA aplicables. Texto extraíble y una columna no son por sí solos certificación PDF/UA o compatibilidad ATS universal.
