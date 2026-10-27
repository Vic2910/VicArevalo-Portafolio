# Research: 005-cv-bilingue

Fecha:2026-10-27. Base: spec 005, constitución 1.0.0 y diseños 001–004. Revisión independiente delegada sobre ReportLab, Unicode, fuentes y extracción; hallazgos consolidados aquí.

## 1. Fuente coherente y vigencia

- **Decision**: Lectura nueva por petición en transacción READ ONLY REPEATABLE READ sobre publicaciones, selección y traducciones aprobadas; construir DTO/manifiesto inmutable en memoria y cerrar transacción antes del render. Sin caché PDF ni reutilización de snapshot entre solicitudes.
- **Rationale**: Varias llamadas independientes pueden mezclar revisiones. Una petición posterior a commit obtiene fuente nueva; una iniciada antes puede terminar con versión anterior coherente. Hash canónico del manifiesto permite identificar versión sin mutar un contador global por cada feature.
- **Alternatives considered**: Consultas REST separadas; guardar PDF generado hasta invalidación; bloquear publicaciones durante render; mantener una transacción larga abierta mientras se dibuja.
- **Sources**: [PostgreSQL isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [Psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).

## 2. Traducciones aprobadas por hechos

- **Decision**: Español usa contenido publicado aprobado; inglés usa revisión aprobada de sus textos, ligada al digest de proyección curricular vigente del elemento. Identidad propia, nombres técnicos/propios y direcciones pueden ser invariantes explícitamente revisadas. Estructura/datos/destinos vienen de la fuente y no se sobreescriben mediante traducción.
- **Rationale**: Cambiar hechos/texto curricular invalida traducción anterior; cambiar solo imagen u orden de galería no modifica hechos del CV ni necesita traducir otra vez. No traducir automáticamente ni omitir un proyecto incluido para ocultar traducción pendiente. Elementos no incluidos no bloquean idioma.
- **Alternatives considered**: Traducir en descarga; confiar solo en idioma etiquetado; reutilizar texto inglés sin correspondencia de fuente; fallback español silencioso.

## 3. Educación y mínimo

- **Decision**: Extender registros académicos 001/002 con record_kind education/academic confirmado por Victor. No inferir educación a partir de descripción ni crear institución/fechas. Usar educación publicada y habilidades verificadas; actividades académicas publicadas pertinentes y proyectos seleccionados cubren la sección de evidencia.
- **Rationale**: Los modelos anteriores mezclan formación/actividades pero el mínimo del CV exige distinguir educación. La clasificación es un dato editorial revisado; backfill conservador academic y publicación educativa explícita, sin inventar información pendiente.
- **Alternatives considered**: Tratar carrera del perfil como educación completa; crear entidad educativa desconectada de la fuente pública; inferir tipo por palabras.

## 4. Selección curricular independiente

- **Decision**: Selección/orden por IDs de proyectos públicos, una sola configuración confirmada para es/en, con versión propia y guard 002. A descarga, resolver contra proyectos publicados del snapshot; retirados/eliminados se excluyen sin sustitutos. Corrección del mismo proyecto usa publicación actual; república del retirado requiere nueva inclusión explícita según estado confirmado.
- **Rationale**: Independencia respecto de galería y borradores. Una selección puede quedar sin proyectos; vuelve a comprobar mínimo con experiencia académica real. Cambio de selección no publica ni ordena galería.
- **Alternatives considered**: Incluir toda galería; topN por orden/fecha; listas separadas por idioma; copiar textos de proyecto al seleccionar y quedar obsoletos.

## 5. Generación y layout

- **Decision**: ReportLab OSS Platypus, un frame, Paragraph/Spacer y salto automático; A 4, márgenes 18 mm y cuerpo 11 pt como base sobria. Encabezados junto a primera línea, entradas extensas divisibles; no KeepTogether de bloques grandes. Sin tablas/imágenes/columnas, ni datos esenciales en encabezados/pies.
- **Rationale**: Conserva texto lineal y permite varias páginas sin reducir legibilidad. No reproducir logotipos/plantillas institucionales ni afirmar garantía ATS.
- **Alternatives considered**: PDF SaaS; captura HTML como imagen; diseño multicolumna; canvas con coordenadas manuales para todos los párrafos; una página forzada.
- **Sources**: [Platypus](https://docs.reportlab.com/reportlab/userguide/ch5_platypus/), [Paragraphs](https://docs.reportlab.com/reportlab/userguide/ch6_paragraphs/).

## 6. Unicode, seguridad y metadatos

- **Decision**: DejaVu Sans TTF regular/negrita locales incrustadas y cobertura de glifos validada. Escapar texto antes de Paragraph XML y solo permitir markup generado internamente; URLs se imprimen como texto, sin descargar recursos. Metadatos title/author/lang explícitos, nombre de archivo _es/_en y sin secretos/paths internos.
- **Rationale**: Helvetica estándar puede ser insuficiente para Unicode; markup arbitrario puede interpretar etiquetas no previstas. Fuentes e imágenes remotas contradicen disponibilidad y privacidad buscadas. Identificar idioma no equivale a PDF/UA o tagging automático.
- **Alternatives considered**: Fuentes del sistema, sustitución silenciosa de caracteres, HTML editorial como markup, autotagging comercial.
- **Sources**: [ReportLab fonts](https://docs.reportlab.com/reportlab/userguide/ch3_fonts/), [PDF accessibility](https://docs.reportlab.com/pdf-accessibility/), [DejaVu license](https://github.com/dejavu-fonts/dejavu-fonts/blob/master/LICENSE).

## 7. Validación y recursos

- **Decision**: Pytest+pypdf compara contenido esperado/orden y metadatos; generar fixtures mono/multipágina es/en y renderizar todas con Poppler para revisión visual. Pruebas de tildes, enlaces largos, saltos y texto máximo. Buffer final solo se entrega tras completar validación; sin PDF parcial o antiguo en error. Medir p 95<=10 s.
- **Rationale**: Extraer correctamente no demuestra layout correcto y una imagen correcta no demuestra Unicode/orden. No se genera PDF real en planificación; QA forma parte de implementación.
- **Alternatives considered**: Solo captura de una página; comprobar únicamente status 200 o firma %PDF; OCR como sustituto de texto real.
- **Source**: [pypdf extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html).

## 8. Licencias y límites

- **Decision**: ReportLab libre BSD, pypdf BSD-3-Clause, DejaVu licencia Bitstream/DejaVu y Poppler GPL como herramienta de QA. Conservar avisos y validar licencias de versiones/transitivas al bloquear; no incorporar ReportLab Plus ni servicios de pago. Supabase Free y mismos controles de permisos 002, sin mensajes 004.
- **Rationale**: Constituye una cadena local gratuita, con fuente distribuible y herramientas estándar. Contenido real pendiente bloquea idioma hasta aprobación, no se rellena con mocks en producción.
- **Sources**: [ReportLab source/license](https://docs.reportlab.com/developerfaqs/), [pypdf license](https://github.com/py-pdf/pypdf/blob/main/LICENSE), [Poppler](https://poppler.freedesktop.org/), [Supabase pricing](https://supabase.com/pricing).

[Changelog Supabase](https://supabase.com/changelog) revisado; usar clientes/TLS soportados. No se identificó cambio que altere el diseño de instantánea/RLS. El bloqueo de conservación de004 no se intenta resolver ni afecta el correo público autorizado del perfil. No quedan preguntas técnicas necesarias abiertas; no se afirma aceptación documental antes de ejecutar pruebas/revisión humana.
