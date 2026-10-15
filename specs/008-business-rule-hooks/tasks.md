---
description: "Lista de tareas para los hooks de reglas de negocio (reglas 1 y 2, +3)"
---

# Tareas: Hooks de reglas de negocio (reglas 1 y 2, +3)

**Entrada**: Documentos de diseño en `specs/008-business-rule-hooks/`

**Prerrequisitos**: plan.md, spec.md. Depende de #6 (ya en `main`).

**Pruebas**: INCLUIDAS, deterministas sin LLM (SC-001..005, FR-007).

**Organización**: por historia de usuario. `state.py` es la base; luego hooks; luego el cableado.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias)

---

## Fase 3: Historia de usuario 1 - Estado de sesión desde resultados de herramientas (Prioridad: P1)

### Implementación

- [x] T001 [US1] `agent/state.py`: `SessionState` (campos derivados de resultados: `identity_verified`, `insured_id`, `policy_valid_from/to`, `policy_number`, `coverage`, `triage`) + `record_identity/record_policy/record_coverage/record_triage(resp: dict)` (setean solo si `ok` y el hecho es afirmativo) + propiedad `injuries_reported`. Campos en inglés; valores de dominio en español.
- [x] T002 [US1] `agent/hooks.py`: `extract_structured(tool_response) -> dict` (usa `structuredContent` si está; si no, parsea el JSON del `content` — para `registrar_triage`) + callbacks PostToolUse que llaman a los `record_*` del estado y devuelven `{}`. (depende de T001)

### Pruebas

- [x] T003 [P] [US1] `agent/test_hooks.py`: `record_*` contra `tool_response` sintéticos (forma `model_dump()` del server y JSON-en-`content` de `registrar_triage`) → el estado queda bien poblado; un resultado con `ok=false` (o `verified=false`) NO marca el hecho.

**Punto de control**: el estado se deriva solo de resultados de herramientas.

---

## Fase 4: Historia de usuario 2 - `guard_abrir_reclamo` niega por defecto (Prioridad: P1) 🎯

### Implementación

- [x] T004 [US2] `agent/state.py`: `motivos_bloqueo() -> list[str]` **función pura** con los motivos (sin identidad; póliza no vigente en la fecha vía comparación ISO `valid_from <= triage.incident_date <= valid_to`; severidad ≠ `leve`; lesiones; cobertura == `no`). Vacía ⇒ se puede abrir. **Revisado contra el enunciado**: solo `cobertura no` bloquea (`incierto`/sin verificar no; regla 5 va por prompt) para no falso-bloquear el caso "leve → apertura automática". (depende de T001)
- [x] T005 [US2] `agent/hooks.py`: `guard_abrir_reclamo` (PreToolUse) → si `state.motivos_bloqueo()` no está vacía, devuelve `permissionDecision:"deny"` con `permissionDecisionReason` = motivos unidos + "escala a un ajustador"; si está vacía, `{}` (permite). (depende de T004)

### Pruebas

- [x] T006 [P] [US2] `agent/test_hooks.py`: (a) `motivos_bloqueo()` por caso con estados a mano (cada motivo + caso permitido); (b) `guard_abrir_reclamo` **llamado directamente** → sin identidad devuelve `deny` con motivo que sugiere escalar; con estado completo y `leve` permite.

**Punto de control**: el guard niega determinísticamente en cada caso de bloqueo y permite solo cuando corresponde.

---

## Fase 5: Historia de usuario 3 - `escalar_a_ajustador` fuerza prioridad alta (Prioridad: P1)

### Implementación

- [x] T007 [US3] `agent/hooks.py`: `force_priority_on_injuries` (PreToolUse sobre `escalar_a_ajustador`) → si `state.injuries_reported`, devuelve `permissionDecision:"allow"` + `updatedInput` con el `handoff` y `priority="alta"`; sin lesiones, `{}`. (depende de T001)

### Pruebas

- [x] T008 [P] [US3] `agent/test_hooks.py`: estado con lesiones + handoff `prioridad=media` → `updatedInput` con `priority="alta"`; sin lesiones → sin cambios.

**Punto de control**: la prioridad alta ante lesiones es determinista, no depende del modelo.

---

## Fase 6: Cableado en el agente (#6)

### Implementación

- [x] T009 [US1] `agent/hooks.py`: `build_hooks(state) -> dict[event, list[HookMatcher]]` con los matchers por nombre MCP completo (`mcp__cordillera__verificar_identidad`, `...consultar_poliza`, `...verificar_cobertura`, `mcp__triage__registrar_triage` → PostToolUse; `mcp__cordillera__abrir_reclamo`, `...escalar_a_ajustador` → PreToolUse). `agent/core.py`: `build_options(model, state=None)` adjunta `hooks=build_hooks(state)` solo si hay estado; `run()` crea un `SessionState` y lo pasa.

### Pruebas

- [x] T010 [P] [US1] `agent/test_hooks.py`: `build_options(state=...)` adjunta `hooks` con los matchers correctos; `build_options()` sin estado no rompe (el test de #6 sigue verde).

**Punto de control**: los hooks quedan cableados sin romper el loop ni la conexión MCP.

---

## Fase N: Pulido

- [x] T011 Ejecutar `pytest` — toda la suite en verde.
- [x] T012 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- **T001** (estado base) primero. **T002** depende de T001; **T004** depende de T001; **T005** depende de T004; **T007** depende de T001.
- US1 (T001→T002→T003), US2 (T004→T005→T006) y US3 (T007→T008) pueden solaparse tras T001 (distintos métodos/archivos), con T005 esperando a T004.
- **T009** (cableado) depende de T002/T005/T007; **T010** depende de T009.
- Pulido (T011–T012) al final.

## Notas

- Estado SOLO desde resultados de herramientas (Principio I); `motivos_bloqueo()` es lógica pura separada de los callbacks para testear sin LLM.
- El guard del agente es la **primera** barrera; el server (`open_claim`, #4) ya valida rule 1 como segunda barrera — no se elimina.
- Reglas 4 y 5 siguen siendo prompt (#6); el guard solo bloquea ante `cobertura no` (red determinista), no ante `incierto` (esa es la regla 5 = juicio del prompt, y luego el subagente #8). La interfaz de chat es #9; las pruebas con modelo real/e2e son #12.
- A confirmar en implementación (ver plan.md): forma exacta de `tool_response` en runtime (aislada en `extract_structured`); que el matcher use el nombre MCP completo; que `updatedInput` se respete sobre una tool del server externo.
- Commits Conventional, sin atribución a IA (Principio V).
