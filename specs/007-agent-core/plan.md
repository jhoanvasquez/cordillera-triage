# Plan de implementación: Núcleo del agente (loop, system prompt, conexión MCP)

**Rama**: `007-agent-core` | **Fecha**: 2026-10-15 | **Especificación**: `specs/007-agent-core/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/007-agent-core/spec.md`

## Resumen

Se arma el núcleo ejecutable del agente con el **Claude Agent SDK** (`ClaudeSDKClient`). El agente
abre una sesión con un **system prompt versionado**, conecta las dos superficies MCP en un único
`mcp_servers` —el servidor **`cordillera` externo por stdio** (6 tools de negocio) y un servidor
**in-process del SDK** que expone `registrar_triage` (spec 006)— y corre un loop que termina por el
`ResultMessage` del SDK, registrando la razón de parada. La imposición determinista de las reglas de
negocio (hooks) es #7; la interfaz de chat es #9; las pruebas con modelo real son #12.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12

**Dependencias principales**: `claude-agent-sdk` (NUEVA — hoy solo `mcp`, `pydantic`); reutiliza
`mcp` (servidor `cordillera`) y `pydantic` (esquema `Triage`).

**Pruebas**: `pytest`, colocadas (`agent/test_agent.py`), **deterministas sin LLM** (cliente/stream simulado).

**Plataforma destino**: CLI/servicio local. El SDK de Python requiere runtime del Claude Agent CLI
(Node) y credenciales (`ANTHROPIC_API_KEY`); ambos son prerrequisitos **de runtime**, no de las
pruebas deterministas.

**Restricciones**: el loop termina por el `ResultMessage` del SDK, nunca por conteo ni palabras clave
(Principio "Ciclo agéntico correcto"); campos/código en inglés, prompt/dominio en español (Principio VI).

## Verificación de la constitución

*PUERTA: aprobar antes de implementar.*

- **Principio I (reglas por hooks, no prompt)**: en #6 el system prompt **guía** (reglas 4 y 5, orquestación); la **imposición determinista** de reglas 1, 2 y 3 son hooks del SDK en **#7**. #6 NO pretende imponer reglas por prompt como mecanismo final — las deja explícitamente a #7 (dependencia declarada). El loop termina por la razón de parada del modelo. CUMPLE (con dependencia a #7 para el cumplimiento de negocio en producción).
- **Principio III (SDD)**: existen `spec.md` y este `plan.md`; `tasks.md` sigue. El hook `require_spec` permite escribir en `src/**`. CUMPLE.
- **Principio IV (estructurado)**: `registrar_triage` in-process produce salida estructurada validada (`structuredContent`), nunca texto libre. CUMPLE.
- **Principio VI (idioma)**: identificadores/campos en inglés; system prompt y dominio en español. CUMPLE.

Sin violaciones.

## Estructura del proyecto (paquete `agent/`)

```text
src/cordillera/agent/
├── __init__.py
├── triage.py          # (existe) TriageResult + registrar_triage(data) -> TriageResult
├── system_prompt.md   # NUEVO — prompt versionado (español, contenido de producto); fuente única
├── prompt.py          # NUEVO — load_system_prompt() -> str  (lee system_prompt.md)
├── sdk_tools.py       # NUEVO — registrar_triage envuelto como @tool + create_sdk_mcp_server("triage", ...)
├── core.py            # NUEVO — build_options(); consume(messages) -> RunResult; run(report)
├── test_triage.py     # (existe)
└── test_agent.py      # NUEVO — pruebas deterministas (sin LLM)
```

**Decisión de estructura**: el prompt vive en `system_prompt.md` (artefacto revisable, español) y se
carga vía `Path(__file__).parent / "system_prompt.md"` — robusto con el layout de código del repo
(`pythonpath=["src"]`). `prompt.py` es la fuente única que lo lee (FR-004).

## Decisiones técnicas (cableado del SDK)

**Conexión MCP (una sola config `mcp_servers`)**:

```python
options = ClaudeAgentOptions(
    model="claude-opus-4-8",                    # configurable; por defecto Opus 4.8
    system_prompt=load_system_prompt(),         # string -> reemplaza el prompt por defecto
    mcp_servers={
        "cordillera": {                         # servidor externo por stdio (6 tools de negocio)
            "type": "stdio",
            "command": "python",
            "args": ["-m", "cordillera.mcp_server.server"],
        },
        "triage": triage_server,                # servidor in-process del SDK (registrar_triage)
    },
    allowed_tools=[
        "mcp__cordillera__buscar_asegurado", "mcp__cordillera__verificar_identidad",
        "mcp__cordillera__consultar_poliza", "mcp__cordillera__verificar_cobertura",
        "mcp__cordillera__abrir_reclamo", "mcp__cordillera__escalar_a_ajustador",
        "mcp__triage__registrar_triage",
    ],
)
```

**`registrar_triage` como tool in-process** (`sdk_tools.py`): `registrar_triage` es síncrono y
devuelve un `TriageResult` (Pydantic). El SDK espera `async def -> {"content": [...]}`. Se envuelve en
un adaptador delgado que llama la función existente y serializa el resultado como contenido MCP
(incluyendo `structuredContent` con el `Triage` validado o el `ErrorInfo` de validación); luego
`create_sdk_mcp_server(name="triage", version="1.0.0", tools=[registrar_triage_tool])`. No se duplica
la lógica de `triage.py`.

**Loop y terminación** (`core.py`): `run(report)` abre `ClaudeSDKClient(options)` como context
manager async, hace `client.query(report)` y delega el consumo a `consume(...)`. `consume` itera el
stream y **termina cuando llega `ResultMessage`** (el generador `receive_response()` se cierra ahí);
registra `ResultMessage.stop_reason` / `terminal_reason` / `subtype`. **No hay conteo de iteraciones
ni matching de palabras clave.** `consume` recibe un `AsyncIterable[Message]` (no el cliente), para
poder inyectar un stream simulado en pruebas.

**Fallo de MCP** (FR-008): si la sesión no se puede abrir o la conexión stdio falla, `run` captura el
error y lo reporta de forma clara (no queda colgado); `stderr` de `ClaudeAgentOptions` se cablea al log.

## Modelo de datos y contratos

- Reutiliza `Triage` (`mcp_server/models.py`) y `registrar_triage`/`TriageResult` (`agent/triage.py`).
- `RunResult` (nuevo, en `core.py`): resultado mínimo del loop para pruebas/uso — texto final del
  agente + la razón de parada registrada. Campos en inglés.
- Contrato de tools expuestas: 6 de `cordillera` + `registrar_triage` (nombres `mcp__<server>__<tool>`).

## Estrategia de pruebas (deterministas, sin LLM)

- **`build_options()`**: afirma que `mcp_servers` tiene `cordillera` (stdio con el comando correcto) y `triage` (in-process); que `allowed_tools` lista las 7 tools; que `system_prompt` es el prompt cargado; y el modelo por defecto.
- **`load_system_prompt()`**: afirma que el prompt se lee de `system_prompt.md` y contiene la guía de triage ("lo no mencionado queda nulo", tipos de siniestro) y de orquestación (preguntar vehículo, verificar antes de abrir reclamo, usar `registrar_triage`).
- **`registrar_triage_tool`**: adaptador async → datos válidos producen contenido con `Triage` validado; inválidos, contenido de error de validación (delega en `registrar_triage`, ya probado en 006).
- **`consume(stream)`**: con un `AsyncIterable` simulado `[AssistantMessage(...), ResultMessage(stop_reason=...)]`, afirma que registra la razón de parada y termina en el `ResultMessage` (sin conteo ni keywords).

Los casos con modelo real y e2e son #12.

## Seguimiento de complejidad

Sin violaciones. El diseño separa deliberadamente `consume(stream)` del cliente vivo para hacer
testeable la terminación del loop sin modelo (sostiene el Principio "Ciclo agéntico correcto" y la
puerta de pruebas deterministas de #10). Una sola dependencia nueva (`claude-agent-sdk`).

## Puntos a confirmar en implementación

- Firma exacta de `receive_response()` / tipos de mensaje (`AssistantMessage`, `ResultMessage`) y campo real de la razón de parada por turno, contra la doc instalada de `claude-agent-sdk`.
- Prerrequisito de runtime del SDK (Claude Agent CLI/Node) y su efecto en CI: las pruebas deterministas NO deben requerirlo (de ahí la inyección del stream en `consume`).
- Forma exacta del contenido MCP que debe devolver el adaptador de `registrar_triage` para exponer `structuredContent`.
