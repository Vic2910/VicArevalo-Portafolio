# Research: 007-ia-asistida

Fecha:2026-10-27. Base:spec 007, constitución 1.0.0 y diseños 002/003/005. Investigación independiente delegada de modelo/runtime/licencias/cancelación consolidada aquí; no se descargaron pesos ni se ejecutó inferencia.

## 1. Modelo y licencia

- **Decision**: Qwen/Qwen2.5-1.5B-Instruct-GGUF Q4_K_M oficial, Apache-2.0, y llama.cpp MIT. Fijar revisión de pesos y runtime, SHA256, chat template y licencias en manifiesto antes de usar. Local CPU al inicio, sin endpoint remoto.
- **Rationale**: Modelo pequeño con soporte multilingüe español/inglés y cuantización oficial, adecuado para ensayar asistencia acotada; no garantiza veracidad/calidad. Archivo oficial alrededor 1.12 GB, distinto del coste RAM real con KV/runtime.
- **Alternatives considered**: Modelo grande sin memoria demostrada; pesos con licencia restrictiva; proveedor de prueba/créditos; Ollama con catálogo/download implícito; tratar endpoint OpenAI-compatible local como autorización para usar nube.
- **Sources**: [model card](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF), [archivos](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/tree/main), [llama.cpp licencia](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE).

## 2. Recursos y fallo útil

- **Decision**: Contexto 4096, salida<=768 tokens, deadline 60 s desde petición, una generación global. Umbral inicial propuesto 4 GiB libres y benchmark real antes de habilitar. Si no basta, asistencia indisponible y tareas manuales intactas; no fallback ni cambio automático de modelo/proveedor.
- **Rationale**: Pesos no equivalen a RAM libre y CPU varía. Hosting gratuito de poca memoria no se presume apto; modo local significa mismo host de aplicación, no conexión implícita desde cloud al ordenador de Victor.
- **Alternatives considered**: Prometer inferencia gratis ilimitada; cargar modelo al importar app bloqueando rutas; contratar cómputo; convertir IA en dependencia de publicar/CV.

## 3. Proceso aislado y transporte

- **Decision**: Subproceso llama-server por generación, solo 127.0.0.1/puerto efímero y clave local de transporte efímera; backend envía texto por HTTP loopback, no argumentos de shell. Entorno hijo allowlist sin credenciales app/DB/HuggingFace, modelo local verificado, offline/log/cache desactivados. Terminar al completar/cancelar/timeout, sin mantener KV para otra revisión.
- **Rationale**: Evita heredar secretos y conservar contexto entre personas/revisiones. Cerrar fetch no prueba que se detuvo inferencia; controlar proceso además de invalidar nonce. No tools, MCP, ejecución de código, rutas de archivos/URLs del usuario ni acciones del modelo.
- **Alternatives considered**: Modelo embebido con acceso al proceso completo de app; servidor expuesto 0.0.0.0; servicio compartido con logs/prompts/slots; enviar texto por argv o archivo temporal; inferir aborto solo por desconexión HTTP.
- **Sources**: [llama.cpp](https://github.com/ggml-org/llama.cpp), [server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md).

## 4. Entrada mínima y límites previos

- **Decision**: Allowlist de campos editoriales, fuente seleccionada y contexto mostrados antes de enviar. No leer contactos/mensajes/configuración para formar prompt. Rechazar patrones de secretos/contacto identificados y cualquier source_kind no permitido. Límite por caracteres más cota conservadora de bytes del prompt completo antes de iniciar runtime; sin recorte silencioso ni transmisión para averiguar si cabe.
- **Rationale**: Limitar fuentes es más fuerte que pedir al modelo no leer secretos. Detector de texto libre no es infalible; preview y confirmación de Victor siguen obligatorias. Cota de bytes sacrifica capacidad para evitar contar tokens mediante envío previo del contenido.
- **Alternatives considered**: Contexto automático de todo portafolio/DB; tokenizar entrada en proveedor antes de validar privacidad/límites; scanner de secretos como única garantía; pegar datos de visitantes como contexto.

## 5. Sugerencia efímera y ciclo del editor

- **Decision**: Prompt/respuesta solo memoria de petición/subproceso y DOM actual. No recuperar por GET, jobs duraderos, Supabase, sesión, storage del navegador o historial. Nueva instancia de editor invalida revisión anterior del mismo campo; pagehide/recarga/cancelación invalidan nonces y AbortController, y heartbeat técnico acota procesos abandonados. BFCache/restauración limpia estado IA antes de mostrar.
- **Rationale**: FR-013 exige descarte y no recuperación. Persistir solo controles técnicos sin texto permite rate limit/cancelación entre workers, sin historial de propuestas. Tras fallo/cierre, el nuevo editor jamás consulta o aplica salida anterior.
- **Alternatives considered**: Tabla de sugerencias; sessionStorage/localStorage; restaurar job/output al reabrir; aplicar al recibir respuesta sin comprobar instancia/fuente.

## 6. Aceptación y traducción

- **Decision**: Salida identificada no aprobada, editable junto a fuente. Aceptar crea revisión de borrador solo del campo elegido con guard/versionado habitual; otros campos guardados/publicaciones intactos. Traducción es/en parte de fuente aprobada vigente y se guarda como borrador en 005 o destino español 002/003; nunca hereda aprobación.
- **Rationale**: El modelo puede inventar o alterar experiencia; prompt no demuestra veracidad. Fuente/target cambiados producen 409/revisión nueva en vez de sobrescritura silenciosa. Aprobar/publicar sigue siendo otra acción humana y autorizada.
- **Alternatives considered**: Publicar al aceptar; considerar salida marcada en como traducción aprobada; ejecutar instrucciones generadas; reemplazar toda entidad/campos vecinos.

## 7. Accesibilidad y evaluación

- **Decision**: Comparación lineal con textarea/labels, botones con nombres explícitos y status accesible; teclado y lector para generar/revisar/editar/aceptar/descartar/cancelar. JS pequeño aporta lifecycle/cancelación sin framework; si falta, IA explica indisponibilidad y flujo manual completo permanece.
- **Rationale**: Sin dependencia de modal/hover/color/stream de tokens. Evaluación humana de hechos es/en antes de aprobación, más pruebas de respuestas malas y fallback esencial sin IA.
- **Alternatives considered**: Chat público, streaming que roba foco, UI solo por gesto o editor bloqueado durante inferencia.
- **Source**: [WCAG2.1](https://www.w3.org/TR/WCAG21/).

[Changelog Supabase](https://supabase.com/changelog) revisado; controles técnicos usan RLS/roles mínimos de002 sin claves privilegiadas. HTTPX existente006, licencias/transitivas fijadas al implementar. Descarga/instalación se realiza solo como aprovisionamiento separado, sin prompts ni uso de endpoints de inferencia de terceros; esta planificación no lo ejecuta. No quedan preguntas técnicas necesarias pendientes.
