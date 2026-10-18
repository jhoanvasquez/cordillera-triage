---
description: "Lista de tareas para el ecosistema: hooks + comando /ship"
---

# Tareas: Ecosistema — hooks + comando /ship

**Entrada**: Documentos de diseño en `specs/016-ecosystem-hooks-ship/`

**Prerrequisitos**: plan.md, spec.md. Reusa los subagentes + `ticket-flow` de #14.

**Pruebas**: pipes de JSON de muestra (exit codes) + `settings.json` JSON válido; `pytest` sigue verde.

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Hooks (scripts)

- [x] T001 [P] [US1] `.claude/hooks/require_spec.py` (PreToolUse): lee stdin → `tool_input.file_path`; fuera de `src/` → exit 0; bajo `src/` sin `specs/<rama>/spec.md` → exit 2 + stderr; con spec → exit 0. A prueba de fallos (excepción → exit 0).
- [x] T002 [P] [US2] `.claude/hooks/block_real_ids.py` (PreToolUse): lee stdin UTF-8; escanea `content`/`new_string` **repo-wide** y bloquea (exit 2 + stderr) una placa `[A-Z]{3}[0-9]{3}` o documento `\d{8,11}` **solo en contexto de identidad/placa** (keyword ES+EN adyacente). Sin contexto (montos, timestamps, `CHK###`, `ERR-001`) → exit 0; `FIC`/`DOC-FIC` → exit 0. A prueba de fallos.
- [x] T003 [P] [US3] `.claude/hooks/format.sh` (PostToolUse, vía `bash`): extrae `file_path` del stdin con `python -c` (sin `jq`); si `.py` → `ruff format`; exit 0 siempre.

---

## Fase 2: Cableado + comando

- [x] T004 [US1/US2/US3] `.claude/settings.json`: agregar `hooks.PreToolUse` (matcher `Edit|Write` → `require_spec.py` + `block_real_ids.py`) y `hooks.PostToolUse` (matcher `Edit|Write` → `bash format.sh`). JSON válido.
- [x] T005 [US4] `.claude/skills/ship/SKILL.md`: comando versionado (`argument-hint: "<issue-number>"`, `disable-model-invocation: true`) cuyo cuerpo orquesta code-reviewer + compliance-reviewer → PR `Closes #<issue>` → In review + comentario (reusa `ticket-flow`). Si un revisor marca CRITICAL/NO CUMPLE → arreglar antes del PR.

---

## Fase 3: Validación

- [x] T006 Pipes de JSON: `require_spec` (src/ sin spec → 2; con spec → 0; no-src → 0); `block_real_ids` (`{"documento":"<8–11>"}` → 2; `{"placa":"<3+3>"}` → 2; `cédula <8–11>` UTF-8 → 2; monto/timestamp/`CHK-001`/`ERR-001` sin contexto → 0; `DOC-FIC-0001`/`FIC-01A` → 0); `format.sh` (`.py` → ruff; `.md` → no-op).
- [x] T007 `settings.json` JSON válido; `/ship` frontmatter válido; `pytest` → suite sigue verde.

---

## Dependencias y orden

- T001–T003 independientes (archivos distintos). T004 depende de T001–T003 (los cablea). T005 independiente. Validación (T006/T007) al final.

## Notas

- Hooks a prueba de fallos (excepción → exit 0): un bug del hook no rompe el flujo.
- `block_real_ids` matchea por **contexto de identidad** (keyword adyacente), no "a secas": una placa 3+3 colisiona con IDs de código (`CHK###`, `ERR-001`) y un run 8–11 dígitos con montos/timestamps/teléfonos. Alta precisión → escanea repo-wide; el invariante lo respalda el check de CI/pre-commit (constitución, Principio II). Lee stdin UTF-8 por las keywords acentuadas (`cédula`) en Windows.
- Portabilidad: blockers en Python; `format.sh` vía `bash` (hay git bash; `.sh` pelado falla en Windows).
- `/ship` reusa los recursos de #14 (subagentes + `ticket-flow`); el plugin que los empaqueta es #16.
- Commits Conventional, sin atribución a IA (Principio V).
