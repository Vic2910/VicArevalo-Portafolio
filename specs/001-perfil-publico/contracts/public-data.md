# Contract: lectura pública de datos

Flask consume Supabase Data API mediante clave publicable o anon compatible, sin sesión administrativa. Navegador recibe HTML sin SDK. Protección obligatoria también ante consultas directas con clave pública. No crear API JSON propia.

## Adaptador

- get_profile(): cero o un perfil publicado, columnas públicas explícitas. Cero = empty; duplicado o estructura inválida = unavailable.
- list_skills(profile_id): publicaciones de perfil publicado, orden display_order/id; lista completa vacía = empty.
- list_academic_experiences(profile_id): mismo contrato de estados y orden.

Tres operaciones lógicas por petición, colecciones paginadas de 100 hasta última página; sin truncamiento silencioso. Plazo global 6 s, configurable e inyectable; no iniciar llamadas tras agotarlo. Timeout, 429, pausa, error HTTP, configuración ausente o respuesta inválida = unavailable. Sin reintento automático, escritura, GitHub ni IA.

Proyección explícita, nunca select=* en aplicación; filtrar published_at no nulo y profile_id como defensa adicional. No exponer cuerpos del proveedor, claves, URLs sensibles ni traceback.

## Permisos

RLS en todas las tablas expuestas; grants SELECT explícitos para anon y authenticated; políticas solo para publicaciones vigentes. Hijos exigen perfil publicado. Índices FK/orden y unicidad singleton. Sin INSERT/UPDATE/DELETE públicos ni políticas permisivas por mera autenticación. Borradores/datos privados en esquema no expuesto, sin permisos de estos roles. No columnas privadas en filas públicas. Sin vistas que eludan RLS, SECURITY DEFINER ni service_role. Escritura administrativa pertenece a 002.

## Aceptación directa

En proyecto aislado preparar instantánea aprobada, borrador privado, contacto privado y fila retirada con valores centinela sintéticos. Con anon y autenticado no administrador consultar tablas, select=*, UUID conocidos y joins: solo publicaciones aprobadas. Esquema privado inaccesible; mutaciones denegadas o sin filas afectadas. Verificar DB después de intentos, no solo HTTP.

Tras retirar perfil, hijos invisibles incluso por acceso directo. Modificar borrador no altera instantánea. Nunca registrar tokens ni payloads; fixtures no son fallback público. Mocks no acreditan este contrato de permisos.
