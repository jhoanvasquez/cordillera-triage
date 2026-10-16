---
description: "Lista de tareas para la capa de pruebas de escenario e2e (modelo real)"
---

# Tareas: Capa de pruebas de escenario e2e (modelo real)

**Entrada**: Documentos de diseño en `specs/013-e2e-scenario-tests/`

**Prerrequisitos**: plan.md, spec.md. Depende de #6–#10 (ya en `main`).

**Pruebas**: Los e2e SON las pruebas (capa 2, modelo real, opt-in). La suite por defecto debe quedar verde con los e2e salteados.

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Harness + marker

- [x] T001 `pyproject.toml`: registrar el marker `e2e` en `[tool.pytest.ini_options] markers` (evita warnings; permite `pytest -m e2e`).
- [x] T002 [US1] `src/cordillera/agent/scenario.py`: `ScenarioResult` (`tool_trace`, `state`, `text`) + `run_scenario(messages, *, model=DEFAULT_MODEL) -> ScenarioResult` que corre el agente real (reusa `build_options`/`SessionState`/`ClaudeSDKClient`), captura `ToolUseBlock.name` y `TextBlock.text` del stream por turno hasta `ResultMessage`. Helpers `called(trace, name)` (endswith) y `delegated(trace)` (`Agent`/`Task`).

---

## Fase 2: Los 8 casos obligatorios

- [x] T003 [US1] `src/cordillera/agent/test_e2e_scenarios.py`: `pytestmark = [pytest.mark.e2e, pytest.mark.skipif(not RUN_E2E, ...)]` + los 8 tests (guiones con los datos ficticios existentes), cada uno asertando sobre trace/outcome (no wording):
  1. Mensaje ejemplo (lesión) → escala `prioridad alta` + cobertura revisada + sin claim.
  2. Choque leve → `abrir_reclamo` + `claim_id`; sin escalamiento.
  3. Pide persona → escala; sin `abrir_reclamo`.
  4. Dos vehículos → sin claim, texto con `?` (preguntó).
  5. Póliza vencida → sin claim; cobertura `no` o escala.
  6. Sin identidad → `claim_id is None` (invariante `claim_id ⇒ identity_verified`).
  7. Transitoria (`DOC-FIC-9999`) → run completa sin crash; `buscar_asegurado` en trace; manejo con gracia.
  8. Cobertura incierta (reparto) → escala o `coverage == "incierto"`; sin claim.

- [x] T004 [US2] En el caso 7, verificar explícitamente el **manejo con gracia** del error transitorio (sin excepción no manejada; escala o respuesta clara), usando el flaky record (#10).

---

## Fase 3: Validación

- [x] T005 Suite por defecto: `pytest` → la capa determinista queda verde y los 8 e2e **salteados** (RUN_E2E no seteado).
- [x] T006 **Smoke-test en vivo**: `RUN_E2E=1` con `model="claude-sonnet-4-6"` (override barato) sobre 1–2 casos (ej. leve-auto-open y bloqueo-sin-identidad) para validar auth + wiring. Si la auth no alcanza desde este contexto, reportarlo (los tests quedan escritos/corribles).
- [x] T007 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- **T001** y **T002** primero (marker + harness). **T003/T004** dependen de T002. **T005** tras T003. **T006** (smoke) tras T005.

## Notas

- Aserción sobre comportamiento (trace de tools + `SessionState`), nunca sobre wording → robusto al no-determinismo.
- Opt-in `RUN_E2E=1` para evitar gasto accidental de tokens; la suite por defecto nunca corre el modelo.
- Las tool-calls internas del subagente no aparecen en el trace principal (solo `Agent`); por eso cobertura se aserta como `delegated(trace)` OR `verificar_cobertura`.
- Esta capa valida los seams pendientes (forma de `tool_response`/`ToolUseBlock`, delegación real, contexto multi-turno).
- Commits Conventional, sin atribución a IA (Principio V).
