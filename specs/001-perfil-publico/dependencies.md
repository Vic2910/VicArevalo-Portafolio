# Dependencias y licencias

CPython 3.12.15. Versiones y hashes en requirements.lock; resolución reproducible en uv.lock. Inventario de metadatos instalados. Conservar LICENSE y avisos al redistribuir. Todas las bibliotecas se ejecutan localmente sin cobro por uso.

Psycopg y binario LGPL-3.0-only: herramientas de prueba cargadas dinámicamente; conservar avisos y posibilidad de reemplazo al redistribuir. Certifi MPL-2.0 conserva sus avisos y no fue modificado.

Flask/Jinja/Pytest son locales y gratuitos. Ante falta de dependencias instalar desde lock en entorno compatible. Supabase Free: respetar cuotas; pausa/fallo produce unavailable sin upgrade ni fallback ficticio. PostgreSQL local gratuito permite probar políticas, sin acreditar la API Supabase.

Fuentes verificadas: [cliente Python](https://supabase.com/docs/reference/python/initializing), [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [Free](https://supabase.com/pricing), [changelog](https://supabase.com/changelog). changelog.md devolvió content-type no soportado y se revisó HTML. El aviso de retirada CBC TLS 1.2 para noviembre no modifica consultas con Python/OpenSSL actual; revalidar al desplegar.

Herramientas auxiliares: CLI Supabase, PostgreSQL 17, Playwright y axe-core solo desarrollo. Chrome preinstalado solo navegador de pruebas, no se distribuye. No hay fuentes ni imágenes remotas ni CDN en el producto. Alternativa a herramientas browser: auditoría manual gratuita, nunca declarar conformidad pendiente.

| Paquete | Versión exacta | Licencia declarada |
|---|---|---|
| annotated-types | 0.8.0 | MIT |
| anyio | 4.15.1 | MIT |
| beautifulsoup4 | 4.15.0 | MIT License |
| blinker | 1.9.0 | MIT License |
| certifi | 2026.10.23 | MPL-2.0 |
| cffi | 2.1.1 | MIT-0 |
| click | 8.5.0 | BSD-3-Clause |
| colorama | 0.4.6 | BSD License |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause |
| deprecation | 2.1.0 | Apache 2 |
| Flask | 3.1.3 | BSD-3-Clause |
| h11 | 0.16.0 | MIT |
| h2 | 4.4.1 | MIT |
| hpack | 4.2.0 | MIT |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| hyperframe | 6.1.0 | The MIT License (MIT) |
| idna | 3.20 | BSD-3-Clause |
| iniconfig | 2.3.1 | MIT |
| itsdangerous | 2.2.0 | BSD License |
| Jinja2 | 3.1.6 | BSD License |
| MarkupSafe | 3.0.4 | BSD-3-Clause |
| multidict | 7.2.1 | Apache-2.0 |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pluggy | 1.7.0 | MIT |
| postgrest | 2.33.0 | MIT |
| propcache | 0.5.4 | Apache-2.0 |
| psycopg | 3.3.6 | LGPL-3.0-only |
| psycopg-binary | 3.3.6 | LGPL-3.0-only |
| pycparser | 3.12 | BSD-3-Clause |
| pydantic | 2.14.1 | MIT |
| pydantic_core | 2.50.1 | MIT |
| Pygments | 2.21.0 | BSD-2-Clause |
| PyJWT | 2.15.1 | MIT |
| pytest | 8.4.2 | MIT |
| realtime | 2.33.0 | MIT |
| soupsieve | 3.0.4 | MIT |
| storage3 | 2.33.0 | MIT |
| StrEnum | 0.4.15 | MIT License |
| supabase | 2.33.0 | MIT |
| supabase-auth | 2.33.0 | MIT |
| supabase-functions | 2.33.0 | MIT |
| typing-inspection | 0.4.4 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
| tzdata | 2026.5 | Apache-2.0 |
| websockets | 15.0.1 | BSD-3-Clause |
| Werkzeug | 3.1.9 | BSD-3-Clause |
| yarl | 1.25.1 | Apache-2.0 |

Herramientas verificadas: Supabase CLI 2.122.0; Chrome 156.0.8078.48; axe-core 4.14.0.
