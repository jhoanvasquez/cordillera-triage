# Plan de implementación: Capa de pruebas de escenario e2e (modelo real)

**Rama**: `013-e2e-scenario-tests` | **Fecha**: 2026-10-16 | **Especificación**: `specs/013-e2e-scenario-tests/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/013-e2e-scenario-tests/spec.md`

## Resumen

Un harness `run_scenario` corre un guion de conversación contra el agente real (reusando #6–#9) y captura
el **trace de tool-calls** (de los `ToolUseBlock` del stream) + el `SessionState` final + el texto. Los
8 casos obligatorios se escriben como tests marcados `e2e`, que asertan sobre trace/outcome (no wording).
La suite por defecto los excluye/saltea (opt-in `RUN_E2E=1`), así la capa determinista (#10) sigue verde
sin modelo. Se hace un smoke-test en vivo para validar el harness.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12. **Pruebas**: `pytest`, `test_e2e_scenarios.py`. **Runtime e2e**: modelo real (`claude-agent-sdk` + `claude` CLI/Node + auth).

## Verificación de la constitución

- **Principio I**: las aserciones se basan en el trace de tools y en `SessionState` (poblado de resultados), no en texto del modelo. CUMPLE.
- **Principio III (SDD)**: spec/plan/tasks presentes. CUMPLE.
- **Enunciado — casos obligatorios**: los 8 casos existen y son corribles. CUMPLE (verde depende de auth del evaluador).

Sin violaciones.

## Estructura del proyecto

```text
src/cordillera/agent/
├── scenario.py            # NUEVO — run_scenario(messages) -> ScenarioResult (harness e2e)
└── test_e2e_scenarios.py  # NUEVO — los 8 casos, @pytest.mark.e2e + skipif RUN_E2E
pyproject.toml             # MODIF — registrar el marker `e2e`
```

## Decisiones técnicas

**Harness** (`scenario.py`):
```python
@dataclass
class ScenarioResult:
    tool_trace: list[str]   # nombres de tools llamadas, en orden
    state: SessionState     # estado final (identity, coverage, triage, claim_id, escalation)
    text: str               # texto del agente concatenado

async def run_scenario(messages, *, model=DEFAULT_MODEL) -> ScenarioResult:
    state = SessionState(); options = build_options(model=model, state=state)
    async with ClaudeSDKClient(options=options) as client:
        for m in messages:
            await client.query(m)
            async for msg in client.receive_response():
                # AssistantMessage.content: recolectar ToolUseBlock.name y TextBlock.text
                ... hasta ResultMessage (fin del turno)
    return ScenarioResult(trace, state, text)
```
- El trace sale de `ToolUseBlock.name` en el stream. Las tools MCP aparecen como `mcp__cordillera__...`; la delegación al subagente aparece como `Agent` (las tool-calls internas del subagente corren en su contexto y NO aparecen en el trace principal). Helpers: `called(trace, "abrir_reclamo")` = `any(t.endswith(...))`; `delegated(trace)` = `"Agent" in trace or "Task" in trace`.
- `SessionState` ya captura `identity_verified`, `coverage`, `triage` (severidad/lesiones), `claim_id`, `escalation_*` vía los hooks PostToolUse (#7/#9) — base de las aserciones de outcome.

**Marker + skip-guard** (`test_e2e_scenarios.py`):
```python
pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not os.environ.get("RUN_E2E"),
                       reason="e2e opt-in: set RUN_E2E=1 (needs model auth; spends tokens)"),
]
```
`pyproject` registra el marker `e2e` (evita warnings). Por defecto `pytest` saltea los e2e (RUN_E2E no seteado) → la capa determinista sigue verde. `RUN_E2E=1 pytest -m e2e` los corre.

**Aserciones por caso** (comportamiento, no wording):
1. Lesión → `state.escalation_id` seteado, `escalation_priority == "alta"`; cobertura revisada (`delegated(trace)` o `called(trace,"verificar_cobertura")`); `state.claim_id is None`.
2. Leve sin heridos → `called(trace,"abrir_reclamo")` y `state.claim_id`; `state.escalation_id is None`.
3. Pide persona → `state.escalation_id`; `not called(trace,"abrir_reclamo")`.
4. Dos vehículos → `state.claim_id is None` y `not called(trace,"abrir_reclamo")`; el texto final contiene `?` (preguntó).
5. Póliza vencida → `state.claim_id is None`; `state.coverage == "no"` o `state.escalation_id`.
6. Sin identidad → `state.claim_id is None` (invariante: `claim_id ⇒ identity_verified`).
7. Transitoria (`DOC-FIC-9999`) → el run completa sin excepción; `called(trace,"buscar_asegurado")`; manejo con gracia (escala o respuesta no vacía).
8. Cobertura incierta (reparto) → `state.escalation_id` o `state.coverage == "incierto"`; `state.claim_id is None`.

Cada test tolera el no-determinismo: afirma el invariante central del caso, no una secuencia exacta.

**Smoke-test en vivo** (validación del harness): correré 1–2 casos (p. ej. caso 2 leve-auto-open y caso 6 bloqueo) con `RUN_E2E=1`, usando un modelo más barato (`claude-sonnet-4-6`) vía el override de `run_scenario`, para validar auth + wiring sin quemar tokens de Opus. Si la auth no funciona desde este contexto, se reporta: los tests quedan escritos y corribles; el evaluador los corre con su `.env`.

## Modelo de datos y contratos

- `ScenarioResult` (nuevo). Reutiliza `build_options`/`SessionState`/`ClaudeSDKClient`/`AssistantMessage`/`ToolUseBlock`/`ResultMessage` de #6–#9. Guiones basados en los datos ficticios existentes (ver tabla del spec).

## Estrategia de pruebas

- Los e2e SON las pruebas (capa 2). No hay unit tests del harness más allá de que la suite por defecto siga verde (e2e salteados) y que el smoke-test en vivo valide el harness.
- Regresión: `pytest` por defecto → 82 verdes + 8 e2e salteados.

## Puntos a confirmar en el smoke-test (los seams pendientes)

- Forma real de `ToolUseBlock.name` para tools MCP (`mcp__cordillera__...` vs bare) — los helpers usan `endswith`, robustos.
- Que la delegación aparezca como `Agent`/`Task` y que el contexto conversacional persista entre `query()`.
- Forma de `tool_response` en los hooks PostToolUse (hasta ahora aislada en `extract_structured`).
- Que la auth del `claude` CLI alcance para correr sin `ANTHROPIC_API_KEY` en el entorno.

## Hallazgos del smoke-test en vivo (modelo real, sonnet)

El smoke-test cumplió su propósito: validó el harness y destapó dos cosas.

1. **Bug CRÍTICO (arreglado)**: la forma real de `tool_response` de las tools MCP es un **string JSON**
   (p. ej. `'{"ok":true,"verified":true,...}'`), no un dict. `extract_structured` no lo manejaba →
   devolvía `{}` → el `SessionState` **nunca se poblaba** en runtime → el guard de #7 habría bloqueado
   todo y el chat de #9 no mostraría eventos. Los tests deterministas lo enmascaraban (mockeaban dicts).
   **Fix**: rama de string-JSON en `extract_structured` + test determinista que fija la forma real.
   Confirmado en vivo: `identity_verified: True`, `coverage` poblado.
2. **Refinamiento de cobertura (aplicado)**: el agente/subagente verificaba cobertura por el nombre del
   tipo de siniestro (`colisión`) en vez de por el **amparo contratado** (`danos`) → cobertura `no` para
   un daño cubierto → el caso leve no abría. **Fix**: guía en `system_prompt.md` y
   `coverage_reviewer_prompt.md` para evaluar contra los amparos de la póliza. Confirmado en vivo: caso 2
   abre `claim_id: RCL-0001` con `coverage: si`.

Caminos críticos validados en vivo (sonnet): caso 2 (auto-open) y caso 6 (bloqueo sin identidad: el
agente no abre). Los 6 casos restantes quedan escritos/corribles; el evaluador los corre con su auth.

## Seguimiento de complejidad

Sin violaciones. El harness es delgado sobre #6–#9; las aserciones son por comportamiento. Sin
dependencias nuevas. El único cambio fuera de tests es registrar el marker `e2e` en `pyproject`.
