# Quickstart de validación: 003-gestion-proyectos

Guía para la futura implementación. Actualmente solo existen documentos: aplicación, lock, migraciones y suites aquí descritos aún no se han creado. No son resultados de pruebas ya ejecutadas.

## Preparación

Python 3.12, dependencias bloqueadas con Pillow y codecs JPEG/PNG/WebP, y configuración de 002 para autenticación/edición. Proyecto Supabase Free de prueba, esquema y grants/RLS de contratos, cuenta admin aprobada y no administrador, sin datos productivos. Añadir PROJECT_MEDIA_DATABASE_URL para rol backend_project_media SELECT mínimo, TLS verificado, sin BYPASSRLS/propiedad/privilegios editoriales. No se requieren bucket ni credenciales Storage/service_role.

Operador aplica migraciones/roles solo en entorno aislado; usar CLI --help y flujo de migraciones indicado por habilidad Supabase durante implementación. Variables de 002, ADMIN_ALLOWED_ORIGIN y URL media por entorno protegido; .env.example vacío y .env excluido de Git. No registrar valores reales en guía, historial compartido ni informes.

Desde raíz del repositorio, PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m flask --app app:create_app run --cert adhoc
.\.venv\Scripts\python.exe -m pytest tests/unit/projects tests/contract/projects -q
.\.venv\Scripts\python.exe -m pytest tests/integration/projects -m security -q
```

Usar HTTPS local confiable y origen configurado igual para comprobar Secure/CSRF; adhoc es solo desarrollo y requiere confiar localmente en certificado. No desactivar seguridad para acreditar aceptación. Integración recibe TEST_* equivalentes por entorno protegido; fixtures/limpieza verifican identificador del proyecto aislado antes de mutar. Si faltan recursos, omitir explícitamente y reportar aceptación incompleta; mocks no acreditan RLS ni atomicidad real.

## Fixtures previstas

Tres proyectos sintéticos: A publicado, B publicado compartiendo un asset con A y C solo borrador; además cambios pendientes en A y bytes exclusivos de C. Textos/ficheros claramente de prueba, nunca visibles como proyectos reales de Victor. Crear variantes JPEG/PNG/WebP válidas, una imagen válida de exactamente 5 MiB, otra >5 MiB, MIME/extensión discrepantes, nombres peligrosos, ejecutable renombrado, archivo corrupto, animado y bomba de descompresión. La fixture exacta debe ser un archivo de imagen válido, no solo un buffer arbitrario de ese tamaño.

## Matriz automatizada

| Escenario | Resultado comprobable | Cobertura |
|---|---|---|
| Guardar y reabrir borrador incompleto | Persisten datos seguros y asociaciones, sin cambios públicos | FR-001/003, SC-008 |
| Publicar con campos/tecnología/imagen/alt/derechos faltantes | 422 junto a campos, sin publicación parcial; datos ficticios/no revisados no aprobados automáticamente | FR-002/011, SC-001 |
| Repositorio existente sin revisión humana | No se crea ni publica automáticamente; autoría, veracidad y derechos requieren confirmación de la revisión concreta | FR-011, SC-001 |
| Revisión exacta y corrección | Solo versión confirmada cambia galería/ficha/fuente CV; resto de borradores intactos | FR-003/012, SC-004 |
| Vacío público / lectura fallida | 200 vacío honesto o 503, sin tarjetas ficticias ni confundir fallo con vacío | FR-006/013 |
| Proyecto C privado y assets privados, IDs conocidos | Data API, ficha, GET/HEAD/Range y previews sin permiso no revelan datos | FR-006/007, SC-002 |
| Login sin permiso, sesión caducada/retirada, JWT admin directo | Cero modificaciones/acceso privado, sin bypass por API o rol media | FR-007, SC-002 |
| JPEG/PNG/WebP, 5 MiB exactos, >5 MiB | Válidos exactos pasan tamaño; exceso 413; formatos/MIME/contenido/nombres no admitidos rechazados | FR-008, SC-003 |
| Pixel bomb, corrupto, animado, codec ausente | Rechazo seguro, sin bytes persistidos ni sustitución de archivo válido | FR-008/013, SC-003/008 |
| Normalización | Orientación correcta, variantes y hash válidos, sin EXIF/metadatos originales ni original servible | FR-008/006, SC-002/003 |
| HTTP/HTTPS y enlaces ausentes/peligrosos | Opcionales omitidos; esquema inseguro rechazado, texto escapado en preview/público; ningún fetch SSRF | FR-009, SC-002 |
| A/B comparten imagen; reemplazar A en borrador | Cero imágenes públicas cambian; nueva referencia solo en A | FR-015, SC-009 |
| Publicar reemplazo de A | Solo A cambia; B conserva bytes/alt/archivo; URL de revisión vieja de A ya no entrega | FR-015, SC-009 |
| Orden confirmado con borradores pendientes | Orden persiste al recargar y no publica ningún cambio editorial | FR-004, SC-005 |
| Orden con lista incompleta/duplicada o catálogo obsoleto | 422/409 sin cambios parciales ni nueva publicación | FR-004/014, SC-005 |
| Retirar A y republicar explícitamente | A no aparece en galería/ficha/fuente CV ni ruta de imagen; conserva editor privado; B sigue sirviendo asset compartido | FR-005/012, SC-004 |
| Cancelar retiro/borrado y confirmar borrado | Cancelación cero cambios editoriales; confirmar quita proyecto/admin/publicación y solo assets sin referencias | FR-005/012, SC-005 |
| Referencia desde otro borrador/revisión privada | Eliminación de A no borra assets todavía usados allí | FR-012/015, SC-005/009 |
| Dos guardados o publicación/retirada/orden concurrentes | Versiones detectan conflicto, sin sobrescritura ni pérdida de referencias | FR-014, SC-005 |
| Carga concurrente cerca del cupo y medición DB fallida | Sin exceso por carrera; rechazo sin cambios/upgrade ni limpieza destructiva | FR-001/013, SC-008 |
| Inyectar fallo tras cada paso SQL | Rollback de asset/revisión/referencia/punteros/orden/recibo/auditoría; estado confirmado íntegro | FR-013, SC-008 |
| Doble envío/desconexión al commit | Recibo resuelve resultado sin duplicar carga/publicación/eliminación; no éxito falso ni retry automático | FR-013/014, SC-008 |
| CSRF/origen inválido o sesión caduca durante carga | Cero guardado parcial y cero repetición al reautenticar | FR-007/013, SC-002/008 |

RLS real: probar anon, autenticado no admin, JWT de admin en Data API, backend_editor sin contexto y backend_project_media; consultas select=* y UUID conocidos no revelan borradores/bytes privados. Rol media no puede escribir, ver sesiones ni acceder a assets sin publicación activa. Comprobar DB tras intentos de modificación, no solo HTTP. No cambiar roles/recursos de producción.

Para consumidores, usar lector controlado de public_projects y asociaciones: no crear PDF ni depender de GitHub/IA. Comparar antes/después de publicar, ordenar, retirar y eliminar. Ensayar que una nueva petición tras commit de retirada rechaza imagen antigua aunque conserve querystring/cache headers/Range; bytes ya descargados están fuera de control.

## Recorrido visual, accesibilidad y rendimiento

Trazabilidad de accesibilidad: FR-010 y SC-006 se evalúan sobre todos los flujos y estados siguientes, no solo galería o página inicial.

1. Victor crea/reabre borrador, adjunta imagen, completa contenido, revisa autoría/derechos y publica, con material preparado y sin ayuda en <=5 min; explica diferencia entre guardar y publicar (SC-007).
2. Repetir galería/ficha y flujos de carga, corrección, orden, confirmación/cancelación, retirada y eliminación solo con teclado y lector de pantalla. Campos numéricos ordenan sin arrastrar; foco visible, etiquetas y errores enlazados comprensibles.
3. Romper carga de una imagen publicada: alt/leyenda y resto de contenido siguen disponibles; ningún botón queda inutilizable. Revisar alternativas pertinentes con contenido real antes de publicar.
4. Texto al 200 %, ancho320 px CSS, espaciado ampliado, móvil/escritorio y orientación: sin pérdidas ni recortes. Medir contraste; no depender solo de color, hover o gesto. Sin JS y con movimiento reducido sigue todo el flujo.
5. Ejecutar auditoría gratuita como axe y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables, incluyendo estados vacío/error/carga/conflicto/sesión vencida. Registrar justificación de no aplicables; puntuación automática no acredita conformidad.
6. Medir memoria/tiempo de validación con máximo de archivo/píxeles, consultas sin N+1, paginación12 y bytes de derivados. Verificar límites físicos/payload y margen compartido con 001/002. Si recursos no bastan, ajustar propuesta antes de activar cargas, sin bajar controles ni activar cargos.
7. Inspeccionar headers, HTML, DB grants, logs y errores sanitizados: sin originales, secretos, bytes privados embebidos o URLs directas persistentes. Comprobar no-store también en previews y errores.

## Evidencia y aceptación

Registrar commit, versiones/lock/licencias, entorno, esquema/roles/RLS revisados, Pytest, casos de límite exacto, evidencias de referencias compartidas/rollback, medidas de recursos y matriz WCAG. Redactar secretos y contenido privado. SC-001–009 deben quedar demostrados sin defectos funcionales, de seguridad o accesibilidad aplicables. La planificación no acredita esas pruebas ni autoriza publicación de proyectos reales sin revisión de Victor.
