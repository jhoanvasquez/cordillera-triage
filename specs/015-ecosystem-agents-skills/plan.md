# Plan de implementación: Ecosistema — 2 subagentes + 2 skills

**Rama**: `015-ecosystem-agents-skills` | **Fecha**: 2026-10-16 | **Especificación**: `specs/015-ecosystem-agents-skills/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/015-ecosystem-agents-skills/spec.md`

## Resumen

Se crean 2 subagentes read-only (`code-reviewer`, `compliance-reviewer`) y 2 skills (`ticket-flow`,
`design-review`) con formatos nativos confirmados. Formaliza los revisores de contexto fresco que se
corrieron a mano en #6–#13. No se toca código de producción.

## Contexto técnico

**Tipo**: config de ecosistema (no `src/**`). **Validación**: estructural (frontmatter YAML válido, campos y tools correctos). `pytest` sigue verde.

## Verificación de la constitución

- **Principio I (revisión independiente)**: materializa la "revisión independiente antes del PR" (code-reviewer) y la "revisión de cumplimiento" (compliance-reviewer) de la sección de calidad. CUMPLE.
- **Principio III (SDD)**: spec/plan/tasks presentes. CUMPLE.
- **Principio V (idioma)**: artefactos/prompts en español; campos/claves técnicas en inglés. CUMPLE.

Sin violaciones.

## Estructura del proyecto (archivos nuevos)

```text
.claude/agents/code-reviewer.md         # NUEVO — read-only, revisión por severidad
.claude/agents/compliance-reviewer.md   # NUEVO — read-only, checklist reglas 1–5
.claude/skills/ticket-flow/SKILL.md     # NUEVO — coreografía GitHub (mcp__github__*)
.claude/skills/design-review/SKILL.md   # NUEVO — forked, crítica de arquitectura del plan.md
```

## Decisiones técnicas (formatos nativos confirmados)

**`code-reviewer.md`**:
```yaml
---
name: code-reviewer
description: Revisión independiente de código antes del PR (contexto fresco). Correctitud, edge cases, estándares, convención de idioma, calidad de tests.
tools: Read, Grep, Glob, Bash(git diff:*)
model: opus
---
```
Cuerpo: revisar el diff; verificar contra el SDK/estándares cuando aplique; reportar por severidad
(CRITICAL merge-blocking / WARNING / SUGGESTION) con `file:line`; NO modificar archivos. Read-only por el
allowlist (sin Write/Edit).

**`compliance-reviewer.md`**:
```yaml
---
name: compliance-reviewer
description: Verifica que las reglas de negocio 1–5 estén implementadas como se especificaron, contra la constitución. Salida: checklist pass/fail.
tools: Read, Grep, Glob, Bash(git diff:*)
model: opus
---
```
Cuerpo: leer `.specify/memory/constitution.md` + `docs/business-rules.md`; verificar reglas 1–5 (hooks vs
prompt; regla 1 identidad+póliza; 2 severidad; 3 lesiones; 4 pide persona; 5 cobertura incierta); salida
= checklist **pass/fail por regla** + banderas de auto-fail (regla por prompt, dato con forma real, credencial).

**`ticket-flow/SKILL.md`**:
```yaml
---
name: ticket-flow
description: Coreografía del GitHub Project de un ticket (mover estado, comentar, abrir/cerrar PR).
argument-hint: "<issue-number> start|pr|done"
allowed-tools: mcp__github__*
disable-model-invocation: true
---
```
Cuerpo: `start` → mover issue a In progress + comentar inicio; `pr` → abrir PR que referencia y cierra el
issue + mover a In review; `done` → mover a Done al mergear. Usa el MCP de GitHub (issues, projects,
pull_requests). Resuelve necesidad #10.

**`design-review/SKILL.md`**:
```yaml
---
name: design-review
description: Crítica de arquitectura del plan.md de un ticket (riesgos, alternativa descartada, SOLID/hexagonal, sobre-ingeniería). Rol de arquitecto senior.
context: fork
allowed-tools: Read, Grep, Glob
argument-hint: "<ticket>"
---
```
Cuerpo: leer `specs/<ticket>/plan.md` (+ spec); devolver crítica estructurada: riesgos, alternativa
descartada, alineación SOLID/hexagonal/screaming, sobre-ingeniería, y un veredicto. Bounded artifact
review, no chat. Corre forked (contexto aislado), read-only.

**Cobertura de campos entre los 2 skills** (mínimo del enunciado): `context: fork` (design-review),
`allowed-tools` (ambos), `argument-hint` (ambos). ✓

## Modelo de datos y contratos

Sin modelo. Reutiliza la constitución (`.specify/memory/constitution.md`) y `docs/business-rules.md`
(dueño documental de las reglas, de #13) como fuentes del compliance-reviewer.

## Estrategia de pruebas (estructural)

- Frontmatter YAML válido en los 4 archivos; campos requeridos presentes.
- `code-reviewer`/`compliance-reviewer`: `tools` sin Write/Edit (read-only).
- Entre los 2 skills: `context: fork` (design-review), `allowed-tools` (ambos), `argument-hint` (ambos).
- `ticket-flow`: `allowed-tools` incluye `mcp__github__*`.
- `pytest` → suite sigue verde (no se tocó código).

## Seguimiento de complejidad

Sin violaciones. Cada recurso resuelve una necesidad (#8/#9/#10 + revisión de diseño); sin piezas
decorativas. Los subagentes formalizan un patrón ya probado 7 veces.
