# Especificación de funcionalidad: Interfaz de chat (consola)

**Rama de funcionalidad**: `010-chat-interface`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #9. Una interfaz tipo chat en la **terminal** donde toda la interacción es
legible para alguien que **no conoce el código** (comportamiento obligatorio #11 del enunciado). Se
califica la legibilidad, no el diseño visual: una consola basta (sin front-end web). Construye sobre el
agente (#6/#7/#8): corre el loop y muestra la conversación turno a turno, dejando **evidente** cuándo el
agente abre un reclamo o escala.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Conversación turno a turno legible (Prioridad: P1)

La interfaz corre en la terminal (stdin/stdout). Muestra los **mensajes del asegurado** y las
**respuestas del agente** claramente distinguibles (etiquetas de rol), turno a turno.

**Por qué esta prioridad**: Es el núcleo del comportamiento #11: alguien que no conoce el código debe
poder seguir la conversación.

**Prueba independiente**: Renderizar una secuencia de turnos (asegurado/agente) → cada uno aparece con
su etiqueta de rol, distinguible, sin ambigüedad de quién habló.

**Escenarios de aceptación**:

1. **Dado** un mensaje del asegurado, **Cuando** se renderiza, **Entonces** aparece claramente etiquetado como del asegurado.
2. **Dado** una respuesta del agente, **Cuando** se renderiza, **Entonces** aparece claramente etiquetada como del agente, distinguible del asegurado.
3. **Dado** varios turnos, **Entonces** se presentan en orden, uno a uno.

---

### Historia de usuario 2 - Acciones evidentes: reclamo abierto / escalamiento (Prioridad: P1)

Cuando el agente **abre un reclamo** o **escala a un ajustador**, la interfaz lo hace **evidente** con
una línea clara (p. ej. `✓ Reclamo abierto #CLM-...` / `↑ Escalado a ajustador — prioridad alta`),
distinta de un mensaje de chat normal.

**Por qué esta prioridad**: El enunciado exige que, cuando el agente abre un reclamo o escala, la
interfaz lo deje evidente (behavior #11).

**Prueba independiente**: Renderizar un evento de reclamo abierto (con su id) y uno de escalamiento (con
id y prioridad) → cada uno produce una línea evidente y distinguible de los turnos de chat.

**Escenarios de aceptación**:

1. **Dado** un reclamo abierto con `claim_id`, **Cuando** se renderiza, **Entonces** aparece una línea evidente con el id del reclamo.
2. **Dado** un escalamiento con `escalation_id` y `prioridad`, **Cuando** se renderiza, **Entonces** aparece una línea evidente con la prioridad (p. ej. `alta`) y el id. (La causa es input del modelo, no resultado; se ve en el turno de texto del agente — no se mete en el estado, por Principio I.)
3. **Dado** un evento, **Entonces** es visualmente distinto de un turno de chat (no se confunde con texto del agente).

---

### Historia de usuario 3 - Ejecutable en terminal, sin web ni diseño visual (Prioridad: P1)

La interfaz se ejecuta en la terminal (stdin/stdout), lee los mensajes del asegurado y corre el agente
(#6) por cada turno. No hay front-end web ni trabajo de diseño visual.

**Por qué esta prioridad**: El issue acota el alcance: consola, foco en MVP; nada de web.

**Prueba independiente**: Existe un punto de entrada ejecutable (p. ej. `python -m cordillera.agent.chat`)
que arranca el loop de chat; el renderizado no depende de librerías de UI web.

**Escenarios de aceptación**:

1. **Dado** el módulo de chat, **Cuando** se invoca, **Entonces** arranca un loop que lee del stdin y escribe al stdout.
2. **Dado** el alcance, **Entonces** no se introduce ninguna dependencia de front-end web.

### Casos límite

- El agente hace una pregunta (p. ej. cuál vehículo) → se muestra como un turno del agente normal; la conversación continúa con la respuesta del asegurado.
- Un turno que abre reclamo Y responde una pregunta (grúa) → se ven ambas cosas: la respuesta y la línea evidente del reclamo.
- Fin de la sesión (EOF / comando de salida) → el loop termina de forma limpia.
- Fallo del agente/MCP (#6 FR-008) → se muestra un error claro, no se cuelga.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: DEBE existir una interfaz de **consola** (stdin/stdout) que muestre la conversación turno a turno; sin front-end web.
- **FR-002**: Los turnos del **asegurado** y del **agente** DEBEN ser claramente distinguibles (etiquetas de rol).
- **FR-003**: Cuando el agente abre un reclamo o escala, la interfaz DEBE mostrar una **línea evidente** (reclamo con id; escalamiento con id y prioridad — ambos derivados del resultado de la tool), distinta de un turno de chat. La causa del escalamiento (input del modelo) se ve en el turno de texto del agente, no en el estado (Principio I).
- **FR-004**: DEBE existir un punto de entrada ejecutable para el chat (p. ej. `python -m cordillera.agent.chat`).
- **FR-005**: El renderizado DEBE ser **lógica pura** separada del loop de E/S, para probarlo sin modelo ni terminal.
- **FR-006**: El chat DEBE reusar el agente de #6 (`run`/loop) y reflejar su comportamiento (hooks #7, subagente #8); no reimplementa reglas.
- **FR-007**: DEBEN existir pruebas deterministas (sin LLM) del renderizado: etiquetas de rol, línea de reclamo con id, línea de escalamiento con prioridad, distinguibilidad.
- **FR-008**: NO se introduce ninguna dependencia de UI web; la terminal basta (texto plano; una TUI ligera como Rich es opcional y no requerida).

### Entidades clave *(include if feature involves data)*

- **ChatEvent**: representación de lo que se muestra — turno del asegurado, turno del agente, reclamo abierto (`claim_id`), escalamiento (`escalation_id`, `priority`).
- **Renderer**: funciones puras `evento → texto legible` (etiquetas, líneas evidentes). Fuente de la legibilidad; testeable.
- **Chat loop**: punto de entrada que lee stdin, corre el agente por turno y renderiza (capa de E/S delgada).

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: El renderer produce turnos de asegurado y agente distinguibles por etiqueta (verificable sin LLM).
- **SC-002**: Un reclamo abierto se renderiza con una línea evidente que incluye el `claim_id`; un escalamiento, con su id y la prioridad.
- **SC-003**: Existe un punto de entrada de chat en terminal; sin dependencia de UI web.
- **SC-004**: La suite de pruebas del renderizado corre en verde.

## Supuestos

- **Legibilidad, no diseño**: el enunciado no califica el diseño visual sino que se entienda qué pasó. Texto plano con etiquetas claras basta; Rich es opcional.
- **Núcleo testeable**: el **renderer** (lógica pura) es lo que se prueba determinísticamente; el loop vivo que corre el modelo y lee stdin se verifica en #12 (casos de prueba con modelo real en la interfaz).
- **Origen de los eventos de acción**: el reclamo abierto y el escalamiento se detectan de los **resultados de herramientas** del agente (consistente con el Principio I), no del texto del modelo. El mecanismo exacto (observación de resultados de `abrir_reclamo`/`escalar_a_ajustador`) se fija en el plan y se confirma end-to-end en #12.
- **No reimplementa reglas**: el chat solo presenta; las reglas las garantizan los hooks (#7) y el prompt (#6/#8).
- **Acción bloqueada**: cuando el guard (#7) niega `abrir_reclamo`, no hay una línea evidente propia — el bloqueo se ve en el turno de texto del agente (que explica por qué escala). Behavior #11 solo exige evidencia para reclamo/escalamiento; una línea evidente de bloqueo (derivada de `motivos_bloqueo`) es una mejora opcional diferida a #12.
- **Idioma**: etiquetas y líneas de cara al usuario en español (contrato de cara al asegurado); identificadores y código en inglés (convención VI).
- **Fuera de alcance**: casos de prueba e2e con modelo real en la interfaz (#12); cualquier front-end web.
