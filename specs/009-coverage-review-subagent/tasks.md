---
description: "Lista de tareas para el subagente de revisión de cobertura (revisor-cobertura)"
---

# Tareas: Subagente de revisión de cobertura (`revisor-cobertura`)

**Entrada**: Documentos de diseño en `specs/009-coverage-review-subagent/`

**Prerrequisitos**: plan.md, spec.md. Depende de #6 y #7 (ya en `main`).

**Pruebas**: INCLUIDAS, deterministas sin LLM (SC-001..004, FR-007).

**Organización**: por historia de usuario. El veredicto (US2) y el prompt son hojas; el subagente los usa; el cableado va al final.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias)

---

## Fase 3: Historia de usuario 2 - Veredicto de cobertura estructurado (Prioridad: P1)

### Implementación

- [x] T001 [US2] `agent/coverage.py`: `CoverageVerdict` (Pydantic) con `covered: Literal["si","no","incierto"]`, `coverage_type: str | None`, `deductible: int | None`, `tow_covered: bool | None`, `reason: str | None` (lo no mencionado queda nulo) + `parse_coverage_verdict(text) -> CoverageVerdict` (JSON válido → validado; inválido → error de validación). Claves inglés, valores español (mapeo al issue en el docstring).

### Pruebas

- [x] T002 [P] [US2] `agent/test_coverage.py`: veredicto válido (incl. `covered="incierto"`) → validado; `covered` fuera de `{si,no,incierto}` → error; `tow_covered` ausente → `None`.

**Punto de control**: el veredicto se valida contra un esquema, con `incierto` de primera clase.

---

## Fase 4: Historia de usuario 1 - Subagente con herramientas restringidas (Prioridad: P1) 🎯

### Implementación

- [x] T003 [US1] `agent/coverage_reviewer_prompt.md`: prompt versionado (español neutro) del subagente — rol de revisión de cobertura; usa solo `consultar_poliza`/`verificar_cobertura`; emite el veredicto como JSON conforme a `CoverageVerdict` (incl. `incierto`); no abre reclamos ni escala.
- [x] T004 [US1] `agent/prompt.py`: `load_coverage_reviewer_prompt() -> str` que lee `coverage_reviewer_prompt.md` (mismo patrón que `load_system_prompt`).
- [x] T005 [US1] `agent/coverage.py`: `build_coverage_reviewer() -> AgentDefinition` con `description`, `prompt=load_coverage_reviewer_prompt()`, `tools=["mcp__cordillera__consultar_poliza","mcp__cordillera__verificar_cobertura"]` (solo esas), `model="inherit"`. (depende de T004)

### Pruebas

- [x] T006 [P] [US1] `agent/test_coverage.py`: `build_coverage_reviewer().tools` == exactamente las 2 de cobertura; `description` y `prompt` no vacíos; el prompt se cargó del `.md` (contiene guía de cobertura/veredicto).

**Punto de control**: `revisor-cobertura` existe como `AgentDefinition` con tools limitadas a su rol.

---

## Fase 5: Historia de usuario 3 - Delegación con contexto explícito + escalar ante `incierto` (Prioridad: P1)

### Implementación

- [x] T007 [US3] `agent/system_prompt.md`: agregar guía de delegación — delegar la cobertura en `revisor-cobertura` pasando contexto explícito (nº póliza, fecha del siniestro, tipo, uso del vehículo, pregunta del asegurado); y escalar ante veredicto `incierto` (regla 5).

### Pruebas

- [x] T008 [P] [US3] `agent/test_coverage.py`: el system prompt principal contiene la guía de delegación (menciona `revisor-cobertura` y el contexto a pasar) y la instrucción de escalar ante `incierto`.

**Punto de control**: el agente principal sabe delegar con contexto explícito y escalar la cobertura no clara.

---

## Fase 6: Cableado en el agente (#6)

### Implementación

- [x] T009 [US1] `agent/core.py`: `build_options` registra `agents={"revisor-cobertura": build_coverage_reviewer()}` y agrega `"Agent"` y `"Task"` a `ALLOWED_TOOLS` (habilitar la delegación). **Actualizar** `agent/test_agent.py`: el aserto de `allowed_tools` de #6 ahora incluye `Agent`/`Task` (ya no son exactamente 7). (depende de T005)

### Pruebas

- [x] T010 [P] [US1] `agent/test_coverage.py`: `build_options()` → `agents` contiene `revisor-cobertura`; `allowed_tools` incluye `Agent` y las 2 tools de cobertura. (Regresión: `test_agent.py`/`test_hooks.py` de #6/#7 siguen verdes con el aserto actualizado.)

**Punto de control**: el subagente queda cableado sin romper el loop, los hooks ni la conexión MCP.

---

## Fase N: Pulido

- [x] T011 Ejecutar `pytest` — toda la suite en verde.
- [x] T012 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- **T001** (veredicto) y **T003→T004** (prompt) son hojas, en paralelo.
- **T005** (AgentDefinition) depende de T004. **T009** (cableado) depende de T005 y actualiza el test de #6.
- US2 (T001→T002), US1 (T003→T004→T005→T006), US3 (T007→T008); cableado (T009→T010) al final.
- Pulido (T011–T012) al final.

## Notas

- Subagente del **Agent SDK** (behavior #10), invocado con la tool `Agent` (habilitada en `allowed_tools`). Distinto de los subagentes de **Claude Code** del ecosistema (#14).
- El subagente devuelve texto; `CoverageVerdict`/`parse_coverage_verdict` es el contrato + utilidad testeable. En runtime el modelo principal lee el veredicto y decide escalar (`incierto`→escalar = regla 5 = prompt, como en #7). El consumo end-to-end es #12.
- A confirmar en runtime (#12): nombre exacto de la tool de delegación (`Agent`/`Task`); que el veredicto llegue al principal de forma utilizable.
- Commits Conventional, sin atribución a IA (Principio V).
