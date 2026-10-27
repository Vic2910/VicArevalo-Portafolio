# Quickstart de validación: 002-administracion

Guía para implementación futura. Actualmente solo existen documentos; comandos, aplicación, fixtures y suites siguientes deberán habilitarse durante implementación. No se ejecutan pruebas funcionales en esta planificación.

## Prerrequisitos

Python 3.12, dependencias estables bloqueadas, proyecto Supabase Free aislado y HTTPS local para comprobar cookies Secure. Operador prepara esquema/migraciones, roles backend_auth/backend_editor mínimos, cuenta Auth aprobada y otra no autorizada; registro público deshabilitado. Sin datos, claves ni mensajes productivos. Generar secretos aleatorios fuera de documentos y repositorio.

Configuración por entorno protegido: SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, ADMIN_AUTH_DATABASE_URL, ADMIN_EDITOR_DATABASE_URL, SECRET_KEY (CSRF/firma), SESSION_ENCRYPTION_KEY, LOGIN_HMAC_KEY y ADMIN_ALLOWED_ORIGIN. La autorización se provisiona en tabla por UUID, nunca se deriva de un correo enviado por cliente. URLs DB con TLS verificado; no usar credenciales postgres/service_role. .env.example contiene nombres vacíos; .env y certificados privados excluidos de Git.

Desde raíz del repositorio en PowerShell, con variables ya inyectadas:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m flask --app app:create_app run --cert adhoc
.\.venv\Scripts\python.exe -m pytest tests/unit/admin tests/contract/admin -q
.\.venv\Scripts\python.exe -m pytest tests/integration/admin -m security -q
```

El modo HTTPS adhoc requiere Werkzeug con cryptography y es solo desarrollo; confiar localmente en el certificado para la prueba o usar certificado local ya confiable. ADMIN_ALLOWED_ORIGIN debe coincidir con origen HTTPS real. No desactivar Secure/CSRF para simular aceptación. No ejecutar migraciones en producción. Usar CLI --help y creación de migración según habilidad Supabase al implementar, nunca inventar aquí migraciones.

Integración recibe configuración TEST_* equivalente, credenciales de usuarios sintéticos por entorno protegido y acceso de operador únicamente para setup/teardown aislado. Verificar identificador de proyecto de prueba antes de cualquier limpieza. Si faltan recursos, marcar pruebas omitidas y aceptación incompleta; skips no acreditan seguridad. Mocks no prueban grants/RLS ni commits reales.

## Matriz automatizada

| Prueba | Evidencia esperada | Requisitos/criterios |
|---|---|---|
| Login correcto/incorrecto/cuenta inexistente/no aprobada | Solo aprobado entra; resto genérico, sin enumeración por texto/estado diferenciador | FR-001/008, SC-001/008 |
| Cinco fallos en 15 min y bloqueo desde quinto | 429 hasta quinto+15 min, Retry-After; éxito reinicia; probar bordes y cuentas inexistentes con reloj controlado | FR-008, SC-008 |
| Intentos paralelos, lease vencida y proveedor caído | No saltan umbral, respuesta tardía no crea sesión, error externo no autentica | FR-008, SC-008 |
| Replay cookie/JWT tras logout, inactividad, absoluto y permiso retirado | Denegación en Flask y Data API; reactivar autorización no revive epoch viejo | FR-002/007, SC-001/002 |
| Auth/DB/guard no verificable | Sin lectura privada ni mutación ni acceso alternativo | FR-002/008, SC-008 |
| Cambio de user_metadata/claims/signup/rol en formulario | Cero elevación de permisos y cero administradores creados | FR-001/002, SC-001 |
| Acceso directo anon/autenticado/admin JWT | Solo SELECT publicado; privados y escrituras denegados. Roles DB sin guard/contexto o contexto anterior también denegados | FR-002/006/009, SC-001 |
| Borrador incompleto seguro y reapertura | Cambios privados persistidos; cero campos públicos alterados | FR-003/013, SC-003 |
| Validación de publicación | Nombre/carrera/resumen perfil; denominación conocimiento; título/descripción académica; bloquear pendientes/no verificado | FR-004/005, SC-003 |
| Revisión A, guardar B, confirmar A | 409, no publicación obsoleta; revisión inválida/ajena/expirada rechazada | FR-004/012, SC-006 |
| Dos editores con versión compartida | Primer commit permanece, segundo 409, sin sobrescritura | FR-012, SC-006 |
| Publicación individual | Solo revisión elegida y su instantánea cambian; otros borradores/publicaciones idénticos | FR-004, SC-003 |
| Retirada con y sin borrador diferente | Sin instantánea pública ni fuente CV; borrador y revisión retirada preservados, otros elementos intactos | FR-015, SC-009 |
| Retirar último hijo / intentar retirar perfil | Sección/ancla oculta según 001; perfil no tiene acción de retirada | FR-015, SC-009 |
| Inyectar fallo en cada paso transaccional | Rollback completo, cero confirmaciones falsas, publicación anterior íntegra | FR-013/015, SC-006/009 |
| Desconexión en commit y doble POST | Recibo resuelve resultado, operation_id no duplica acción; otro cuerpo con mismo id=409 | FR-012/013, SC-006 |
| Caducidad durante formulario, reautenticación | No guardado automático, no publicación ni repetición; nueva acción explícita necesaria | FR-007, SC-002 |
| CSRF ausente/origen ajeno/GET malicioso/HTML/URL ejecutable | Rechazo sin efectos o texto escapado en editor, preview y público | FR-009/010, SC-001 |
| Logout con fallo proveedor/DB | Revocación local bloquea replay aunque falle Auth; sin commit DB no afirmar cierre | FR-007/013, SC-002/006 |
| Auditoría y redacción de secretos | Todas las categorías requeridas; cero passwords/tokens/cookies/textos de mensajes en sinks y superficies | FR-009/011, SC-007 |
| Pool y concurrencia de refresh/revocación | Sin fuga de identidad/contexto, doble refresh ni mutación posterior a revocación confirmada | FR-002/007/012, SC-001/002/006 |

Pruebas de RLS: usar roles reales y SQL/API con IDs conocidos, select=*, mutaciones y esquema privado; comprobar contenido de DB tras intento, no solo HTTP. Para mensajes/archivos aún no implementados, distinguir fixtures representativas de validación futura de sus políticas reales. El consumidor CV de prueba lee solo instantáneas, no genera PDF ni amplía 005.

## Recorrido manual y accesibilidad

1. Con cuenta sintética, iniciar sesión, editar campo, guardar borrador, abrir revisión exacta, confirmar publicación y cerrar. Victor completa el flujo sin ayuda en <=5 minutos con contenido preparado (SC-005); registrar tiempo, pasos y obstáculos.
2. Repetir con teclado y lector de pantalla: etiquetas, autocomplete, encabezados, foco, skip link, resumen de errores con vínculos y confirmaciones entendibles; sin trampas. Corregir campos inválidos y recorrer conflicto/fallo/caducidad.
3. Texto 200 %, ancho 320 px CSS, escritorio/móvil, orientación y espaciado ampliado: sin recortes ni pérdida de controles. Medir contrastes y comprobar señales no basadas solo en color.
4. Probar sin JS y con movimiento reducido. Antes de login, ajustar inactividad de 30 hasta 300 min; comprobar que el valor se respeta. Plazo absoluto 24 h; no depender de avisos JS para cumplir límites ajustables. Reloj simulado en pruebas, no esperar horas.
5. Auditoría automática gratuita (por ejemplo axe) y matriz manual de todos los criterios WCAG 2.1 A/AA aplicables. Registrar criterio, flujo/estado, evidencia, resultado y justificación de no aplicabilidad. Una puntuación automática no equivale a conformidad.
6. Revisar cookies HTTPS, headers no-store/CSP, caché atrás del navegador, HTML/preview, logs y errores. Tras logout ninguna nueva petición privada funciona; no introducir secretos en capturas/informes.

## Aceptación

Registrar commit, versiones/lock y licencias, entorno aislado, roles/grants/RLS revisados, resultados Pytest, evidencia de transacciones y matriz WCAG; redactar todo secreto. Aceptar solo sin incumplimientos aplicables de privacidad, seguridad, funcionalidad o accesibilidad, con SC-001–009 demostrados. No publicar contenido real ni afirmar conformidad de una aplicación a partir de este diseño.
