# Plan de implementación: Ecosistema — jerarquía de CLAUDE.md + reglas path-scoped + settings

**Rama**: `014-ecosystem-claude-md` | **Fecha**: 2026-10-16 | **Especificación**: `specs/014-ecosystem-claude-md/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/014-ecosystem-claude-md/spec.md`

## Resumen

Se crea la capa de configuración de Claude Code del proyecto con formatos **nativos** (confirmados):
`CLAUDE.md` raíz corto con `@import` a `docs/business-rules.md`, un subdir `agent/CLAUDE.md` (lazy), dos
reglas path-scoped (`tests.md`, `mcp-tools.md`), `.claude/settings.json` de equipo con `permissions.deny`
de secretos, y gitignore de los archivos personales (`CLAUDE.local.md`, `.claude/settings.local.json`).
No se toca código de producción.

## Contexto técnico

**Tipo**: configuración de ecosistema (no `src/**`). **Validación**: estructural (archivos, frontmatter YAML, JSON válido, gitignore). La suite `pytest` debe seguir verde (no cambia código).

## Verificación de la constitución

- **Principio III (SDD)**: este ticket de config igual tiene spec/plan/tasks. CUMPLE.
- **Principio V (idioma)**: artefactos/documentación en español; claves técnicas en inglés. CUMPLE.
- **Seguridad (secretos)**: `permissions.deny` materializa "los secretos nunca se leen ni modifican desde Claude Code" (constitución / necesidad #6). CUMPLE.

Sin violaciones.

## Estructura del proyecto (archivos nuevos)

```text
CLAUDE.md                                  # NUEVO — raíz, corto + @import
docs/business-rules.md                     # NUEVO — reglas 1–5 + severidad (textual)
src/cordillera/agent/CLAUDE.md             # NUEVO — convenciones del agente (subdir, lazy)
.claude/rules/tests.md                     # NUEVO — paths: ["**/test_*.py"]
.claude/rules/mcp-tools.md                 # NUEVO — paths: ["src/cordillera/mcp_server/**/*.py"]
.claude/settings.json                      # NUEVO — permissions.deny (equipo, versionado)
.gitignore                                 # MODIF — + CLAUDE.local.md, .claude/settings.local.json
```
`CLAUDE.local.md` y `.claude/settings.local.json` NO se versionan (son personales); solo se agregan al `.gitignore`.

## Decisiones técnicas (formatos nativos confirmados)

- **`CLAUDE.md` raíz**: corto. Convenciones de equipo (SDD; código inglés / dominio español; Conventional Commits sin atribución a IA; tests colocados; solo datos ficticios). Importa el detalle: `Reglas de negocio: @docs/business-rules.md` (ruta relativa al archivo).
- **`docs/business-rules.md`**: las 5 reglas y los 3 criterios de severidad, textuales del enunciado (dueño documental de las reglas de cara al equipo).
- **`src/cordillera/agent/CLAUDE.md`** (lazy al editar `agent/`): estado SOLO desde resultados de tools (Principio I); prompts versionados (`system_prompt.md`, `coverage_reviewer_prompt.md`); los hooks imponen reglas 1/2/3, el prompt guía 4/5; loop termina por la señal del SDK; código inglés, prompts/dominio español.
- **`.claude/rules/tests.md`**: frontmatter `paths: ["**/test_*.py"]`; convenciones: tests colocados junto al código; capa 1 determinista (sin LLM); capa 2 e2e opt-in (`RUN_E2E=1 pytest -m e2e`), aserción por comportamiento; `pytest` + `ruff`.
- **`.claude/rules/mcp-tools.md`**: frontmatter `paths: ["src/cordillera/mcp_server/**/*.py"]`; convenciones: envelope de error con `errorCategory ∈ {transient,validation,business,permissions}` + `isRetryable`; una búsqueda sin resultados NO es error; nombres de tools y descripciones en español; retorno Pydantic → `structuredContent`; capa delgada sobre `service.py`.
- **`.claude/settings.json`**: `permissions.deny` con `Read(.env)`, `Read(.env.*)`, `Edit(.env)`, `Edit(.env.*)`, `Read(**/secrets/**)`, `Edit(**/secrets/**)`, `Read(**/*.pem)`, `Read(**/*.key)`. JSON válido. (Plugin enablement → #16.)

## Modelo de datos y contratos

Sin modelo. Reglas de negocio citadas del enunciado (dueño documental: `docs/business-rules.md`); la constitución (`.specify/memory/constitution.md`) sigue siendo el dueño de principios.

## Estrategia de pruebas (estructural, sin código)

- `git check-ignore CLAUDE.local.md .claude/settings.local.json` → ignorados; `git check-ignore .claude/settings.json` → NO ignorado (versionado).
- `settings.json` parsea como JSON válido (`python -c "import json; json.load(...)"`).
- Las reglas tienen frontmatter `paths` válido (YAML entre `---`).
- `CLAUDE.md` raíz contiene `@docs/business-rules.md`.
- `pytest` → suite sigue verde (no se tocó código).

## Seguimiento de complejidad

Sin violaciones. Cada pieza resuelve una necesidad del enunciado (#1/#2/#3/#6) sin duplicar: subdir
CLAUDE.md (`agent/`) y regla `mcp-tools.md` (`mcp_server/`) scopean a directorios distintos. Plugin
enablement se difiere a #16 por dependencia real.
