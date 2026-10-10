# Informe técnico INC-4092: Falla en la generación de escrituras notariales

**Servicio:** `document-rendering-service` · **Severidad:** P1 · **Estado:** corrección lista, pendiente de despliegue
**Fecha:** 09-10-2026 22:34 · **Autor:** Richard Morales

## 1. Resumen

El 14 de octubre de 2024, la generación de poderes notariales respondió HTTP 500 a los clientes que no tenían estado civil o profesión u oficio. La causa es que la API acepta esos campos como opcionales, pero el renderer los exige. Como el pago se registra antes de generar el documento, los clientes quedaron con el cargo hecho y la escritura en `FAILED`. Soporte reporta 14 casos.

La corrección hace que el renderer escriba "no informado" en esos campos. Pasa los 11 tests de la suite y está pendiente de despliegue. La sección 5 explica cómo volver a generar las escrituras fallidas.

## 2. Evidencia

| Hora (log) | Documento | Pago | Resultado |
|---|---|---|---|
| 08:45:11 | DOC-2024-8835 | tx_pay_902140 | OK |
| 09:12:15 | DOC-2024-8841 | tx_pay_902148 | `KeyError: 'estado_civil'` |
| 09:18:42 | DOC-2024-8845 | tx_pay_902151 | OK |
| 09:35:04 | DOC-2024-8849 | tx_pay_902155 | `KeyError: 'profesion_oficio'` |

Fuente: `logs/rendering_errors.log`, líneas 1 a 8.

- **El log está incompleto.** Solo registra 2 de los 14 casos; por ejemplo, no aparecen `DOC-2024-8853` ni `DOC-2024-8858`. La fuente confiable es la tabla `notarial_deeds`.
- **Los tests ya mostraban el error.** En `main`, 3 de los 7 tests fallan con este mismo error.

## 3. Causa raíz

El error se produce en tres pasos:

1. `app/schemas.py:13-14`: `estado_civil` y `profesion_oficio` son opcionales (`str | None = None`).
2. `app/routers/documents.py:27`: `model_dump(exclude_none=True)` quita los campos nulos. Por eso, aunque el cliente los envíe como `null`, el diccionario llega sin ellos.
3. `app/services/renderer.py` (líneas 42 y 43, antes del cambio): se leían con `client_data["estado_civil"]`, lo que provoca un `KeyError` cuando el campo falta.

El `KeyError` solo nombra el primer campo que falta. Como `estado_civil` se revisa primero, un cliente sin ninguno de los dos aparece en el log solo con `estado_civil`.

**Factores que aumentaron el impacto:**

- **El pago se registra antes de validar los datos.** `document_service.py:46-56` guarda la escritura con `payment_status="COMPLETED"` antes de generar el documento. Ese valor está escrito a mano y no se verifica, aunque el docstring dice que sí. Si la generación falla, queda una escritura `FAILED` con el pago ya cobrado.
- **Un problema de datos responde como error interno.** El cliente recibe un 500 cuando debería recibir un 4xx antes de pagar.
- **No hay protección contra duplicados.** `payment_id` no es único: cada reintento crea un registro nuevo con otro código, y los `FAILED` se van acumulando.
- **No hay CI.** El repositorio no tiene pipeline, y los tests que mostraban este error estaban fallando en `main` sin que nadie lo notara.

## 4. Solución implementada

En `app/services/renderer.py` se agregó la constante `NO_INFORMADO` y la función `_value_or_not_informed(client_data, key)`. La función devuelve "no informado" si el campo falta, es `None`, es `""` o tiene solo espacios; si no, devuelve el valor. Aplica a las plantillas `PODER_ESPECIAL` y `PODER_GENERAL`. El schema, el router y `document_service` no cambian.

**Tests:**
- 2 tests existentes ahora verifican que aparezca "no informado".
- 4 tests nuevos cubren: texto vacío o solo con espacios, valores presentes, `PODER_GENERAL` y envío de `null` explícito por la API.

| | Antes | Después |
|---|---|---|
| Suite de tests | 3 fallan, 4 pasan | 11 pasan |

**Decisión de negocio:** se acepta emitir con "no informado". Aprobado por Constanza Arrau.
**Estado:** el cambio está en la PR #1

**Problemas conocidos que esta corrección no cubre:**
- **Nacionalidad:** el campo no existe en el schema ni en el modelo, así que todas las escrituras dicen "chilena".
- **Domicilio y comuna:** si faltan, se completan con "Santiago".
- **Fecha:** `strftime("%d de %B de %Y")` depende del idioma configurado en el servidor. En los tests salió "10 de October de 2026".
- **Tipo de trámite:** un `deed_type` desconocido genera un `PODER_ESPECIAL` sin avisar. `DECLARACION_JURADA` tiene precio en `pricing.py:8`, pero no tiene plantilla.

## 5. Tratamiento de las escrituras en `FAILED`

Las escrituras fallidas solo guardan RUT, tipo de trámite, pago y error. **No guardan nombre, domicilio ni comuna**, así que para volver a generarlas hay que enviar esos datos de nuevo. El estado civil y la profesión ya no hacen falta.

1. **Desplegar la corrección.** Sin ella, cada reintento vuelve a fallar y crea otro registro `FAILED`.
2. **Identificar los casos pendientes.** La consulta devuelve una fila por pago que no tiene ningún documento emitido:

   ```sql
   SELECT payment_id, customer_rut, deed_type,
          MIN(created_at) AS primer_intento, COUNT(*) AS intentos, MAX(error_log) AS error
   FROM notarial_deeds
   WHERE status = 'FAILED'
     AND payment_id NOT IN (SELECT payment_id FROM notarial_deeds WHERE status = 'COMPLETED')
   GROUP BY payment_id, customer_rut, deed_type
   ORDER BY primer_intento;
   ```

   Comparar el resultado con la lista de Soporte (14 casos).
3. **Conseguir nombre completo, domicilio y comuna** de cada cliente, desde el panel operativo o desde Soporte. La tabla `clients` solo sirve si otro sistema la mantiene: este servicio no la lee ni la escribe.
4. **Volver a generar los documentos:**
   - **Casos urgentes:** usar `POST /documents/generate` con el mismo `payment_id`. Se genera un código nuevo y el registro `FAILED` original queda como está.
   - **Resto de los casos:** usar un script de reproceso, **todavía por desarrollar**, que pase el mismo registro a `COMPLETED` sin cambiar su código ni su fecha. Debe tener un modo de prueba que muestre los cambios antes de aplicarlos.
5. **Verificar** cada documento con `GET /documents/{codigo}/status` y revisar el texto generado.
6. **Entregar a Operaciones la tabla de códigos**, con el código original y el final de cada caso.

Este servicio no hace cobros, así que volver a generar un documento desde aquí no cobra de nuevo. Falta confirmar que el panel tampoco vuelve a pasar por la pasarela de pago.

## 6. Próximos pasos recomendados

1. Desplegar la corrección y volver a generar las escrituras `FAILED` (sección 5).
2. Rotar las credenciales expuestas (riesgo 1).
3. Validar los datos del cliente antes del cobro y responder 422, no 500.
4. Evitar duplicados por pago: `payment_id` único, y reprocesar en lugar de crear un registro nuevo.
5. Agregar CI y lockfile (riesgos 4 y 5).
6. Corregir los datos que el documento completa por su cuenta (nacionalidad, domicilio, fecha), con validación del equipo legal.
