# Contract: página pública y navegación

GET /: text/html UTF-8, lang=es, título comprensible, un h1, header/nav/main/footer y Cache-Control no-store. Solo lectura; configuración inválida no impide renderizar indisponibilidad.

| Condición | HTTP y presentación |
|---|---|
| Perfil aprobado | 200, nombre/carrera confirmados; resumen/contactos solo aprobados. |
| Perfil sin publicación | 200, título genérico y «Perfil aún no disponible»; sin identidad fallback ni hijos. |
| Fallo del perfil | 503, título genérico y «No podemos mostrar el perfil en este momento. Inténtalo más tarde.»; sin hijos ni detalles internos. |
| Colección publicada con perfil válido | 200, sección ordenada y ancla real. |
| Colección vacía o solo borradores | Omitir sección y enlace, sin mensaje vacío ni marcadores. |
| Fallo de colección con perfil válido | 200, resto válido visible; sección con encabezado, explicación accesible y ancla hacia ella. |

Identificadores: contenido (main), perfil, conocimientos, experiencia-academica. Solo enlazar secciones renderizadas. Texto editorial escapado, nunca safe. Sin porcentajes ni sección laboral.

## Destinos futuros

Proyectos (003), contacto (004), CV (005) registrarán endpoint y capacidad disponible en servidor. Resolver URL por router solo si ambos existen. Por defecto todos no disponibles; mostrar etiqueta y «No disponible por ahora» sin href, tabindex ni botón falso. No inventar rutas. Cuando disponible, destino debe corresponder al anuncio y pasar prueba de navegación. CV disponible significa al menos una variante aprobada ofrecida por 005. Tests pueden registrar endpoints de prueba sin implementar otras features. No consultar salud externa por visitante.

## Accesibilidad

Skip link al main; encabezados ordenados; nombres claros; teclado completo, foco visible y sin trampas ni controles solo hover. Layout flexible, URLs con wrapping y sin alturas fijas que recorten. Texto normal 4.5:1, grande 3:1 y elementos no textuales necesarios 3:1. Estado no depende de color. Respetar movimiento reducido y funcionamiento sin JS.

Errores iniciales se comunican por título, encabezado y texto; no depender de aria-live ya renderizado. Si se añaden cambios dinámicos, anunciar mediante región status pertinente. Auditar todos los criterios A/AA aplicables, no solo estos ejemplos.
