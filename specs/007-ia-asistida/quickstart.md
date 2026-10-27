# Quickstart de validación: 007-ia-asistida

Guía para futura implementación. No existen app, modelo instalado, lock, migraciones o suites implementadas. Esta planificación no descarga binarios/pesos, ejecuta inferencia ni usa textos reales. Fixtures no son afirmaciones de Victor.

## Prerrequisitos

Python 3.12, stack 002/HTTPX bloqueados, Supabase Free aislado con controles 007 y fuentes 002/003/005 sintéticas. Un admin aprobado y cuenta sin permiso; guard 002 y TLS/origen de prueba. UI de revisión con JS habilitado para lifecycle/cancelación; editor manual y CV deben seguir disponibles con IA/JS deshabilitados.

Pruebas predeterminadas usan adaptador falso y fake process manager sin modelo/red. Para ensayo local real separado:Qwen2.5-1.5B-Instruct-GGUF Q4_K_M oficial, llama.cpp MIT fijado y pesos Apache-2.0 con revisión/SHA256/chat template/avisos; rutas locales configuradas fuera de Git. Aprovisionamiento de pesos/binario es tarea separada de implementación, sin comandos de descarga automática aquí. Umbral conservador4 GiB libres más benchmark real; no supone capacidad de hosting gratuito remoto.

Entorno protegido:configuración 002, AI_CONTROL_DATABASE_URL, AI_RUNTIME_PATH, AI_MODEL_PATH y manifiesto de límites/checksum. No proveedor remoto, URL del navegador, HF_TOKEN ni token de inferencia externo. Clave efímera loopback solo memoria por proceso; no valor real en .env.example, Git/logs o documentos. Pesos/binarios excluidos de repo. Proceso hijo no hereda variables DB/Supabase/GitHub de app.

Desde raíz, después de implementar:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
.\.venv\Scripts\python.exe -m flask --app app:create_app run --cert adhoc
.\.venv\Scripts\python.exe -m pytest tests/unit/assistance tests/contract/assistance -q
.\.venv\Scripts\python.exe -m pytest tests/integration/assistance -m security -q
.\.venv\Scripts\python.exe -m pytest tests/integration/assistance -m browser_lifecycle -q
```

HTTPS/origen coincidente y certificado local confiable para Secure/CSRF; adhoc solo desarrollo. Operador prepara/limpia solo proyecto de prueba, identificador verificado; TEST_* por entorno protegido. Sin DB/navegador real, skips no acreditan RLS o cierre/recarga. Sin inferencia real no declarar validación de hardware/calidad del modelo, aunque pruebas del flujo con fake pasen.

Antes de habilitar ensayo de modelo local, comprobar configuración/versiones sin enviar texto:

```powershell
& $env:AI_RUNTIME_PATH --help
Get-FileHash -LiteralPath $env:AI_MODEL_PATH -Algorithm SHA256
.\.venv\Scripts\python.exe -m pytest tests/integration/assistance -m local_model -q
```

Validar flags de build contra contrato local-model-and-privacy.md, pesos/hash manifiesto y postura offline/log/cache, proceso oculto y sin credenciales/tools. Test local_model solo explícito con datos sintéticos y máquina apta; no fallback/download al faltar modelo. Registrar memoria/tiempo para 60 s/contexto 4096, y denegar habilitación si no cumple recursos.

## Fixtures y matriz automatizada

Fuentes académicas/perfil/proyecto y traducción es/en sintéticas, aprobadas y en borrador según tarea. Respuestas buenas, needs_information, falso empleo/logro, capacidad elevada, idioma equivocado, HTML/tool-call malicioso, truncada/excesiva y tardía. Secretos/contactos centinela falsos, nunca reales. Adaptador captura exactamente bytes enviados para comprobar allowlist/minimización y ausencia de datos prohibidos.

| Caso | Resultado | Cobertura |
|---|---|---|
| Preview de selección/contexto y purpose/idioma | Coincide exactamente con entrada autorizada; no contexto automático | FR-001, FR-003, SC-004 |
| Entrada vacía/límites exactos/exceso caracteres/bytes | Rechazo previo a proceso/transmisión, sin recorte ni pérdida de manual | FR-009, SC-007 |
| Secretos reconocidos/source contacto/visitor/contexto no permitido | Adaptador recibe cero bytes, sin secretos en errores/logs | FR-003, FR-008, SC-004 |
| Modelo local/manifiesto/checksum/config offline | Runtime autorizado o indisponible; cero egreso remoto/download | FR-002, SC-003, SC-004 |
| Generar sin aceptar | Fuente/borrador/publicación idénticos; propuesta no aprobada junto a fuente | FR-004, SC-001, SC-005 |
| Fuente insuficiente/propuesta con hechos inventados | No se trata como hecho verificado; corregir/descartar antes de aprobación humana | FR-005, SC-006 |
| Editar y aceptar | Solo campo de borrador seleccionado persiste; otros campos/publicación intactos | FR-006, SC-001 |
| Traducción es/en aceptada | Borrador sin aprobación 005 ni disponibilidad CV nueva por sí sola | FR-001, FR-006, SC-001, SC-006 |
| Fuente/campo/versión cambia entre preview, generación y aceptación |stale/409, sin sobrescritura ni aprobación heredada | FR-007, SC-005 |
| Descartar/cancelar/respuesta tardía | Invalidar nonce, ninguna edición automática, contenido previo intacto | FR-004, FR-009, SC-002 |
| Cerrar/recargar/BFCache con propuesta pendiente | Nueva instancia vacía, sin recuperar salida ni cambiar borrador guardado | FR-013, SC-010 |
| Cerrar/recargar mientras genera, pagehide perdido y respuesta tardía | Reapertura invalida anterior; solo canal antiguo descartado, lease termina proceso | FR-009, FR-013, SC-002, SC-010 |
| Sesión caducada/permiso retirado durante inferencia | No entrega ni acepta salida; proceso cancelado, sin retransmisión al login | FR-011, SC-007 |
| Anon/no admin/JWT cliente/CSRF/origen ajeno | No lectura de propuesta/fuente ni envío al modelo/guardado | FR-011, SC-004, SC-007 |
| Modelo ausente/OOM/timeout/frecuencia/saturación | Estado comprensible, edición manual intacta, sin cargos/proveedor alterno | FR-002, FR-009, FR-010, SC-003, SC-007 |
| Inyección/tool-call/HTML/URL en salida | Texto escapado o error de esquema, cero herramientas/secretos/acciones | FR-008, SC-004 |
| Flujo esencial con IA deshabilitada | Editar/guardar/publicar y descargar CV aprobado funcionan sin runtime | FR-010, SC-003 |
| Fallo aceptación/commit incierto/doble operación | Rollback o recibo resuelto, sin borrador duplicado/publicación/reinferencia | FR-006, SC-001, SC-007 |
| Rango Unicode/UTF-16 y otros campos manuales sin guardar | Solo valor/rango destino explícito, sin romper caracteres ni guardar campos vecinos | FR-006, FR-007, SC-001, SC-005 |
| Todos los controles/estados con teclado/lector | Generar, comparar, editar, aceptar, descartar y cancelar completos | FR-012, SC-008, SC-009 |

RLS real:anon/authenticated sin acceso a controles ni fuentes privadas, admin JWT directo no modifica; rol coordinador sin acceso a 004/secretos/publicación y roles editoriales aceptan solo contexto/nonce/target vigente. Comprobar DB tras intentos, no solo HTTP. El proceso hijo local sin entorno app ni conexión DB; endpoint loopback no expuesto a red o navegador.

## Ensayo de ciclo de navegador y privacidad

1. Generar propuesta fake, cambiar manualmente campo antes de resolver y confirmar que se advierte versión anterior, sin aplicar.
2. Cancelar y resolver fake tarde; luego cerrar/recargar/reabrir y restaurar con atrás/adelanteBFCache. No output antiguo ni fetch de historial. Borrador previamente guardado permanece exactamente igual.
3. Inspeccionar Supabase, cookies, localStorage/sessionStorage/IndexedDB, cache, HTML serializado restaurable y logs del proxy/app/runtime:sin prompts/propuestas no aceptados ni datos privados. Solo metadatos técnicos y texto final aceptado en borrador legítimo.
4. Simular pagehide perdido, proceso huérfano/DB caída y segundo worker:invalidación/fencing y capacidad fail-closed, sin nueva inferencia hasta confirmar cleanup. Cancelación lógica se mantiene aunque respuesta física termine tarde.
5. Capturar salida de red durante inferencia sintética:solo loopback propio y DB/Auth de backend; hijo sin red externa y sin credenciales. No petición HuggingFace/OpenAI/OllamaCloud u otro proveedor. No sugerencias en auditoría de diagnóstico.

## Revisión humana, accesibilidad y recursos

Con conjunto bilingüe preparado, Victor compara fuente/propuesta, identifica condición no aprobada y acepta como borrador o descarta en<1 min (SC-009), distinguiéndolo de publicar. Antes de aprobación editorial posterior, cada texto debe conservar hechos/nombres/nivel; probar corrección/descarte de respuestas falsas y declarar evidencia de SC-006 como revisión humana, no garantía del modelo.

Teclado/lector en todo ciclo, labels y status sin lectura intrusiva de tokens, foco visible, errores asociados. Texto 200 %,320 px CSS, orientación/espaciado, contraste, movimiento reducido y ausencia de controles por hover/gesto. Auditoría gratuita como axe más matriz manual de todos los criterios WCAG 2.1 A/AA aplicables; no conformidad por puntuación automática.

Validar cota previa 3072 bytes con tokenizer/template fijados y entradas Unicode adversas; si no puede demostrarse, denegar antes de transmitir y ajustar límite, sin recortar fuente. Medir memoria/CPU/carga/latencia/cancelación de máquina local, una generación y recursos reservados para editor/guardar/CV. No prometer rendimiento en host que no se ensayó.

## Evidencia y aceptación

Registrar commit, versiones/modelo/revisión/checksum/licencias, configuración offline/hardware, entorno/roles/RLS, Pytest, red/privacidad sanitizadas, ciclo de navegador, revisión bilingüe y matrizWCAG. SC-001–010 deben demostrarse; fakes no acreditan hardware/calidad ni skips cumplimiento. Datos reales no van a evidencia. Gate RET-001004 no cambia y 007 no usa mensajes ni activa recepción. Esta planificación no ejecutó inferencia o pruebas.
