# Plan de implementación: Subagente de revisión de cobertura (`revisor-cobertura`)

**Rama**: `009-coverage-review-subagent` | **Fecha**: 2026-10-15 | **Especificación**: `specs/009-coverage-review-subagent/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/009-coverage-review-subagent/spec.md`

## Resumen

Se define el subagente `revisor-cobertura` como `AgentDefinition` (opción `agents` del SDK), con
herramientas restringidas a `consultar_poliza` y `verificar_cobertura`, y un prompt versionado. El
agente principal lo invoca con la tool `Agent` (hay que habilitarla en `allowed_tools`), le pasa
contexto explícito y, ante un veredicto `incierto`, escala (regla 5, por prompt). El veredicto se
modela con `CoverageVerdict` (Pydantic) + un parser testeable. Construye sobre #6 y convive con #7.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas; `claude-agent-sdk` ya está)

**Pruebas**: `pytest`, colocadas (`agent/test_coverage.py`), **deterministas sin LLM**

**Restricciones**: tools del subagente exactamente 2; `incierto→escalar` por prompt (regla 5 = juicio, como se fijó en #7); claves inglés, valores español (Principio VI)

## Verificación de la constitución

*PUERTA: aprobar antes de implementar.*

- **Principio I (reglas por hooks / estado de resultados)**: `incierto→escalar` es regla 5 = juicio ⇒ instrucción del prompt, NO hook (coherente con la decisión de #7). CUMPLE.
- **Principio IV (estructurado)**: el veredicto se modela con `CoverageVerdict` validado. CUMPLE.
- **Principio VI (idioma)**: claves de `CoverageVerdict` en inglés, valores en español; prompt del subagente en español. CUMPLE.
- **Enunciado, behavior #10**: subagente con tools limitadas a su rol, delegación con contexto explícito. CUMPLE.

Sin violaciones.

## Estructura del proyecto (paquete `agent/`)

```text
src/cordillera/agent/
├── coverage.py                   # NUEVO — CoverageVerdict + parse_coverage_verdict + build_coverage_reviewer() -> AgentDefinition
├── coverage_reviewer_prompt.md   # NUEVO — prompt versionado del subagente (español)
├── prompt.py                     # MODIF — + load_coverage_reviewer_prompt()
├── system_prompt.md              # MODIF — guía de delegación + escalar ante incierto
├── core.py                       # MODIF — build_options: agents={"revisor-cobertura":...} + "Agent"/"Task" en allowed_tools
├── test_coverage.py              # NUEVO — pruebas deterministas
└── (test_agent.py)               # MODIF — el test de allowed_tools de #6 ahora incluye "Agent"/"Task"
```

## Decisiones técnicas (API de subagentes, verificada contra `claude-agent-sdk==0.2.168` + docs)

**Definición**: `AgentDefinition(description, prompt, tools, model)` registrada en
`ClaudeAgentOptions.agents["revisor-cobertura"]`. `tools` = `["mcp__cordillera__consultar_poliza",
"mcp__cordillera__verificar_cobertura"]` (solo esas; lo omitido no existe para el subagente).
`model="inherit"` (usa el modelo principal; configurable).

**Invocación**: el agente principal delega con la tool **`Agent`** (en el init figura como `"Task"`).
Hay que **habilitarla en `allowed_tools`** del principal; agrego `"Agent"` y `"Task"` (robustez entre
versiones del CLI). Las 2 tools de cobertura ya están en `allowed_tools` (de #6), así que el subagente
las usa autoaprobadas. **Impacto**: el test de #6 `test_build_options_...` afirma exactamente 7 tools →
se actualiza para incluir `Agent`/`Task`.

**Veredicto**: un subagente del SDK devuelve **texto** (su mensaje final). Como sus tools están
restringidas a las 2 de cobertura, NO se valida con una tool in-process. Por eso:
- `CoverageVerdict` (Pydantic) es el **contrato de forma**: `covered: Literal["si","no","incierto"]`,
  `coverage_type: str | None`, `deductible: int | None`, `tow_covered: bool | None`, `reason: str | None`.
- `parse_coverage_verdict(text) -> CoverageVerdict` valida un veredicto (JSON); entrada inválida → error.
- El prompt del subagente le indica emitir ese JSON (se le inyecta el esquema/campos).
- **En runtime, el modelo principal lee el texto del subagente y decide escalar** (regla 5); el parser
  es contrato + utilidad testeable (y disponible para la interfaz de chat #9). La ejecución real de la
  delegación es #12.

**Delegación con contexto explícito** (system prompt principal): se agrega la instrucción de delegar la
cobertura en `revisor-cobertura` pasando póliza, fecha, tipo de siniestro, uso del vehículo y la
pregunta del asegurado (lo que el subagente necesita, porque solo recibe el prompt de invocación — no
hereda la conversación).

## Modelo de datos y contratos

- `CoverageVerdict` (nuevo, `agent/coverage.py`): campos arriba. Mapeo al issue: `cubierto→covered`, `amparo→coverage_type`, `grua_cubierta→tow_covered`, `motivo→reason`. Lo no mencionado queda nulo.
- `build_coverage_reviewer() -> AgentDefinition`: arma la definición con las 2 tools y el prompt cargado.
- Reutiliza `verificar_cobertura`/`consultar_poliza` del servidor (contrato ya existente).

## Estrategia de pruebas (deterministas, sin LLM)

- `CoverageVerdict`/`parse_coverage_verdict`: veredicto válido (incl. `incierto`) → validado; `covered` inválido → error; `tow_covered` ausente → `None`.
- `build_coverage_reviewer()`: `tools` == exactamente las 2 de cobertura; `description` y `prompt` presentes; prompt cargado de su `.md`.
- `build_options()`: `agents` contiene `revisor-cobertura`; `allowed_tools` incluye `Agent` y las 2 tools de cobertura; el system prompt menciona la delegación y el escalamiento ante `incierto`.
- `load_coverage_reviewer_prompt()`: lee del artefacto versionado.
- Regresión: la suite de #6/#7 sigue verde (con el `allowed_tools` actualizado).

La ejecución real (que el agente invoque al subagente, pase contexto y escale) es #12.

## Puntos a confirmar en implementación

- Nombre exacto a habilitar en `allowed_tools` para la delegación (`Agent` vs `Task`): agrego ambos por robustez; confirmar en runtime (#12).
- Que el modelo principal reciba el veredicto del subagente de forma utilizable (verbatim vs resumido); el prompt principal puede pedir preservarlo. Confirmar en #12.

## Seguimiento de complejidad

Sin violaciones. El veredicto se modela como contrato Pydantic + parser (lógica pura testeable), igual
que `registrar_triage`. Sin dependencias nuevas. El único efecto colateral es habilitar la tool de
delegación en `allowed_tools`, que obliga a actualizar un aserto del test de #6.
