# Research: 001-perfil-publico

Fecha: 2026-10-27. Basado en spec y constitución 1.0.0. Decisiones de diseño, no implementación ni permiso para publicar contenido real.

## Stack y dependencias

- **Decision**: Python 3.12, Flask 3.1/Jinja 3.1, supabase-py 2 y Pytest; fijar versiones exactas y transitivas al implementar. Fuentes de sistema y CSS local.
- **Rationale**: Monolito exigido, renderizado completo sin JS y pruebas mediante adaptador inyectable. Flask/Jinja tienen licencia BSD-3-Clause; Pytest y supabase-py MIT. Conservar avisos y verificar transitivas antes de instalar.
- **Alternatives considered**: SPA, ORM y microservicios añaden complejidad; REST artesanal duplica cliente oficial.
- **Sources**: [Flask installation](https://flask.palletsprojects.com/en/stable/installation/), [Python client](https://supabase.com/docs/reference/python/introduction), [Flask licencia](https://github.com/pallets/flask/blob/main/pyproject.toml), [Jinja licencia](https://github.com/pallets/jinja/blob/main/LICENSE.txt), [Pytest licencia](https://github.com/pytest-dev/pytest/blob/main/pyproject.toml), [supabase-py licencia](https://github.com/supabase/supabase-py/blob/main/LICENSE).

## Publicación y protección

- **Decision**: Tablas expuestas contienen solo instantáneas aprobadas, nunca columnas privadas. Borradores/revisión en esquema no expuesto sin permisos públicos. RLS y grants mínimos; lectura con cliente anon sin sesión administrativa. Sin service_role, vistas ni SECURITY DEFINER.
- **Rationale**: Filtrar en Flask no protege acceso directo; RLS filtra filas, no columnas. Una edición pendiente no modifica lo aprobado. Un contacto no autorizado nunca se almacena en una fila pública.
- **Alternatives considered**: Tabla mixta con filtro UI (insegura), vistas por defecto (pueden eludir RLS), lectura privilegiada (innecesaria).
- **Sources**: [RLS](https://supabase.com/docs/guides/database/postgres/row-level-security), [column security](https://supabase.com/docs/guides/database/postgres/column-level-security), [API security](https://supabase.com/docs/guides/api/securing-your-api).

## Estados y navegación

- **Decision**: Resultados ready/empty/unavailable por recurso. Empty confirmado oculta sección opcional y ancla; unavailable conserva explicación accesible. Destinos disponibles solo si módulo registra endpoint y capacidad habilitada, por defecto deshabilitados.
- **Rationale**: No confundir falta de publicación con cuota, timeout o dato inválido. No inventar rutas ni enlaces #.
- **Alternatives considered**: Convertir excepciones en listas vacías; mostrar traceback; consultar salud de destinos por visitante.

## Cuotas y rendimiento

- **Decision**: Tres operaciones de lectura, proyección explícita, orden estable, páginas de 100 y plazo global de 6 s sin reintentos inmediatos. Cache-Control no-store para evitar publicaciones retiradas en caché. Servicio Free sin upgrade; indisponibilidad al fallar. Fixtures solo para validación local, nunca fallback público.
- **Rationale**: Limitar tiempo y transferencia sin nueva infraestructura. Revalidar condiciones gratuitas al desplegar; no prometer servicio ilimitado.
- **Alternatives considered**: Redis, copias persistentes obsoletas, upgrades y datos ficticios ante caída.
- **Sources**: [pricing](https://supabase.com/pricing), [changelog](https://supabase.com/changelog). El índice changelog.md no fue legible por el lector web por content-type; se revisó HTML. No se identificó una incompatibilidad que cambie esta arquitectura; revisar nuevamente al fijar versiones.

## Accesibilidad y verificación

- **Decision**: HTML semántico español, skip link, encabezados ordenados, foco visible, texto flexible y sin animaciones necesarias. Escape Jinja, texto editorial plano y contactos tipados. Pytest con fixtures/cliente Flask y prueba RLS separada real; revisión manual de todos los criterios A/AA aplicables además de automatización.
- **Rationale**: Mantiene navegación sin JS. Mocks no acreditan RLS ni una puntuación automática acredita WCAG. Movimiento reducido es requisito explícito del proyecto.
- **Alternatives considered**: HTML editorial confiable, navegación obligatoriamente JS y validación solo con mocks.
- **Sources**: [WCAG 2.1](https://www.w3.org/TR/WCAG21/), [Flask templating](https://flask.palletsprojects.com/en/stable/templating/), [Flask testing](https://flask.palletsprojects.com/en/stable/testing/).

Investigación delegada conforme a la habilidad: contraste independiente de Flask, pruebas, accesibilidad y licencias; conclusiones consolidadas aquí. No quedan clarificaciones técnicas necesarias abiertas. Datos personales pendientes se omiten conforme a spec.
