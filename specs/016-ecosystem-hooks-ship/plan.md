# Plan de implementación: Ecosistema — hooks + comando /ship

**Rama**: `016-ecosystem-hooks-ship` | **Fecha**: 2026-10-16 | **Especificación**: `specs/016-ecosystem-hooks-ship/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/016-ecosystem-hooks-ship/spec.md`

## Resumen

Tres hooks (dos bloqueantes pre-ejecución + uno post-edición) cableados en `.claude/settings.json`, más
el comando versionado `/ship`. Formaliza los guardrails de la constitución y el flujo de review pre-PR.
No se toca código de producción.

## Contexto técnico

**Tipo**: config de ecosistema (no `src/**`). Scripts de hook en Python (portables) + `format.sh` vía `bash`. **Validación**: pipes de JSON de muestra (exit codes) + `settings.json` JSON válido + `pytest` verde.

## Verificación de la constitución

- **Principio III (SDD)**: `require_spec` materializa "no se escribe código en `src/**` sin spec". CUMPLE.
- **Principio II (solo datos ficticios)**: `block_real_ids` materializa "ningún archivo con forma de documento/placa real". CUMPLE.
- **Seguridad/calidad**: `format` (post-edición) + `/ship` (revisión independiente antes del PR). CUMPLE.
- **Principio V (idioma)**: artefactos/mensajes en español; código de los hooks en inglés. CUMPLE.

Sin violaciones.

## Estructura del proyecto (archivos nuevos)

```text
.claude/hooks/require_spec.py       # NUEVO — PreToolUse, bloquea src/** sin spec
.claude/hooks/block_real_ids.py     # NUEVO — PreToolUse, bloquea IDs/placas reales
.claude/hooks/format.sh             # NUEVO — PostToolUse, ruff format del .py editado
.claude/skills/ship/SKILL.md        # NUEVO — comando /ship
.claude/settings.json               # MODIF — + hooks.PreToolUse/PostToolUse
```

## Decisiones técnicas (formatos nativos confirmados)

**`require_spec.py`** (PreToolUse `Edit|Write`):
- Lee stdin como UTF-8 (`sys.stdin.buffer.read().decode("utf-8")`; en Windows stdin es cp1252 por defecto) → `tool_input.file_path`. Normaliza backslashes.
- Si NO está bajo `src/` → `exit 0` (permite).
- "Bajo `src/`" = `norm.startswith("src/")` **o** `"/src/" in norm` (cubre rutas absolutas que pasa el SDK).
  FP latente aceptado: una ruta como `docs/src/x.md` también matchearía; riesgo bajo en este repo y preferible
  a no cubrir rutas absolutas. Si apareciera, se precisa con `Path.relative_to(<raíz>/src)`.
- Si está bajo `src/`: obtiene la rama (`git rev-parse --abbrev-ref HEAD`) y la raíz del repo
  (`git rev-parse --show-toplevel`, para no depender del CWD del hook); si `<raíz>/specs/<rama>/spec.md`
  existe → `exit 0`; si no → `print(motivo, file=stderr); exit 2` (bloquea).
- A prueba de fallos: cualquier excepción → `exit 0` (no romper el flujo por un bug del hook).

**`block_real_ids.py`** (PreToolUse `Edit|Write`):
- Lee stdin como UTF-8 (keywords acentuadas como `cédula` en Windows). Escanea `tool_input.content`
  (Write) + `tool_input.new_string` (Edit) **repo-wide** (cualquier ruta).
- **Match por contexto de identidad (alta precisión).** Bloquea solo cuando la forma real aparece junto a
  una palabra/campo clave, dentro de ~20 chars en la misma línea (ventana elegida para cubrir separadores
  JSON típicos `": "` y prosa corta `cédula <número>`, sin cruzar a campos vecinos ni a otra línea; si un
  JSON pretty-print separa clave y valor >20 chars, cae en la limitación deferida a CI de abajo):
  - placa: `(?i:placa|patente|plate|license_?plate)` + gap + `\b([A-Z]{3}[0-9]{3})\b`
  - documento: `(?i:documento|cédula|cedula|identificación|nit|dni|document|national_?id)` + gap + `\b(\d{8,11})\b`
- **Motivo del contexto**: una placa (3+3) es léxicamente idéntica a IDs de código (checklist `CHK###`,
  `ERR-001`) y un run de 8–11 dígitos a montos/timestamps/teléfonos. Un match “a secas” daría FP justo
  sobre los fixtures. Exigir contexto de identidad lo vuelve de alta precisión → se escanea repo-wide (más
  fuerte que acotar por ruta). El invariante lo respalda además el check de CI/pre-commit (Principio II).
- Si matchea → `print(valor+motivo, file=stderr); exit 2`. Si no → `exit 0`.
- (Ficticios `DOC-FIC-0001`/`FIC-01A` no matchean: 4 dígitos y placa con dash/letra.)
- **Limitación conocida (deferida a CI)**: un valor con forma real **sin** contexto adyacente (p. ej. un
  volcado en un CSV donde el header está en otra línea) no lo captura el hook; lo cubre el check repo-wide
  de CI/pre-commit.

**`format.sh`** (PostToolUse `Edit|Write`, invocado `bash .claude/hooks/format.sh`):
- Lee stdin; extrae `file_path` con `python -c` (sin `jq`). Si termina en `.py` → `ruff format "$file"`.
- Busca `ruff` en cascada: `.venv/Scripts/python.exe` (Windows) → `.venv/bin/python` (Unix) → `python -m ruff`
  → `ruff`. **Decisión de alcance**: si NINGUNO existe, el hook hace **no-op silencioso** (`>/dev/null 2>&1 || true`);
  un post-hook no-bloqueante nunca debe romper el flujo por falta del formateador. El formateo verificado en
  CI es la red (no se confía solo en el hook local).
- `exit 0` siempre (post-edición no bloquea).

**`settings.json`** — agregar:
```json
"hooks": {
  "PreToolUse": [
    { "matcher": "Edit|Write", "hooks": [
      { "type": "command", "command": "python .claude/hooks/require_spec.py" },
      { "type": "command", "command": "python .claude/hooks/block_real_ids.py" }
    ] }
  ],
  "PostToolUse": [
    { "matcher": "Edit|Write", "hooks": [
      { "type": "command", "command": "bash .claude/hooks/format.sh" }
    ] }
  ]
}
```

**`/ship` SKILL.md**:
```yaml
---
name: ship
description: Orquesta el flujo pre-PR de un ticket — revisión independiente + cumplimiento, luego abre el PR y sincroniza el ticket.
argument-hint: "<issue-number>"
disable-model-invocation: true
---
```
Cuerpo: (1) correr `code-reviewer` y `compliance-reviewer` (subagentes de #14) sobre el diff/working tree;
(2) si pasan, abrir el PR con `Closes #<issue>`; (3) mover el ticket a In review y comentar el avance
(reusa `ticket-flow pr`). Si un revisor marca CRITICAL/NO CUMPLE → arreglar antes de abrir el PR.

## Modelo de datos y contratos

Sin modelo. Reutiliza los subagentes `code-reviewer`/`compliance-reviewer` y el skill `ticket-flow` (#14),
y la convención de ramas `NNN-name` ↔ `specs/NNN-name/`.

## Estrategia de pruebas (pipes de JSON, deterministas)

- `require_spec.py`: JSON `Write src/x.py` en rama sin spec → exit 2; con spec (la rama actual tiene `specs/<rama>/spec.md`) → exit 0; `Write README.md` → exit 0.
- `block_real_ids.py` (repo-wide, match por contexto): `{"documento":"<8–11 díg>"}` → exit 2; `{"placa":"<3+3>"}` → exit 2; `cédula <8–11 díg>` en prosa (UTF-8) → exit 2; `DOC-FIC-0001`/`FIC-01A` → exit 0; **sin contexto**: monto (`10.000.000`), timestamp (`2026-01-01`), teléfono, `CHK-001`, `ERR-001` → exit 0.
- **Composición de blockers** (R1): un JSON que viola AMBAS reglas a la vez (escritura a `src/x.py` en rama
  sin spec + `{"documento":"<8–11>"}`) → cada hook por separado devuelve exit 2, por lo que la escritura
  queda bloqueada sea cual sea el orden/agregación del runtime (ambos listados en el mismo matcher). Se
  verifica pipeando el mismo JSON a cada script.
- `format.sh`: JSON con `.py` → corre `ruff format` (exit 0); con `.md` → no-op (exit 0).
- `settings.json` parsea como JSON válido; `/ship` SKILL.md con frontmatter válido.
- `pytest` → suite sigue verde.

## Puntos a confirmar

- Los hooks se activan al (re)iniciar la sesión; se validan standalone por pipe y en composición (ver R1 en
  la estrategia de pruebas) antes de confiar en runtime.
- `format.sh` depende de `bash` disponible (hay git bash en el entorno; portable a Unix); documentado.

## Decisiones de alcance (gaps reconocidos)

- **`require_spec` chequea solo `spec.md`, no los tres artefactos.** El Principio III nombra `spec.md`,
  `plan.md` y `tasks.md`, pero la constitución define el *hook* como "bloquea salvo que exista
  `specs/<rama>/spec.md`" (línea 32). `spec.md` es el gate mínimo deliberado: es el primer artefacto del
  ciclo y el que habilita empezar; la completitud de los tres la verifica `/speckit.analyze` + el review
  humano, no este hook. Se documenta la diferencia para no afirmar de más.

## Seguimiento de complejidad

Sin violaciones. Cada hook resuelve una necesidad (#4/#5/#7) y `/ship` la #8 + el comando propio. Los
hooks son a prueba de fallos (excepción → exit 0) para no romper el flujo por un bug propio.

**Alternativa descartada — un hook combinado vs dos.** `require_spec` y `block_real_ids` son ambos
PreToolUse `Edit|Write` y podrían fusionarse en un `pre_write_guard.py` (un solo `json.load`). Se eligen
**dos hooks, uno por responsabilidad** (SRP): cada uno mapea a un principio (III, II), es testeable por
pipe de forma aislada y legible. El costo (parsear stdin dos veces) es despreciable frente a la claridad.
La duplicación de la normalización de `src/` entre hooks se tolera por YAGNI (son 3 hooks); si crece, se
extrae un `_hooklib.py` compartido.
