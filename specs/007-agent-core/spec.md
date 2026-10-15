# Especificación de funcionalidad: Núcleo del agente (loop, system prompt, conexión MCP)

**Rama de funcionalidad**: `007-agent-core`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #6. Arma el núcleo del agente de triage: un loop agéntico con
`ClaudeSDKClient` (Claude Agent SDK) conectado al servidor MCP `cordillera` por stdio, un system
prompt versionado, y el cableado de `registrar_triage` como tool in-process del SDK. Los bloques
previos ya proveen los datos (#1), las tools de negocio del MCP (#2–#4) y el esquema/salida
estructurada de triage (#5, spec `006-triage-schema`). Este bloque los junta en un agente ejecutable.
Las **hooks de reglas de negocio** (reglas 1, 2 y 3) y la **interfaz de chat** quedan fuera: son #7 y #9.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Loop agéntico con terminación por el SDK (Prioridad: P1)

El agente corre un loop con `ClaudeSDKClient` conectado al servidor MCP `cordillera` (stdio). El loop
termina cuando el SDK emite su resultado final (mensaje de resultado / `stop_reason` del modelo),
**nunca** contando iteraciones ni matcheando palabras clave en el texto. En cada turno se registra
(log) la razón de parada que reporta el modelo.

**Por qué esta prioridad**: Es el núcleo ejecutable del agente; sin el loop no hay producto. La
terminación guiada por el SDK es un criterio de aceptación explícito del issue y evita loops
frágiles basados en heurísticas de texto.

**Prueba independiente**: Correr el agente contra un reporte simple con el MCP `cordillera` levantado;
el agente ejecuta las tools necesarias y termina por la señal de resultado del SDK; el log contiene
la razón de parada de cada turno.

**Escenarios de aceptación**:

1. **Dado** el servidor MCP `cordillera` disponible por stdio, **Cuando** se inicia el agente, **Entonces** `ClaudeSDKClient` queda conectado y las tools del servidor (`buscar_asegurado`, `verificar_identidad`, `consultar_poliza`, `verificar_cobertura`, `abrir_reclamo`, `escalar_a_ajustador`) quedan disponibles para el modelo.
2. **Dado** un turno del modelo, **Cuando** el modelo pide usar una tool, **Entonces** el loop ejecuta la tool y continúa; **Cuando** el SDK emite su resultado final, **Entonces** el loop termina (no por conteo de iteraciones ni por coincidencia de palabras clave).
3. **Dado** cualquier turno, **Entonces** la razón de parada reportada por el modelo queda registrada en el log.

---

### Historia de usuario 2 - System prompt versionado (Prioridad: P1)

El comportamiento del agente se define en un **system prompt versionado** bajo `src/cordillera/agent/`.
El prompt guía el triage (tipos frecuentes de siniestro, "lo no mencionado queda nulo") y la
orquestación de tools (preguntar cuál vehículo ante ambigüedad; verificar identidad y cobertura antes
de abrir un reclamo; emitir el triage como salida estructurada vía `registrar_triage`).

**Por qué esta prioridad**: El prompt es el contrato de comportamiento del agente. La regla "lo no
mencionado queda nulo" (behavior #5) y la guía de tipos de siniestro (que el esquema NO enumera, ver
`006-triage-schema` FR-002) viven en el prompt, no en el código.

**Prueba independiente**: Cargar el system prompt desde su artefacto versionado; verificar que es el
texto que recibe `ClaudeSDKClient` como instrucción de sistema (sin reconstruirlo en varios lugares).

**Escenarios de aceptación**:

1. **Dado** el agente iniciado, **Cuando** se arma la sesión, **Entonces** el system prompt se lee de su artefacto bajo `src/cordillera/agent/` (fuente única).
2. **Dado** el system prompt, **Entonces** incluye la guía de triage ("lo no mencionado queda nulo", tipos frecuentes de siniestro) y la guía de orquestación de tools (preguntar vehículo, verificar antes de abrir reclamo, producir el triage con `registrar_triage`).

---

### Historia de usuario 3 - `registrar_triage` como tool in-process del SDK (Prioridad: P1)

El agente expone `registrar_triage` (spec `006-triage-schema`) como **tool in-process del SDK**, de
modo que el modelo produce el triage como **salida estructurada validada**, nunca texto libre.

**Por qué esta prioridad**: Cierra el pendiente explícito de `006-triage-schema` ("el wiring de
`registrar_triage` como tool in-process del SDK y el loop del agente son #6"). Es el mecanismo por el
cual el agente emite el triage.

**Prueba independiente**: Con el agente iniciado, la tool in-process `registrar_triage` está
disponible para el modelo junto con las tools del servidor `cordillera`; invocarla con datos válidos
produce un `Triage` validado; con datos inválidos, un error de validación (no un triage a medias).

**Escenarios de aceptación**:

1. **Dado** el agente iniciado, **Cuando** se arma la sesión, **Entonces** `registrar_triage` está disponible como tool in-process del SDK, además de las tools del servidor `cordillera`.
2. **Dado** que el modelo llama `registrar_triage` con datos válidos, **Entonces** devuelve un `Triage` validado; con datos inválidos, devuelve un error de validación.

### Casos límite

- El servidor MCP `cordillera` no arranca o la conexión stdio se cae → el agente reporta un error claro y no queda colgado.
- El modelo devuelve una razón de parada no prevista → el loop no entra en bucle infinito; termina de forma segura según la señal del SDK.
- Reporte que requiere una sola tool (p. ej. una duda de cobertura) → el agente usa la tool, responde y termina sin pasos innecesarios.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: El agente DEBE usar `ClaudeSDKClient` (Claude Agent SDK) conectado al servidor MCP `cordillera` por **stdio**.
- **FR-002**: El loop DEBE terminar por el **resultado/razón de parada que emite el SDK**, nunca contando iteraciones ni matcheando palabras clave en el texto del modelo.
- **FR-003**: El agente DEBE registrar (log) la **razón de parada** del modelo en cada turno.
- **FR-004**: El **system prompt** DEBE estar versionado bajo `src/cordillera/agent/` y ser la fuente única que recibe `ClaudeSDKClient`.
- **FR-005**: El system prompt DEBE incluir la guía de triage (lo no mencionado queda nulo; tipos frecuentes de siniestro, que el esquema no enumera) y la guía de orquestación de tools (preguntar cuál vehículo ante ambigüedad; verificar identidad y cobertura antes de abrir un reclamo; producir el triage con `registrar_triage`).
- **FR-006**: El agente DEBE exponer `registrar_triage` como **tool in-process del SDK**, además de las tools del servidor `cordillera`, de modo que el triage se produzca como salida estructurada validada (behavior #5), nunca texto libre.
- **FR-007**: El agente DEBE dejar disponibles para el modelo las seis tools de negocio del servidor `cordillera` (`buscar_asegurado`, `verificar_identidad`, `consultar_poliza`, `verificar_cobertura`, `abrir_reclamo`, `escalar_a_ajustador`).
- **FR-008**: Ante fallo de arranque o de conexión del servidor MCP, el agente DEBE reportar un error claro y no quedar colgado.
- **FR-009**: `claude-agent-sdk` DEBE agregarse como dependencia en `pyproject.toml` (hoy solo están `mcp` y `pydantic`).
- **FR-010**: DEBEN existir pruebas colocadas del núcleo del agente que no dependan del modelo (deterministas): construcción de la sesión con el system prompt y las tools correctas, disponibilidad de `registrar_triage` in-process, y la condición de terminación del loop por la señal del SDK (con un cliente simulado). Los casos con modelo real son #12.

### Entidades clave *(include if feature involves data)*

- **System prompt**: artefacto de texto versionado bajo `src/cordillera/agent/`; define el comportamiento del agente. Fuente única.
- **Agente / loop**: orquesta `ClaudeSDKClient`, la conexión MCP stdio a `cordillera`, la tool in-process `registrar_triage`, y la terminación por la señal de resultado del SDK.
- **`registrar_triage`**: función ya existente (`agent/triage.py`) envuelta como tool in-process del SDK.
- **Servidor `cordillera`**: servidor MCP FastMCP sobre stdio (`mcp_server/server.py`) lanzado como subproceso; expone las seis tools de negocio.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: El agente se conecta al servidor `cordillera` por stdio y expone sus seis tools más `registrar_triage` in-process (verificable sin modelo real, inspeccionando la sesión construida).
- **SC-002**: El loop termina por la señal de resultado del SDK; no hay conteo de iteraciones ni matching de palabras clave en el código (verificable con un cliente simulado).
- **SC-003**: La razón de parada del modelo queda en el log en cada turno.
- **SC-004**: El system prompt se carga de su artefacto versionado bajo `src/cordillera/agent/` (fuente única) y contiene la guía de triage y de orquestación.
- **SC-005**: La suite de pruebas colocada (deterministas) corre en verde.

## Supuestos

- **Dos superficies MCP**: el agente usa (a) el servidor **externo `cordillera`** por stdio para las seis tools de negocio, y (b) una superficie **in-process del SDK** para `registrar_triage`. El `.mcp.json` de la raíz es del harness de Claude Code (solo GitHub) y NO describe la conexión del agente a `cordillera`; el agente lanza `cordillera` como subproceso stdio por su cuenta.
- **Reglas de negocio**: en #6 el system prompt **guía** el comportamiento (verificar identidad y cobertura antes de abrir reclamo, preguntar cuál vehículo). La **imposición determinista** de las reglas 1, 2 y 3 vía **SDK hooks** es #7; no se duplica aquí.
- **Mecanismo exacto de terminación**: el criterio es "terminar por el resultado del SDK". El mecanismo concreto del Claude Agent SDK (mensaje de resultado vs. `stop_reason` por turno) se confirma en diseño/implementación contra la documentación del `claude-agent-sdk`; el spec fija el comportamiento, no la firma.
- **Modelo por defecto**: Claude Opus 4.8 (`claude-opus-4-8`) salvo indicación contraria; configurable.
- **Convención de idioma**: especificaciones y prompts en español; identificadores y código en inglés (convención #20). El system prompt es contenido de producto en español.
- **Fuera de alcance**: interfaz de chat/consola (#9), pruebas con modelo real y e2e (#12), y la capa de hooks de reglas (#7).
