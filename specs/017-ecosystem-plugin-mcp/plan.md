# Plan de implementación: Ecosistema — plugin + marketplace + 2 MCP servers

**Rama**: `017-ecosystem-plugin-mcp` (stackeada sobre `016`) | **Fecha**: 2026-10-16 | **Especificación**: `specs/017-ecosystem-plugin-mcp/spec.md`

## Resumen

Empaqueta un subconjunto curado de las piezas del ecosistema como plugin instalable `cordillera-devkit`,
publica un marketplace en el propio repo, lo habilita (dog-fooding) desde `settings.json`, y completa
`.mcp.json` con el server `cordillera` (ya existía `github`). No se toca código de producción (`src/**`).

**Dependencia de rama**: el plugin empaqueta `format.sh` (hook de #16, aún en PR #32 sin merge), por eso `017`
stackea sobre `016`. El PR de `017` apunta a `016` (o a `main` tras mergear `016`).

## Contexto técnico

**Tipo**: config de ecosistema (no `src/**`). **Validación**: JSON válido de los 4 archivos + presencia de los
recursos empaquetados + `pytest` verde. El server `cordillera` ya existe (FastMCP stdio, `main()` en
`src/cordillera/mcp_server/server.py`).

## Verificación de la constitución

- **Principio II (solo datos ficticios / sin credenciales)**: `.mcp.json` usa `${GITHUB_PERSONAL_ACCESS_TOKEN}`, cero literales. CUMPLE.
- **Principio V (idioma)**: artefactos/descripciones en español; identificadores/JSON en inglés. CUMPLE.
- **Reutilización**: el plugin empaqueta piezas existentes sin reescribir el historial ni las ubicaciones nativas. CUMPLE.

Sin violaciones.

## Decisión de arquitectura: estructura del plugin

**Elegida — Opción A: paquete aparte con subconjunto curado** (`plugins/cordillera-devkit/` con copias de
`code-reviewer` + `design-review` + `format.sh`, su propio `.claude-plugin/plugin.json`; marketplace apunta ahí;
`settings.json` lo habilita).

**Por qué (lente MVP + rúbrica)**:
- **Traceabilidad (15%)**: no mueve archivos que las specs de 14/15/16 ya describen; el historial y la evidencia quedan coherentes.
- **No invasivo / bajo riesgo**: no re-cablea los hooks de `settings.json` (recién fijados en #16).
- **Autocontenido para otro equipo**: el trío no referencia piezas externas; `design-review` y `code-reviewer` son genéricos (un "dev-quality kit"), `format.sh` idempotente.
- **Frontera de empaquetado explícita y defendible**: `.claude/` = config de trabajo del repo; `plugins/cordillera-devkit/` = redistribuible versionado.

**Costo aceptado**: duplica 3 archivos pequeños (dos fuentes). Se mitiga (a) manteniendo el subconjunto chico y
genérico, y (b) con un **test de equivalencia copia↔original** (hash byte-a-byte de cada copia del plugin contra
su fuente en `.claude/`) — convierte "duplicación aceptada" en "duplicación controlada": cualquier deriva futura
falla la validación. El doble disparo del hook en dog-fooding es inofensivo por elegir `format.sh` (idempotente).

### Alternativas descartadas

- **B — referencia in-place (`source: "."`, plugin.json apunta a `.claude/`)**: cero duplicación, pero
  **doble registro** con la config nativa del mismo repo — hooks doble-fire, agentes/skills duplicados.
  Dog-fooding roto. Descartada.
- **C — mover las piezas al plugin (fuente única)**: dog-food real y sin duplicación, pero **invasivo**:
  mueve ubicaciones que fijaron 14/15/16 (rompe la coherencia spec↔repo, penaliza traceabilidad) y re-cablea
  los hooks de `settings.json`. Sobredimensionado para un MVP. Descartada.

## Estructura del proyecto (archivos nuevos/modificados)

```text
plugins/cordillera-devkit/.claude-plugin/plugin.json   # NUEVO — manifest
plugins/cordillera-devkit/agents/code-reviewer.md      # NUEVO — copia curada
plugins/cordillera-devkit/skills/design-review/SKILL.md# NUEVO — copia curada
plugins/cordillera-devkit/hooks/hooks.json             # NUEVO — cablea format.sh del plugin
plugins/cordillera-devkit/hooks/format.sh              # NUEVO — copia
.claude-plugin/marketplace.json                        # NUEVO — marketplace del repo
scripts/run_cordillera_mcp.sh                          # NUEVO — launcher del server (cascada de venv)
scripts/check_plugin_equivalence.sh                    # NUEVO — guard copia↔original (CI/pre-commit)
.claude/settings.json                                  # MODIF — + enabledPlugins + extraKnownMarketplaces
.mcp.json                                              # MODIF — + server cordillera (stdio, vía wrapper)
```

## Decisiones técnicas (formatos nativos confirmados)

**`plugin.json`** (`plugins/cordillera-devkit/.claude-plugin/`): `name: "cordillera-devkit"`, `version`,
`description`, `author`. Recursos por convención de carpetas del plugin (`agents/`, `skills/`, `hooks/hooks.json`)
— rutas relativas al plugin root (`plugins/cordillera-devkit/`).

**`hooks/hooks.json`** (del plugin): `PostToolUse` matcher `Edit|Write` → `bash ${CLAUDE_PLUGIN_ROOT}/hooks/format.sh`.

**`marketplace.json`** (`.claude-plugin/`): `name`, `owner`, `plugins: [{ name: "cordillera-devkit", source: "./plugins/cordillera-devkit", description, version }]`.

**`settings.json`** — agregar:
```json
"extraKnownMarketplaces": {
  "cordillera-marketplace": { "source": { "source": "directory", "path": "." } }
},
"enabledPlugins": { "cordillera-devkit@cordillera-marketplace": true }
```

**`.mcp.json`** — agregar `cordillera` junto al `github` existente:
```json
"cordillera": {
  "type": "stdio",
  "command": "bash",
  "args": ["scripts/run_cordillera_mcp.sh"]
}
```
El `command` NO es `python` pelado: el python del sistema no tiene `mcp`/`pydantic`, así que si Claude Code
arranca sin el venv activo, el server fallaría silencioso. El wrapper `scripts/run_cordillera_mcp.sh` elige el
intérprete del venv (cascada `.venv/Scripts/python.exe` → `.venv/bin/python` → `python`, misma filosofía que
`format.sh`) y fija `PYTHONPATH=src`. Portable Windows/Unix.

## Estrategia de pruebas (deterministas)

- JSON válido: `plugin.json`, `marketplace.json`, `.mcp.json`, `settings.json` parsean (`python -m json.tool`).
- Plugin: los 3 recursos declarados existen en el paquete; ninguna pieza referencia otra fuera del plugin.
- **Equivalencia copia↔original**: `scripts/check_plugin_equivalence.sh` (cmp byte-a-byte de las 3 copias del
  plugin contra sus fuentes en `.claude/`) → exit 0. Runnable hoy; pertenece al check de CI/pre-commit para la
  protección ongoing (el repo aún no tiene CI).
- **Launcher de `cordillera`**: `printf '' | bash scripts/run_cordillera_mcp.sh` → el server inicia con el
  intérprete del venv (sin `ModuleNotFoundError`) y cierra limpio en EOF.
- `.mcp.json`: `mcpServers` = {`github`, `cordillera`}; token es `${...}` (no literal); `cordillera` importable (`PYTHONPATH=src python -c "import cordillera.mcp_server.server"`).
- Sin credenciales literales (grep de tokens tipo `ghp_`/`github_pat_`/claves → 0).
- `pytest` → suite sigue verde.

## Puntos a confirmar

- **Verificación en vivo del toolset de projects** (criterio del issue: listar items + cambiar estado): necesita token con scope `project`; el `GITHUB_TOKEN` de la sesión solo tiene `repo`. La config queda correcta; la verificación en vivo se hace con el token adecuado (sustentación).
- **Lanzamiento de `cordillera`**: depende del intérprete con `mcp`/`pydantic` (venv del proyecto) + `PYTHONPATH=src`. Documentado.

## Seguimiento de complejidad

Sin violaciones. Un plugin + un marketplace + un server MCP agregado, todo mapeado a la necesidad #11 y al
mínimo de 2 MCP servers. Subconjunto del plugin deliberadamente chico (pocas piezas bien ubicadas).
