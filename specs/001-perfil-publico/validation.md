# Validación de 001-perfil-publico

Fecha local: 2026-10-27. Base Git: `29733036b92c20bce3d1d7d6409bb418184f6d47`; implementación aún sin commit. Estado: **implementación local verificable, aceptación incompleta**.

## Autorización y fidelidad SDD

Victor autorizó continuar con las dos excepciones documentadas del checklist de requisitos. El checklist permanece intacto. No se alteraron spec, plan ni constitución. Los nombres de migración propuestos en tareas se sustituyeron por los generados por la CLI: `20261028003054_public_profiles.sql` y `20261028003106_public_collections.sql`. Su fecha UTC corresponde al 27 de octubre local.

## Entorno y resultados

- Windows / PowerShell; CPython 3.12.15 instalado con uv; versiones exactas y hashes en requirements.lock y uv.lock.
- Suite inicial: fallo de importación de create_app antes de implementación. Se escribieron también pruebas de colecciones antes de su implementación; no se registró una ejecución roja separada de cada historia. Esto es una limitación de la evidencia TDD, no una prueba retroactiva.
- Suite consolidada anterior a las últimas pruebas adicionales: **67 passed** con cuatro casos RLS reales incluidos. Resultado final: **76 passed en 4.17 s**, incluidos cuatro casos RLS; sin skips con entorno aislado configurado.
- Sin variables de integración, los cuatro casos RLS se omiten explícitamente. Las pruebas unitarias y de contrato bloquean conexiones de red.
- PostgreSQL 17 real en clúster nuevo `.postgres-test`, puerto local 55432, separado del servicio preexistente. Migraciones aplicadas mediante bootstrap local; anon y authenticated son roles NOLOGIN sin bypassrls. Fixtures sintéticos en transacción y rollback final.
- RLS PostgreSQL: **4 passed**. Lectura publicada, mutaciones denegadas, comprobación posterior de filas, privados inaccesibles, edición privada que conserva instantánea y retirada del padre que oculta hijos. Esto NO acredita todavía el esquema expuesto/JWT/joins a través de PostgREST de Supabase.
- SDK supabase-py real con MockTransport: GET/proyección/filtro, errores 401/429/500, una llamada sin reintentos y sin payload del proveedor en resultados.
- Navegador Chrome + Playwright: 12 escenarios, sin desbordamiento a 320 px ni al 200 % de texto y espaciado ampliado; enlace de salto enfoca contenido. Movimiento reducido y prueba separada sin JavaScript. axe sin violaciones A/AA en los escenarios evaluados. Evidencia: `evidence/browser-audit.json`, `evidence/desktop.png`, `evidence/mobile.png`.

## Trazabilidad

| Requisitos | Evidencia | Límite |
|---|---|---|
| FR-001/003/007, SC-001 | test_public_profile, test_profile_repository, test_sdk_transport, test_profile_rls | Falta API real Supabase y aprobación de contenido |
| FR-002/005/007, SC-004 | test_public_collections, test_collections_repository, test_validation, test_collections_rls | Falta API real y verificación completa de fechas/centinelas por HTTP |
| FR-004, SC-004 | Matriz de endpoints/capacidades y variante CV aprobada | Solo endpoints locales controlados; módulos 003–005 ausentes |
| FR-005/006/008, SC-002/003 | Contratos HTML, axe, navegador, capturas, accessibility.md | Falta NVDA y revisión humana completa |

No-store está probado para perfil ready/empty/unavailable. El adaptador no escribe, no entrega listas parciales y comparte presupuesto monotónico entre operaciones/páginas. Se prueban 101 registros, fallo de página posterior y agotamiento del presupuesto. No se probó latencia real del proveedor ni cuotas reales. Los timeouts de socket acotan fases de E/S; DNS y planificación del sistema no permiten prometer un corte duro exacto a los 6 segundos.

Se comprueban centinelas en HTML/resultados/logs controlados y privacidad en DB. No hay SDK navegador, API JSON propia, service_role ni datos reales de Victor como fallback. La vista sintética vive exclusivamente en tests/preview.py y exige una ejecución explícita separada de app:create_app.

## Pendientes que bloquean aceptación

1. Ejecutar API real de Supabase aislada con clave publicable y JWT de autenticado no administrador: select=*, UUID conocidos, joins, esquema privado, escrituras sin efecto y verificación posterior en DB.
2. Completar revisión humana de todos los criterios aplicables, teclado completo y NVDA; ver accessibility.md.
3. Confirmar contenido, capacidades, contactos y variantes futuras antes de activar información real. No hay despliegue ni publicación en esta entrega.

No existe `.specify/extensions.yml`: no hay hooks previos ni posteriores registrados. Las tareas que incluyen pruebas pendientes permanecen sin marcar aunque su código esté preparado.

## Cierre de ejecución

- CLI Supabase 2.122.0; Chrome 156.0.8078.48; axe-core 4.14.0.
- 76 pruebas Pytest aprobadas; 12 escenarios Chrome/axe sin violaciones detectadas; escenario sin JavaScript aprobado.
- pyproject.toml y supabase/config.toml analizados correctamente con tomllib. git diff --check sin errores (solo aviso de normalización LF/CRLF).
- 29/35 tareas marcadas; T009/T013/T023/T026/T034/T035 abiertas según límites documentados. Los validadores SQL no conceden EXECUTE a lectores; no se expone una RPC adicional de validación.
- No se hizo commit, push ni despliegue. Se detuvieron las herramientas temporales después de la evaluación.
