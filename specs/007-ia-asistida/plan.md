# Implementation Plan: Asistencia editorial local y revisable

**Branch**: `007-ia-asistida` (contexto solicitado; rama Git actual: `clarifying-specs`) | **Date**: 2026-10-27 | **Spec**: [spec.md](spec.md)

**Input**: `specs/007-ia-asistida/spec.md`. main en la spec es metadato histórico; no se cambia de rama.

## Summary

Añadir ayuda de redacción de perfil/proyecto y traducción es/en, exclusivamente local al inicio. Victor revisa texto/contexto antes de generar; salida no confiable comparada con fuente, editable y descartable. Generar no modifica contenido; aceptar guarda solo el campo de borrador elegido mediante 002/003/005, nunca publica ni habilita una traducción del CV.

Modelo propuesto Qwen2.5-1.5B-Instruct-GGUF Q4_K_M, licencia Apache-2.0, con llama.cpp MIT. Proceso aislado por generación en el mismo host Flask, endpoint loopback autenticado solo entre backend/runtime, sin acceso del navegador, DB, herramientas o secretos del proyecto. Pesos preinstalados y modo offline; sin proveedor remoto ni descarga automática. Sugerencias no aceptadas solo en RAM/DOM de revisión activa, sin historial recuperable.

La IA es opcional para tareas esenciales:equipo sin memoria/modelo mantiene edición/publicación/CV aprobado manuales. Hosting gratuito pequeño no se presume capaz de inferencia; habilitar solo donde existan recursos locales probados, sin túnel al equipo de Victor ni puente remoto implícito. RET-001004 permanece bloqueado; mensajes y datos de visitantes nunca son fuente.

Solo diseño:no código, inferencia, descargas, credenciales, migraciones, tasks.md o despliegue. Los otros módulos son diseños previos, no aplicación ya existente.

## Technical Context

**Language/Version**: Python 3.12, Flask/Jinja, HTML/CSS y módulo JavaScript pequeño para ciclo de revisión efímera, AbortController y comparación de campo. Editor manual y CV 005 siguen sin requerir esa mejora.

**Primary Dependencies**: Stack002 y HTTPX006 para loopback; stdlib subprocess para aislamiento. Runtime llama.cpp y pesos Qwen oficiales, versiones/revisión/SHA256/licencias fijadas en manifiesto al aprovisionar. No SDK remoto/servicio SaaS/transformers obligatorio ni entrenamiento.

**Storage**: Supabase Free solo controles técnicos de instancia/request/lease/cuotas y auditoría sin payload. Fuente/borrador existente sigue 002/003/005. Prompt y propuesta no se guardan en Supabase, sesiones, localStorage/sessionStorage/IndexedDB, archivos, logs o caché de prompts; solo texto final explícitamente aceptado pasa al borrador normal.

**Testing**: Pytest con adaptador local falso, reloj controlado y process manager fake; pruebas de límite/cancelación/respuesta tardía/source changed/permisos. Integración RLS real aislada y pruebas de navegador con recarga/cierre/BFCache; ensayo local opcional del modelo real y revisión humana bilingüe antes de aceptar comportamiento asistido. Sin datos privados reales.

**Target Platform**: Desarrollo Windows/PowerShell, ejecución CPU local en host de aplicación con memoria suficiente y WSGI con capacidad concurrente para cancelar/seguir editando. Proceso hijo oculto en Windows. Despliegue sin recursos muestra IA indisponible sin cambiar proveedor o deshabilitar funciones manuales.

**Project Type**: Monolito modular con inferencia local auxiliar acotada, sin chatbot público, agentes con herramientas, broker o proveedor remoto.

**Performance Goals**: SC-009:Victor identifica estado no aprobado y acepta como borrador/descarta en<1 min con propuesta preparada. Generación tiene deadline total 60 s incluyendo carga/tokenización; una activa global. Cancelar invalida resultado inmediatamente y proceso se termina al observar cancelación/lease o timeout. Umbral de habilitación propuesto 4 GiB libres más prueba real de CPU/memoria, no requisito oficial ni garantía de latencia.

**Constraints**: Fuente seleccionada 1–1500 caracteres Unicode, contexto 0–500, idiomas es/en; prompt serializado completo<=3072 bytes UTF-8 como cota conservadora previa para contexto 4096 tokens, reserva 768 salida+256 control. Máximo salida 4000 caracteres/16 KiB, sin truncamiento silencioso.6 inicios/10 min por admin y 20/h global, una activa; exceso 429 con espera. Respuesta incompleta/truncada no aceptable como propuesta lista. Límites visibles antes de enviar, texto manual intacto.

**Scale/Scope**: Un administrador, perfil breve/descripciones de proyecto y campos textuales de traducción 005. Sin contactos, archivos, bandeja, métricas, internet, herramientas, publicación o aprobación desde modelo. Traducción usa fuente aprobada vigente; mejora de redacción puede usar selección editorial actual de borrador.

## Constitution Check

Gates antes de Phase 0 y después de Phase 1. PASS de diseño; no verificación funcional ni aprobación de afirmaciones reales ya ejecutadas.

| Gate | Antes | Después | Evidencia / obligación |
|---|---|---|---|
| I. WCAG 2.1 A/AA | PASS | PASS | Generar/comparar/editar/aceptar/descartar/cancelar por teclado/lector y matriz completa. JS justificado por cancelación/lifecycle, sin bloquear edición manual. |
| II. Honestidad y control humano | PASS | PASS | Toda salida no aprobada; evidencia faltante se solicita, no se presume; aceptación solo borrador y revisión/publicación aparte. |
| III. Pytest | PASS | PASS | Matriz de privacidad, concurrencia, fuentes, fallo local, recarga y flujo esencial sin IA; RLS real adicional. |
| IV. Gratuidad y privacidad | PASS | PASS | Licencias libres, inferencia local, sin payload persistido, modelos sin credenciales/tools y sin fallback remoto. |
| V. Simplicidad | PASS | PASS | Mismo Flask/Supabase, proceso local descartable y adaptador estrecho; sin nuevo proveedor ni servicio externo. |
| Independencia de tareas esenciales | PASS | PASS | IA indisponible no cambia guard 002, publicación 003, CV 005 ni gate 004. |

Sin violaciones/enmiendas. Aprovisionar solo tras comprobar licencias/checksums/configuración/hardware. No se promete detector infalible de secretos ni modelo sin alucinaciones:prevención por fuentes mínimas, bloqueo de patrones identificados y revisión humana. No confundir una sugerencia correcta en test con aprobación editorial automática.

## Project Structure

### Documentation (this feature)

```text
specs/007-ia-asistida/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── assistance-http.md
    └── local-model-and-privacy.md
```

### Source Code (repository root, propuesto)

```text
app/
├── __init__.py
├── config.py
├── admin/
├── security/
├── assistance/
│   ├── routes.py
│   ├── forms.py
│   ├── service.py
│   ├── source_policy.py
│   ├── repository.py
│   ├── local_adapter.py
│   ├── process_manager.py
│   └── prompts.py
├── templates/assistance/
│   ├── preview.html
│   └── review.html
├── static/js/assistance.js
└── static/css/site.css
config/ai-model-manifest.json
third_party/ai/NOTICE
tests/
├── fixtures/assistance/
├── unit/assistance/
├── contract/assistance/
└── integration/assistance/
supabase/migrations/
pyproject.toml
requirements.lock
.env.example
.gitignore
```

**Structure Decision**: Adaptador solo recibe texto/contexto aprobados para envío y devuelve texto estructurado no confiable. No recibe cliente DB ni servicios de publicación. Proceso hijo y endpoint loopback se destruyen por generación; solo controles técnicos sobreviven temporalmente en DB. Pesos/binarios fuera de Git por configuración local; manifiesto/avisos sin secretos sí versionables.

## Phase 0 — Research

Completada en research.md:modelo/licencia/recursos, aislamiento, límites, privacidad, efimeridad, aceptación y accesibilidad. Investigación delegada conforme a habilidad. No quedan clarificaciones técnicas necesarias abiertas; versión exacta/checksum se fijarán al instalar sin cambiar opción local elegida.

## Phase 1 — Design & Contracts

Modelo/ciclo de vida en data-model.md, interfaces y aislamiento en contracts/ y escenarios/comandos previstos en quickstart.md. No crear otra aprobación paralela:002/003/005 siguen siendo autoridades de guardado/publicación/traducción. Cierre/recarga invalida revisión y ningún resultado anterior se recupera al volver.

## Complexity Tracking

Sin violaciones. JS y proceso local aislado son necesarios para revisión efímera/cancelación y evitar persistencia o permisos del modelo; no introducen SPA ni agente autónomo.
