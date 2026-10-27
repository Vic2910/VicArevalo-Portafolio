# Contract: imágenes, permisos y transacciones de proyectos

## Frontera y permisos

Reutilizar sesión, verificación Auth y autorización actual de 002, sin claves service_role ni funciones SECURITY DEFINER. Extender grants explícitos de backend_editor únicamente a tablas de proyectos; su capacidad de eliminación no alcanza revisiones de perfil/conocimientos/experiencia. Contexto SQL establecido localmente por backend verificado y limpiado al devolver conexión; usuario no suministra identidad/rol.

| Rol | Lectura pública | Contenido privado/bytes | Escritura |
|---|---|---|---|
| anon/authenticated vía Data API, incluso JWT de admin | SELECT solo public_projects y asociaciones vigentes por RLS | Ninguna | Ninguna |
| backend_project_media, solo servidor | SELECT de asociaciones vigentes | SELECT solo columnas de variantes normalizadas/metadata con al menos una referencia pública activa, mediante RLS | Ninguna; sin sesiones, auditoría privada, borradores, propiedad ni BYPASSRLS |
| backend_editor, solo servidor | SELECT | SELECT editorial y bytes solo bajo sesión/autoridad vigentes | Mutaciones de proyectos bajo guard/RLS; sin modificar bytes existentes ni autorización |
| backend_auth de 002 | Según permisos previos | Sin acceso nuevo a imágenes/proyectos | Sin grants nuevos editoriales |

RLS en tablas expuestas y privadas; esquema privado no expuesto y sin USAGE para anon/authenticated. FK desde asociación pública no concede acceso al asset privado. Rol media recibe solo permisos mínimos para políticas basadas en EXISTS sobre asociaciones públicas vigentes, sin privilegios sobre revisiones/sesiones. Consultas de galería/ficha agrupan campos y metadatos de imágenes de la misma revisión en una sola instantánea SQL/transacción de lectura, sin cargar BYTEA ni hacer N+1. Paginación pública no garantiza una foto histórica entre peticiones: cada página refleja publicaciones vigentes. La ruta exige coincidencia project_id/revision_id/association_id/variant; no acepta asset_id global como autorización. Tabla no tiene archivos privados diferentes de imágenes de proyectos; no ampliar grants a mensajes/otros recursos.

Las credenciales DB son secretas de servidor, TLS verify-full y roles no propietarios/superusuarios. No valores reales en documentos ni Git. Queries parametrizadas y nombres fijos. El acceso público a bytes se hace con consulta que verifica asociación activa y selecciona variante en la misma instantánea; ante fallo se deniega sin bytes ni fallback. Solicitudes posteriores a commit de retirada/eliminación no acceden por esa ruta, aunque archivo siga compartido con otro proyecto.

## Pipeline de carga

1. Comprobar sesión/permiso, CSRF, origen, proyecto y versión; comunicar límites antes del input. Petición multipart <=6 MiB, exactamente un archivo y campos acotados; leer máximo 5 MiB+1 del archivo, no confiar en Content-Length.
2. Rechazar más de 5 MiB; exactamente 5 MiB pasa validación de tamaño. Normalizar nombre Unicode y rechazar vacío, separadores de ruta, traversal, controles/NUL, nombres reservados o extensión no JPEG/PNG/WebP. No sanear silenciosamente un nombre peligroso para aceptarlo ni usar nombre cliente como ruta persistida.
3. Comprobar firma y formato declarado con decoder permitido. MIME presente debe ser coherente, extensión también; si MIME ausente inferir solo del decoder validado. Rechazar ejecutable renombrado, SVG/GIF/HTML, corruptos, truncados, multiframe/animados, >12 MP o lado>6000. Convertir avisos de bomba de descompresión en error y no habilitar aceptación de imágenes truncadas.
4. Verificar y reabrir/decodificar completamente con Pillow antes de aceptar. Aplicar orientación aprobada por metadatos, convertir a RGB/RGBA y reencodificar raster WebP principal/miniatura con límites descritos en modelo; excluir EXIF, ICC/comentarios y otros metadatos originales. Mostrar preview de versión normalizada al revisar; originales se descartan al finalizar petición y nunca se sirven.
5. Procesar fuera de locks SQL, máximo un archivo en procesamiento por proceso; temporales, si necesarios, privados y eliminados al terminar/error. Medir memoria/tiempo en implementación antes de fijar hosting gratuito. No enviar a IA, antivirus SaaS ni transformador de pago.
6. Volver a verificar sesión/autoridad/version dentro de transacción. Bloquear presupuesto, comprobar bytes globales, límites por revisión y tamaño físico DB con margen. Insertar asset y nueva revisión/referencias, incrementar borrador/version, contador, auditoría y recibo en un único commit. Si falla cualquier paso, no queda asset/referencia huérfano ni se reemplaza una imagen confirmada.

Calcular hash de derivados y validar octet_length; no tomar hash/size del cliente como autoridad. Variantes principal y thumbnail suman en presupuesto global. No ejecutar contenido original ni conservarlo como descarga. Validar que el backend/runtime cuenta con codecs WebP y formatos necesarios; si no, bloquear habilitación de carga con diagnóstico interno, no aceptar parcialmente.

## Publicación y revisión

Publicar exige título, descripción, >=1 tecnología y >=1 imagen, una sola representativa, alt y autorización de cada referencia, y confirmación explícita de autoría/veracidad/derechos de la revisión concreta. Confirmación y digest incluyen orden de imágenes, alt, enlaces y assets. Revisión/version cambiada o token de sesión caducado=denegar/conflicto, sin autoguardado/publicación tras reautenticar.

Cada publicación cambia exclusivamente instantánea del proyecto confirmado y sus asociaciones. Guardar/reemplazar archivo cambia solo borrador, nunca bytes/alt/derechos de otros proyectos. Archivo compartido es inmutable: no UPDATE binario, ni endpoints globales de reemplazo. Al publicar el reemplazo, antigua URL de imagen de esa revisión deja de servir para el proyecto corregido; los demás proyectos conservan sus propias asociaciones y URLs.

## Orden, retirada, eliminación y concurrencia

Orden global de locks: autorización→sesión→catálogo (si afecta publicación/orden)→proyecto→presupuesto (si cambia almacenamiento)→assets UUID ordenados. No hacer llamadas Auth, normalización ni render bajo locks. Reutilizar timeout SQL y recibos/idempotencia de 002; sin retry automático de escrituras.

- Guardado/carga/asociación crea revisión privada y actualiza solo draft_revision_id/lock_version. Todos los miembros deben pertenecer al proyecto o ser assets explícitamente autorizados para asociación por admin.
- Publicar valida guard/version/revisión actual y reconstituye una sola instantánea/asociaciones en transacción con puntero/version, catalog_version, auditoría y recibo. Alta/republicación se añade al final; corrección mantiene posición. No publicar lotes de borradores.
- Ordenar bloquea catálogo, compara catalog_version y lista exacta de IDs públicos; actualiza posiciones de forma atómica, sin tocar payload editorial ni punteros. Persistir orden 1..N sin duplicados. Una publicación/retirada/eliminación concurrente cambia versión catálogo y causa 409 en formulario antiguo.
- Retirar borra instantánea y asociaciones del proyecto, limpia puntero publicado, conserva borrador y revisiones/bytes. Actualiza catálogo/version/recibo/auditoría. No eliminar asset por el solo hecho de retirar.
- Eliminar con confirmación ligada a proyecto/version borra solo ese contenido: publicación, proyecto, revisiones y referencias. Antes de borrar assets, comprobar ausencia de cualquier referencia desde cualquier revisión de otro proyecto, incluidas privadas. FKs restrictivas y locks impiden carrera con nueva asociación. Recalcular/decrementar presupuesto solo para bytes realmente eliminados. Todos estos efectos en la misma transacción; otros proyectos y sus imágenes intactos.
- Auditoría/recibo de borrado conservan UUID/digest mínimo, no payload ni bytes, sin FK que mantenga contenido eliminado. Cancelar no ejecuta mutación editorial; logs/sesión normales de navegación no cuentan como cambio de proyecto.

Para limpieza de assets verdaderamente sin referencias, usar operación backend acotada con guard o mantenimiento de operador, locks presupuesto/asset y comprobación FK transaccional; no eliminar por contador desactualizado ni solo por no estar publicado. No limpieza basada en antigüedad de revisiones referenciadas. La UI no ofrece historial restaurable ni elimina proyectos automáticamente por cuota.

## Fallos, privacidad y límites

El éxito solo se emite tras commit y recibo. Rollback comprobado conserva último estado confirmado. Desconexión durante commit produce resultado por comprobar mediante operation_id, nunca falsa certeza de fallo ni reintento silencioso. Una operación repetida con mismo id/actor/digest devuelve recibo; con otro contenido=409. La carga usa hash de derivados en digest para distinguir archivos.

No-store en fichas/imágenes/previews; no servir signed URLs, bases64 de borradores en HTML público, paths internos, thumbnails privadas ni variantes originales. Rechazar HEAD/Range/condicionales privados igual que GET. Tras retirada no se garantiza eliminar copias ya descargadas ni respuestas iniciadas anteriormente.

Cupo preventivo: contador de payload <=64 MiB, por revisión<=20 MiB y medición física DB<350 MiB o límite más conservador derivado de plan vigente. Uso de otras features, TOAST, mantenimiento y transferencia pueden reducir margen: medir y denegar nuevas cargas si no hay capacidad comprobada. No subir de plan, evadir cuota ni borrar archivos referenciados para continuar. Una caída de lectura muestra indisponibilidad, no galería vacía ni proyectos ficticios.

Auditar altas, guardados, carga rechazada/aceptada, publicaciones, cambios de orden, retirada, eliminación, conflictos y accesos denegados con tipo/resultado/fecha/actor y UUID. Sin bytes, textos editoriales privados, nombres de archivo peligrosos, cookies, tokens, passwords ni URLs DB en logs/errores.
