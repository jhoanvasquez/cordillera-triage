# Plan de implementación: Interfaz de chat (consola)

**Rama**: `010-chat-interface` | **Fecha**: 2026-10-16 | **Especificación**: `specs/010-chat-interface/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/010-chat-interface/spec.md`

## Resumen

Un chat de consola que corre el agente (#6) turno a turno y muestra la conversación de forma legible,
dejando **evidente** cuándo se abre un reclamo o se escala. El loop mantiene UN `ClaudeSDKClient` y UN
`SessionState` a lo largo de la sesión (contexto conversacional). El renderizado es **lógica pura**
(testeable sin modelo). Los eventos de acción (reclamo/escalamiento) se derivan de **resultados de
herramientas** reusando la observación PostToolUse de #7 (Principio I). Sin dependencias web.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas; texto plano, Rich opcional no requerido)

**Pruebas**: `pytest`, colocadas (`agent/test_chat.py`), **deterministas sin LLM** (renderer + estado)

**Restricciones**: legibilidad > diseño; eventos desde resultados de tools (Principio I); el chat solo presenta, no reimplementa reglas; etiquetas de cara al usuario en español, código inglés (VI)

## Verificación de la constitución

*PUERTA: aprobar antes de implementar.*

- **Principio I (estado de resultados)**: los eventos de reclamo/escalamiento se derivan de resultados de herramientas (PostToolUse), no del texto del modelo. CUMPLE.
- **Principio IV / VI**: el chat solo presenta; reusa el agente. Etiquetas de cara al usuario en español; identificadores en inglés. CUMPLE.
- **Enunciado behavior #11**: terminal, legible para quien no conoce el código, acciones evidentes; sin web. CUMPLE.

Sin violaciones.

## Estructura del proyecto (paquete `agent/`)

```text
src/cordillera/agent/
├── chat.py         # NUEVO — render_* (puras) + run_chat() + __main__ (python -m cordillera.agent.chat)
├── state.py        # MODIF — + claim_id, escalation (id/priority) + record_claim/record_escalation
├── hooks.py        # MODIF — make_post_tool_use enruta abrir_reclamo→record_claim, escalar→record_escalation
├── test_chat.py    # NUEVO — pruebas deterministas (render + estado + selección de eventos nuevos)
└── (test_hooks.py) # MODIF menor — dispatch de los nuevos recorders
```

## Decisiones técnicas

**Loop de chat** (`chat.py::run_chat`): crea un `SessionState` y un `ClaudeSDKClient(build_options(state=...))`
UNA vez (persisten el contexto y los hooks de #7 a lo largo de la sesión). Por cada mensaje del
asegurado (línea de stdin): `render_insured` → `client.query(linea)` → `consume(client.receive_response())`
(reusa #6) → `render_agent(result.text)` → renderiza los **eventos nuevos** observados en el estado. EOF
o comando de salida termina limpio; un `ClaudeSDKError` se reporta claro (reusa FR-008 de #6).

**Detección de eventos** (Principio I): se extiende la observación PostToolUse de #7. `make_post_tool_use`
ya enruta por nombre de tool; se agregan dos rutas:
- `abrir_reclamo` → `state.record_claim(resp)`: si `ok`, guarda `claim_id` (de `ClaimResponse`).
- `escalar_a_ajustador` → `state.record_escalation(resp)`: si `ok`, guarda `escalation_id` y `priority`
  (de `EscalationResponse`; la prioridad es la que el hook de #7 ya forzó a `alta` ante lesiones).

El chat compara el estado antes/después de cada turno (o lleva un "ya renderizado") para emitir solo los
eventos nuevos. La prioridad/`claim_id` vienen del **resultado** de la tool (autoritativo), no del texto.

**Renderer** (puro, `chat.py`): `render_insured(text)`, `render_agent(text)`, `render_claim_opened(claim_id)`,
`render_escalation(escalation_id, priority)` → strings con etiqueta/indicador evidente (p. ej.
`Asegurado: …`, `Agente: …`, `✓ Reclamo abierto #…`, `↑ Escalado a ajustador — prioridad alta (#…)`).
Separado de la E/S para testear sin terminal ni modelo.

**Sin dependencias web**: texto plano a stdout. Rich queda opcional y NO se agrega (foco MVP del issue).

## Modelo de datos y contratos

- `SessionState` (extendido): `claim_id: str | None`, `escalation_id: str | None`, `escalation_priority: str | None` + `record_claim(resp)`, `record_escalation(resp)`. No altera `motivos_bloqueo()` (#7).
- Reusa `ClaimResponse` (`claim_id`) y `EscalationResponse` (`escalation_id`, `priority`) del servidor.
- Reusa `run`/`consume`/`build_options` de #6 y los hooks de #7.

## Estrategia de pruebas (deterministas, sin LLM)

- `render_insured`/`render_agent`: etiquetas de rol distinguibles.
- `render_claim_opened`: la línea incluye el `claim_id` y un indicador evidente; `render_escalation`: incluye la prioridad (`alta`) y es distinta de un turno de chat.
- `state.record_claim`/`record_escalation`: contra `tool_response` sintéticos (forma `model_dump()`) → guardan `claim_id`/`priority`; `ok=false` no marca.
- Dispatch de `make_post_tool_use`: `abrir_reclamo`/`escalar_a_ajustador` enrutan a los nuevos recorders.
- Selección de "eventos nuevos": dado un estado que pasa de sin-reclamo a con-reclamo, se emite exactamente un evento de reclamo (no se re-renderiza).
- Regresión: #6/#7/#8 siguen verdes.

El loop vivo (leer stdin, correr el modelo, ver los casos de prueba en la interfaz) es #12.

## Puntos a confirmar en implementación / runtime (#12)

- Que `ClaudeSDKClient` mantenga el contexto conversacional entre `query()` sucesivos (multi-turno) — confirmado por la doc; validar en #12.
- Forma exacta de `tool_response` para `abrir_reclamo`/`escalar_a_ajustador` (aislada en `extract_structured`, igual que #7).
- Interleaving exacto evento/texto dentro de un turno (se renderiza texto del agente y luego los eventos nuevos del turno).

## Seguimiento de complejidad

Sin violaciones. El renderer es lógica pura; la detección de eventos reusa el camino PostToolUse de #7
(sin un segundo mecanismo). Sin dependencias nuevas. Extender `SessionState` con `claim_id`/`escalation`
es aditivo y consistente ("hechos de sesión derivados de resultados de herramientas").
