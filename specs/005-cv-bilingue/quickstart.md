# Quickstart de validación: 005-cv-bilingue

Guía para la futura implementación. Aplicación, lock, migraciones, fuentes y pruebas todavía no existen; esta planificación no genera PDFs ni ejecuta validación funcional. No completar datos reales de Victor con fixtures.

## Prerrequisitos

Python 3.12, stack 002 y ReportLab OSS/pypdf bloqueados, fuentes DejaVu TTF local regular/negrita con licencia, y Poppler disponible para QA. Usar dependencias de workspace si están disponibles, o instalación verificada gratuita; Poppler no es dependencia de descarga runtime. Supabase Free aislado con publicaciones 001/003 y extensiones 005, cuenta admin aprobada y no administrador.

Entorno protegido: variables 002, CV_READ_DATABASE_URL (rol backend_cv_read), CV_ADMIN_DATABASE_URL (rol backend_cv_admin) y origen permitido. TLS verificado, sin service_role ni credenciales de propietario; .env.example vacío y .env ignorado. Operador prepara migraciones/roles/fixtures solo en proyecto aislado, verificando identificador antes de cualquier limpieza. RET-001 de 004 continúa bloqueado y ninguna prueba del CV lo habilita.

Desde raíz del repositorio en PowerShell, después de implementación y con variables ya inyectadas:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m flask --app app:create_app run --cert adhoc
.\.venv\Scripts\python.exe -m pytest tests/unit/cv tests/contract/cv -q
.\.venv\Scripts\python.exe -m pytest tests/integration/cv -m security -q
.\.venv\Scripts\python.exe -m pytest tests/integration/cv -m pdf_visual -q
```

HTTPS/certificado confiable local y origen coincidente para cookies/CSRF; adhoc solo desarrollo. Tests reciben TEST_* equivalentes/cuentas sintéticas por entorno protegido. Sin Supabase/Poppler/fuentes, marcar aceptación incompleta y explicar faltante; mocks/skips no prueban RLS o layout.

Suite pdf_visual deberá producir PDFs de fixtures en output/pdf/cv-fixture-es.pdf y cv-fixture-en.pdf, manifiestos de contenido esperado y PNGs en tmp/pdfs. No son CVs reales. Para inspección independiente:

```powershell
pdfinfo output/pdf/cv-fixture-es.pdf
pdftotext -layout output/pdf/cv-fixture-es.pdf tmp/pdfs/cv-fixture-es.txt
pdftoppm -r 150 -png output/pdf/cv-fixture-es.pdf tmp/pdfs/cv-fixture-es
pdfinfo output/pdf/cv-fixture-en.pdf
pdftotext -layout output/pdf/cv-fixture-en.pdf tmp/pdfs/cv-fixture-en.txt
pdftoppm -r 150 -png output/pdf/cv-fixture-en.pdf tmp/pdfs/cv-fixture-en
```

Crear directorios de QA durante implementación y revisar todas las páginas generadas. pypdf complementa extracción Poppler; comparar con manifiesto, no con otro PDF que podría compartir el mismo error. Tras un cambio significativo de layout/fuente, volver a generar y renderizar ambas variantes.

## Fixtures necesarias

Perfil con nombre/tildes y correo autorizado, educación explícitamente clasificada, habilidades, actividad académica y proyectos A/B/C publicados con traducciones revisadas. Selección CV B,A y galería A,B,C; C sin traducción para probar que no bloquea al no estar seleccionado. Borradores/privados con centinelas, proyecto retirado/eliminado, inglés pendiente/desactualizado, datos mínimos faltantes y caracteres especiales/URLs/textos largos para varias páginas. Aprobaciones sintéticas solo en prueba, nunca presentadas como reales.

## Matriz automatizada

| Caso | Resultado | Cobertura |
|---|---|---|
| Elegir es/en y solicitud directa desconocida | PDF del idioma pedido o 400 sin fallback | FR-001, SC-005 |
| Perfil/contacto/educación/habilidad/evidencia mínimos ausentes | Idioma bloqueado también por ruta directa, sin completar datos | FR-003, FR-011, SC-003 |
| Borradores/secretos/mensajes centinela | Cero presencia en fuente del renderer, PDF, metadatos o logs | FR-005, SC-003 |
| Inglés faltante/desactualizado de elemento incluido | Solo inglés bloqueado si español completo; nunca mezcla ni PDF viejo | FR-004, SC-005 |
| C no seleccionado y sin traducción | No aparece ni bloquea; ambos idiomas usan solo B,A | FR-004, FR-013, SC-009 |
| Cambio curricular publicado | Primera solicitud posterior usa nueva fuente/hash; aprobación inglesa anterior no vale | FR-002, FR-004, SC-004, SC-005 |
| Solo imagen u orden de galería cambia | Hechos/orden CV y vigencia de traducción conservados | FR-013, SC-009 |
| Publicar mientras se genera | PDF corresponde entero a snapshot anterior; solicitud siguiente usa nuevo, sin mezcla | FR-002, SC-001, SC-004 |
| Selección B,A confirmada y cambio de galería | Mismo orden CV en es/en; selección no altera galería y viceversa | FR-013, SC-009 |
| Selección vacía o proyecto retirado/eliminado | Excluir sin sustitución; validar mínimo con actividad académica, o bloquear si no basta | FR-005, FR-011, FR-013, SC-003, SC-009 |
| Republicación después de retirada | No reaparece por epoch viejo, requiere nueva selección explícita | FR-013, SC-009 |
| Traducción/source/selección en carrera o sesión caducada |409/401 sin aprobación obsoleta, reejecución automática o cambios parciales | FR-004, FR-013, SC-003, SC-009 |
| Sin IA/GitHub/SMTP/contacto 004 | Generación sigue con publicaciones disponibles; ningún request a esos servicios | FR-008, SC-001 |
| Texto mono/multipágina, tildes y enlaces largos | Texto completo, orden lineal, sin glifos perdidos ni recortes | FR-006, FR-012, SC-002, SC-006 |
| Estructura PDF y metadatos | Una columna, TTF incrustada, es/en identificado, sin imágenes/tablas/JS/Launch/adjuntos | FR-006, FR-009, SC-002, SC-006 |
| Convenciones sobrias y afirmaciones | Sin empleo ficticio ni afiliación Harvard/Oxford o garantía ATS | FR-003, FR-007, SC-001, SC-003 |
| Markup malicioso y URLs de fuente | Texto escapado en web/PDF, sin recursos externos ni acciones PDF no previstas | FR-005, FR-008, SC-003 |
| Fuente DB/render/glifo/timeout fallan |503 HTML accesible con reintento, sin bytes PDF/caché obsoleta/falso éxito | FR-010, SC-008 |
| Disponibilidad/descarga/errores/gestión por teclado y lector | Flujos completos y estados comprensibles | FR-009, SC-007 |

Roles reales: anon/authenticated/admin JWT en Data API no pueden modificar ni consultar traducciones privadas; backend_cv_read no escribe, no accede a mensajes/archivos/sesiones ni a traducción fuera de hash vigente; admin sin autorización/sesión actual rechazado. Probar IDs conocidos, select=*, joins y SQL con contexto ausente, verificando efectos DB, no solo HTTP.

Validación de texto: comparar todos los bloques esperados del manifiesto y su orden en ambos motores de extracción, conservando tildes/puntuación; normalizar solo espacios/saltos de layout. Resolver URLs partidas según caracteres originales sin truncarlas o añadir guiones. Comparar mismos facts_version para equivalencia de hechos es/en; una publicación entre dos descargas puede producir versiones distintas legítimas.

## Revisión manual y rendimiento

1. Abrir selector es/en, descargar cada PDF, revisar idioma visible/nombre/metadatos y seleccionar/copiar texto completo. Probar lector y orden, sin deducir PDF/UA de texto extraíble.
2. Renderizar todas las páginas de cada fixture y revisar márgenes, continuidad, encabezados con primer texto, interlineado, caracteres, URLs y saltos sin recortes/superposiciones. Sin forzar una página ni reducir cuerpo para ocultar desbordes.
3. Recorrer selector/indisponibilidad/reintento y selección/aprobación administrativa con teclado/lector, foco, etiquetas, resumen de errores y estados. Texto 200 %, ancho 320 px CSS, espaciado ampliado, contraste, sin depender de color y movimiento reducido; sin JS conserva funcionalidad.
4. Auditoría automática gratuita como axe y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables con evidencia/justificación de no aplicables. No aceptar por puntuación automática.
5. Medir al menos 100 solicitudes por idioma con contenido representativo y conexión normal: >=95 % completas en<=10 s. Registrar percentiles, tamaños, memoria, consultas y fallos por saturación; no solo tiempo de render local. Probar textos largos aparte y verificar que fallos no entreguen documento parcial.
6. Validar permisos, headers no-store/idioma/attachment, ausencia de bytes antes de finalizar generación y no reutilización después de publicar/retirar. Confirmar que PDF/HTML/logs no contienen paths, secretos o datos privados.

## Evidencia y aceptación

Registrar commit, versiones/lock/licencias/fuentes, entorno y roles/RLS, manifiesto/facts_version, Pytest, extracción íntegra/orden, PNGs revisados de todas las páginas, revisión semántica de ambos idiomas por Victor, WCAG web y medicionesSC-008. No subir datos o secretos reales a evidencia. SC-001–009 deben demostrarse sin defectos aplicables. Datos pendientes no se inventan; ambas variantes completas son necesarias para aceptación total, aunque en operación un idioma pueda estar temporalmente indisponible.
