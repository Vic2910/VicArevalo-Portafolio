# Data model: 001-perfil-publico

Diseño lógico, sin migraciones ejecutadas. Consolidar nombres con 002 antes de implementar edición. Cada instantánea contiene solo campos aprobados; borradores nunca se mezclan con publicación.

## Entidades

| Tabla propuesta | Campos | Validación |
|---|---|---|
| public_profiles | id UUID PK; full_name y degree texto requeridos; summary texto nullable; public_contacts JSON array; published_at timestamptz nullable | Perfil único mediante restricción singleton; identidad confirmada; resumen pendiente se omite; contactos solo autorizados. |
| public_skills | id UUID PK; profile_id FK; name requerido; description nullable; display_order entero; published_at nullable | Capacidades verificadas, sin porcentajes ni niveles inferidos. |
| public_academic_experiences | id UUID PK; profile_id FK; activity requerida; institution nullable; start_date/end_date date nullable; ongoing boolean; description nullable; display_order entero; published_at nullable | end_date >= start_date si ambas existen; ongoing prohíbe end_date. Nunca representa empleo. |

Relaciones: un perfil a muchos conocimientos/actividades. Hijos visibles solo con perfil publicado. Retirar perfil hace ilegibles todos sus hijos en la misma transacción. FK con borrado restringido.

Texto plano con trim; rechazar cadenas vacías y marcadores pendientes al publicar. Presupuestos técnicos iniciales: nombre/carrera/actividad/institución 200 caracteres; resumen 2000; descripción 4000; valor de contacto 2048; máximo 10 contactos. Los formularios futuros compartirán estas reglas. Texto largo válido debe redistribuirse.

public_contacts: objetos {kind, label, value}; kind email/https/phone, etiqueta comprensible requerida. Validar correo, URL HTTPS o teléfono; construir mailto/tel en servidor. No aceptar HTML, javascript ni data. Ausencia = array vacío. Datos privados y evidencia de aprobación no pertenecen a esta tabla.

Fechas pendientes se omiten sin completar día/mes por inferencia. Si solo se conoce año o mes, conservar null hasta ampliar explícitamente el modelo. Fechas aisladas se etiquetan como inicial/final; «Actualidad» solo si ongoing aprobado. Orden de listas: display_order ASC, id ASC.

## Editorial y transiciones

002 definirá borradores, revisiones e identidad autorizada en esquema privado no expuesto, sin USAGE/SELECT público. Flujo conceptual: borrador privado → revisión humana → copia aprobada transaccional a publicación → sustitución aprobada o retirada. Una edición privada conserva la instantánea anterior hasta aprobación. Retirar elimina instantánea o pone published_at null. Ningún visitante o autenticado no administrador puede escribir. No se implementa panel ni aprobación automática en esta feature; fixtures aislados permiten probar publicación.

## Modelos no persistidos

- ResourceResult: state ready/empty/unavailable; data solo para ready; error interno categorizado sin payload privado. Excepción nunca equivale a lista vacía.
- PublicPage: resultados independientes de perfil/conocimientos/experiencia y destinos.
- Destination: key projects/contact/cv; available/unavailable; URL solo cuando disponible, derivada del router y configuración del servidor.

Sin perfil publicado no se muestran hijos. Fallo de una colección conserva los otros recursos válidos. Respuesta estructuralmente inválida produce unavailable y log sanitizado sin payload.
