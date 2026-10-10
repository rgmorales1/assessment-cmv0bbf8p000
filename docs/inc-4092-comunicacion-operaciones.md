# Comunicación a Operaciones Legales: INC-4092

**Para:** Operaciones Legales y Soporte al Cliente

**De:** Equipo de Ingeniería

**Asunto:** INC-4092: Emisión de poderes notariales. Qué pasó, qué hicimos y cómo recuperamos los documentos

Hola, equipo:

Les escribimos para explicar qué pasó con la emisión de poderes notariales del 14 de octubre, qué hicimos para solucionarlo y cómo vamos a recuperar los documentos que quedaron con error.

## Qué pasó

El sistema que redacta las escrituras necesitaba dos datos del cliente: **estado civil** y **profesión u oficio**. Sin embargo, el formulario no los pide como obligatorios. Cuando un cliente no los había ingresado, el sistema no podía terminar de redactar el documento y mostraba "Error interno del servidor".

El cobro se procesa antes de redactar el documento. Por eso estos clientes vieron el cargo en su tarjeta aunque no recibieron su poder.

Los clientes que sí tenían esos dos datos no se vieron afectados.

## A quién afectó

Soporte identificó 14 casos, 4 de ellos prioritarios por su hora de notaría. Vamos a revisar la lista contra nuestros registros para confirmar que todos se deben a esta misma causa y avisarles si aparece algún caso adicional.

## Qué hicimos

Ajustamos el sistema para que, cuando falte el estado civil o la profesión u oficio, el documento se emita igual e indique **"no informado"** en ese dato. Este criterio fue aprobado por Constanza Arrau.

El ajuste ya está probado y se publicará el 09-10 a las 23:00. Desde ese momento, los nuevos poderes se emitirán sin este error.

## Qué pasará con los documentos con error

Cuando el ajuste esté publicado, volveremos a generar todos los documentos que quedaron con error:

1. **Primero, los casos urgentes (con hora de notaría).** Estos documentos tendrán un **código nuevo**. Les enviaremos una tabla con el código antiguo y el nuevo de cada caso para que puedan informarlo al cliente y a la notaría.
2. **Después, el resto de los casos.** Se recuperarán con su **código original**.

Volver a generar un documento **no implica un nuevo cobro** al cliente.

Para esto necesitamos su ayuda: el registro con error no guarda todos los datos del cliente. Les pediremos confirmar el **nombre completo, domicilio y comuna** de cada caso. Si el cliente nos da su estado civil y su profesión, también podemos incluirlos y el documento saldrá completo.

Les avisaremos en `#incidencias-ops-legal` a medida que cada documento esté disponible para descargar.

## Mensaje sugerido para clientes

> Estimado/a [nombre]: le informamos que tuvimos un inconveniente técnico al emitir su poder notarial. Su pago fue recibido correctamente y no se le hará ningún cobro adicional. Su documento estará disponible el [fecha/hora] y le avisaremos apenas esté listo. Lamentamos las molestias.

## Puntos que requieren revisión del equipo legal

Durante la revisión encontramos situaciones que no generan errores, pero sí pueden afectar el contenido de los documentos. **Todavía no están corregidas:**

- **Nacionalidad:** todos los poderes especiales dicen "de nacionalidad chilena", también los de clientes extranjeros, porque el sistema no recibe ese dato.
- **Domicilio y comuna:** si el cliente no los informa, el documento pone "Santiago".
- **Fecha:** el mes puede aparecer en inglés (por ejemplo, "14 de October de 2024").
- **Tipo de trámite:** si se solicita una declaración jurada, el sistema emite un poder especial.

Les sugerimos revisar con el equipo legal los documentos ya emitidos que podrían estar afectados.

## Qué haremos para que no vuelva a ocurrir

- Revisar que los datos del cliente estén completos **antes** del cobro, para que pueda corregirlos en el momento.
- Evitar que un mismo pago genere más de un documento.

Quedamos atentos a sus comentarios.

Equipo de Ingeniería
