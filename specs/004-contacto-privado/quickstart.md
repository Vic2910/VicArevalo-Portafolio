# Quickstart de validación: 004-contacto-privado

Diseño con bloqueo RET-001. No existen aplicación, lock, migraciones o suites implementadas. Los comandos siguientes son guía para implementación futura y pruebas sintéticas; no habilitan recepción real ni acreditan borrado físico/copia del proveedor.

## Prerrequisitos y ejecución futura

Python 3.12, stack 002 bloqueado y validador de correo compatible, HTTPS local y proyecto Supabase Free aislado. Operador crea roles de recepción/admin/purga mínimos y esquema/RLS mediante migraciones revisadas; no usar producción, service_role ni credenciales postgres como runtime. Datos sintéticos y reloj controlado; nunca esperar 90 días ni usar mensajes reales.

Entorno protegido: variables 002 más CONTACT_RECEIVE_DATABASE_URL, CONTACT_ADMIN_DATABASE_URL, CONTACT_RETENTION_DATABASE_URL, CONTACT_TOKEN_SIGNING_KEY, CONTACT_PAYLOAD_HMAC_KEY y origen permitido exacto. IDs/secretos no se escriben aquí ni en .env.example; .env ignorado. Evidencia RET-001 permanece bloqueada: no documentar un flag que la salte. Modo de pruebas solo permite fixtures en proyecto identificado como aislado.

Desde raíz del repositorio, PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m flask --app app:create_app run --cert adhoc
.\.venv\Scripts\python.exe -m pytest tests/unit/contact tests/contract/contact -q
.\.venv\Scripts\python.exe -m pytest tests/integration/contact -m security -q
```

Certificado local confiable/origen coincidente para Secure/CSRF; adhoc solo desarrollo. Variables TEST_* correspondientes y cuentas sintéticas por entorno protegido; setup/teardown verifican proyecto de prueba antes de modificar. Falta de recursos=skip explícito y aceptación incompleta, nunca PASS. Integración real verifica grants/RLS/commits, mocks cubren fallos.

## Estado público obligatorio actual

Abrir /contacto sin evidencia de garantía estricta:503 y explicación sin campos de contacto. Enviar POST directo mientras bloqueado:rechazo antes de parsear/guardar; cero mensajes, recibos con payload o datos personales en logs. Navegación 001 comunica contacto no disponible. Este escenario debe permanecer aunque funcionen TTL y cron de prueba.

## Matriz automatizada

| Caso | Resultado | Trazabilidad |
|---|---|---|
| Aviso/tres campos cuando mecanismo acreditado se simula en test aislado | Finalidad/90 días previos al envío; sin adjuntos ni campos personales extra | FR-001, SC-003 |
| Trim/Unicode y límites exactos 1/100,254,10/5000 | Válidos exactos aceptados; vacíos/invalid email/un carácter fuera rechazados sin persistencia; interior/saltos conservados | FR-002, SC-003 |
| Recepción nueva | Un mensaje pending, received_at/expires_at correctos y confirmación solo tras commit | FR-003, SC-001 |
| Doble POST concurrente y pérdida de respuesta | Mismo token produce un solo mensaje y recibo; reintento no consume otra recepción | FR-003/004, SC-001 |
| Mismo token con cuerpo distinto |409 sin duplicar ni sobrescribir | FR-003, SC-001 |
| Reintento después de eliminación manual | Tombstone técnica devuelve anterior no disponible, sin recrear ni revelar contenido | FR-003, SC-001 |
| Token vencido tras limpiar recibo y después de 90 días | Nunca inserta, aunque no exista tombstone | FR-003, SC-001 |
| Fallo/commit incierto/cuota | No falso éxito ni afirmación de ausencia; reintento con token original | FR-004, SC-001 |
| Anon/no admin/admin JWT directo | Ninguna lista/detalle/conteo o mutación por Data API; roles previos sin grants nuevos | FR-005, SC-002 |
| Abrir detalle y marcar explícitamente | GET conserva pending y fechas; POST revisado/pendiente persiste, sin ampliar vencimiento | FR-006, SC-006 |
| Cancelar/confirmar eliminación | Cancelar cero cambios; confirmar quita mensaje/conteos y digest personal, deja solo constancia mínima | FR-007, SC-006 |
| Política/evidencia/mecanismo ausentes | Formulario sin campos y POST bloqueado, incluso cron de prueba healthy sin garantía | FR-008, SC-005 |
| t=recepción+90 días−1 microsegundo / exactamente 90 días | Antes permanece si no borrado manual; al vencer no hay acceso/conteo. Purga y copias se evalúan por separado, sin declarar SC-004 por TTL | FR-009, SC-004 pendiente de evidencia estricta |
| Pendiente/revisado y cambios repetidos | Misma fecha de vencimiento y mismo tratamiento de purga | FR-009, SC-004 |
| Frecuencia, CSRF, origen y cuota en carrera |429 con espera o rechazo seguro, sin mensaje extra; límites globales pese a nuevas sesiones | FR-010, SC-003/005 |
| Texto malicioso y redacción de superficies | Jinja escapa, sin ejecutar/autoenviar a terceros/IA ni texto en logs | FR-011, SC-002 |
| Sin SMTP/IA/notificaciones externas | Recepción de prueba y bandeja funcionan; alerta operativa solo privada | FR-012, SC-001/006 |
| Teclado/lector/zoom/estados | Flujos completos accesibles según revisión manual | FR-013, SC-007 |
| Caducidad, estado obsoleto y fallo al marcar/borrar | Sin falso éxito ni reejecución tras login;409 evita sobrescritura | FR-014, SC-006 |
| Fallo de purga, heartbeat atrasado o salud no verificable | Suspender recepción, alerta admin persistente y reintentos sin cambiar expires_at | FR-015, SC-005 |
| Vacío verdadero/error y cantidades |200 vacío o 503 sin ceros inventados; conteos del mismo snapshot, sin eliminados/vencidos | FR-016, SC-006 |

RLS real: anon, authenticated no admin, JWT admin, roles receive/admin/retention y roles anteriores. Ingestión no SELECT de contenido ni bandeja; mantenimiento no lee remitente/texto ni extiende fechas; admin sin sesión/contexto/permiso vigente denegado. Probar IDs conocidos, select=*, conteos, mutaciones y FK/joins, comprobando DB tras intentos, no solo HTTP.

## Conservación: evidencia necesaria y límite de pruebas

Ensayar purga candidata con reloj inyectado para antes/al/después del límite, mensajes pending/reviewed, eliminados manualmente y fallos en cada paso. Acreditar rollback, constancias sin datos personales, reintentos de purga y puerta fail-closed. Separar resultados:caducidad de acceso, DELETE lógico, restos MVCC/WAL y copias físicas/respaldos.

La suite no puede certificar por sí sola destrucción del proveedor. RET-001 permanece ERROR aunque todas las pruebas funcionales pasen. Antes de activar se necesita evidencia verificable del mecanismo que cumple exigencia estricta, tratamiento de todas las copias/restauración y recursos gratuitos. Si no puede acreditarse, mantener contacto deshabilitado; no inventar SLA ni añadir tolerancia de cron. El plazo 90 ya aprobado no se reabre por esta guía.

Restauración de ensayo siempre aislada: recepción/lectura cerradas, vencimientos y borrados reconciliados, tokens viejos incapaces de recrear mensajes. No generar nuevos dumps de contenido real ni activar PITR de pago para probar.

## Recorrido manual y accesibilidad

1. Con fixtures/garantía simulada solo en test, visitante completa envío preparado en <2 minutos; Victor localiza, lee y marca en <1 minuto (SC-008). Registrar tiempo sin datos personales en evidencia.
2. Repetir formulario/errores/429/confirmación, bandeja/marcado y cancelar/confirmar eliminación con teclado y lector:etiquetas, orden, foco, resumen enlazado y resultado comprensible.
3. Texto 200 %, ancho 320 px CSS, espaciado ampliado, orientaciones y móvil/escritorio; sin pérdida de contenido/controles. Medir contraste, no usar solo color y respetar movimiento reducido. Todo funciona sin JS.
4. Comprobar indisponibilidad sin campos, error distinto de vacío y alertas de conservación privadas. No mostrar conteos a visitante ni contenido de mensaje en respuesta de estado del envío.
5. Auditoría gratuita como axe y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables, con evidencia/justificación de no aplicables; no conformidad por puntuación automática.
6. Inspeccionar HTML/cookies/URLs/logs/errores/cachés, incluidos SQL/SDK:sin nombre/correo/cuerpo fuera de fila privada, sin tokens/credenciales. No-store incluso en errores y páginas de confirmación.

## Informe y aceptación

Registrar commit, versiones/licencias, entorno y roles, resultados Pytest, carreras/límites, revisión WCAG y resultados de conservación separados. SC-001–003 y 005–008 pueden validarse con datos sintéticos; SC-004 y gate RET-001 no se declaran cumplidos hasta evidencia estricta. Sin ella no hay aceptación para activar recepción, aunque diseño/controles estén implementados. No se han ejecutado estas pruebas durante planificación.
