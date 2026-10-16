---
description: "Lista de tareas para el ecosistema: 2 subagentes + 2 skills"
---

# Tareas: Ecosistema — 2 subagentes + 2 skills

**Entrada**: Documentos de diseño en `specs/015-ecosystem-agents-skills/`

**Prerrequisitos**: plan.md, spec.md.

**Pruebas**: estructurales (frontmatter YAML, tools, cobertura de campos); la suite `pytest` sigue verde (no se toca código).

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Subagentes (read-only)

- [x] T001 [P] [US1] `.claude/agents/code-reviewer.md`: frontmatter (`name`, `description`, `tools: Read, Grep, Glob, Bash(git diff:*)`, `model: opus`) + prompt de revisión por severidad (CRITICAL/WARNING/SUGGESTION), verificar contra SDK/estándares, NO modificar archivos.
- [x] T002 [P] [US2] `.claude/agents/compliance-reviewer.md`: frontmatter read-only + prompt que lee `.specify/memory/constitution.md` + `docs/business-rules.md` y produce checklist **pass/fail** de reglas 1–5 + banderas de auto-fail (regla por prompt, dato con forma real, credencial).

---

## Fase 2: Skills

- [x] T003 [P] [US3] `.claude/skills/ticket-flow/SKILL.md`: frontmatter (`argument-hint: "<issue-number> start|pr|done"`, `allowed-tools: mcp__github__*`, `disable-model-invocation: true`) + cuerpo con las 3 transiciones (start → In progress + comentar; pr → PR que cierra el issue + In review; done → Done al mergear) vía MCP de GitHub.
- [x] T004 [P] [US4] `.claude/skills/design-review/SKILL.md`: frontmatter (`context: fork`, `allowed-tools: Read, Grep, Glob`, `argument-hint: "<ticket>"`) + cuerpo: leer `specs/<ticket>/plan.md` (+ spec) y devolver crítica estructurada (riesgos, alternativa descartada, SOLID/hexagonal, sobre-ingeniería, veredicto).

---

## Fase 3: Validación

- [x] T005 Estructural: frontmatter YAML válido en los 4 archivos; `code-reviewer`/`compliance-reviewer` sin Write/Edit en `tools`; entre los 2 skills aparecen `context: fork` (design-review), `allowed-tools` (ambos), `argument-hint` (ambos); `ticket-flow` tiene `mcp__github__*`.
- [x] T006 `pytest` → la suite sigue verde (no se tocó código).

---

## Dependencias y orden

- T001–T004 independientes (archivos distintos). Validación (T005/T006) al final.

## Notas

- Formaliza los revisores de contexto fresco corridos a mano en #6–#13 (reutilizables de acá en más).
- `ticket-flow` asume el MCP de GitHub con toolset de projects (en `.mcp.json`; se afina en #16).
- `/ship` (que orquesta code-reviewer + compliance-reviewer) y los hooks son #15; el plugin, #16.
- Commits Conventional, sin atribución a IA (Principio V).
