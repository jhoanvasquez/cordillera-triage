---
description: "Lista de tareas para el núcleo del agente (loop, system prompt, conexión MCP)"
---

# Tareas: Núcleo del agente (loop, system prompt, conexión MCP)

**Entrada**: Documentos de diseño en `specs/007-agent-core/`

**Prerrequisitos**: plan.md, spec.md

**Pruebas**: INCLUIDAS, deterministas sin LLM (SC-001..005, FR-010).

**Organización**: por historia de usuario. Las fases se ordenan por dependencia de build
(US2 prompt y US3 tool son hojas; US1 integra y cablea).

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias)

---

## Fase 1: Configuración

- [x] T001 `pyproject.toml`: agregar `claude-agent-sdk` a `dependencies` y correr `uv lock`. (instalado `claude-agent-sdk==0.2.168`)

---

## Fase 3: Historia de usuario 2 - System prompt versionado (Prioridad: P1)

### Implementación

- [x] T002 [US2] `agent/system_prompt.md`: prompt versionado (español, contenido de producto). Incluye guía de triage ("lo no mencionado queda nulo"; tipos frecuentes de siniestro, que el esquema NO enumera) y guía de orquestación (preguntar cuál vehículo ante ambigüedad; verificar identidad y cobertura antes de abrir reclamo; producir el triage con `registrar_triage`; reglas 4 y 5 como instrucción). NO impone reglas 1/2/3 (son hooks de #7).
- [x] T003 [US2] `agent/prompt.py`: `load_system_prompt() -> str` que lee `system_prompt.md` vía `Path(__file__).parent`; fuente única (FR-004).

### Pruebas

- [x] T004 [P] [US2] `agent/test_agent.py`: `load_system_prompt()` lee de `system_prompt.md` y el texto contiene la guía de triage y de orquestación.

**Punto de control**: el prompt versionado se carga desde su artefacto único.

---

## Fase 4: Historia de usuario 3 - `registrar_triage` como tool in-process (Prioridad: P1)

### Implementación

- [x] T005 [US3] `agent/sdk_tools.py`: `registrar_triage_tool` — adaptador `@tool` async que llama `registrar_triage` (de `agent/triage.py`) y devuelve el `Triage` validado como JSON en `content` (datos inválidos → `is_error` con el `ErrorInfo`). El esquema de entrada del tool ES el modelo de triage (`Triage.model_json_schema()`). Luego `triage_server = create_sdk_mcp_server(name="triage", version="1.0.0", tools=[registrar_triage_tool])`. No duplica la lógica de `triage.py`. **Verificado**: el bridge in-process del SDK solo reenvía `content`/`is_error` (descarta `structuredContent`); la garantía estructural la da la validación Pydantic, no el campo de transporte.

### Pruebas

- [x] T006 [P] [US3] `agent/test_agent.py`: el adaptador con datos válidos → contenido con `Triage` validado; con severidad inválida → contenido de error de validación.

**Punto de control**: `registrar_triage` queda expuesto como tool in-process con salida estructurada.

---

## Fase 5: Historia de usuario 1 - Loop con terminación por el SDK + conexión MCP (Prioridad: P1) 🎯

### Implementación

- [x] T007 [US1] `agent/core.py`: `RunResult` (texto final + razón de parada; campos en inglés) + `consume(messages: AsyncIterable[Message]) -> RunResult` que itera el stream, registra `ResultMessage.stop_reason`/`terminal_reason`/`subtype` y termina en el `ResultMessage` (SIN conteo de iteraciones ni matching de palabras clave). Recibe un `AsyncIterable`, no el cliente (testeable sin LLM).
- [x] T008 [US1] `agent/core.py`: `build_options() -> ClaudeAgentOptions` — cablea `mcp_servers` con `cordillera` (`{"type":"stdio","command":"python","args":["-m","cordillera.mcp_server.server"]}`) y `triage` (`triage_server` de T005); `allowed_tools` con las 7 tools (`mcp__cordillera__*` + `mcp__triage__registrar_triage`); `system_prompt=load_system_prompt()` (T003); `model="claude-opus-4-8"` por defecto. (depende de T003, T005)
- [x] T009 [US1] `agent/core.py`: `run(report)` — abre `ClaudeSDKClient(build_options())` como context manager async, `await client.query(report)` y delega el consumo a `consume(client.receive_response())`; cablea `stderr` al log; captura fallo de arranque/conexión del MCP y lo reporta claro, sin colgarse (FR-008).

### Pruebas

- [x] T010 [P] [US1] `agent/test_agent.py`: (a) `consume` con `AsyncIterable` simulado `[AssistantMessage(...), ResultMessage(stop_reason=...)]` → registra la razón de parada y termina en el `ResultMessage` (sin conteo/keywords). (b) `build_options()` → `mcp_servers` tiene `cordillera` (stdio con el comando correcto) y `triage` in-process; `allowed_tools` lista las 7 tools; `system_prompt` es el prompt cargado; modelo por defecto.

**Punto de control**: el agente se construye con las 2 superficies MCP y el loop termina por el SDK (verificable sin modelo real).

---

## Fase N: Pulido

- [x] T011 Ejecutar `pytest` — toda la suite en verde.
- [x] T012 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- **T001** primero (habilita importar `claude_agent_sdk`).
- **US2** (T002→T003→T004) y **US3** (T005→T006) son independientes entre sí y pueden ir en paralelo tras T001.
- **US1**: T007 (`consume`) es independiente y puede ir en cualquier momento tras T001. **T008 (`build_options`) depende de T003 y T005**; T009 (`run`) depende de T008. T010 depende de T007 y T008.
- Pulido (T011–T012) al final.

## Notas

- Dos superficies MCP en una sola config: `cordillera` externo por stdio + `triage` in-process (el `.mcp.json` de la raíz es del harness de Claude Code, no describe esta conexión).
- El cumplimiento determinista de las reglas de negocio 1/2/3 (hooks del SDK) es **#7**; la interfaz de chat es **#9**; las pruebas con modelo real y e2e son **#12**.
- Confirmado contra la lib instalada (`claude-agent-sdk==0.2.168`): `AssistantMessage.stop_reason` da la razón de parada por turno y `ResultMessage` (`terminal_reason`/`subtype`/`stop_reason`) la terminal; `@tool` acepta un JSON Schema completo como `input_schema`; el bridge in-process descarta `structuredContent` (solo `content`/`is_error`). Pendiente real: el runtime del SDK (Claude Agent CLI/Node) para `run()` end-to-end — es #12, no afecta las pruebas deterministas.
- Commits Conventional, sin atribución a IA (Principio V).
