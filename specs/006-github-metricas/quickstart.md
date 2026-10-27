# Quickstart de validación: 006-github-metricas

Guía para implementación futura. Hoy solo existen documentos:no aplicación, lock, migraciones, worker ni pruebas. No se sincronizan recursos reales de Vic 2910 durante planificación o tests predeterminados.

## Prerrequisitos y ejecución prevista

Python 3.12, stack 002 y HTTPX bloqueados, proyecto Supabase Free aislado, cuentas/roles sintéticos, esquema 006 y fuentes 003/004 de prueba. Guard 002 vigente para dashboard/start/resume. Worker mismo monolito e inyección de HTTPX MockTransport con fixtures para GitHub, sin token/red real. RET-001004 permanece bloqueado aunque se ensayen conteos con mensajes sintéticos.

Entorno protegido:configuración 002 más METRICS_DATABASE_URL, GITHUB_SYNC_DATABASE_URL, origen permitido y contexto/API version. GITHUB_READ_TOKEN opcional solo para operación real posterior, con alcance público mínimo verificado; vacío en pruebas. Nunca valores reales en .env.example, Git, capturas o logs; .env ignorado. Preparación de migraciones/roles por operador solo en proyecto aislado, identificador verificado antes de limpiar.

Desde raíz, PowerShell, una vez implementado:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m flask --app app:create_app run --cert adhoc
.\.venv\Scripts\python.exe -m pytest tests/unit/metrics tests/contract/metrics -q
.\.venv\Scripts\python.exe -m pytest tests/integration/metrics -m security -q
```

Para worker en terminal de pruebas separada, si no se inicia el worker embebido del proceso:

```powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app github-worker
```

Este comando propio propuesto espera solicitudes autorizadas persistidas, no sincroniza por sí solo ni crea calendario. Fixtures deben sustituir cliente antes de usarlo en prueba; producción no permite transport de fixtures como si fuera información real. HTTPS/origen coincidentes para Secure/CSRF; certificado adhoc solo desarrollo. Variables TEST_* y cuentas aisladas por entorno protegido. Sin DB real no aceptar RLS; skips/mocks no son evidencia de permisos.

## Fixtures y oráculos

Cuenta objetivo ID 100 y ajena ID 200, repos propio source R 1 y fork R 2 con mismo SHA atribuible en ambos, otro repo ajeno/privado para rechazo. Commits own/other/author=null, integrador objetivo pero autor ajeno, nombres/emails coincidentes sin cuenta y fecha futura. Múltiples páginas repetidas, Link correcto/cíclico/inseguro,304 con/sin caché, repository rename por mismoID, perfilID diferente, repo vacío,404/409 genérico, force-push y cambio default branch/head. Datos de proyectos published con borrador de corrección, draft nunca publicado, retired y eliminado; mensajes pending/reviewed/vencido/eliminado.

Oráculo de count explícito por parejas repo/SHA y autoría elegible; no calcular expected con misma función del código. Mismo SHA own en R 1 y R 2 suma 2, repetición en R 1 suma 0 adicional. Otro autor/unknown/committer objetivo no suma. Reloj inyectable para 60 min/Retry-After/reset/lease, sin sleeps reales.

## Matriz automatizada

| Caso | Resultado | Cobertura |
|---|---|---|
| Catálogo owner multipágina incluye forks | Recorrer todo, verificar public/ownerID, no privados/ajenos | FR-001, FR-011, SC-002 |
| Commit multipágina por cabeza SHA fija | Historia completa, fechas de autoría locales, sin detener por orden no monótono | FR-001, FR-005, SC-004 |
| Cuenta top-level author vs name/email/committer/firma | Solo accountID propio cuenta; unknown/other cero | FR-003, SC-002 |
| Página repetida/SHA en ramas y forks/repos distintos | Una pareja repo/SHA; SHA entre repos cuenta de nuevo con explicación | FR-003, FR-005, SC-001, SC-002 |
| Repetir run sin cambios 200/304 | Count idéntico, sin duplicados; checked_at avanza solo al completar | FR-006, FR-012, SC-001, SC-004 |
|304 primera página pero segunda pendiente/cache miss | No declarar completo; recuperar representación o parcial | FR-008, FR-012, SC-003 |
| Force-push/default branch nuevo | Nuevo resultado reconstruye miembros, no acumula commits inaccesibles antiguos | FR-012, SC-004 |
| Cambio catálogo/head durante recorrido | Parcial/incompatible etiquetado, sin mezclar ni promover | FR-005, FR-008, FR-012, SC-003 |
| Fecha futura y autoría inválida/estructura inválida | Futura fuera del período explicada; dato esencial inválido parcial/error, no pérdida silenciosa | FR-003, FR-005, SC-004 |
| Empty confirmado vs 404/409 genérico/perfilID distinto | Cero solo comprobado; errores/identidad no se convierten en 0 | FR-008, SC-003 |
| Dashboard 20 GET sin red GitHub | Cero requests/starts, incluso polling local; usar transport que falla si se invoca | FR-002, SC-005 |
| Conteos proyectos | Published con corrección suma una vez; retired fuera de published/draft; deleted fuera | FR-004, SC-004 |
| Conteos mensajes | Solo vivos/no eliminados, pending correcto; sin contenido o remitentes leídos | FR-004, SC-004, SC-006 |
| Fallo de una métrica/esquema contacto ausente | Solo esa tarjeta indisponible, otras válidas; no 0 ficticio ni habilitar 004 | FR-004, FR-008, SC-003 |
| Sin sincronización satisfactoria/primer parcial | Ausencia de total completo, parcial con alcance/fecha propios | FR-005, FR-008, SC-003 |
|403/429 Retry-After/reset/backoff | Persistir espera más conservadora y cortar HTTP; no reintentar desde GET | FR-006, SC-003, SC-005 |
| Intentos antes/durante/al cumplir 60 min | Rechazo antes/activo; permitir al vencer si proveedor/recursos/guard permiten | FR-007, SC-005 |
| Dos POST/worker doble/lease vencido | Una reserva activa, fence rechaza worker viejo y respuesta tardía; sin promoción duplicada | FR-007, FR-012, SC-005 |
| Corte por presupuesto y continuación manual | Progreso aislado, mismo manifiesto solo si compatible, nuevo intento respeta ventana | FR-005, FR-007, FR-008, SC-003 |
| Fallo en cada persistencia y commit incierto | Último completo/fecha intactos salvo commit verificado; recibo resuelve sin doble inicio | FR-008, FR-012, SC-003 |
| Token privado/amplio, Link host ajeno/redirect inseguro | Rechazo sin leer privado ni exponer credencial; no SSRF/forward a otrohost | FR-009, FR-011, SC-006 |
| Anon/no admin/JWT cliente directo/CSRF/sesión revocada | Sin metrics privadas, requests ni mutaciones; worker deja de llamar/promover | FR-009, SC-006 |
| Repositorio sincronizado | Cero cambios de proyectos 003, CV 005 o empleo; ninguna publicación automática | FR-011, SC-002 |
| Alcance/antigüedad/parcial/espera por teclado/lector | Comprensibles en éxito/error, sin depender de color | FR-010, SC-007, SC-008 |

Integración real de grants/RLS:roles anon/authenticated, admin JWT en Data API, backend_metrics_read y backend_github_sync con/sin contexto/lease/permiso. Consultas con IDs conocidos y conteos privados denegadas a no autorizados; rol métricas no lee textos 004 y sync no escribe proyectos/mensajes/CV. Verificar DB tras intentos y que credenciales no aparezcan en superficies. Ningún token verdadero en fixtures.

## Revisión manual y accesibilidad

1. Abrir dashboard con datos locales y GitHub desconectado:ver métricas válidas, sin cero falso. Identificar mensajes pendientes, última fecha válida y parcial/completo sin ayuda en<1 min (SC-008).
2. Iniciar actualización controlada y consultar estado local; distinguir 202 queued, running, parcial, espera y final completo. Comprobar que recargar no hace requestsGitHub y que botón/estado de espera no aparenta acción disponible.
3. Leer explicación:período/corte, repos/forks, ramas/cabezas, autoría por cuenta, dedupe repo/SHA y repetición entre repos, exclusiones/antigüedad; no historial global ni experiencia laboral.
4. Teclado/lector, foco, encabezados/regiones, nombres de controles, status dinámico opcional, errores/reintento y fechas con zona. Texto 200 %,320 px CSS, espaciado/orientación, contraste, movimiento reducido y uso sin JS.
5. Auditoría gratuita como axe y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables y estados. Puntuación automática no prueba conformidad. Validar mensajes/vencimientos sin afirmar que resuelve retención física 004.

## Evidencia y aceptación

Registrar commit, versiones/API header, licencias/lock, entorno, roles/RLS, fixtures/oráculos, resultados Pytest, trazasHTTP sanitizadas con cantidad de requests, casos de paginación/304/cuota/fencing y matrizWCAG. SC-001–008 deben quedar demostrados sin defectos aplicables. No se necesita token real ni sincronizar Vic 2910 para acreditar algoritmo con respuestas controladas; una comprobación operativa real posterior requiere configuración protegida y sigue cuotas. Esta planificación no ejecutó esas pruebas ni modificó datos del usuario.
