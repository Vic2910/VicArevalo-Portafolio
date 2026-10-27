# Contract: asistencia editorial HTTP y revisión activa

Solo administración con guard 002 vigente en cada solicitud, consulta de estado técnico y aceptación. HTTPS, CSRF/origen en POST, no-store/CSP/headers 002, JSON/HTML escapado. Ningún endpoint público de chatbot ni endpoint para recuperar propuestas antiguas.

## Rutas propuestas

| Ruta | Contrato |
|---|---|
| GET /admin/asistencia/disponibilidad | Estado/configuración segura de modalidad local, límites y causa de indisponibilidad; nunca carga modelo o inicia generación. |
| POST /admin/asistencia/revisiones | target_kind/id/field permitido; crear nuevo editor_nonce y cerrar revisión anterior del mismo admin/campo. Sin fuente/contexto almacenados. |
| POST /admin/asistencia/revisiones/<nonce>/previsualizar | purpose, selección/contexto, source_ref/version, target/digest/rangos e idioma; verificar y devolver preview exacto/proof, sin inferencia. |
| POST /admin/asistencia/revisiones/<nonce>/generar | Mismo contenido confirmado y preview_token+request_id; revalidar guard/límites/privacidad, admitir una generación local y devolver resultado una vez. No streaming de tokens ni guardado editorial. |
| POST /admin/asistencia/revisiones/<nonce>/latido | Solo nonce/estado técnico; renovar revisión activa dentro de sesión, nunca extender sesión administrativa por polling. |
| POST /admin/asistencia/revisiones/<nonce>/cancelar | Invalidar request/epoch, abortar proceso correspondiente y devolver cancelación lógica sin cambiar texto guardado. |
| POST /admin/asistencia/revisiones/<nonce>/descartar | Limpiar propuesta cliente y cerrar request técnico; sin modificación editorial. |
| POST /admin/asistencia/revisiones/<nonce>/cerrar | Cierre explícito o pagehide best-effort; invalidar requests. Nueva apertura no depende de que este aviso haya llegado. |
| POST /admin/asistencia/revisiones/<nonce>/aceptar | Proof de propuesta vigente, final_value editado, expected_revision/version, operation_id, confirmación explícita y CSRF; guardar solo borrador del campo, responder éxito después de commit. |
| GET /admin/asistencia/operaciones/<operation_id> | Recibo técnico propio de aceptación, sin texto original de sugerencia; no reconstruye propuesta. |

Generar devuelve 200 solo con propuesta completa no aprobada o needs_information, nunca actualización de contenido. Incompleta/truncada 422 o error 502, sin propuesta aceptable parcial. Respuesta incluye fuente/proof ya confirmados, idioma declarado, request/epoch y aviso de revisión de hechos; no llama publicación ni aprobación 005.

Validar retorno de esquema acotado:status suggestion/needs_information, language es/en, text y missing_information opcional. Campos de acciones/tools/URLs de ejecución se rechazan o tratan como texto no ejecutable; ningún tool call se procesa. Etiqueta language del modelo no demuestra idioma correcto:Victor lo revisa/corrige o descarta.

## Entrada y privacidad

Solo campos/ref permitidos de modelo; fuente/contexto visibles y corregibles antes de confirmar. No contexto de bandeja/configuración/GitHub ni lectura automática de todo perfil. Credenciales/PEM/JWT/formato de claves identificados, emails/contactos pegados no pertinentes o source_kind no permitido se bloquean antes de transmitir; mensaje genérico, sin eco de secreto en error/log.

Límites visibles:fuente 1500 caracteres, contexto 500, prompt serializado 3072 bytes, respuesta 4000 caracteres/16 KiB, deadline 60 s, una generación y frecuencia 6/10 min por admin+20/h global. No truncar automáticamente; orientar a seleccionar fragmento menor sin inventar hechos. Requests<=64 KiB, sin adjuntos. Preview inválido no consume una generación.

## Estados y errores

Sin sesión/caducada 401; sin permiso 403; CSRF 400/origen ajeno 403; fuente/target inexistente 404; límites/formato o datos no permitidos 422; longitud HTTP 413; revisión/source/field digest cambiado 409. Frecuencia 429 con Retry-After y espera comprensible, sin texto perdido. Modelo/binario/checksum/hardware ausente 503 con edición manual disponible; timeout 504/cancelación estado cancelado, nunca fallback remoto.

Revalidar identidad/autoridad antes de enviar y antes de entregar salida; sesión vencida/revocada en curso destruye/descarta respuesta, no la devuelve sin guard. Si DB/guard no verificables, no inferir ni aceptar. Actualización de campo después del preview/generación señala stale y no sobrescribe. Respuesta tardía de cancelado/nonce viejo se ignora en servidor y cliente, aunque haya terminado físicamente.

Aceptación guarda solo final_value del campo bajo validaciones 002/003/005 y lock_version; fallos conservan última revisión confirmada, sin publicar ni repetir tras login. Commit incierto consulta recibo de aceptación, no regenera ni recupera salida. Doble operación/cuerpo igual retorna recibo, distinto 409. Traducir/aceptar no cambia estado aprobado 005 ni disponibilidad CV, salvo efectos normales posteriores de publicación explícita fuera de 007.

## Interfaz y ciclo del documento

Comparación fuente/propuesta con encabezados/labels y textarea de propuesta editable; estado «Sugerencia no aprobada» siempre visible. Acciones «Generar propuesta», «Aceptar como borrador», «Descartar» y «Cancelar generación» claramente distintas de «Publicar». No aplicar al llegar, cambiar campo original ni deshabilitar edición manual por inferencia.

JS pequeño gestiona fetch/AbortController, nonce y digest enRAM; no framework o almacenamiento persistente. Nueva página, pagehide y restauraciónBFCache limpian propuesta/contexto IA no aceptado, invalidan revisión y registran nonce nuevo antes de usar resultado. No estado en URL/hiddenfield serializado para recuperar tras recarga. No GET de salida ni POST automático que regenere al recargar. Si JS no disponible, explicar IA indisponible y mantener editor manual/publicación/CV completos.

Todos los controles operables con teclado/lector; foco visible y orden lógico, status de generación/cancelación/error sin lectura intrusiva de cada token, sin modal/hover/drag obligatorio. No mover foco inesperadamente al recibir respuesta; resumen de errores asociado a campos. Texto 200 %,320 px CSS, espaciado, contraste, movimiento reducido y auditoría de todos los criterios WCAG 2.1 A/AA aplicables. Con propuesta preparada, estado y aceptación/descarte distinguibles en<1 min.
