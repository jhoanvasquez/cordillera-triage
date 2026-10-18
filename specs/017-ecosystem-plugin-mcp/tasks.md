---
description: "Lista de tareas para el ecosistema: plugin + marketplace + 2 MCP servers"
---

# Tareas: Ecosistema — plugin + marketplace + 2 MCP servers

**Entrada**: Documentos de diseño en `specs/017-ecosystem-plugin-mcp/`

**Prerrequisitos**: plan.md, spec.md. Reusa piezas de #14/#15/#16 (copias curadas). Rama stackeada sobre `016`.

**Pruebas**: JSON válido de los 4 archivos + presencia de recursos + equivalencia copia↔original + sin
credenciales literales + `pytest` verde.

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Paquete del plugin

- [x] T001 [US1] `plugins/cordillera-devkit/.claude-plugin/plugin.json`: manifest (`name: "cordillera-devkit"`, `version`, `description`, `author`) que empaqueta agente + skill + hook por convención de carpetas.
- [x] T002 [P] [US1] Copiar (byte-idéntico) `code-reviewer.md` → `plugins/cordillera-devkit/agents/code-reviewer.md`.
- [x] T003 [P] [US1] Copiar (byte-idéntico) `skills/design-review/SKILL.md` → `plugins/cordillera-devkit/skills/design-review/SKILL.md`.
- [x] T004 [P] [US1] Copiar (byte-idéntico) `hooks/format.sh` → `plugins/cordillera-devkit/hooks/format.sh` + `plugins/cordillera-devkit/hooks/hooks.json` (PostToolUse `Edit|Write` → `bash ${CLAUDE_PLUGIN_ROOT}/hooks/format.sh`).

---

## Fase 2: Marketplace + habilitación + MCP

- [x] T005 [US2] `.claude-plugin/marketplace.json` (raíz): `name`, `owner`, `plugins: [{name: "cordillera-devkit", source: "./plugins/cordillera-devkit", ...}]`.
- [x] T006 [US3] `.claude/settings.json`: `extraKnownMarketplaces` (local `directory`, `.`) + `enabledPlugins: {"cordillera-devkit@cordillera-marketplace": true}`. JSON válido.
- [x] T007 [US4] `.mcp.json`: agregar `cordillera` (stdio, `bash scripts/run_cordillera_mcp.sh` — wrapper con cascada de venv + `PYTHONPATH=src`, evita el `python` del sistema sin `mcp`) junto al `github`. Cero credenciales literales.

---

## Fase 3: Validación

- [x] T008 JSON válido: `plugin.json`, `marketplace.json`, `.mcp.json`, `settings.json` parsean.
- [x] T009 Plugin: los 3 recursos existen; **equivalencia** (`scripts/check_plugin_equivalence.sh`, cmp byte-a-byte copia↔original); `cordillera` arranca vía `bash scripts/run_cordillera_mcp.sh` con el intérprete del venv (sin ModuleNotFound, cierra en EOF).
- [x] T010 Sin credenciales literales (token = `${...}`; grep de `ghp_`/`github_pat_` → 0); `pytest` → suite sigue verde.

---

## Dependencias y orden

- T001–T004 (paquete) antes de T005 (marketplace lo referencia). T006/T007 independientes. Validación (T008–T010) al final.

## Notas

- **Opción A** (paquete aparte con copias) elegida sobre B (doble registro) y C (mover, invasivo). Ver plan.
- **Namespacing verificado** (doc): skills/agents del plugin coexisten con los nativos; hook idempotente (`format.sh`) → doble disparo inofensivo.
- **Equivalencia copia↔original**: seguro barato contra deriva; pertenece además al check de CI.
- **SC-006** (listar/mover items del Project vía MCP en vivo): verificado-en-sustentación (token con scope `project`).
- Commits Conventional, sin atribución a IA (Principio V).
