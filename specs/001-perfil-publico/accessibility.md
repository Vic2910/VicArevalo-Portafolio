# Matriz WCAG 2.1 A/AA

Estado: **evaluación parcial; no se declara conformidad**. Referencia: [WCAG 2.1 del W3C](https://www.w3.org/TR/WCAG21/).

Evidencia automática: `evidence/browser-audit.json` y pruebas `tests/contract/test_accessible_page.py`. Chrome/Playwright/axe: ready, empty, unavailable y fallo parcial; 1280×900, 320×760, 760×320. Capturas inspeccionadas: móvil y escritorio. Texto 200 %, espaciado ampliado, movimiento reducido y sin JavaScript.

Leyenda: **Parcial** = comprobación automatizada/inspección de código, requiere revisión humana; **Pendiente** = no acreditado; **N/A propuesta** = ausente en esta página, confirmar al revisar el incremento. Ningún N/A equivale a conformidad global.

| Criterio | Nivel | Escenario/evidencia | Resultado |
|---|---|---|---|
| 1.1.1 Contenido no textual | A | No hay imágenes, iconos ni controles gráficos | N/A propuesta |
| 1.2.1 Solo audio/vídeo | A | No hay multimedia | N/A propuesta |
| 1.2.2 Subtítulos grabados | A | No hay multimedia | N/A propuesta |
| 1.2.3 Audiodescripción/alternativa | A | No hay multimedia | N/A propuesta |
| 1.2.4 Subtítulos en directo | AA | No hay multimedia | N/A propuesta |
| 1.2.5 Audiodescripción grabada | AA | No hay multimedia | N/A propuesta |
| 1.3.1 Información y relaciones | A | Regiones, listas, h1/h2/h3; axe; falta NVDA | Parcial |
| 1.3.2 Secuencia significativa | A | Orden DOM lineal, capturas; falta NVDA | Parcial |
| 1.3.3 Características sensoriales | A | No hay instrucciones basadas en posición/color | Parcial |
| 1.3.4 Orientación | AA | Viewports vertical y horizontal; sin bloqueo | Parcial |
| 1.3.5 Propósito de entrada | AA | No hay campos de entrada | N/A propuesta |
| 1.4.1 Uso del color | A | Enlaces subrayados y estados textuales | Parcial |
| 1.4.2 Control del audio | A | No hay audio | N/A propuesta |
| 1.4.3 Contraste mínimo | AA | axe sin violaciones en escenarios evaluados | Parcial |
| 1.4.4 Cambio tamaño texto | AA | Texto 200 % sin desbordamiento en 12 escenarios | Parcial |
| 1.4.5 Imágenes de texto | AA | Solo texto HTML | N/A propuesta |
| 1.4.10 Redistribución | AA | 320 px y texto ampliado; evidencia navegador | Parcial |
| 1.4.11 Contraste no textual | AA | Foco #92400e sobre fondos claros; revisión visual pendiente | Parcial |
| 1.4.12 Espaciado de texto | AA | Override CSS 1.5/.12em/.16em/2em, sin desbordamiento | Parcial |
| 1.4.13 Contenido hover/foco | AA | No hay popovers ni tooltips | N/A propuesta |
| 2.1.1 Teclado | A | Tab/Enter al skip link; falta recorrido completo humano | Parcial |
| 2.1.2 Sin trampas | A | Solo enlaces nativos; falta recorrido completo humano | Parcial |
| 2.1.4 Atajos caracteres | A | No hay atajos | N/A propuesta |
| 2.2.1 Tiempo ajustable | A | No hay sesiones, tareas cronometradas ni interacción con límite | N/A propuesta |
| 2.2.2 Pausar/detener/ocultar | A | No hay movimiento ni actualización automática | N/A propuesta |
| 2.3.1 Tres destellos | A | Sin animación ni vídeo | N/A propuesta |
| 2.4.1 Evitar bloques | A | Skip link enfoca main#contenido en 12 escenarios | Parcial |
| 2.4.2 Página titulada | A | Título diferenciado para estados, contrato Pytest | Parcial |
| 2.4.3 Orden del foco | A | Orden DOM natural, sin tabindex positivo; revisión humana pendiente | Parcial |
| 2.4.4 Propósito enlaces | A | Nombres y destinos comprobados; revisión editorial pendiente | Parcial |
| 2.4.5 Múltiples vías | AA | Única página del incremento; revisar al añadir páginas | N/A propuesta |
| 2.4.6 Encabezados/etiquetas | AA | Jerarquía en contratos y axe; falta NVDA | Parcial |
| 2.4.7 Foco visible | AA | Outline CSS 3 px; revisión humana completa pendiente | Parcial |
| 2.5.1 Gestos puntero | A | Solo enlaces nativos | N/A propuesta |
| 2.5.2 Cancelación puntero | A | Activación nativa de enlaces, sin handlers | Parcial |
| 2.5.3 Etiqueta en nombre | A | Texto nativo de enlace; axe | Parcial |
| 2.5.4 Activación movimiento | A | Sin sensores ni gestos | N/A propuesta |
| 3.1.1 Idioma página | A | lang=es probado | Parcial |
| 3.1.2 Idioma partes | AA | Fixtures españoles; contenido real requiere revisión | Pendiente |
| 3.2.1 Al recibir foco | A | Sin handlers de foco ni navegación automática | Parcial |
| 3.2.2 Al introducir datos | A | No hay formularios | N/A propuesta |
| 3.2.3 Navegación coherente | AA | Una plantilla y orden estable entre estados | Parcial |
| 3.2.4 Identificación coherente | AA | Etiquetas estables de destinos/secciones | Parcial |
| 3.3.1 Identificación errores | A | No hay entradas del usuario | N/A propuesta |
| 3.3.2 Etiquetas/instrucciones | A | No hay entradas del usuario | N/A propuesta |
| 3.3.3 Sugerencias errores | AA | No hay entradas del usuario | N/A propuesta |
| 3.3.4 Prevención errores | AA | No hay transacciones ni edición | N/A propuesta |
| 4.1.1 Procesamiento | A | HTML analizado en contratos; axe; revisión DOM parcial | Parcial |
| 4.1.2 Nombre/función/valor | A | Enlaces nativos; indisponibles sin controles falsos; axe | Parcial |
| 4.1.3 Mensajes de estado | AA | Estados iniciales por títulos/encabezados/texto; sin cambios dinámicos | Parcial |

## Procedimiento humano pendiente

1. Ejecutar la vista sintética indicada en quickstart; recorrer todos los enlaces con Tab, Shift+Tab y Enter. Confirmar foco visible, orden y ausencia de trampas en todos los estados.
2. Con NVDA gratuito, leer título, idioma, regiones y jerarquía (H), enlaces (K) y estados vacíos/fallidos. Confirmar pronunciación y nombres; registrar versión y resultado por criterio.
3. Revisar capturas y navegador a 320 px, ambas orientaciones, texto 200 %, espaciado ampliado y URLs extensas. Confirmar que no hay pérdida ni solapamiento, además de la ausencia automatizada de overflow.
4. Verificar contrastes manuales de texto/foco, movimiento reducido y contenido sin JS. Evaluar cada N/A propuesto con el contenido final.

El informe automático no sustituye estas comprobaciones. T023/T035 permanecen abiertos.
