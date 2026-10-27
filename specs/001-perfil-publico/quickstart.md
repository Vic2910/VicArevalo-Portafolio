# Quickstart de validación: 001-perfil-publico

Guía para la futura implementación: hoy solo existen documentos. No se han creado aplicación, lock, migraciones ni pruebas. Estos comandos son el contrato de validación previsto, no evidencia de ejecución.

## Preparación

Python 3.12; dependencias bloqueadas; Supabase Free aislado con esquema/políticas de contracts/public-data.md y fixtures sintéticos. Sin producción ni facturación. Mocks permiten evaluar aplicación sin red; RLS exige servicio real. Aprovisionar/limpiar fixtures mediante operador autorizado fuera del cliente público.

Desde raíz del repositorio, PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock
$env:SUPABASE_URL = '<URL de prueba>'
$env:SUPABASE_PUBLISHABLE_KEY = '<clave publicable de prueba>'
.\.venv\Scripts\python.exe -m flask --app app:create_app run
```

Variables por entorno protegido, nunca valores reales en docs o repositorio; .env.example vacío y secretos ignorados. No service_role. Servidor de desarrollo solo local.

## Automatización prevista

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit tests/contract -q
.\.venv\Scripts\python.exe -m pytest tests/integration -m rls -q
```

Suite RLS recibe TEST_SUPABASE_URL, TEST_SUPABASE_PUBLISHABLE_KEY y TEST_NONADMIN_ACCESS_TOKEN por entorno. Sin variables, omitir explícitamente y reportar aceptación de seguridad incompleta; skip nunca equivale a PASS.

| Escenario | Resultado | Trazabilidad |
|---|---|---|
| Identidad aprobada y campos pendientes | Datos exactos, omisión sin marcadores | US1, FR-001/007, SC-001 |
| Borradores/contactos privados centinela | Ausentes en HTML y API directa, incluso select=* y UUID | FR-003, SC-001 |
| Conocimiento y actividad publicados | Orden, fechas conocidas y datos aprobados; sin empleo ni porcentaje | US2, FR-002/005 |
| Vacío y solo borradores en cada combinación | Sin sección ni ancla ni mensaje vacío | FR-007, SC-004 |
| Timeout, cuota, pausa, datos inválidos por recurso | Estado previsto, resto válido conservado, sin error privado | FR-007, SC-004 |
| Perfil vacío/fallido | 200/503 respectivamente; sin hijos ni identidad fallback | FR-001/003/007 |
| Retirada y edición pendiente | Retirada invisible con hijos; borrador no altera publicación | FR-001/003 |
| Anon y autenticado no administrador | Solo SELECT aprobado, mutaciones sin efecto y privados inaccesibles | FR-003, SC-001 |
| Destinos disponibles/no disponibles | Enlace correcto o texto sin acción aparente | FR-004, SC-004 |
| HTML, URL peligrosa y texto largo | Escape, rechazo de esquema y wrapping | FR-005/008 |
| Más de 100 registros | Paginación completa ordenada o error al agotar plazo; nunca truncar | FR-003/007 |

## Revisión visual y WCAG

Abrir sitio local con fixtures, evaluar estados completos, parciales, vacíos y fallidos. Ejecutar herramienta gratuita como axe y complementar manualmente todos los criterios A/AA de WCAG 2.1, justificando cada no aplicable.

1. Tab/Shift+Tab/Enter y skip link: orden lógico, foco visible, sin trampas y nombres claros.
2. Lector de pantalla (por ejemplo NVDA): idioma, título, regiones, encabezados, enlaces y errores comprensibles, sin depender de live regions iniciales.
3. Texto 200 %, viewport 320 px CSS, móvil/escritorio y ambas orientaciones: sin pérdidas ni scroll horizontal no justificado, incluso texto/URLs largos.
4. Medir contrastes de texto/foco/componentes y señales independientes de color. Revisar espaciado de texto, hover/focus y alternativas de imágenes si se incorporan.
5. Movimiento reducido y JavaScript desactivado: conservar información y navegación.
6. Completar matriz del resto de criterios aplicables, incluidos lectura, enlaces, consistencia, destellos y tiempos: criterio, escenario, resultado, evidencia y defectos.

## Evidencia y aceptación

Registrar commit, versiones, entorno, resultados Pytest, evidencia RLS sanitizada, herramientas y matriz WCAG. No incluir tokens ni datos privados. Contenido real exige aprobación de Victor. Aceptar solo sin defectos funcionales, de privacidad o accesibilidad aplicables. La planificación no acredita conformidad ni pruebas ya superadas.
