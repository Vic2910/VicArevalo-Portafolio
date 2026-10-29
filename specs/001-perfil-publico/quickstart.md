# Validación local: 001-perfil-publico

Implementación Flask/Jinja local. Sin configuración de Supabase, GET / muestra HTTP 503 sin contenido ficticio. La aplicación no carga automáticamente archivos .env.

## Instalación y ejecución (PowerShell desde la raíz)

```powershell
uv python install 3.12
uv sync --locked
```

Alternativa con Python 3.12 instalado:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.lock
```

Configurar SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY y PUBLIC_READ_TIMEOUT_SECONDS mediante entorno protegido. Solo claves publicables o anon compatibles; nunca service_role ni sb_secret. HTTP únicamente para localhost/127.0.0.1, HTTPS para proveedor remoto.

```powershell
.\.venv\Scripts\python.exe -m flask --app app:create_app run --host 127.0.0.1
.\.venv\Scripts\python.exe -m pytest tests/unit tests/contract -q
.\.venv\Scripts\python.exe -m pytest tests/integration -m rls -q
```

## Migraciones y Supabase aislado

Usar exclusivamente un proyecto Free de prueba vacío o Supabase local, nunca producción ni activar facturación. No ejecutar reset/push contra un proyecto productivo. Esta entrega no enlaza proyectos remotos.

La CLI generó config.toml y las migraciones 20261028003054_public_profiles.sql y 20261028003106_public_collections.sql. Sus nombres difieren del ejemplo en tasks.md porque los creó la CLI con la fecha UTC actual. Consultar la ayuda de cada comando antes de operar. En un entorno local con Docker preparado:

```powershell
npm exec --yes --package=supabase -c 'supabase start --help'
npm exec --yes --package=supabase -c 'supabase migration up --help'
npm exec --yes --package=supabase -c 'supabase start'
npm exec --yes --package=supabase -c 'supabase migration up --local'
```

Alternativa: operador autorizado aplica ambos SQL en orden mediante psql/psycopg a base aislada vacía. private no está expuesto; grants y RLS son explícitos. No hay borradores reales ni publicación automática.

## RLS real de PostgreSQL

La suite implementada usa TEST_ISOLATED=1 y TEST_DATABASE_URL (DSN del operador de pruebas). Crea fixtures sintéticos en transacción sobre base sin perfiles, cambia a anon/authenticated y revierte al terminar. No requiere credenciales privilegiadas en la aplicación.

Se verificó con PostgreSQL 17 en clúster independiente .postgres-test, puerto 55432. Para reproducir con PostgreSQL instalado, inicializar un clúster NUEVO con propietario portfolio_test, puerto 55432 y escucha exclusiva en 127.0.0.1. No reutilizar el servicio existente. tests/integration/bootstrap_local.py crea roles NOLOGIN, base portfolio_rls_test y aplica migraciones; se niega a repetir si existe anon. Autenticación trust solo para ese clúster local efímero; detenerlo después de probar.

```powershell
.\.venv\Scripts\python.exe tests/integration/bootstrap_local.py
$env:TEST_ISOLATED = '1'
# Configurar TEST_DATABASE_URL mediante un mecanismo protegido externo.
.\.venv\Scripts\python.exe -m pytest tests/integration -m rls -q
```

Sin variables: skip explícito, seguridad incompleta. Esto no sustituye la prueba pendiente por Data API/JWT de Supabase. TEST_SUPABASE_URL, TEST_SUPABASE_PUBLISHABLE_KEY y TEST_NONADMIN_ACCESS_TOKEN están reservadas para completar esa prueba; aún no las consume una suite HTTP real. Verificar select=*, UUID, joins, privados, mutaciones sin efecto y DB posterior.

Limpieza: rollback automático de fixtures. Detener únicamente el clúster local con pg_ctl -D .postgres-test -m fast -w stop. No eliminar/mover recursivamente rutas calculadas. El clúster está ignorado en Git. No copiar secretos ni logs privados a evidencias.

## Vista sintética y accesibilidad

```powershell
$env:PYTHONPATH = '.'
.\.venv\Scripts\python.exe tests/preview.py
```

Abrir http://127.0.0.1:5051. Parámetros: ?state=empty, ?state=unavailable, ?skills=unavailable&academic=ready. Vista exclusiva de pruebas, separada de app:create_app. Detener con Ctrl+C.

tests/browser-audit.cjs usa Playwright incluido en Codex, Chrome instalado y AXE_SCRIPT_PATH apuntando a axe.min.js. En otro entorno instalar Playwright/axe gratuitos y adaptar la ruta del runtime. CHROME_PATH permite seleccionar Chrome. Ejecutar node tests/browser-audit.cjs; AXE_SCRIPT_PATH es obligatorio para afirmar auditoría axe. Produce capturas y JSON sintéticos en evidence/.

Completar teclado, NVDA gratuito y todos los criterios A/AA de accessibility.md. Revisar 320 px, texto 200 %, orientación, contraste, espaciado, contenido largo, movimiento reducido y ausencia de JS. Axe no acredita conformidad por sí solo.

## Límites

No hay despliegue, panel ni features 002–007. Proyectos/contacto/CV siguen indisponibles hasta registrar endpoint y capacidad en PUBLIC_DESTINATIONS; CV exige approved_variant. Contenido real requiere aprobación de Victor. Ver validation.md; tareas pendientes permanecen abiertas.
