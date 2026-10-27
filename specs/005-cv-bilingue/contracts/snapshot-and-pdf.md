# Contract: snapshot aprobado, idiomas y PDF

## Lectura y coherencia

Cada solicitud obtiene una conexión limpia y transacción nueva READ ONLY REPEATABLE READ; ningún snapshot iniciado por otra petición se reutiliza desde pool. Primer SELECT establece punto de versión coherente al comenzar generación. Leer perfil/contactos publicados, educación/actividades clasificadas y habilidades publicadas, selección curricular confirmada, proyectos vigentes seleccionados por id+epoch y traducciones aprobadas de esos elementos. No fotos, mensajes, tokens, revisiones privadas o métricas GitHub.

Completar lecturas en ese mismo snapshot, incluidas comprobaciones de disponibilidad/hashes. Sin N+1 ni llamadas Data API separadas que mezclen commits; cerrar transacción antes de renderizar. Publicación que confirma después de snapshot puede quedar fuera de este PDF, pero su siguiente solicitud debe verla. Nunca volver a consultar algunos campos durante render ni usar un archivo anterior si falla lectura.

Construir facts_version del manifiesto canónico común: IDs/tipos, campos/fuentes vigentes, selección/orden CV, contactos autorizados, mínimos y hashes. document_version agrega idioma, aprobaciones utilizadas, catálogo estático y versión de layout/fuentes. Hash no es secreto ni aprobación humana; permite comparar evidencia. Cada PDF corresponde a un único facts_version, aunque su contenido no muestre hashes técnicos al lector.

## Proyecciones/hashes y traducciones

Añadir cv_projection_hash a publicaciones de perfil, habilidades, académicos y proyectos mediante migración 005. Protocolo canónico versionado definido una sola vez: función/trigger puro SECURITY INVOKER sobre columnas públicas actualiza hash en toda publicación/corrección, sin consultar privados ni elevar privilegios. Excluir fotos/alt, orden de galería, timestamps técnicos; incluir todos los campos curriculares, contactos, fechas, clasificación y enlaces. Backfill calcula hash de datos ya aprobados sin inventar hechos.

La aprobación inglesa guarda hash de proyección vigente. RLS de proyección traducida exige fuente publicada y hash coincidente; borrador/aprobación histórica no cumplen. El renderer recibe hash autoritativo de snapshot y vuelve a comprobar correspondencia del DTO. Cambios a fuente curricular invalidan inglés en siguiente petición; imágenes/orden de galería no. Registro académico education/academic se aprueba en 002 y nunca se infiere del texto.

Cada elemento incluido debe tener todos sus textos ingleses necesarios aprobados o campos invariantes explícitamente revisados. Ningún texto estructural/datos numéricos cambia por traducción: nombres propios legítimos, tecnologías y direcciones se conservan; fechas se formatean con catálogo es/en sin alterar fecha real. No traducir en descarga, consultar IA ni reutilizar un texto viejo para hechos nuevos. Proyecto no seleccionado no participa de disponibilidad.

Español deriva de fuente publicada aprobada; inglés no altera conjunto/orden de entidades. Si falta traducción de un elemento incluido, bloquear inglés en vez de ocultarlo o mezclar idiomas. Otro idioma completo sigue disponible. Catálogos de encabezados y nombres de idioma revisados/versionados; encabezados PDF en idioma pedido, no etiquetas UI españolas incrustadas en inglés.

## Mínimos y selección

Nombre, correo autorizado, perfil breve, educación, >=1 habilidad y >=1 proyecto seleccionado publicado o actividad académica pertinente. Un registro de educación no se duplica como actividad para satisfacer mínimo. Incluir educaciones/habilidades/actividades publicadas en su orden aprobado; proyectos únicamente selección CV, sin sustitución automática. Sin empleo, logros, porcentajes o datos pendientes inventados.

Selección compartida es/en, versionada e independiente de display_order de galería. Confirmación compara versión propia, IDs/epochs y publicaciones mostradas dentro de transacción; misma operation_id/cuerpo no duplica y cuerpo distinto=409. Guardar no publica borrador de proyecto ni cambia galería. Snapshot siguiente resuelve solo IDs aún publicados del mismo ciclo; retirado/eliminado desaparece, republicado requiere selección nueva por epoch. Recalcular mínimo e inglés al excluir elementos.

Administración usa guard 002, CSRF/origen, SQL parametrizado, control optimista, revisión explícita y recibo/auditoría transaccionales. Aprobar traducción compara fuente/revisión/digest actuales; cambio concurrente o sesión expirada no se confirma ni reintenta al login. Si fuente cambia después del commit de aprobación, comparación de hashes evita reutilizarla para hechos distintos. Resultado incierto consulta recibo, no éxito falso.

## Roles y privacidad

- backend_cv_read: solo SELECT de proyecciones públicas 001/003/005; RLS solo permite contenido publicado, selección id+epoch vigente y traducciones/hash actuales. Sin escritura, sesiones, mensajes 004, imágenes privadas o metadatos editoriales.
- backend_cv_admin: guard 002 vigente y permisos mínimos en borradores/aprobaciones/selección/recibos 005; solo lectura de fuentes públicas. No publicar proyectos/perfil ni cambiar sus hechos desde traducción.
- anon/authenticated en Data API: solo proyecciones explícitamente públicas y vigentes; ninguna mutación ni revisión privada. Una clave o JWT de admin en cliente no concede edición directa.

Roles sin propiedad/BYPASSRLS/superusuario; sin service_role ni SECURITY DEFINER. Tablas privadas no expuestas y con RLS. Nuevas funciones de hash/políticas no elevan privilegios ni conceden acceso a otras fuentes. Secretos fuera del repo/HTML/PDF/logs; conexiones TLS verificadas, contexto de sesión local y limpio según 002. Logs de descarga solo idioma/versión pública/duración/código de error, no payload ni datos privados.

## Layout y fuentes

ReportLab OSS Platypus con un solo frame por página. A 4, márgenes 18 mm, DejaVu Sans 11 pt y negrita para jerarquía como base; contraste negro/blanco, espaciado consistente y títulos textuales. Identidad/contacto están en cuerpo de primera página, no en encabezado/pie; sin elementos repetidos esenciales. Orden:identidad/contacto, perfil, educación, habilidades, proyectos seleccionados y actividades académicas cuando existan. Secciones opcionales vacías se omiten.

Solo Paragraph/Spacer y paginación automática. Mantener título de sección con primera línea; permitir dividir entradas largas sin KeepTogether gigante. No forzar página única, recortar ni reducir fuente indefinidamente. No tablas/columnas, imágenes, barras, logos, testimonios o estilos que afirmen afiliación universitaria.

TTF regular/negrita incluidas localmente con licencia/avisos y registro de familia una vez por proceso. Validar cobertura de glifos del texto aprobado; si falta glifo, error útil, nunca sustituirlo por cuadro o quitar tildes. No descargar fuentes en runtime ni depender de instalación del equipo. Texto editorial pasa por escape XML antes de Paragraph; markup solo lo genera código. URLs aprobadas se imprimen como texto con wrapping sin añadir guiones/cambiar caracteres, no tags link/img del usuario.

Metadatos: título localizado, autor público aprobado y lang es/en. Sin JavaScript PDF, Launch, archivos embebidos, formularios o protección que impida seleccionar/copiar. No se afirma PDF/UA/autotagging ni compatibilidad ATS garantizada. Se validan lectura textual, estructura, contenido y layout; el flujo web sí debe cumplir todos los criterios WCAG 2.1 A/AA aplicables.

## Generación, comprobación y fallos

Renderizar snapshot inmutable a buffer privado en memoria; completar PDF antes de enviar headers/bytes. Validación runtime mínima: PDF reabrible, páginas presentes, idioma/metadatos, ausencia de fuentes/glifos faltantes y texto de identidad/encabezados esperado; suite completa de extracción/layout se ejecuta en QA. No usar OCR ni imagen como texto.

Presupuesto operativo 8 MiB de buffer, una generación simultánea por proceso y tiempo acotado; saturación/timeout/error=503 con reintento explícito, sin bytes parciales/caché vieja. Si se necesita aislar timeout de CPU, usar subproceso local acotado dentro del monolito y limpiar su buffer/temporales; no introducir cola con copia persistente. Medir y ajustar recursos antes de aceptar p 95<=10 s. No recortar contenido para cumplir presupuesto.

QA genera ambos idiomas con fuente/facts_version controlados, reabre con pypdf y compara todos los bloques esperados y orden. Normalizar únicamente whitespace causado por maquetación; para URL partida reconstruir saltos conocidos y comparar caracteres exactos. Nunca quitar tildes/puntuación/palabras para hacer pasar prueba. Renderizar todas las páginas con Poppler y revisar PNGs para recortes, superposición, glifos, márgenes y continuidad. Extraer texto no sustituye revisión visual; capturas tampoco prueban selección/orden.

No PDF real ni pruebas se ejecutan en esta planificación. La implementación solo se acepta con ambas variantes completas y evidencias funcionales, semánticas, visuales y web accesibles.
