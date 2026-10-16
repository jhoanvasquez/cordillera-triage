# Especificación de funcionalidad: Ecosistema — hooks + comando /ship

**Rama de funcionalidad**: `016-ecosystem-hooks-ship`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #15. Ecosistema (parte 3/4): los guardrails deterministas — hooks que
bloquean antes de ejecutar y actúan después de editar — más el comando propio `/ship` que orquesta el
flujo pre-PR. Resuelve las necesidades del enunciado #4 (no hay código sin spec), #5 (no hay IDs/placas
reales), #7 (formateo tras edición), #8 (revisión invocada desde `/ship`) y "1 comando propio versionado".

**Formatos confirmados como nativos**: hooks en `.claude/settings.json` (`hooks.PreToolUse`/`PostToolUse`
con `matcher` por nombre de tool y `command`); input por **stdin JSON** (`tool_input.file_path`,
`tool_input.content`, `tool_input.new_string`); **bloqueo = exit 2 + stderr**; en Windows el `.sh` pelado
falla → se usa `python .../x.py` (blockers) y `bash .../format.sh` (formateo).

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Hook `require_spec` (no hay código sin spec) (Prioridad: P1)

Un hook **PreToolUse** sobre `Edit|Write` bajo `src/**` **bloquea** la escritura salvo que exista
`specs/<rama-actual>/spec.md` (exit 2 + stderr). Los tickets de config no escriben `src/**`, así que el
hook solo protege producción.

**Por qué esta prioridad**: Necesidad #4; materializa el Principio III (SDD).

**Prueba independiente**: pipe de un JSON de `Write` sobre `src/x.py` sin spec en la rama → exit 2; con spec → exit 0; sobre un archivo fuera de `src/**` → exit 0.

**Escenarios de aceptación**:

1. **Dado** `Write` sobre `src/**` sin `specs/<rama>/spec.md`, **Entonces** el hook bloquea (exit 2) con un motivo claro.
2. **Dado** que existe `specs/<rama>/spec.md`, **Entonces** permite (exit 0).
3. **Dado** un archivo fuera de `src/**`, **Entonces** permite (exit 0).

---

### Historia de usuario 2 - Hook `block_real_ids` (no hay IDs/placas reales) (Prioridad: P1)

Un hook **PreToolUse** sobre `Edit|Write` escanea el contenido a escribir y **bloquea** (exit 2) un valor
con forma de documento de identidad real o placa real **solo cuando aparece en contexto de identidad/placa**
— es decir, junto a una palabra/campo clave (`documento`, `cédula`, `placa`, `patente` y sus equivalentes
de campo en inglés `document`, `plate`, `national_id`…). Los marcadores ficticios imposibles por diseño
(`DOC-FIC-0001`, `FIC-01A`) NO se bloquean.

**Por qué el match por contexto**: una placa (3 letras + 3 dígitos) es léxicamente idéntica a identificadores
de código legítimos (checklist de Spec Kit `CHK###`, códigos de error `ERR-001`); y un run de 8–11 dígitos es
idéntico a un monto, un timestamp o un teléfono. Un match “a secas” daría falsos positivos justo sobre los
fixtures que más importa escanear. Exigir el contexto de identidad lo vuelve de alta precisión y permite
escanear **repo-wide** (más fuerte que acotar por ruta). El invariante repo-wide lo respalda además el check
de CI/pre-commit que manda la constitución (Principio II).

**Por qué esta prioridad**: Necesidad #5; falta grave del enunciado (dato con forma real).

**Prueba independiente**: `{"documento": "<8–11 dígitos>"}` o `{"placa": "<3 letras+3 dígitos>"}` → exit 2;
un monto/timestamp/teléfono sin contexto de identidad → exit 0; un `CHK-001`/`ERR-001` → exit 0;
`DOC-FIC-0001`/`FIC-01A` → exit 0.

**Escenarios de aceptación**:

1. **Dado** un valor `[A-Z]{3}[0-9]{3}` junto a `placa`/`plate`, **Entonces** bloquea (exit 2).
2. **Dado** un run de 8–11 dígitos junto a `documento`/`cédula`/`document`, **Entonces** bloquea (exit 2).
3. **Dado** `DOC-FIC-0001`/`FIC-01A`, **Entonces** permite (exit 0).
4. **Dado** una forma real **sin** contexto de identidad (monto, timestamp, teléfono, `CHK-001`, `ERR-001`), **Entonces** permite (exit 0) — alta precisión; el repo-wide lo cubre CI/pre-commit.

---

### Historia de usuario 3 - Hook `format` (formateo tras edición) (Prioridad: P1)

Un hook **PostToolUse** sobre `Edit|Write` corre `ruff format` sobre el archivo `.py` editado.

**Por qué esta prioridad**: Necesidad #7 (código formateado después de cada edición).

**Prueba independiente**: tras editar un `.py`, el hook corre `ruff format` sobre ese archivo (y no sobre no-`.py`).

**Escenarios de aceptación**:

1. **Dado** una edición de un `.py`, **Entonces** el hook corre `ruff format` sobre ese archivo (exit 0).
2. **Dado** una edición de un no-`.py`, **Entonces** el hook no hace nada (exit 0).

---

### Historia de usuario 4 - Comando propio `/ship` (orquesta el flujo pre-PR) (Prioridad: P1)

Un comando versionado `/ship <issue>` que: corre `code-reviewer` + `compliance-reviewer` (de #14) → abre
el PR con `Closes #<issue>` → mueve el ticket a In review → comenta el avance (reusa `ticket-flow`).

**Por qué esta prioridad**: Necesidad #8 (revisión independiente invocada desde `/ship`) + el mínimo "1 comando propio versionado".

**Prueba independiente**: `.claude/skills/ship/SKILL.md` existe, user-invocable, con `argument-hint`, y su cuerpo describe la secuencia (review → PR → In review → comentario).

**Escenarios de aceptación**:

1. **Dado** `/ship <issue>`, **Entonces** el cuerpo orquesta code-reviewer + compliance-reviewer, luego el PR (`Closes #<issue>`), In review y comentario.
2. **Dado** el skill, **Entonces** está versionado y es user-invocable.

### Casos límite

- **Mínimo de hooks**: ≥1 pre-ejecución bloqueante (`require_spec`, `block_real_ids`) + ≥1 post-edición (`format`). Cumplido.
- Rutas Windows con backslash → el hook normaliza antes de matchear `src/`.
- `require_spec`: la rama actual mapea a `specs/<rama>/` (los nombres coinciden, p. ej. `016-...` ↔ `specs/016-.../`).

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: `.claude/hooks/require_spec.py` (PreToolUse `Edit|Write`): bloquea (exit 2 + stderr) escrituras bajo `src/**` sin `specs/<rama>/spec.md`; permite fuera de `src/**`.
- **FR-002**: `.claude/hooks/block_real_ids.py` (PreToolUse `Edit|Write`): bloquea (exit 2) una placa (`[A-Z]{3}[0-9]{3}`) o un documento (8–11 dígitos) **solo en contexto de identidad/placa** (palabra/campo clave adyacente, ES+EN); escanea repo-wide; no bloquea `FIC`/`DOC-FIC` ni formas reales sin contexto (montos, timestamps, códigos). Lee stdin como UTF-8 (keywords acentuadas en Windows).
- **FR-003**: `.claude/hooks/format.sh` (PostToolUse `Edit|Write`): corre `ruff format` sobre el `.py` editado; invocado con `bash` (portable; parseo de stdin sin `jq`).
- **FR-004**: `.claude/skills/ship/SKILL.md` (comando versionado, user-invocable, `argument-hint: "<issue-number>"`): orquesta code-reviewer + compliance-reviewer → PR (`Closes #<issue>`) → In review → comentario.
- **FR-005**: Los hooks se cablean en `.claude/settings.json` (`hooks.PreToolUse`/`PostToolUse`, `matcher: "Edit|Write"`, `command: python/bash ...`).
- **FR-006**: ≥1 hook bloqueante pre-ejecución + ≥1 hook post-edición.
- **FR-007**: Los scripts de hook son portables (Python para los blockers; `format.sh` vía `bash`).

### Entidades clave

- **Hooks** (`.claude/hooks/`): `require_spec.py`, `block_real_ids.py`, `format.sh`; cableados en `settings.json`.
- **Comando** (`.claude/skills/ship/`): `/ship` orquesta los subagentes (#14) + `ticket-flow` (#14).

## Criterios de éxito *(obligatorio)*

- **SC-001**: `require_spec` bloquea `src/**` sin spec y permite con spec / fuera de `src/**` (verificable por pipe de JSON).
- **SC-002**: `block_real_ids` bloquea placa/documento real y permite `FIC`/`DOC-FIC`.
- **SC-003**: `format` corre `ruff format` sobre el `.py` editado.
- **SC-004**: `/ship` existe, versionado, con la secuencia review → PR → In review → comentario.
- **SC-005**: `settings.json` sigue JSON válido; la suite `pytest` sigue verde.

## Supuestos

- **Formaliza lo manual**: `/ship` es el flujo de review pre-PR que se corrió a mano en cada ticket (ahora orquesta los subagentes reales de #14). Los hooks son los guardrails que la constitución ya describía.
- **Portabilidad Windows**: blockers en Python (`python .claude/hooks/x.py`); `format.sh` vía `bash .claude/hooks/format.sh` (el `.sh` pelado falla en Windows). Decisión documentada.
- **`block_real_ids` por contexto de identidad**: una placa (3 letras + 3 dígitos) colisiona con IDs de código legítimos (checklist `CHK###`, códigos `ERR-001`) y un run de 8–11 dígitos con montos/timestamps/teléfonos. Por eso bloquea solo cuando la forma real aparece junto a una palabra/campo clave de identidad/placa (ES+EN). Alta precisión → escanea repo-wide; el invariante lo respalda el check de CI/pre-commit (constitución, Principio II). Los marcadores ficticios (`FIC`/`DOC-FIC`) son imposibles por diseño y no matchean.
- **Validación por shell**: los hooks son scripts en `.claude/hooks/` (fuera de `testpaths`); se validan con pipes de JSON de muestra (exit codes), no con `pytest`.
- **Fuera de alcance**: plugin + marketplace que empaqueta estos recursos (#16); README/DECISIONES (#11).
