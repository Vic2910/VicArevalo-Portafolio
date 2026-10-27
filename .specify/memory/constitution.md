<!--
Sync Impact Report
- Versión: plantilla sin ratificar → 1.0.0 (adopción inicial de la línea base).
- Principios incorporados:
  I. Accesibilidad verificable: WCAG 2.1 AA.
  II. UI/UX universal y representación honesta.
  III. Calidad verificable con Pytest.
  IV. Recursos exclusivamente gratuitos y datos protegidos.
  V. Simplicidad y arquitectura mantenible.
- Secciones incorporadas: Restricciones funcionales, técnicas y de seguridad;
  Proceso de calidad y criterios de aceptación; Governance.
- Secciones eliminadas: ninguna obligación previa; se sustituyó la plantilla sin ratificar.
- Pendientes intencionales: todos los marcadores de «Información pendiente» representan
  datos personales, contenido aprobado, conservación de mensajes y configuración externa
  aún no definidos. Se conservan por instrucción del propietario; no son huecos normativos.
  Nunca se completarán con secretos en este documento ni se mostrarán al público.
- Revisión humana: retirar este informe temporal antes de confirmar el documento en Git.
-->

# Portafolio personal de Victor Rafael Arévalo Sierra Constitution

## Core Principles

### I. Accesibilidad verificable: WCAG 2.1 AA

El sitio público y el panel administrativo DEBEN cumplir todos los criterios aplicables de los niveles A y AA de WCAG 2.1. La accesibilidad es una condición de aceptación desde el diseño, no una mejora posterior. Se exige HTML semántico, jerarquía coherente de encabezados, nombres accesibles, textos alternativos pertinentes, etiquetas explícitas y errores asociados a los campos. Toda función debe poder utilizarse con teclado, sin trampas de foco, con foco visible y orden lógico; los cambios de estado deben comunicarse a tecnologías de asistencia.

El contraste mínimo será 4.5:1 para texto normal y 3:1 para texto grande; los componentes y elementos gráficos necesarios cumplirán el contraste no textual aplicable de 3:1. El color nunca será el único medio de información. Se admitirán ampliación del texto al 200 %, redistribución a 320 píxeles CSS sin pérdida de funcionalidad y orientación flexible, salvo excepciones justificadas del estándar. Se respetará la preferencia de movimiento reducido. La conformidad requiere evaluación automática y revisión manual con teclado y lector de pantalla; una puntuación automática no acredita por sí sola el cumplimiento.

Referencia normativa: WCAG 2.1, W3C.

### II. UI/UX universal y representación honesta

El diseño DEBE ser profesional, moderno, adaptable y comprensible para personas con distintas capacidades, dispositivos y niveles de experiencia. Se aplicarán jerarquía visual, consistencia, legibilidad, reconocimiento sobre memorización, prevención de errores y retroalimentación clara. La navegación, los botones y los formularios tendrán comportamientos previsibles; los estados de carga, vacío, éxito y error ofrecerán instrucciones útiles. Ninguna animación ni decoración podrá impedir leer, navegar o completar una tarea.

La identidad pública será Victor Rafael Arévalo Sierra, estudiante de Ingeniería en Desarrollo de Software, actualmente sin experiencia profesional. La experiencia académica se distinguirá de cualquier experiencia laboral futura. Los conocimientos declarados deberán corresponder a capacidades verificadas por Victor; se prohíben porcentajes arbitrarios de dominio, logros, empleos, certificaciones o testimonios inventados. La IA no podrá publicar ni elevar el nivel de una afirmación sin revisión humana. El portafolio y el CV compartirán una fuente de información aprobada.

### III. Calidad verificable con Pytest

Toda modificación funcional DEBE contar con validación proporcional al riesgo mediante Pytest. La cobertura obligatoria comprende lógica de negocio, rutas públicas y administrativas, autenticación y autorización, validación y persistencia del contacto, generación del CV en español e inglés y capa de acceso a Supabase. Se verificarán escenarios satisfactorios, entradas inválidas, accesos denegados y fallos de dependencias externas.

Las comprobaciones usarán mocks controlados o datos aislados de prueba; nunca mensajes reales, credenciales productivas ni modificaciones de datos públicos. Los mocks no bastan para acreditar políticas RLS: su eficacia deberá verificarse adicionalmente en un entorno de prueba con roles representativos. El CV requerirá validación de contenido, idioma y extracción de texto. Pytest complementará, sin sustituirlas, las revisiones manuales de accesibilidad y presentación. Ningún cambio se aceptará con fallos pendientes en verificaciones obligatorias. Esta constitución establece obligaciones de calidad; no contiene implementaciones ni casos de prueba.

### IV. Recursos exclusivamente gratuitos y datos protegidos

Se prohíben componentes de pago: hosting, APIs, base de datos, almacenamiento, IA, dominio, fuentes, imágenes, bibliotecas y generación de PDF. Supabase se utilizará exclusivamente en su capa gratuita. Se utilizará un subdominio gratuito cuando corresponda. No se admitirán pruebas temporales de pago, créditos promocionales como dependencia permanente, sobrecostes automáticos ni servicios que requieran activar facturación. Cada dependencia debe tener licencia compatible y condiciones gratuitas comprobadas al seleccionarla.

Los límites gratuitos se tratarán como restricciones reales: se limitarán consultas, tamaño de archivos y frecuencia de sincronización. Al agotarse una cuota, el sistema deberá informar y degradar la función afectada sin activar cargos. No se prometerá disponibilidad ilimitada. Una alternativa local o gratuita deberá preservar las funciones esenciales dentro de los recursos disponibles.

Supabase requiere mínimo privilegio, RLS y separación entre contenido público y datos privados. Las claves secretas o privilegiadas, incluida service_role, SOLO podrán existir en el backend y nunca en el navegador, repositorio, PDF, registros o mensajes de error. El uso de una clave privilegiada exige autorización explícita en el servidor porque puede eludir RLS. Referencias oficiales: claves de API y protección de datos.

### V. Simplicidad y arquitectura mantenible

La aplicación será un monolito modular en Python con Flask, plantillas Jinja y mejora progresiva mediante JavaScript solo donde aporte valor. Flask se elige por su alcance reducido y adecuado para un portafolio con formularios, sesiones y administración renderizada en servidor; permite evitar una SPA y servicios separados innecesarios. Las responsabilidades de presentación, negocio y acceso a datos deberán estar diferenciadas sin imponer capas sin utilidad.

Supabase, basado en PostgreSQL, será la base de datos única para contenido, proyectos, mensajes y datos sincronizados de GitHub. Supabase Auth administrará la identidad del administrador. La generación de PDF se realizará en el backend con una biblioteca libre y gratuita, como ReportLab, mediante un documento textual de una sola columna. Las decisiones deberán favorecer comprensión, mantenimiento y uso eficiente de la capa gratuita. Cualquier cambio de framework o incorporación de infraestructura adicional requiere justificación y aprobación conforme a Governance.

## Restricciones funcionales, técnicas y de seguridad

**Contenido y administración.** La presentación incluirá nombre, carrera y perfil breve aprobado; los conocimientos y la experiencia académica serán editables. La galería permitirá administrar proyectos con título, imágenes con texto alternativo, descripción, tecnologías y enlaces válidos a repositorios o demostraciones cuando existan. Se distinguirán borradores y publicaciones. El administrador podrá editar contenido, gestionar proyectos e imágenes y consultar, marcar y eliminar mensajes; toda operación administrativa requerirá autenticación y autorización comprobadas en el backend.

**Contacto y privacidad.** El formulario recopilará únicamente nombre, correo de respuesta y mensaje, con aviso claro de finalidad. El éxito solo se mostrará después de confirmar la persistencia en Supabase. Se exigirán validación en servidor, límites de longitud y frecuencia, defensa contra spam accesible y protección CSRF cuando corresponda. Los mensajes no serán consultables por visitantes ni enviados a la IA. Victor deberá definir una política de conservación y eliminación antes de habilitar el formulario; no habrá retención indefinida por defecto. El envío de correo o una notificación externa no será requisito para recibir mensajes.

**Acceso a Supabase.** Las tablas expuestas deberán tener RLS habilitada y permisos mínimos: lectura anónima únicamente del contenido publicado; escritura de contenido y lectura de mensajes exclusivamente para el administrador autorizado. El contacto se procesará en el backend sin conceder lectura pública ni acceso anónimo general a los mensajes. Estar autenticado no equivaldrá a ser administrador: la autorización se basará en una identidad aprobada y un rol no modificable por el cliente. Las políticas de Storage seguirán la misma separación para imágenes públicas y archivos privados. Las claves publicables o anon no otorgarán privilegios por sí mismas y, si se exponen, dependerán de políticas efectivas.

Los secretos se gestionarán mediante configuración externa protegida; deberán poder rotarse y no se documentarán valores reales en esta constitución. Las sesiones utilizarán cookies HttpOnly, Secure y SameSite apropiado, caducidad y cierre de sesión efectivo. Se exigirán HTTPS, protección contra intentos repetidos de acceso, escape de contenido, consultas parametrizadas y validación de archivos por formato, tamaño y contenido. No habrá registro público de administradores. Los registros excluirán credenciales y contenido privado de mensajes.

**IA asistida.** El panel integrará un modelo local con licencia compatible y sin coste de uso para sugerir redacciones, descripciones y traducciones a partir de datos suministrados por Victor. Un proveedor remoto solo será admisible si cumple el principio de gratuidad y sus condiciones de privacidad son aprobadas. Las sugerencias serán borradores identificables, revisables y descartables. No se enviarán secretos ni datos de visitantes. La ausencia del modelo o de recursos suficientes nunca bloqueará la edición manual, publicación o generación del CV con textos ya aprobados.

**GitHub y métricas.** El backend consultará la API REST pública de GitHub para el perfil Vic2910, sus repositorios públicos y commits accesibles. Implementará paginación, consultas condicionales cuando proceda, caché persistida en Supabase y deduplicación por repositorio y SHA. Se identificarán los commits atribuibles a Vic2910; el autor de un commit ajeno en un repositorio propio no se contará automáticamente como Victor. Las métricas explicarán su período, repositorios, ramas y alcance, sin presentar una consulta parcial como el historial total ni equiparar commits con experiencia profesional.

Se respetarán las cabeceras de cuota y reintento, los límites primarios y secundarios, con espera progresiva y suspensión temporal ante restricciones. No se evadirán cuotas ni se hará una consulta por visitante. Si se utiliza un token de lectura, permanecerá en el backend con permisos mínimos. El dashboard leerá desde Supabase cantidades de proyectos, commits sincronizados y mensajes totales y pendientes, con fecha de última sincronización y advertencias de datos incompletos. Una caída de GitHub conservará los últimos datos válidos y mostrará su antigüedad; los errores no se representarán como conteos cero. Referencias: límites REST y buenas prácticas.

**CV actualizado y ATS.** El visitante podrá elegir español o inglés y descargar un PDF generado desde la última información publicada y aprobada del portafolio. Se conservarán variantes lingüísticas revisadas; faltantes de traducción se resolverán antes de ofrecer el idioma correspondiente, sin traducciones improvisadas ni mezcla silenciosa de idiomas. La IA no será una dependencia obligatoria para descargarlo.

El CV seguirá convenciones sobrias de modelos universitarios como Harvard u Oxford: encabezados textuales claros, datos de contacto autorizados, perfil breve, educación, habilidades y proyectos o experiencia académica pertinente. Se omitirá una sección de empleo mientras no exista experiencia profesional. El documento tendrá una sola columna, orden de lectura lineal, fuentes legibles y texto seleccionable y extraíble; no contendrá tablas, gráficos, barras de habilidad, imágenes de texto ni información esencial en encabezados o pies que dificulte el análisis automático. Los títulos y secciones tendrán significado claro en cada idioma. No se afirmará afiliación institucional ni compatibilidad garantizada con todos los ATS. La generación no utilizará servicios PDF de pago ni publicará mensajes privados, borradores o campos incompletos.

**Información pendiente.** Victor completará: [CORREO_PUBLICO], [UBICACION_PUBLICA_OPCIONAL], [PERFIL_PROFESIONAL_APROBADO], [INSTITUCION_EDUCATIVA], [FECHAS_ACADEMICAS], [CONOCIMIENTOS_VERIFICADOS], [PROYECTOS_REALES_E_IMAGENES_AUTORIZADAS], [TEXTOS_APROBADOS_ES_EN] y [PLAZO_DE_CONSERVACION_DE_MENSAJES]. La configuración externa requerirá [SUPABASE_URL], [SUPABASE_CLAVE_PUBLICABLE], [SUPABASE_SECRETO_BACKEND_SI_ES_NECESARIO] y [IDENTIDAD_ADMIN_AUTORIZADA]; estos marcadores nunca se sustituirán por secretos dentro del documento. Los pendientes se mostrarán solo en administración o documentación interna: se ocultarán en el sitio y CV hasta completarse. Ningún dato faltante se inventará.

## Proceso de calidad y criterios de aceptación

Antes de desarrollar una función se definirán su propósito, datos utilizados, permisos, estados de interacción y criterio de aceptación. Las decisiones sobre dependencias registrarán licencia, gratuidad, cuotas y alternativa ante indisponibilidad. Las modificaciones de acceso a datos requerirán revisión de permisos y compatibilidad con la información existente.

Toda revisión verificará los cinco principios, alcance funcional, protección de secretos, ausencia de contenido inventado y funcionamiento bajo fallos externos. Los cambios de contenido exigirán aprobación de Victor antes de publicarse. Los cambios funcionales deberán superar las verificaciones Pytest aplicables y una revisión visual y accesible de los flujos afectados. No bastará con que una ruta responda: deberán respetarse los permisos y mantenerse la integridad de los datos.

La aceptación del proyecto exige que el sitio y el panel cumplan WCAG 2.1 AA en sus páginas y flujos completos; que el contacto persista y permanezca privado; que las acciones administrativas rechacen usuarios no autorizados; que los datos de GitHub se interpreten con alcance y fecha visibles; y que ambos CV representen el contenido aprobado en el idioma solicitado con extracción de texto coherente. Se revisarán estados vacíos y de error, uso móvil y de escritorio, navegación por teclado y lectura asistida. No podrán aceptarse defectos abiertos de seguridad, privacidad o accesibilidad que incumplan esta constitución.

Este documento fija reglas y criterios; quedan fuera de esta entrega el código de aplicación, el árbol detallado de carpetas, las pruebas implementadas y las instrucciones de despliegue.

## Governance

Esta constitución es la autoridad normativa del proyecto y prevalece sobre preferencias de implementación, sugerencias de IA y decisiones no aprobadas. Victor Rafael Arévalo Sierra es propietario y autoridad final sobre alcance, contenido y decisiones técnicas. La persona responsable de arquitectura propondrá alternativas y documentará sus consecuencias; si no existe una designación distinta, Victor asumirá también esa responsabilidad. La IA podrá asesorar, pero no aprobar cambios ni sustituir la revisión humana.

Toda propuesta y revisión deberá identificar los principios afectados y aportar evidencia proporcional de cumplimiento. Una decisión contraria a la constitución será bloqueada hasta corregirse o tramitarse una enmienda explícita; no existen excepciones tácitas por urgencia o conveniencia. Los cambios que afecten autenticación, políticas RLS, secretos, privacidad, costes o CV requerirán revisión específica de sus impactos. Ante desacuerdo se conservará la última decisión conforme y aprobada mientras Victor resuelve.

Las enmiendas deberán documentar motivo, redacción anterior y propuesta, alternativas, impacto sobre datos y funciones, riesgos y medidas de adaptación. Victor deberá aprobarlas expresamente antes de su vigencia. Ninguna enmienda podrá introducir experiencia o logros falsos. Levantar la exclusividad de recursos gratuitos o reducir la accesibilidad mínima requerirá además un cambio explícito del alcance solicitado por el propietario; nunca se inferirá autorización para contratar servicios.

La versión seguirá MAJOR.MINOR.PATCH: MAJOR para cambios incompatibles o eliminación de obligaciones; MINOR para nuevos principios, obligaciones o ampliaciones sustanciales; PATCH para aclaraciones sin alterar obligaciones. Cada enmienda actualizará la versión y la fecha Last Amended y conservará su historial de aprobación. Ratified conservará la fecha de adopción inicial. Esta versión inicial constituye la línea base del proyecto.

**Version**: 1.0.0 | **Ratified**: 2026-10-27 | **Last Amended**: 2026-10-27
