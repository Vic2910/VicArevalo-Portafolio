# Research: 003-gestion-proyectos

Fecha: 2026-10-27. Contexto: spec 003, constitución 1.0.0 y diseños 001/002. Investigación delegada independiente sobre Storage, URLs firmadas, BYTEA y cuotas; decisiones consolidadas aquí.

## 1. Persistencia de imágenes y retirada

- **Decision**: Imágenes normalizadas BYTEA en tablas privadas de Supabase PostgreSQL; roles mínimos sin BYPASSRLS, ruta Flask que verifica asociación publicada por petición y no-store. Sin producto Storage en este alcance.
- **Rationale**: Ni spec ni constitución obligan a usar Storage. Atomicidad local evita archivos públicos huérfanos, compensación entre servicios y URLs firmadas todavía válidas tras retirada. Es adecuado para imágenes acotadas y un portafolio pequeño, a costa de usar cuota DB y transferencia.
- **Alternatives considered**: Bucket público (privacidad/retirada insuficientes); bucket privado + URLs firmadas (viven hasta expirar); Storage privado + proxy/principal técnico (posible, pero añade credenciales, políticas y compensación no transaccional); filesystem (no cumple fuente Supabase única para persistencia).
- **Sources**: [BYTEA](https://www.postgresql.org/docs/current/datatype-binary.html), [TOAST](https://www.postgresql.org/docs/current/storage-toast.html), [servir Storage](https://supabase.com/docs/guides/storage/serving/downloads), [Storage schema](https://supabase.com/docs/guides/storage/schema/design).

## 2. Validación y normalización

- **Decision**: Input JPEG/PNG/WebP <=5 MiB inclusive; nombre seguro, MIME/extensión/formato decodificado coherentes; verificar archivo y decodificar por completo con Pillow. Rechazar corruptos, ejecutables disfrazados, formatos ajenos, animados/multiframe y bombas de descompresión. Límites adicionales explícitos: 12 MP/lado6000. Normalizar orientación y generar WebP principal <=1600 px/2 MiB y miniatura <=480 px/256 KiB, sin EXIF ni metadatos; no conservar original.
- **Rationale**: Extensión o MIME solos no demuestran imagen segura. Recodificar elimina metadatos/payloads del original y genera contenido raster servido con tipo fijo y nosniff. Procesar antes de transacción, con recursos acotados, sin alterar archivo válido anterior al fallar.
- **Alternatives considered**: Confiar en secure_filename/MIME; SVG/HTML o archivo original servido; transformaciones SaaS o dependientes de pago; procesamiento bajo locks.
- **Sources**: [Pillow Image](https://pillow.readthedocs.io/en/stable/reference/Image.html), [Flask uploads](https://flask.palletsprojects.com/en/stable/patterns/fileuploads/), [Pillow licencia](https://pillow.readthedocs.io/en/stable/about.html).

## 3. Presupuestos gratuitos

- **Decision**: Máximo 10 imágenes y 20 MiB de derivados únicos por revisión; agregado global 64 MiB de bytes, incluidas revisiones retenidas. Bloquear nuevas cargas ante umbral físico DB 350 MiB o antes si cuota vigente exige más margen; transacción serializa presupuesto para evitar carreras. Informar límites antes de adjuntar. Una sola imagen por petición multipart, hasta 5 MiB; sobrecarga de formulario separada.
- **Rationale**: La cuota gratuita DB es compartida con todas las features y payload no equivale a tamaño físico (TOAST, índices, filas muertas y mantenimiento). Medir cuota real y transferencia; detener nuevas cargas antes de agotarla, sin auto-upgrade. No prometer que 64 MiB sea capacidad disponible garantizada.
- **Alternatives considered**: Aprovechar todo el espacio gratis sin margen; medir solo archivos visibles; eliminar revisiones o imágenes referenciadas para liberar espacio silenciosamente.
- **Sources**: [Supabase pricing](https://supabase.com/pricing), [database size](https://supabase.com/docs/guides/platform/database-size). Condiciones verificadas para planificación, revalidar antes de desplegar.

## 4. Revisiones, referencias y eliminación

- **Decision**: Proyecto con punteros borrador/publicado y lock_version; revisiones inmutables, referencias de imagen por revisión con alt/orden/autorización propios. Bytes inmutables y compartibles solo por selección explícita del administrador. Reemplazo crea nueva referencia local; publicación mueve solo ese proyecto. Retirada conserva borrador y versión retirada; eliminación confirmada borra contenido/revisiones de ese proyecto, manteniendo archivos usados por otros.
- **Rationale**: Alt y autorización son contextuales, no atributos globales que deban propagarse al compartir un archivo. No conceder DELETE a revisiones de perfil de 002 para resolver eliminación de proyectos; módulo tiene tablas específicas. Cancelación no altera datos editoriales.
- **Alternatives considered**: Sobrescribir archivo compartido; borrado en cascada del asset global; borrador/publicación en una fila mutable; exponer historial restaurable fuera de alcance.
- **Source**: [PostgreSQL transacciones](https://www.postgresql.org/docs/current/tutorial-transactions.html).

## 5. Orden y consumidores

- **Decision**: Catálogo con versión y posiciones públicas independientes. Ordenar requiere confirmar lista completa de proyectos actualmente publicados; cambio solo de posiciones, sin leer/publicar borradores. Nueva publicación se añade al final; corrección conserva posición; retirada elimina su posición, republicación vuelve al final. Conflictos de miembros/versiones producen 409.
- **Rationale**: Evita que cambiar orden publique títulos/imágenes pendientes. Galería/ficha/futuro CV leen misma instantánea; sin GitHub ni IA en la petición. Galería vacía tiene estado honesto, diferente de secciones vacías del inicio de 001.
- **Alternatives considered**: Posición dentro del payload editorial; ordenar al guardar borrador; orden por fecha que no respeta intención aprobada.

## 6. Seguridad, UX y verificación

- **Decision**: Reutilizar guard y sesiones revocables 002, CSRF, audit/recibos y controles de versión. URLs HTTP/HTTPS sin credenciales ni esquemas ejecutables; no descargar URLs introducidas (sin SSRF). Jinja escapa texto; links ausentes omitidos. Orden con campos numéricos y confirmación, sin drag-and-drop obligatorio. Imagen fallida conserva alt y texto restante; sin carrusel necesario.
- **Rationale**: Cumple teclado/lector y evita falsa confirmación o acciones vacías. La validación automática no demuestra veracidad ni conformidad WCAG: Victor confirma autoría y derechos sobre versión concreta; pruebas reales verifican RLS.
- **Alternatives considered**: Autoimportar repositorios; publicar al subir; validar enlaces mediante peticiones del servidor; enlaces placeholder; orden solo por gesto.
- **Sources**: [WCAG 2.1](https://www.w3.org/TR/WCAG21/), [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).

Pillow usa licencia libre HPND/MIT-CMU; conservar avisos y revisar licencias transitivas/codecs al bloquear versión estable compatible con Python 3.12. Otras dependencias siguen 001/002. Se revisó [changelog Supabase](https://supabase.com/changelog) HTML: no se identificó cambio que obligue a alterar esta arquitectura; el lector web no soportó el índice .md en revisión previa. No usar PostgreSQL de desarrollo: validar contra versión soportada del proyecto de prueba.

No quedan incógnitas técnicas necesarias abiertas. Los presupuestos son propuestas operativas a validar con los recursos gratuitos antes de implementar; contenido real y aprobación de autoría no se inventan ni se solicitan para planificar.
