# Data model: 003-gestion-proyectos

Modelo lógico, sin migraciones ejecutadas. UUID para entidades y operaciones; timestamptz UTC, fechas localizadas en UI. Tablas `private` no expuestas a Data API. Imágenes se persisten como bytes raster normalizados, nunca originales ni archivos del filesystem público.

## Entidades editoriales y archivos privados

| Tabla propuesta | Campos principales | Reglas |
|---|---|---|
| private.projects | id PK, draft_revision_id, published_revision_id nullable, lock_version, created_at, updated_at | Identidad estable, punteros a revisiones del mismo proyecto. Estado derivado: borrador, publicado con/sin cambios, retirado. Sin slug editable; URL por UUID. |
| private.project_revisions | id PK, project_id FK, revision_number, title, description, technologies array, repository_url nullable, demo_url nullable, created_by, created_at | UNIQUE(project_id, revision_number). Inmutables mientras exista proyecto; solo eliminación explícita del proyecto permite borrar sus revisiones. Sin UI de restauración histórica. |
| private.project_revision_images | revision_id FK, association_id UUID, asset_id FK, alt_text nullable en borrador, position, representative boolean, use_authorized boolean | PK(revision_id, association_id); orden único por revisión. Alt, derechos y papel representativo pertenecen a referencia contextual, nunca al archivo global. |
| private.project_image_assets | id PK, main_bytes BYTEA, thumbnail_bytes BYTEA, mime=image/webp, width/height, main_size, thumbnail_size, sha256, created_at | Bytes inmutables y decodificados. Tamaños congruentes con octet_length. No UPDATE de contenido; reemplazo usa asset nuevo o selección explícita de otro existente. Sin deduplicación automática pública. |
| private.project_catalog | singleton PK, version | Serializa cambios de membresía/orden público y detecta formulario de orden desactualizado. |
| private.project_media_budget | singleton PK, stored_bytes, updated_at | Contador de ambas variantes de todos los assets, no solo visibles. Actualización bajo lock y límites de recurso; reconciliación con sumas reales. |
| private.project_operations | operation_id PK, actor_id, project_id nullable, action, request_digest, result_revision_id nullable, result_version, catalog_version, committed_at | Recibos atómicos e idempotencia de guardar, adjuntar, publicar, ordenar, retirar, eliminar. Referencias de recibo no deben impedir eliminar contenido del proyecto. |
| private.project_publication_events | id PK, project_id, revision_id, action, actor_id, content_digest, operation_id único, confirmed_at | Evidencia de revisión/publicación/retirada/eliminación. Tras eliminación conservar solo UUID/digest/evento, sin textos ni bytes. |

Auditoría reutiliza security_events de 002, ampliando eventos de proyecto y target UUID sin FK que impida eliminación. No añadir permisos DELETE sobre editorial_revisions de 002. RLS de proyectos exige sesión/autoridad actuales de 002, incluso para reads/previews privadas.

## Instantáneas públicas

| Tabla | Campos visibles | Relación |
|---|---|---|
| public.public_projects | id PK, revision_id, title, description, technologies, repository_url/demo_url nullable, display_order, published_at | Solo versión aprobada vigente. No borrador, metadatos privados ni bytes. |
| public.public_project_images | project_id FK, revision_id, association_id, asset_id, alt_text, position, representative, width/height | Asociaciones exactas de la publicación actual; FK/restricciones deben impedir mezcla de versiones. URLs se construyen con router, no se guardan URLs firmadas. |

Galería, ficha y fuente de futuros CV usan public_projects. Retirar/eliminar quita la instantánea y asociaciones en una transacción. La consulta de galería no carga bytes ni revisiones privadas. Datos públicos no implican que la tabla privada de assets sea accesible con clave anon.

## Validación y presupuestos

- Título hasta 200 caracteres; descripción hasta 10000; tecnologías máximo 20, cada una hasta 80, sin duplicados tras trim/casefold. Publicar exige título/descripción y >=1 tecnología, sin marcadores ni afirmaciones no revisadas. Borrador seguro permite campos faltantes, normalizados a vacío/null según tipo.
- URLs opcionales hasta 2048, HTTP/HTTPS con host y puerto válidos, sin credenciales ni controles. No aceptar javascript/data, protocolo relativo o atributos HTML. No realizar fetch servidor para comprobar el enlace.
- Imágenes: máximo 10 referencias por revisión; exactamente una representativa al publicar; toda referencia informativa requiere alt no vacío hasta 300 y autorización explícita de uso. Mismo asset compartido puede tener alt diferente por proyecto. Autoría/veracidad se confirman en revisión, no se deducen de repositorios o IA.
- Entrada por archivo <=5,242,880 bytes inclusive; formato JPEG/PNG/WebP, estático, <=12 MP y lado<=6000. Filename normalizado seguro con extensión coherente; no rutas/control/reservados. Derivados principal<=2 MiB/1600 px y thumbnail<=256 KiB/480 px, WebP sin metadatos.
- Una petición de carga lleva un archivo; límite HTTP multipart 6 MiB para permitir sobrecarga, manteniendo contador real de archivo de 5 MiB. Formularios editoriales sin archivo siguen 64 KiB de 002.
- Por revisión <=20 MiB de derivados únicos, global<=64 MiB de assets de todos los borradores/revisiones. Medir también tamaño físico DB y margen compartido; límite preventivo inicial 350 MiB. Si falta medición o cupo, denegar carga sin guardar parcialmente. Los límites no prometen disponibilidad física ilimitada.

Índices: FKs de revisiones/asociaciones; asset_id para referencias; UNIQUE(project_id, revision_number); orden de galería display_order/id; revision_id/association_id para media; operation_id único. No índices sobre BYTEA ni payload completo. Check de tamaños y FK complementan validación de aplicación.

## Transiciones

1. Crear/guardar: comparar lock_version, insertar revisión y referencias, mover draft_revision_id, incrementar versión; publicación intacta.
2. Adjuntar/reemplazar: validar/normalizar fuera de transacción; con guard vigente y versión esperada, insertar asset inmutable y nueva revisión con una referencia nueva/local. Guardar esta nueva revisión de borrador y su recibo juntos. Compartir asset existente requiere selección explícita del admin y nueva referencia contextual; no copiar alt/derechos como aprobación automática.
3. Revisar/publicar: confirmar revisión/digest/lock_version concretos con autoría y derechos; revalidar campos, bytes y referencias. Materializar solo esa revisión, mover published_revision_id y registrar aprobación/recibo. Nueva publicación recibe posición al final; corrección conserva posición. No modificar otros proyectos ni sus imágenes.
4. Ordenar: confirmar lista exacta de IDs públicos actuales y catalog_version, sin duplicados/omisiones. Actualizar solo display_order y versión catálogo. No tocar revisiones/borradores ni versiones de contenido.
5. Retirar: confirmar proyecto/versión publicada y lock_version; eliminar instantánea/asociaciones públicas, poner published_revision_id null, conservar borrador y todas las revisiones/bytes referenciados. Republicar requiere nueva revisión/confirmación explícita y vuelve al final.
6. Eliminar: confirmación separada que identifica proyecto y versión; borrar publicación, proyecto, revisiones y referencias de ese proyecto en una transacción. Mantener recibo/auditoría mínima sin contenido. Limpiar únicamente assets sin referencia desde ninguna revisión de ningún proyecto, contando borradores y publicaciones. Cancelar no modifica datos editoriales.

Retirada y borrado invalidan nuevas consultas a ficha y rutas de imagen específicas del proyecto/revisión, aunque otro proyecto conserve el mismo asset. Una petición pública puede seguir sirviendo ese archivo por la URL válida del otro proyecto. No se intenta borrar copias descargadas anteriormente por terceros.
