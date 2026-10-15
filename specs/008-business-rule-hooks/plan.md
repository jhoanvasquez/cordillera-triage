# Plan de implementación: Hooks de reglas de negocio (reglas 1 y 2, +3)

**Rama**: `008-business-rule-hooks` | **Fecha**: 2026-10-15 | **Especificación**: `specs/008-business-rule-hooks/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/008-business-rule-hooks/spec.md`

## Resumen

Se agrega un **estado de sesión derivado de resultados de herramientas** (`SessionState`) y los
**hooks del SDK** que hacen cumplir las reglas 1, 2 y la parte determinista de la 3. Hooks
**PostToolUse** pueblan el estado desde los resultados de `verificar_identidad`, `consultar_poliza`,
`verificar_cobertura` y `registrar_triage`. Un hook **PreToolUse** `guard_abrir_reclamo` niega la
apertura salvo que `state.motivos_bloqueo()` esté vacía. Un hook **PreToolUse** sobre
`escalar_a_ajustador` fuerza `prioridad=alta` ante lesiones. Todo se cablea en `build_options` (#6).

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas; `claude-agent-sdk` ya está desde #6)

**Pruebas**: `pytest`, colocadas (`agent/test_hooks.py`), **deterministas sin LLM** (estado y hooks llamados directamente)

**Restricciones**: estado SOLO desde resultados de herramientas (Principio I); el loop termina por el SDK (#6); campos inglés, valores/motivos de dominio español (Principios IV/VI)

## Verificación de la constitución

*PUERTA: aprobar antes de implementar.*

- **Principio I (reglas por hooks; estado solo de resultados)**: ESTE es el ticket que lo materializa. Reglas 1, 2 y el bloqueo por lesiones de la 3 son hooks deterministas; el estado se deriva de `tool_response`, nunca de texto del modelo. CUMPLE (es su razón de ser).
- **Principio IV (estructurado)**: el estado se arma de resultados estructurados de las tools; `motivos_bloqueo()` es determinista. CUMPLE.
- **Principio VI (idioma)**: identificadores/campos en inglés; valores de dominio y motivos (de cara al modelo) en español. `motivos_bloqueo` conserva su nombre español (contrato del issue). CUMPLE.
- **Reglas 4 y 5**: siguen siendo instrucciones del prompt (#6); NO se convierten en hooks aquí (salvo el gate `cobertura si` del guard, defensa en profundidad). CUMPLE con el alcance.

Sin violaciones.

## Estructura del proyecto (paquete `agent/`)

```text
src/cordillera/agent/
├── state.py        # NUEVO — SessionState (+ motivos_bloqueo, record_*, injuries_reported)
├── hooks.py        # NUEVO — callbacks PreToolUse/PostToolUse + build_hooks(state) + extract_structured
├── core.py         # MODIF — build_options(model, state=None) adjunta hooks; run() crea el estado
├── test_hooks.py   # NUEVO — pruebas deterministas de estado y hooks
└── (test_agent.py) # MODIF menor — build_options() sin estado sigue verde (hooks solo si hay estado)
```

## Decisiones técnicas (API de hooks, verificada contra `claude-agent-sdk==0.2.168`)

**Registro**: `ClaudeAgentOptions.hooks: dict[event, list[HookMatcher]]`. `HookMatcher(matcher="<nombre tool>", hooks=[callback])`. Callback async `(input, tool_use_id, context) -> SyncHookJSONOutput`.

**Matchers**: por nombre MCP completo — `mcp__cordillera__abrir_reclamo`, `mcp__cordillera__escalar_a_ajustador`, `mcp__cordillera__verificar_identidad`, `mcp__cordillera__consultar_poliza`, `mcp__cordillera__verificar_cobertura`, `mcp__triage__registrar_triage`.

**Negar** (`guard_abrir_reclamo`, PreToolUse):
```python
return {"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "<motivos> — escala a un ajustador.",
}}
```
Si `motivos_bloqueo()` está vacía → `{}` (permite).

**Modificar input** (`force_priority_on_injuries`, PreToolUse sobre `escalar_a_ajustador`): si el estado indica lesiones, devolver `permissionDecision:"allow"` + `updatedInput` con el `handoff` y `priority="alta"` (sobrescribe lo del modelo). Sin lesiones → `{}`.

**Poblar el estado** (PostToolUse): leen `input.tool_response` (el resultado de la tool) y actualizan el `SessionState` (capturado por closure). Devuelven `{}`.

**Seam incierto — forma de `tool_response`**: `PostToolUseHookInput.tool_response` es `Any`; su forma concreta para tools MCP la fija el CLI en runtime. Se aísla en `extract_structured(tool_response) -> dict` (defensivo: usa `structuredContent` si está; si no, parsea el texto JSON de `content` — necesario para `registrar_triage`, cuyo bridge in-process solo devuelve `content`). La lógica de registro se prueba contra dicts limpios; la forma exacta se confirma end-to-end en #12.

## Modelo de datos y contratos

`SessionState` (`agent/state.py`), campos derivados de resultados (todos opcionales, defaults "no logrado"):
- `identity_verified: bool = False`, `insured_id: str | None = None`
- `policy_valid_from / policy_valid_to / policy_number: str | None` (de `consultar_poliza`)
- `coverage: Literal["si","no","incierto"] | None = None` (de `verificar_cobertura`)
- `triage: Triage | None = None` (validado, de `registrar_triage`; da `severity`, `injuries_reported`, `incident_date`)

Métodos:
- `record_identity/record_policy/record_coverage/record_triage(resp: dict)` — setean campos solo si `ok` y el hecho es afirmativo (p. ej. identidad solo si `verified=true`).
- `injuries_reported -> bool` (del triage).
- `motivos_bloqueo() -> list[str]` **pura**: agrega motivos
  1. sin identidad verificada,
  2. póliza no vigente en la fecha (`policy_valid_from <= triage.incident_date <= policy_valid_to`, comparación ISO como en `service.py:204/267`; falta de póliza o fecha ⇒ bloquea),
  3. severidad ≠ `leve` (incl. triage ausente),
  4. lesiones reportadas,
  5. cobertura == `no` (solo un `no` afirmativo bloquea; `incierto`/sin verificar NO — regla 5 va por prompt).
  Vacía ⇒ se puede abrir.

**Política más reciente**: el estado guarda la última póliza/cobertura consultada (el prompt #6 guía a consultar el vehículo correcto). Refinamiento posible (no en #7): exigir que `numero_poliza` de `abrir_reclamo` coincida con la póliza del estado.

## Estrategia de pruebas (deterministas, sin LLM)

- `motivos_bloqueo()`: estados a mano → sin identidad bloquea con su motivo; póliza fuera de fecha bloquea; `moderada`/`grave` bloquea; lesiones bloquea; cobertura `no`/`incierto` bloquea; todo en orden + `leve` ⇒ vacía.
- `guard_abrir_reclamo` **llamado directamente** (criterio del issue): con estado sin identidad → salida con `permissionDecision:"deny"` y motivo que sugiere escalar; con estado completo `leve` → permite.
- `force_priority_on_injuries`: estado con lesiones + handoff `prioridad=media` → `updatedInput` con `priority="alta"`; sin lesiones → sin cambios.
- `record_*`: contra `tool_response` sintéticos (forma `model_dump()` del server, y el JSON-en-content de `registrar_triage`) → el estado queda bien poblado; resultados con `ok=false` no marcan el hecho.
- `build_options(state=...)` adjunta `hooks` con los matchers correctos; `build_options()` sin estado no rompe (test de #6 sigue verde).

Las pruebas con modelo real (que el CLI realmente niegue la tool) son #12.

## Puntos a confirmar en implementación

- Forma exacta de `tool_response` en runtime para tools MCP (aislada en `extract_structured`).
- Que el matcher use el nombre MCP completo (`mcp__cordillera__abrir_reclamo`) y no el bare; confirmar contra el comportamiento del CLI.
- Que `updatedInput` sobre una tool MCP del server externo se respete (forzado de prioridad).

## Seguimiento de complejidad

Sin violaciones. El estado y `motivos_bloqueo()` se diseñan como lógica pura separada de los callbacks, para probar el cumplimiento sin modelo ni CLI (sostiene el Principio I y la puerta determinista de #10). Sin dependencias nuevas.
