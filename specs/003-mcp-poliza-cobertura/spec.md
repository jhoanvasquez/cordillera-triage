# Especificación de funcionalidad: MCP — consultar_poliza + verificar_cobertura

**Rama de funcionalidad**: `003-mcp-poliza-cobertura`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #3. Dos herramientas del servidor MCP `cordillera` con descripciones
claras y NO solapadas (behavior #3), reutilizando el loader y el envelope de la funcionalidad #2.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Consultar la póliza de un vehículo (Prioridad: P1)

`consultar_poliza` devuelve la póliza completa de un vehículo específico: vigencia, amparos
contratados y deducibles.

**Por qué esta prioridad**: El agente necesita conocer el contenido de la póliza para clasificar y
decidir; es la base de la revisión de cobertura.

**Prueba independiente**: Contra las fixtures, consultar por la placa de A1 devuelve su póliza con
los amparos (incluida grúa); una placa inexistente devuelve resultado vacío sin error.

**Escenarios de aceptación**:

1. **Dado** la placa `FIC-01A`, **Cuando** se consulta la póliza, **Entonces** se devuelve la póliza vigente con sus amparos (incluye `grua`) y el deducible.
2. **Dado** una placa inexistente, **Cuando** se consulta, **Entonces** la respuesta es `ok=true` con póliza vacía (no es un error).
3. **Dado** que el asegurado tiene varios vehículos y no se indica cuál, **Entonces** la descripción de la herramienta guía al agente a **preguntar primero** en lugar de adivinar.

---

### Historia de usuario 2 - Verificar la cobertura (Prioridad: P1)

`verificar_cobertura` responde UNA pregunta: ¿el tipo de siniestro X está cubierto por la póliza P
en la fecha D? Devuelve `cubierto: si | no | incierto` con un motivo.

**Por qué esta prioridad**: Es el insumo de la decisión de abrir vs. escalar (reglas 2 y 5); el
`incierto` dispara escalamiento (regla 5).

**Prueba independiente**: Contra las fixtures, grúa en la póliza de A1 → `si`; daños en la póliza de
A4 (uso particular + domicilios) → `incierto`; cualquier cobertura en la póliza vencida de A3 →
`no` (no vigente en la fecha).

**Escenarios de aceptación**:

1. **Dado** la póliza `POL-FIC-0001`, tipo `grua`, fecha `2026-10-10`, **Cuando** se verifica, **Entonces** `cubierto = si`.
2. **Dado** la póliza `POL-FIC-0005` (A4), tipo `danos`, fecha `2026-10-10`, **Cuando** se verifica, **Entonces** `cubierto = incierto` con el motivo del uso (domicilios).
3. **Dado** la póliza `POL-FIC-0004` (A3, vencida), cualquier tipo, fecha `2026-10-10`, **Cuando** se verifica, **Entonces** `cubierto = no` con motivo "no estaba vigente en la fecha".
4. **Dado** una póliza inexistente (número que no existe), **Cuando** se verifica, **Entonces** se devuelve un **error** de categoría `business` — NO un resultado vacío. Preguntar por la cobertura de una póliza que no existe no es "una búsqueda sin resultados": no se puede responder, por eso es error.

---

### Historia de usuario 3 - Descripciones que evitan confusión (Prioridad: P1)

Las dos herramientas dejan claro cuándo usar cada una, sin solaparse (behavior #3).

**Por qué esta prioridad**: El enunciado evalúa explícitamente que el agente no confunda
`consultar_poliza` con `verificar_cobertura`.

**Prueba independiente**: La descripción de `consultar_poliza` indica "póliza completa de un vehículo
específico" y la guía multi-vehículo; la de `verificar_cobertura` indica "responde una sola
pregunta de cobertura". Son textualmente distintas.

**Escenarios de aceptación**:

1. **Dado** las descripciones registradas de ambas herramientas, **Cuando** se comparan, **Entonces** no se solapan y cada una expresa su propósito distintivo.
2. **Dado** la descripción de `consultar_poliza`, **Entonces** incluye la guía de preguntar cuál vehículo cuando hay varios.

### Casos límite

- Placa sin vehículo asociado → resultado vacío (no error).
- Póliza sin amparo del tipo consultado → `cubierto = no` con motivo "amparo no contratado".
- Fecha fuera de la vigencia → `cubierto = no` (prevalece sobre el estado del amparo).
- Número de póliza inexistente en `verificar_cobertura` → **error (`business`), NO vacío** — contrasta con la consulta/búsqueda, donde vacío no es error.
- Registro flaky (`DOC-FIC-9999` o su vehículo) → error `transient` reintentable.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: `consultar_poliza` DEBE devolver la póliza completa (vigencia, amparos, deducible) de un vehículo específico, identificado por placa.
- **FR-002**: Si no hay vehículo/póliza para la placa, `consultar_poliza` DEBE devolver `ok=true` con resultado vacío (no un error).
- **FR-003**: `verificar_cobertura` DEBE responder `cubierto: si | no | incierto` con un `motivo`, dados póliza, tipo y fecha.
- **FR-004**: Si la póliza no estaba vigente en la fecha, `verificar_cobertura` DEBE devolver `cubierto = no` (prevalece sobre el amparo).
- **FR-005**: Un amparo marcado `incierto` DEBE producir `cubierto = incierto` con el motivo del amparo (p. ej. uso particular + domicilios).
- **FR-006**: Las descripciones de ambas herramientas DEBEN ser distintas y no solaparse; `consultar_poliza` DEBE incluir la guía de preguntar cuál vehículo cuando hay varios.
- **FR-007**: Ambas herramientas DEBEN usar el envelope estructurado de #2 y las categorías de error.
- **FR-008**: DEBEN existir pruebas colocadas que cubran `si` / `no` / `incierto`, póliza vencida, vacío y categorías de error.
- **FR-009**: Si el número de póliza no existe, `verificar_cobertura` DEBE devolver un **error** (`business`), NO un resultado vacío. Contraste con FR-002: una consulta/búsqueda sin coincidencias sí es vacío-sin-error; preguntar por una póliza inexistente es un error porque no se puede responder.

### Entidades clave *(incluir si la funcionalidad involucra datos)*

- **Póliza / Amparo / Vehículo**: reutilizados de #1 (solo lectura).
- **RespuestaPoliza**: `ok`, `poliza` (o nulo), `error`.
- **RespuestaCobertura**: `ok`, `cubierto` (`si|no|incierto`), `motivo`, `deducible`, `error`.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: `consultar_poliza` devuelve la póliza completa de un vehículo y vacío-sin-error para placas inexistentes.
- **SC-002**: `verificar_cobertura` produce correctamente `si`, `no` (incluida póliza vencida) e `incierto` según los datos.
- **SC-003**: Las descripciones de las dos herramientas son distintas y `consultar_poliza` incluye la guía multi-vehículo.
- **SC-004**: La suite de pruebas colocada corre en verde.

## Supuestos

- Reutiliza el loader, el envelope y los modelos base de #2 (no los redefine).
- `abrir_reclamo` / `escalar_a_ajustador` y el subagente de cobertura NO son de este ticket (#4 y #8).
- El `tipo` de `verificar_cobertura` se alinea con los tipos de amparo de las fixtures (`danos`, `grua`).
- Los valores de dominio permanecen en español (`cubierto`, `si|no|incierto`).
