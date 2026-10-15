# Cordillera Triage Constitution

First-contact auto-claims triage agent for *Aseguradora Cordillera*, built with the
Claude Agent SDK and a scenario MCP server. This constitution captures the principles
every ticket must respect. The business rules and severity criteria below are quoted
**verbatim in Spanish** on purpose: the brief states they are non-negotiable, so they are
reproduced, not translated or paraphrased.

## Core Principles

### I. Business Rules Guaranteed by Hooks, Not Prompts (NON-NEGOTIABLE)
Anything whose violation is a **business, security or compliance failure is enforced with a
hook** (SDK or Claude Code); **style and judgment calls go in instructions**. A business rule
that depends only on the prompt is a grave fault.
- Session state is built **only from tool results**, never from what the model says.
- Rules 1 and 2 (and the deterministic part of rule 3) are **SDK hooks**. Rules 4 and 5 are
  judgment calls → instructions + the coverage subagent.
- Determining severity is judgment (prompt + schema); acting on severity is a rule (hook).

### II. Fictitious Data Only (NON-NEGOTIABLE)
No real-looking data anywhere in the repository — not in fixtures, logs, tests, or config.
- Fake identifiers use impossible-by-design shapes that cannot match real Colombian formats:
  documents as `DOC-FIC-0001`, plates as `FIC-01A`. A reserved `FIC`/`DOC-FIC` marker is
  mandatory.
- A PreToolUse hook (`block_real_ids`) and a CI/pre-commit check reject anything shaped like
  a real ID or plate before the file exists.

### III. Spec-Driven Development (NON-NEGOTIABLE)
No production code under `src/**` without a backing `spec.md`, `plan.md` and `tasks.md`.
- A PreToolUse hook (`require_spec`) blocks writes under `src/**` unless
  `specs/<current-branch>/spec.md` exists. Config tickets don't produce production code, so the
  hook guards only `src/**`.
- Functional requirements live in `spec.md`; architecture/technical decisions in `plan.md`;
  project principles here; ecosystem mechanism choices in `DECISIONES.md`. Separation is by
  artifact, not a post-hoc split.
- Spec Kit artifacts are versioned; they are evidence reviewed in the defense.

### IV. Structured Over Free Text
Triage and tool I/O are validated against schemas, never free text.
- Triage is produced as structured output (Pydantic): tipo de siniestro, severidad, lesiones
  reportadas, terceros, datos faltantes. **What the report does not mention stays null; the
  agent does not invent it.**
- Tools return the native MCP shape (`isError`, `content`, `structuredContent`). Errors carry
  `errorCategory` in `transient | validation | business | permissions` and `isRetryable`.
  **An empty search is not an error** (`isError: false`, `resultCount: 0`).
- Convention: MCP transport/error envelope in English; domain values in Spanish
  (`severidad: leve|moderada|grave`, `cubierto: si|no|incierto`).

### V. Autonomous Traceability
The GitHub Project and issues are the single source of truth and update themselves.
- Tickets move Todo → In progress (start) → In review (PR) → Done (merge) without manual edits.
- Every PR references and closes its issue; every issue gets progress comments.
- Commits follow Conventional Commits (`<type>(<scope>): <subject>`), no AI attribution. An
  evaluator must be able to reconstruct the project from GitHub alone.

## Business Rules & Severity Criteria (verbatim — no se negocian)

**Criterios de severidad de la aseguradora:**
- **Leve**: Daños en piezas exteriores. El vehículo puede seguir circulando.
- **Moderada**: Daños que impiden circular o que afectan partes mecánicas o eléctricas.
- **Grave**: Posible pérdida total, incendio o volcamiento.

**Reglas de negocio de la aseguradora, que tu solución debe respetar:**
1. Ningún reclamo se abre sin identidad verificada del asegurado y sin confirmar que la póliza estaba vigente en la fecha del siniestro.
2. Un siniestro de severidad leve puede abrirse como reclamo de forma automática. Uno de severidad moderada o grave requiere un ajustador humano.
3. Si el reporte menciona lesiones a personas, el caso se escala a un ajustador con prioridad alta, sin importar la severidad del daño.
4. Si el asegurado pide explícitamente hablar con una persona, se escala de inmediato, sin investigar primero.
5. Si la póliza no cubre el caso con claridad, por ejemplo un vehículo particular que estaba haciendo domicilios, el agente escala en lugar de improvisar.

**Enforcement mapping (hooks vs instructions):**

| Rule | Mechanism | Where |
|---|---|---|
| 1 — identity + policy valid | **Hook** | PreToolUse `abrir_reclamo` denies unless identity verified AND policy valid on claim date |
| 2 — leve auto, moderada/grave human | **Hook** | PreToolUse `abrir_reclamo` denies unless severity `leve`; else escalate |
| 3 — injuries → escalate, prioridad alta | **Hook** | PreToolUse `escalar_a_ajustador` forces `prioridad = alta`; `abrir_reclamo` denied if injuries |
| 4 — asks for a human → escalate now | Instruction | System prompt; no investigation first |
| 5 — coverage unclear → escalate | Instruction + subagent | `revisor-cobertura`; `incierto` → escalate |

## Security, Secrets & Quality Gates

- **Secrets** are never read or modified from Claude Code: `permissions.deny` on `Read/Edit`
  of `.env*` and `**/secrets/**`. No credential, `.env`, or token in the repo or the delivery
  `.zip` — git history cannot be rewritten, so a leak is permanent.
- **Formatting** runs after every edit: PostToolUse hook → `ruff format` on the edited file.
- **Independent review before PR**: a `code-reviewer` subagent (fresh context, read-only) and a
  `compliance-reviewer` subagent (business rules 1–5 vs this constitution) run before opening a
  PR, orchestrated by `/ship`.
- **Correct agentic loop**: the loop ends on the model's stop reason — never on an iteration
  count or by matching words in the text.

## Governance

This constitution supersedes other practices for this repository. The business rules and
severity criteria are fixed by the assessment brief and MUST NOT be altered. Other principles
may be amended by updating this file with a version bump and a one-line rationale; amendments
must keep the repo consistent with the brief. Every spec, plan and review verifies compliance
with these principles; any added complexity must map to a real need or be removed.

**Version**: 1.0.0 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-14
