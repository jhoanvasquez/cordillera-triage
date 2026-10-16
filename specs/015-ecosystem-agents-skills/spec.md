# Especificación de funcionalidad: Ecosistema — 2 subagentes + 2 skills

**Rama de funcionalidad**: `015-ecosystem-agents-skills`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #14. Ecosistema (parte 2/4): la inteligencia de revisión — 2 subagentes de
Claude Code (read-only, tools restringidas a su rol) + 2 skills. Resuelve las necesidades del enunciado
#8 (revisión independiente pre-PR), #9 (revisión de cumplimiento), #10 (sincronización de estado de
tickets, vía `ticket-flow`), más la revisión de arquitectura en tiempo de diseño. Los comandos de Spec
Kit NO cuentan para los mínimos.

**Formatos confirmados como nativos**: `.claude/agents/*.md` (frontmatter `name`/`description`/`tools`/
`model`; allowlist = read-only sin Write/Edit); SKILL.md con `context: fork` (corre en subagente
aislado), `allowed-tools` (scopeable, incl. `mcp__github__*`) y `argument-hint`.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Subagente `code-reviewer` (revisión independiente pre-PR) (Prioridad: P1)

Un subagente read-only, de contexto fresco (≠ la sesión que escribió el código), revisa el diff antes
del PR: correctitud, edge cases, estándares, convención de idioma (VI), calidad de tests. Herramientas
restringidas: `Read, Grep, Glob, Bash(git diff:*)` (sin Write/Edit).

**Por qué esta prioridad**: Necesidad #8 del enunciado (revisión independiente de la sesión que generó el código).

**Prueba independiente**: `.claude/agents/code-reviewer.md` existe con `tools` restringidas (sin Write/Edit) y un prompt de revisión por severidad (CRITICAL/WARNING/SUGGESTION).

**Escenarios de aceptación**:

1. **Dado** el subagente, **Entonces** su frontmatter `tools` es `Read, Grep, Glob, Bash(git diff:*)` (read-only, sin Write/Edit).
2. **Dado** el prompt, **Entonces** instruye revisar el diff por severidad, verificar contra el SDK/estándares, y NO modificar archivos.

---

### Historia de usuario 2 - Subagente `compliance-reviewer` (reglas 1–5 vs constitución) (Prioridad: P1)

Un subagente read-only verifica que las reglas de negocio 1–5 estén implementadas **como se
especificaron** contra la constitución/enunciado; su salida es un **checklist pass/fail** por regla, y
marca banderas de fallo automático (regla por prompt, dato con forma real, credencial).

**Por qué esta prioridad**: Necesidad #9 del enunciado.

**Prueba independiente**: `.claude/agents/compliance-reviewer.md` existe, read-only, con un prompt que produce un checklist pass/fail de las reglas 1–5.

**Escenarios de aceptación**:

1. **Dado** el subagente, **Entonces** es read-only (sin Write/Edit) y referencia `.specify/memory/constitution.md` + `docs/business-rules.md`.
2. **Dado** el prompt, **Entonces** la salida es un checklist pass/fail por regla 1–5 + banderas de auto-fail.

---

### Historia de usuario 3 - Skill `ticket-flow` (coreografía de GitHub) (Prioridad: P1)

Un skill que posee la coreografía del Project de GitHub: `start` (mover el issue a In progress + comentar),
`pr` (abrir PR que referencia y cierra el issue + mover a In review), `done` (mover a Done al mergear).

**Por qué esta prioridad**: Necesidad #10 (estado de tickets sincronizado sin intervención manual).

**Prueba independiente**: `.claude/skills/ticket-flow/SKILL.md` existe con `argument-hint: "<issue-number> start|pr|done"` y `allowed-tools: mcp__github__*`.

**Escenarios de aceptación**:

1. **Dado** el skill, **Entonces** su frontmatter tiene `argument-hint: "<issue-number> start|pr|done"` y `allowed-tools` con `mcp__github__*`.
2. **Dado** el cuerpo, **Entonces** describe las tres transiciones (start/pr/done) usando el MCP de GitHub (issues, projects, pull_requests).

---

### Historia de usuario 4 - Skill `design-review` (arquitecto senior, forked) (Prioridad: P1)

Un skill que corre en **contexto forked** (subagente aislado), lee el `plan.md` de un ticket y devuelve
una crítica de arquitectura estructurada: riesgos, alternativa descartada, alineación SOLID/hexagonal,
sobre-ingeniería. Es el rol de "arquitecto senior": revisión acotada de artefacto, no chat interactivo.

**Por qué esta prioridad**: Revisión de arquitectura en tiempo de diseño (complementa #8/#9 pre-PR).

**Prueba independiente**: `.claude/skills/design-review/SKILL.md` existe con `context: fork`, `allowed-tools: Read, Grep, Glob`, `argument-hint: "<ticket>"`.

**Escenarios de aceptación**:

1. **Dado** el skill, **Entonces** su frontmatter tiene `context: fork`, `allowed-tools: Read, Grep, Glob` y `argument-hint: "<ticket>"`.
2. **Dado** el cuerpo, **Entonces** instruye leer `specs/<ticket>/plan.md` (+ spec) y devolver crítica estructurada (riesgos, alternativa descartada, SOLID/hexagonal, sobre-ingeniería).

### Casos límite

- **Cobertura de campos entre los 2 skills**: `context: fork` (design-review), `allowed-tools` (ambos), `argument-hint` (ambos) — el enunciado exige que entre todas las skills se usen esos tres.
- Los subagentes son **read-only**: el allowlist sin Write/Edit garantiza que no modifican archivos.
- Los recursos NO son de Spec Kit (no cuentan los `speckit-*`); son config de ecosistema genuina.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: `.claude/agents/code-reviewer.md` — read-only (`tools: Read, Grep, Glob, Bash(git diff:*)`), prompt de revisión por severidad; contexto fresco pre-PR (necesidad #8).
- **FR-002**: `.claude/agents/compliance-reviewer.md` — read-only, verifica reglas 1–5 vs constitución, salida checklist pass/fail (necesidad #9).
- **FR-003**: `.claude/skills/ticket-flow/SKILL.md` — `argument-hint: "<issue-number> start|pr|done"`, `allowed-tools: mcp__github__*`; coreografía del Project (necesidad #10).
- **FR-004**: `.claude/skills/design-review/SKILL.md` — `context: fork`, `allowed-tools: Read, Grep, Glob`, `argument-hint: "<ticket>"`; crítica de arquitectura del `plan.md`.
- **FR-005**: Entre los 2 skills DEBEN usarse `context: fork` (design-review), `allowed-tools` (ambos) y `argument-hint` (ambos) — mínimo del enunciado.
- **FR-006**: Cada subagente tiene herramientas restringidas a su rol (allowlist read-only).
- **FR-007**: Todos los artefactos con frontmatter YAML nativo válido.

### Entidades clave

- **Subagentes** (`.claude/agents/`): `code-reviewer`, `compliance-reviewer` (read-only).
- **Skills** (`.claude/skills/`): `ticket-flow` (GitHub, `mcp__github__*`), `design-review` (`context: fork`, read-only).

## Criterios de éxito *(obligatorio)*

- **SC-001**: Los 2 subagentes existen, read-only (sin Write/Edit), con tools restringidas a su rol.
- **SC-002**: Los 2 skills existen; entre ambos usan `context: fork`, `allowed-tools` y `argument-hint`.
- **SC-003**: `ticket-flow` usa `mcp__github__*`; `design-review` corre forked y lee el `plan.md`.
- **SC-004**: La suite del proyecto sigue en verde (no se tocó código).

## Supuestos

- **Formaliza lo ya probado**: `code-reviewer`/`compliance-reviewer` son los dos revisores de contexto fresco que se corrieron manualmente en cada ticket (#6–#13); ahora son recursos reutilizables. `design-review` es el rol de arquitecto senior como skill forked.
- **GitHub MCP**: `ticket-flow` asume el MCP de GitHub configurado con el toolset de projects (en `.mcp.json`; el toolset se confirma/afina en #16). Ninguna credencial en el repo.
- **No es `src/**` de producción**: config de ecosistema; igual con spec/plan/tasks (Principio III).
- **Fuera de alcance**: hooks + `/ship` que orquesta estos revisores (#15); plugin + marketplace (#16); la ejecución real de los subagentes/skills con modelo (se demuestra en uso / sustentación).
