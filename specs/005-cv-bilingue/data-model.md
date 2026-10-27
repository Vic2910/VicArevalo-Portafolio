# Data model: 005-cv-bilingue

Diseño lógico sin migraciones ejecutadas. Fuentes públicas 001/003, aprobación 002 y configuración curricular 005. Ningún acceso a mensajes 004, imágenes binarias 003, secretos o borradores ajenos a la edición autorizada de traducciones.

## Extensiones explícitas a fuentes anteriores

1. Académicos 001/002: añadir record_kind education/academic a payload/revisión y public_academic_experiences. Victor confirma clasificación al revisar; registros anteriores se tratan conservadoramente como academic, sin inferir institución, grado o fechas. Educación aprobada requiere actividad/programa y descripción aprobados según 002; institución/fechas opcionales se omiten si pendientes. Una fila education no se cuenta además como actividad para satisfacer dos mínimos.
2. Proyectos 003: añadir publication_epoch UUID por ciclo de publicación, guardado en private.projects y public_projects. Primera publicación/republicación genera epoch nuevo; correcciones mientras siga publicado lo conservan. Retirada quita publicación, eliminación borra proyecto. Selección curricular se liga a id+epoch para impedir reaparición automática al republicar un retirado sin nueva inclusión explícita.
3. Añadir cv_projection_hash a las cuatro publicaciones de fuente, calculado por helper/trigger puro SECURITY INVOKER sobre proyección curricular canónica y actualizado atómicamente al publicar; políticas de traducción comparan este hash vigente. No aceptar un hash del cliente como autoridad.
4. No alterar orden ni payload de la galería por operaciones de CV; no cambiar reglas de publicación 002/003. Estas extensiones se consolidarán y probarán en migraciones futuras, sin reescribir documentos anteriores como si ya existiera código.

## Entidades de selección

| Tabla propuesta | Campos | Reglas |
|---|---|---|
| public.cv_project_selection | singleton PK, selection_version entero, confirmed_at | Una configuración compartida es/en, sin lista independiente por idioma. Sin selección inicial implícita. |
| public.cv_project_selection_items | project_id, selected_epoch, position, selection_version | ID/epoch vigente seleccionado por Victor; posición única. Lectura pública/RLS solo cuando publicación id+epoch está vigente. Fuera de esa condición no expone referencias retiradas. |

Confirmar selección compara expected_selection_version y conjunto/versiones de publicaciones mostradas; cero duplicados o IDs no publicados. Guardar selección actualiza filas/version/recibo/auditoría en una transacción. Lista vacía es válida; la disponibilidad se recalcula según mínimos. Cambio de galería no cambia selection_version ni posiciones CV. Retirada/eliminación excluye dinámicamente por join de publicaciones; no completar lista con otros proyectos. FK de project_id a private.projects con borrado de referencias al eliminar; RLS pública resuelve elegibilidad mediante public_projects, sin otorgar acceso al padre privado. Eliminar limpia referencias sin conservar contenido en selección. Republicar exige nueva selección por epoch, decisión conservadora de este diseño.

## Variantes lingüísticas

| Entidad / tabla | Campos | Reglas |
|---|---|---|
| private.cv_translation_revisions | id UUID PK, source_kind profile/skill/education/academic/project, source_id, language=en, source_projection_hash, texts JSON, invariant_fields array, lock_version, created_by, created_at | Revisión inmutable, textos seguros aunque incompletos en borrador; solo campos textuales permitidos. No puede sustituir IDs, fechas, contactos, URLs o lista de hechos. |
| private.cv_translation_approvals | id PK, translation_revision_id, source_projection_hash, actor_id, confirmed_at | Confirmación humana sobre revisión/digest actuales; no aprobación de IA ni herencia automática de otra fuente. |
| public.cv_approved_translations | source_kind/source_id/language PK, source_projection_hash, texts, invariant_fields, approval_version | Solo proyección aprobada; RLS exige fuente pública vigente y hash curricular coincidente. No expone traducciones antiguas o de fuente retirada. Evidencia/identidad del revisor permanece privada. |
| private.cv_operations | operation_id PK, actor_id, action, request_digest, result_version, completed_at | Idempotencia/resultado incierto de selección y aprobación, sin secretos ni textos en recibo. |

Español usa los textos publicados aprobados de fuente; no duplicar una versión española separada que pueda quedar obsoleta. Catálogos estáticos de encabezados/fechas/idioma es/en son versionados en código y revisados en QA. Si se requiere cambiar hechos/redacción española, usar la edición/publicación 002/003, no una traducción que sustituya fuente.

Textos traducibles: perfil (carrera, resumen, etiquetas de contacto), habilidad (nombre/descripción cuando requieren traducción), educación/actividad (título/descripción), proyecto (título/descripción). Nombres propios/técnicos pueden conservarse como invariant_fields revisados explícitamente; no asumirlo automáticamente por mayúsculas o heurística. Descripciones vacías opcionales se omiten en ambos idiomas. Traducción no puede añadir ni quitar hechos; el equivalente semántico lo acredita revisión de Victor, además de controles estructurales.

Proyección curricular canónica incluye campos visibles en CV, identidad/contactos autorizados, tipo académico, fechas, tecnologías, enlaces y existencia de fuentes seleccionadas. Excluye fotos/alt de galería, display_order de galería, timestamps técnicos y borradores. SHA-256 de representación canónica versionada liga aprobación a hechos/textos: cambiar contenido curricular invalida traducción; cambiar solo imagen u orden de galería no. source_id sigue estable; source_projection_hash no lo aporta el formulario como autoridad.

Límites de traducción: equivalentes a campos de fuente, permitiendo hasta el doble de longitud textual para expansión lingüística (títulos 400, resumen 4000, descripción académica 8000 y proyecto 20000); no truncar. Rechazar estructuras desconocidas, marcadores, atributos/markup activos o HTML como instrucciones. Texto se escapa siempre al renderizar.

## Snapshot y documentos no persistidos

- CvFactsSnapshot: perfil, educación[], habilidades[], actividades[], proyectos seleccionados vigentes en orden CV, selección/version y proyecciones/hash de cada fuente; todo en un snapshot SQL nuevo.
- CvLanguageAvailability: es/en, available bool y reason enum de datos mínimos/textos vigentes/error; no detalles de borradores al público.
- CvDocumentModel: facts_version, document_version, language, encabezados/localizaciones, bloques ordenados y texto esperado; inmutable y sin referencias a cliente DB.
- GeneratedCv: buffer PDF completo, language, facts_version, document_version, generated_at, filename. Solo memoria de petición; no tabla ni archivo público histórico.

facts_version=hash del manifiesto común aprobado (hechos/IDs/selección/orden), independiente del idioma. document_version añade idioma, revisiones de traducción utilizadas y versión de layout/fuente. Ambos idiomas del mismo facts_version mantienen mismos elementos/datos/orden. Descargas iniciadas en instantes diferentes pueden tener facts_version diferente si hubo publicación; no prometer igualdad entre versiones distintas.

## Disponibilidad y transiciones

Mínimo por idioma: nombre publicado, correo público autorizado, perfil breve, >=1 educación publicada clasificada, >=1 habilidad verificada y >=1 proyecto seleccionado vigente o actividad académica pertinente publicada. Incluir todas las educaciones/habilidades/actividades académicas publicadas y solo proyectos seleccionados; omitir secciones vacías opcionales. No empleos ni imágenes.

Español ready cuando fuente española/minimos están aprobados y runtime puede generar. Inglés ready solo si todos los textos necesarios de esos mismos hechos tienen aprobación/hash vigente; no omitir una habilidad/proyecto incluido para evitar traducción faltante. Traducción de proyecto no seleccionado o fuente retirada no bloquea. Un idioma incompleto no bloquea otro completo.

Fuente cambiada→recalcular hash/disponibilidad en siguiente snapshot. Borrador guardado→no cambia fuente ni CV. Selección confirmada→siguiente snapshot usa lista nueva. Retirada/eliminación→siguiente snapshot excluye elemento y verifica mínimo/traducciones. Documento iniciado antes puede completar versión anterior coherente; sin actualización retroactiva de PDFs descargados.

## Índices y permisos

PK/FKs e índices source_kind/source_id/hash para traducción; posición única y project_id/epoch para selección; operation_id único. RLS en proyecciones expuestas y privadas, sin vistas que eludan RLS. Rol backend_cv_read solo SELECT de publicaciones/selección/traducciones vigentes, sin borradores, mensajes, archivos, sesiones o escritura. Administración usa rol dedicado/guard 002 con permisos mínimos para tablas 005 y fuente pública de referencia. Sin service_role ni funciones SECURITY DEFINER.
