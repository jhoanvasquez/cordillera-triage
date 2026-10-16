---
description: "Lista de tareas para el ecosistema: jerarquía CLAUDE.md + reglas path-scoped + settings"
---

# Tareas: Ecosistema — jerarquía de CLAUDE.md + reglas path-scoped + settings

**Entrada**: Documentos de diseño en `specs/014-ecosystem-claude-md/`

**Prerrequisitos**: plan.md, spec.md.

**Pruebas**: estructurales (archivos/frontmatter/JSON/gitignore); la suite `pytest` sigue verde (no se toca código).

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Memoria del proyecto (jerarquía + import)

- [x] T001 [US1] `docs/business-rules.md`: las 5 reglas de negocio y los 3 criterios de severidad, textuales del enunciado.
- [x] T002 [US1] `CLAUDE.md` (raíz, corto): convenciones de equipo (SDD; código inglés / dominio español; Conventional Commits sin atribución a IA; tests colocados; solo datos ficticios) + `@docs/business-rules.md`.
- [x] T003 [US4] `src/cordillera/agent/CLAUDE.md` (subdir, lazy): convenciones del agente (estado desde resultados — Principio I; prompts versionados; hooks imponen reglas 1/2/3, el prompt guía 4/5; código inglés, prompts español).

---

## Fase 2: Reglas path-scoped

- [x] T004 [US3] `.claude/rules/tests.md`: frontmatter `paths: ["**/test_*.py"]` + convenciones de testing (colocados; capa 1 determinista sin LLM; capa 2 e2e opt-in `RUN_E2E=1 pytest -m e2e`, por comportamiento; `pytest`/`ruff`).
- [x] T005 [US3] `.claude/rules/mcp-tools.md`: frontmatter `paths: ["src/cordillera/mcp_server/**/*.py"]` + convenciones de tools (categorías de error + `isRetryable`; sin-resultados ≠ error; nombres/descripciones español; retorno Pydantic → `structuredContent`; capa delgada sobre `service.py`).

---

## Fase 3: Settings de equipo + aislamiento personal

- [x] T006 [US4] `.claude/settings.json` (equipo, versionado): `permissions.deny` para `.env`/`.env.*`/`**/secrets/**`/`**/*.pem`/`**/*.key` (Read y Edit). JSON válido. (Plugin enablement → #16.)
- [x] T007 [US2] `.gitignore`: agregar `CLAUDE.local.md` y `.claude/settings.local.json` (personales, no versionados); confirmar que `.claude/settings.json` y `CLAUDE.md` SÍ se versionan.

---

## Fase 4: Validación

- [x] T008 Estructural: `git check-ignore CLAUDE.local.md .claude/settings.local.json` (ignorados) y `.claude/settings.json` (NO ignorado); `settings.json` parsea como JSON; `CLAUDE.md` contiene `@docs/business-rules.md`; las reglas tienen frontmatter `paths`.
- [x] T009 `pytest` → la suite sigue verde (no se tocó código).

---

## Dependencias y orden

- T001 → T002 (el import referencia el doc). T003/T004/T005/T006/T007 independientes. Validación (T008/T009) al final.

## Notas

- Subdir CLAUDE.md en `agent/` (no `mcp_server/`) para no solapar con la regla `mcp-tools.md` (targets distintos).
- Plugin enablement (`enabledPlugins`/`extraKnownMarketplaces`) se difiere a #16 (depende del plugin).
- `CLAUDE.local.md` / `settings.local.json` NO se commitean (son personales); solo van al `.gitignore`.
- Commits Conventional, sin atribución a IA (Principio V).
