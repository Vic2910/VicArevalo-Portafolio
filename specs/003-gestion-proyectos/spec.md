# Feature Specification: Galería y administración de proyectos

**Feature Branch**: `003-proyectos` (referencia del adjunto; no se ha creado una rama, la actual es `main`).

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Mostrar proyectos reales con imágenes, descripción y enlaces, y permitir que Victor los gestione desde el panel."

## Clarifications

### Session 2026-10-27

- Q: Si una imagen se usa en varios proyectos, ¿qué debe ocurrir al reemplazarla desde la edición de uno de ellos? → A: Cambiar solo el proyecto editado; los demás conservan la imagen anterior. El cambio público requiere publicar la nueva versión.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explorar proyectos publicados (Priority: P1)

Como visitante quiero consultar proyectos reales con contexto visual y técnico para conocer el trabajo académico de Victor.

**Why this priority**: La galería ofrece evidencia concreta de sus capacidades sin inventar experiencia profesional.

**Independent Test**: Consultar la galería y una ficha con proyectos publicados de prueba, sin sincronización externa ni asistencia de IA.

**Acceptance Scenarios**:

1. **Given** hay proyectos publicados, **When** abro la galería y una ficha, **Then** veo el orden aprobado, título, descripción, tecnologías e imágenes con alternativas textuales pertinentes.
2. **Given** un proyecto o una imagen pertenecen únicamente a un borrador, **When** intento obtenerlos desde su dirección pública, **Then** no se revela el contenido privado.
3. **Given** no hay proyectos publicados, **When** consulto la galería, **Then** encuentro un estado vacío comprensible sin tarjetas o logros ficticios.
4. **Given** no existe enlace de repositorio o demostración, **When** consulto una ficha, **Then** no aparece una acción vacía ni una dirección inventada.
5. **Given** falla una imagen publicada, **When** consulto la ficha, **Then** conservo acceso a su alternativa textual y al resto del contenido sin controles inutilizables.

---

### User Story 2 - Crear y publicar un proyecto (Priority: P1)

Como Victor quiero preparar proyectos con imágenes autorizadas y revisar su publicación para presentar mi trabajo con precisión.

**Why this priority**: Permite mantener una galería basada en datos reales y aprobados.

**Independent Test**: Con una identidad administrativa de prueba, crear un borrador, adjuntar una imagen válida, completar los campos, revisar y publicar.

**Acceptance Scenarios**:

1. **Given** soy administrador, **When** guardo un proyecto incompleto como borrador y vuelvo a abrirlo, **Then** recupero los datos conservados sin que aparezcan públicamente.
2. **Given** completé los campos obligatorios y revisé autoría y autorización de imágenes, **When** confirmo publicar una versión concreta, **Then** aparece únicamente esa versión aprobada en la galería y ficha.
3. **Given** faltan campos obligatorios, texto alternativo o autorización de uso, **When** intento publicar, **Then** se bloquea la publicación y se señalan los problemas junto a los campos correspondientes.
4. **Given** un archivo tiene formato, contenido o nombre no admitidos, o supera 5 MiB, **When** intento adjuntarlo, **Then** se rechaza sin publicarlo ni sustituir una imagen válida y se explica el motivo.
5. **Given** introduzco un enlace con un esquema distinto de HTTP/HTTPS o contenido destinado a ejecutar instrucciones, **When** guardo o visualizo el proyecto, **Then** el enlace inseguro se rechaza y el contenido no ejecuta esas instrucciones.
6. **Given** soy visitante o una identidad sin permiso, **When** intento crear, modificar, adjuntar imágenes o publicar mediante solicitudes directas, **Then** se deniega la acción sin cambios ni exposición privada.
7. **Given** falla el guardado o la carga de una imagen, **When** termina la operación, **Then** se informa del fallo sin confirmar éxito ni publicar una ficha incompleta.

---

### User Story 3 - Actualizar, ordenar o retirar proyectos (Priority: P2)

Como Victor quiero corregir, ordenar, retirar y eliminar proyectos para mantener la calidad de mi portafolio.

**Why this priority**: Permite controlar la vigencia y presentación de la evidencia publicada.

**Independent Test**: Con proyectos de prueba, preparar una corrección, cambiar el orden, publicar, retirar y eliminar uno comprobando los efectos públicos y las imágenes compartidas.

**Acceptance Scenarios**:

1. **Given** existe un proyecto publicado, **When** guardo una corrección como borrador, **Then** la ficha y la fuente para futuros CV conservan la versión anterior hasta mi confirmación de publicación.
2. **Given** revisé la corrección, **When** la publico, **Then** ficha, galería y fuente para futuras generaciones de CV usan la versión aprobada.
3. **Given** hay varios proyectos publicados, **When** cambio y confirmo su orden, **Then** la galería conserva ese orden al volver a consultarla, sin publicar borradores pendientes.
4. **Given** confirmo retirar un proyecto, **When** consulto galería, antigua dirección y fuente para nuevos CV, **Then** no figura como vigente ni se entrega su ficha; el contenido editorial se conserva privado para una posible republicación.
5. **Given** solicito eliminar un proyecto, **When** cancelo la confirmación, **Then** se conserva; si confirmo, desaparece de la administración y publicación sin eliminar imágenes todavía usadas por otros proyectos.
6. **Given** dos ediciones parten de la misma versión, **When** guardo la segunda después de otra modificación, **Then** recibo una advertencia de conflicto sin sobrescritura silenciosa.
7. **Given** mi sesión caduca o falla la persistencia durante una modificación, **When** intento completarla, **Then** se informa que no se completó y se conserva el último estado confirmado.
8. **Given** varios proyectos comparten una imagen, **When** la reemplazo y guardo el borrador de uno de ellos, **Then** todas las publicaciones conservan la imagen anterior; al confirmar la publicación de la nueva versión, solo el proyecto editado muestra el reemplazo y los demás conservan la imagen anterior.

### Edge Cases

- Sin publicaciones: estado vacío honesto, sin proyectos de muestra presentados como reales.
- Imagen ausente o dañada: alternativa textual y contenido restante utilizable.
- Archivo con extensión engañosa, contenido inseguro, nombre peligroso o tamaño excesivo: rechazo antes de su difusión.
- Exactamente 5 MiB: aceptar si satisface las demás validaciones; más de 5 MiB: rechazar.
- Enlace ausente: omitir la acción. Un enlace externo temporalmente caído no se sustituye por una dirección inventada.
- Imagen compartida: retirar un proyecto no elimina la imagen que otra publicación sigue usando; una imagen exclusiva de un borrador no se vuelve pública.
- Reemplazo de una imagen compartida: modificar únicamente el borrador del proyecto editado; conservar la imagen de las publicaciones vigentes hasta publicar la nueva versión y mantener sin cambios las de los demás proyectos.
- Cuota agotada o almacenamiento indisponible: informar sin activar cargos ni confirmar un guardado inexistente.
- Retirada y borrado: impedir nuevas entregas desde direcciones gestionadas por el sitio; no prometer eliminar copias ya descargadas por terceros.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE conservar proyectos, imágenes asociadas, orden y estados editoriales tras guardar y volver a abrirlos, usando exclusivamente recursos gratuitos (escenarios 2.1 y 3.3).
- **FR-002**: Para publicar DEBE exigir título, descripción, al menos una tecnología y una imagen representativa autorizada con texto alternativo pertinente; repositorio y demostración serán opcionales (escenarios 2.2 y 2.3).
- **FR-003**: Victor DEBE poder crear, editar y guardar borradores sin modificar la versión publicada; publicar requiere confirmar la versión revisada (escenarios 2.1, 2.2 y 3.1).
- **FR-004**: Victor DEBE poder ordenar proyectos y confirmar el orden público sin publicar cambios editoriales pendientes (escenario 3.3).
- **FR-005**: Victor DEBE poder retirar y eliminar proyectos con confirmación explícita de ambas acciones. Retirar conserva el contenido privado; eliminar lo quita de la administración. Cancelar no modifica datos (escenarios 3.4 y 3.5).
- **FR-006**: Galería, fichas y direcciones de imágenes DEBEN mostrar exclusivamente información publicada y autorizada para difusión; borradores y archivos exclusivamente privados no serán accesibles públicamente (escenarios 1.1 y 1.2).
- **FR-007**: Toda modificación y gestión de archivos DEBE comprobar identidad y autorización administrativa, incluso fuera del panel; una sesión identificada sin permiso no concede acceso (escenario 2.6).
- **FR-008**: Solo se DEBEN admitir imágenes JPEG, PNG y WebP cuyo contenido corresponda al formato declarado, hasta 5 MiB inclusive por archivo; deben rechazarse archivos ejecutables, formatos no permitidos y nombres peligrosos antes de publicarlos (escenario 2.4).
- **FR-009**: Los enlaces DEBEN ser direcciones HTTP/HTTPS válidas; títulos, descripciones y direcciones no podrán provocar ejecución de contenido introducido. Enlaces opcionales ausentes no producirán controles vacíos (escenarios 1.4 y 2.5).
- **FR-010**: La galería, fichas y controles administrativos DEBEN cumplir WCAG 2.1 AA, permitiendo explorar, adjuntar, ordenar, publicar, retirar y eliminar mediante teclado, sin depender de hover, color o gestos complejos; errores y cambios de estado serán perceptibles con lector de pantalla (revisión completa de historias 1 a 3 con teclado y lectura asistida).
- **FR-011**: Ningún repositorio DEBE convertirse automáticamente en proyecto publicado. Victor deberá revisar pertinencia, autoría, veracidad y autorización de imágenes antes de publicar; no se inventarán proyectos ni logros (escenario 2.2 y revisión del contenido publicado).
- **FR-012**: Correcciones aprobadas y retiradas DEBEN reflejarse en la fuente de proyectos para futuros CV; las imágenes compartidas todavía referenciadas no se eliminarán al borrar un proyecto (escenarios 3.2, 3.4 y 3.5).
- **FR-013**: Se DEBE confirmar éxito únicamente tras persistir la operación completa; ante fallos, cuota agotada o sesión caducada se informará sin alterar el último estado confirmado ni publicar parcialmente (escenarios 2.7 y 3.7).
- **FR-014**: El sistema DEBE detectar ediciones sobre versiones desactualizadas y evitar sobrescritura silenciosa (escenario 3.6).
- **FR-015**: Reemplazar una imagen compartida DEBE afectar únicamente al borrador del proyecto editado. La imagen de su publicación vigente se conservará hasta confirmar la nueva publicación; las imágenes de los demás proyectos y sus versiones permanecerán sin cambios y sus archivos referenciados no se eliminarán (escenario 3.8).

### Key Entities

- **Proyecto**: identidad estable, título, descripción, tecnologías, enlaces opcionales, posición editorial y estado borrador, publicado o retirado.
- **Imagen de proyecto**: archivo, formato, tamaño, texto alternativo, orden, condición de representativa, autorización de uso y referencias desde proyectos o versiones; un reemplazo cambia solo la referencia del proyecto editado, sin modificar el archivo compartido que otros proyectos o versiones conservan.
- **Versión editorial**: contenido de un proyecto en borrador o aprobado, fecha y aprobación de Victor; permite diferenciar cambios pendientes de una publicación vigente.
- **Publicación**: versión aprobada visible, fecha y vigencia; fuente compartida por galería, ficha y consumidores del CV.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de proyectos publicados evaluados contiene los campos obligatorios e imagen autorizada con alternativa textual pertinente.
- **SC-002**: El 100 % de consultas públicas evaluadas, incluidas direcciones directas de fichas e imágenes, evita revelar borradores y archivos privados; todas las modificaciones sin autorización son rechazadas.
- **SC-003**: El 100 % de archivos evaluados fuera de formatos o límite admitidos se rechaza antes de difundirse; archivos válidos de exactamente 5 MiB superan la validación de tamaño.
- **SC-004**: El 100 % de retiradas confirmadas excluye el proyecto de la galería, ficha y fuente para CV generados posteriormente; las correcciones publicadas aparecen coherentemente en esos consumidores.
- **SC-005**: En todas las pruebas de eliminación y conflicto se conservan imágenes todavía referenciadas y se evitan sobrescrituras silenciosas; cancelar acciones destructivas produce cero cambios.
- **SC-006**: Los flujos completos presentan cero incumplimientos aplicables de WCAG 2.1 A y AA tras revisión automática y manual con teclado y lector de pantalla.
- **SC-007**: Con textos e imágenes preparados, Victor crea, revisa y publica un proyecto sin ayuda externa en un máximo de cinco minutos y puede explicar la diferencia entre guardar borrador y publicar.
- **SC-008**: El 100 % de fallos de carga, persistencia, cuota o sesión evaluados evita publicaciones parciales y confirmaciones falsas de éxito.
- **SC-009**: En el 100 % de reemplazos de imágenes compartidas evaluados, guardar el borrador modifica cero imágenes públicas; publicar cambia solo la imagen del proyecto editado y conserva las imágenes y los archivos referenciados por los demás proyectos.

## Assumptions

- Las operaciones editoriales dependen de `002-administracion`. La lectura pública puede evaluarse con publicaciones aisladas y la integración con CV con un consumidor controlado.
- Victor aportará proyectos reales e imágenes con autorización de uso y verificará su autoría y pertinencia. No se generarán logros ni datos ficticios para completar fichas.
- Se conserva el límite inicial propuesto de 5 MiB por archivo como supuesto de esta especificación, sujeto a validación de Victor antes de implementar según la cuota gratuita. Los límites agregados y medidas de uso eficiente se concretarán durante planificación.
- Se admite más de una imagen por proyecto con orden explícito y una representativa; toda imagen informativa requiere texto alternativo pertinente.
- El orden público se modifica mediante confirmación separada de publicar contenido. No se incluyen filtros, buscador, comentarios, importación automática, historial restaurable ni generación del CV en esta funcionalidad.
- Retirar permite volver a preparar una publicación mediante el mismo proceso de revisión. Eliminar requiere confirmación; no se exige recuperación posterior. Los archivos sin referencias podrán limpiarse sin afectar proyectos activos.
- El retiro afecta las nuevas entregas bajo control del sitio y las futuras generaciones de CV; no elimina documentos o imágenes que terceros descargaron antes.
- La constitución del proyecto 1.0.0 en `.specify/memory/constitution.md` conserva su autoridad sobre arquitectura, persistencia, almacenamiento, permisos, gratuidad y pruebas. Sus decisiones técnicas se concretarán en planificación sin enmendarlas aquí.
- Los criterios de aceptación son objetivos, no resultados ya verificados. La evaluación usará datos aislados, roles representativos y revisión manual de accesibilidad sin modificar publicaciones reales.
