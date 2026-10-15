# Especificación de funcionalidad: MCP — buscar_asegurado + verificar_identidad + error envelope

**Rama de funcionalidad**: `002-mcp-asegurado-identidad`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #2. Primeras herramientas del servidor MCP `cordillera` (FastMCP
sobre stdio) más el envelope de respuesta/error compartido por todas las herramientas. Consume las
fixtures de la funcionalidad #1.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Localizar al asegurado (Prioridad: P1)

El agente debe encontrar al asegurado por documento, nombre o placa, incluso cuando hay varias
coincidencias.

**Por qué esta prioridad**: Es el primer paso del triage; sin identificar al asegurado no hay nada
que procesar.

**Prueba independiente**: Contra las fixtures, buscar por un nombre homónimo devuelve más de uno;
por documento único devuelve exactamente uno; por un valor inexistente devuelve lista vacía SIN error.

**Escenarios de aceptación**:

1. **Dado** el nombre "María Gómez", **Cuando** se busca por nombre, **Entonces** se devuelven dos o más asegurados.
2. **Dado** el documento `DOC-FIC-0001`, **Cuando** se busca por documento, **Entonces** se devuelve exactamente un asegurado.
3. **Dado** un valor inexistente, **Cuando** se busca, **Entonces** la respuesta es `isError: false` con `resultCount: 0` (una búsqueda sin resultados NO es un error).
4. **Dado** la placa `FIC-01A`, **Cuando** se busca por placa, **Entonces** se devuelve el asegurado dueño de ese vehículo.

---

### Historia de usuario 2 - Verificar la identidad (Prioridad: P1)

`verificar_identidad` confirma la identidad del asegurado con un segundo dato (`fecha_nacimiento`);
su resultado alimenta la regla de negocio 1.

**Por qué esta prioridad**: Ningún reclamo se abre sin identidad verificada (regla 1); este
resultado es el insumo del hook de identidad (#7).

**Prueba independiente**: Con el dato correcto → verificado verdadero; con dato incorrecto →
verificado falso (no un error de sistema); la respuesta es consumible por el hook.

**Escenarios de aceptación**:

1. **Dado** un asegurado y su `fecha_nacimiento` correcta, **Cuando** se verifica, **Entonces** el resultado es verificado = verdadero.
2. **Dado** una `fecha_nacimiento` incorrecta, **Cuando** se verifica, **Entonces** el resultado es verificado = falso (no es una falla de sistema).
3. **Dado** un documento inexistente, **Cuando** se verifica, **Entonces** se devuelve un error de categoría apropiada (no un verdadero/falso ambiguo).

---

### Historia de usuario 3 - Errores estructurados y resultados vacíos (Prioridad: P1)

Todas las herramientas devuelven la forma nativa de MCP; los errores distinguen cuatro categorías e
indican si son reintentables; una búsqueda sin resultados no es un error.

**Por qué esta prioridad**: Comportamiento obligatorio #4; el agente necesita decidir reintentar vs.
informar vs. escalar a partir de la categoría y de `isRetryable`.

**Prueba independiente**: Cada categoría de error puede provocarse y se refleja en `errorCategory` +
`isRetryable`; la búsqueda vacía da `isError: false`.

**Escenarios de aceptación**:

1. **Dado** el registro flaky `DOC-FIC-9999`, **Cuando** se consulta, **Entonces** `errorCategory = transient` e `isRetryable = true`.
2. **Dado** un criterio de búsqueda vacío o nulo, **Cuando** se busca, **Entonces** `errorCategory = validation` e `isRetryable = false`.
3. **Dado** una búsqueda sin coincidencias, **Cuando** se busca, **Entonces** `isError: false` con `resultCount: 0`.

### Casos límite

- Criterio de búsqueda vacío o nulo → error de validación (no lista vacía).
- Placa que no corresponde a ningún vehículo → resultado vacío con `isError: false`.
- Registro flaky `DOC-FIC-9999` → error `transient` reintentable (simula la falla transitoria del caso #7).

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: DEBE existir un servidor MCP (FastMCP sobre stdio) que exponga las herramientas del escenario.
- **FR-002**: `buscar_asegurado` DEBE aceptar criterio por documento, nombre o placa, y soportar varias coincidencias.
- **FR-003**: Una búsqueda sin resultados DEBE devolver `isError: false` con `resultCount: 0` (NO un error).
- **FR-004**: `verificar_identidad` DEBE confirmar la identidad con un segundo dato (`fecha_nacimiento`) y devolver un resultado booleano consumible por el hook de identidad.
- **FR-005**: Todas las herramientas DEBEN devolver la forma nativa de MCP (`isError` / `content` / `structuredContent`).
- **FR-006**: Los errores DEBEN llevar `errorCategory` ∈ {`transient`, `validation`, `business`, `permissions`} e `isRetryable`.
- **FR-007**: El registro flaky (`DOC-FIC-9999`) DEBE producir un error `transient` reintentable (simula la falla transitoria para el caso #7).
- **FR-008**: DEBE existir un cargador que lea las fixtures JSON de #1 y las exponga a las herramientas.
- **FR-009**: DEBEN existir pruebas unitarias colocadas (`test_*.py`) que cubran: coincidencia única, múltiple y vacía; identidad correcta e incorrecta; y cada categoría de error.

### Entidades clave *(incluir si la funcionalidad involucra datos)*

- **Asegurado / Vehículo / Póliza**: reutilizados de la funcionalidad #1 (solo lectura).
- **Respuesta MCP (envelope)**: `isError`, `content[]`, `structuredContent` — en éxito lleva los resultados y `resultCount`; en error lleva `errorCategory`, `isRetryable` y `description`.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: Las dos herramientas responden la forma nativa de MCP en el 100% de los casos (éxito y error).
- **SC-002**: `buscar_asegurado` devuelve correctamente 0, 1 y varias coincidencias según los datos.
- **SC-003**: Cada una de las cuatro categorías de error puede provocarse y se refleja con el `isRetryable` correcto.
- **SC-004**: `verificar_identidad` distingue dato correcto e incorrecto; su salida es consumible por el hook de identidad (#7).
- **SC-005**: La suite de pruebas colocada corre en verde.

## Supuestos

- Consume las fixtures de #1 (no crea ni modifica datos).
- La consulta de póliza y cobertura, y abrir/escalar reclamos, NO son de este ticket (#3 y #4).
- Los esquemas Pydantic de entradas/salidas se formalizan aquí, por ser las primeras herramientas.
- Transporte stdio: el agente lanzará el servidor como subproceso (en #6); este ticket entrega el servidor y sus dos primeras herramientas con pruebas.
