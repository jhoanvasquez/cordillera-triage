# Especificación de funcionalidad: Ecosistema — plugin + marketplace + 2 MCP servers

**Rama de funcionalidad**: `017-ecosystem-plugin-mcp`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #16. Ecosistema (parte 4/4): empaquetar piezas reutilizables como un plugin
instalable + marketplace, y registrar los 2 servidores MCP (`github` + `cordillera`) en `.mcp.json`.
"Dog-fooding": el repo habilita su propio plugin desde `.claude/settings.json`. Resuelve la necesidad #11
(otro equipo instala tus piezas reutilizables) y el mínimo "2 servidores MCP (github + cordillera), sin
credenciales en el repo".

**Formatos confirmados como nativos**: `.claude-plugin/plugin.json` (manifest), `.claude-plugin/marketplace.json`
(marketplace), `.claude/settings.json` (`enabledPlugins` + `extraKnownMarketplaces`), `.mcp.json` (`mcpServers`
con expansión `${VAR}`). Rutas del manifest relativas al plugin root.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Plugin `cordillera-devkit` empaqueta piezas reutilizables (Prioridad: P1)

Un plugin versionado `cordillera-devkit` empaqueta un subconjunto **curado y sin dependencias cruzadas** de
las piezas de las partes 2–3: el subagente `code-reviewer`, la skill `design-review` y el hook `format.sh`
(≥1 subagente + ≥1 skill + ≥1 hook). Tiene su propio `.claude-plugin/plugin.json`.

**Por qué este subconjunto**: son genéricos y autocontenidos — útiles para cualquier equipo, sin referenciar
piezas fuera del plugin. (`ship` se descarta: depende de `compliance-reviewer` + `ticket-flow`; `compliance-reviewer`
es específico del dominio seguros, menos reutilizable.)

**Por qué esta prioridad**: Necesidad #11 (piezas reutilizables instalables por otro equipo).

**Prueba independiente**: `plugins/cordillera-devkit/.claude-plugin/plugin.json` es JSON válido, declara `name`,
y referencia 1 agente + 1 skill + 1 hook que existen en el paquete.

**Escenarios de aceptación**:

1. **Dado** el plugin, **Entonces** `plugin.json` es válido y declara ≥1 subagente, ≥1 skill y ≥1 hook.
2. **Dado** cada recurso declarado, **Entonces** el archivo referenciado existe dentro del paquete.
3. **Dado** el subconjunto, **Entonces** ninguna pieza referencia otra pieza fuera del plugin.

---

### Historia de usuario 2 - Marketplace instalable desde el repo (Prioridad: P1)

Un `.claude-plugin/marketplace.json` en la raíz declara el marketplace y una entrada `plugins[]` que apunta
al plugin (`source: "./plugins/cordillera-devkit"`), de modo que otro equipo haga
`/plugin marketplace add <owner/repo>` → `/plugin install cordillera-devkit@<marketplace>`.

**Por qué esta prioridad**: Necesidad #11; el mínimo "plugin reutilizable por otro equipo".

**Prueba independiente**: `marketplace.json` es JSON válido, declara `name`, `owner` y una entrada cuyo `source`
resuelve a un directorio con `.claude-plugin/plugin.json`.

**Escenarios de aceptación**:

1. **Dado** `marketplace.json`, **Entonces** es JSON válido con `name`, `owner` y `plugins[]`.
2. **Dado** la entrada del plugin, **Entonces** su `source` apunta al paquete del plugin en el repo.

---

### Historia de usuario 3 - El repo habilita su propio plugin (dog-fooding) (Prioridad: P1)

`.claude/settings.json` registra el marketplace local (`extraKnownMarketplaces` → `source: directory, path: "."`)
y habilita el plugin (`enabledPlugins: ["cordillera-devkit@<marketplace>"]`).

**Por qué esta prioridad**: el issue pide que el repo "enable su propio plugin desde settings.json".

**Prueba independiente**: `settings.json` sigue JSON válido y contiene ambas claves con el id del plugin correcto.

**Escenarios de aceptación**:

1. **Dado** `settings.json`, **Entonces** `extraKnownMarketplaces` apunta al marketplace local (`directory`, `.`).
2. **Dado** `settings.json`, **Entonces** `enabledPlugins` incluye `cordillera-devkit@<marketplace>`.
3. **Dado** que el plugin trae `format.sh` (idempotente), **Entonces** un doble disparo con el hook nativo es inofensivo.

---

### Historia de usuario 4 - `.mcp.json` registra los 2 servidores MCP (Prioridad: P1)

`.mcp.json` declara `github` (http, toolset `projects` por header, token desde `${GITHUB_PERSONAL_ACCESS_TOKEN}`)
y `cordillera` (stdio, el server del escenario). **Cero credenciales literales.**

**Por qué esta prioridad**: el mínimo "2 servidores MCP (github + cordillera), sin credenciales en el repo".

**Prueba independiente**: `.mcp.json` es JSON válido, `mcpServers` tiene exactamente `github` y `cordillera`;
el token es una referencia `${...}`, no un literal; el comando de `cordillera` lanza el server del escenario.

**Escenarios de aceptación**:

1. **Dado** `.mcp.json`, **Entonces** declara `github` (http) y `cordillera` (stdio).
2. **Dado** `github`, **Entonces** el header incluye `projects` en el toolset y el token es `${GITHUB_PERSONAL_ACCESS_TOKEN}`.
3. **Dado** `cordillera`, **Entonces** el comando (`bash scripts/run_cordillera_mcp.sh`) lanza `cordillera.mcp_server.server` con el intérprete del venv y `PYTHONPATH=src`, sin depender del `python` del sistema.
4. **Dado** todo el archivo, **Entonces** no contiene ninguna credencial literal.

### Casos límite

- **Lanzamiento de `cordillera`**: el paquete no tiene `[build-system]` (no se instala); el wrapper `scripts/run_cordillera_mcp.sh` fija `PYTHONPATH=src` y elige el intérprete del venv (que tiene `mcp`/`pydantic`), porque el `python` del sistema no los tiene y fallaría silencioso. Documentado en README (#11).
- **Doble registro (comportamiento verificado en la doc de Claude Code)**: las piezas nativas de `.claude/` siguen activas; el plugin empaqueta copias curadas. Agente/skill del plugin quedan **namespaced** (`cordillera-devkit:design-review`, `cordillera-devkit:code-reviewer`) → coexisten sin colisión con los nativos (ambos aparecen en el selector; UX algo más cargada, funciona). El hook del plugin y el nativo de `settings.json` **disparan ambos** (registros independientes; el shadowing de la doc es entre dos plugins homónimos, no este caso) → por eso el hook empaquetado es `format.sh`, **idempotente**: doble disparo inofensivo.
- **Toolset de projects**: no viene habilitado por defecto en el MCP de GitHub; se habilita por header `X-MCP-Toolsets`.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: `plugins/cordillera-devkit/.claude-plugin/plugin.json` (manifest con `name`, `version`, `description`) empaqueta `code-reviewer` (agente), `design-review` (skill) y `format.sh` (hook).
- **FR-002**: El paquete contiene los archivos reales de esas 3 piezas bajo las convenciones del plugin (`agents/`, `skills/`, `hooks/`).
- **FR-003**: `.claude-plugin/marketplace.json` (raíz) declara el marketplace + la entrada del plugin (`source: "./plugins/cordillera-devkit"`).
- **FR-004**: `.claude/settings.json` agrega `extraKnownMarketplaces` (local, `directory`, `.`) y `enabledPlugins` con el id del plugin.
- **FR-005**: `.mcp.json` declara `github` (http, toolset `projects`, token `${GITHUB_PERSONAL_ACCESS_TOKEN}`) y `cordillera` (stdio, `bash scripts/run_cordillera_mcp.sh` — wrapper que elige el intérprete del venv y fija `PYTHONPATH=src`; evita el fallo silencioso del `python` del sistema sin `mcp`).
- **FR-006**: Ninguna credencial literal en `.mcp.json` ni en ningún archivo del plugin/marketplace.
- **FR-007**: `settings.json`, `.mcp.json`, `plugin.json` y `marketplace.json` siguen siendo JSON válido; `pytest` sigue verde.

### Entidades clave

- **Plugin** (`plugins/cordillera-devkit/`): `.claude-plugin/plugin.json` + `agents/code-reviewer.md` + `skills/design-review/SKILL.md` + `hooks/` (hooks.json + `format.sh`).
- **Marketplace** (`.claude-plugin/marketplace.json`): entrada que apunta al plugin.
- **MCP** (`.mcp.json`): `github` (http) + `cordillera` (stdio).

## Criterios de éxito *(obligatorio)*

- **SC-001**: `plugin.json` válido, empaqueta ≥1 agente + ≥1 skill + ≥1 hook, archivos presentes.
- **SC-002**: `marketplace.json` válido, instalable por otro equipo (entrada → plugin del repo).
- **SC-003**: `settings.json` habilita el plugin local (dog-fooding) y sigue JSON válido.
- **SC-004**: `.mcp.json` declara `github` + `cordillera`, el header de `github` incluye `projects` en el toolset, sin credenciales literales (verificable sobre el archivo, criterio verde).
- **SC-005**: `pytest` sigue verde; todos los JSON parsean.
- **SC-006** *(verificado-en-sustentación, no verde en este ticket)*: Claude Code lista items del Project y cambia un estado vía el MCP de GitHub. Requiere un token con scope `project`; queda fuera de lo verificable solo con los archivos de este ticket.

## Supuestos

- **Reutiliza, no reescribe historial**: las piezas nativas de `.claude/` quedan intactas (las describen las specs de 14/15/16, evidencia versionada); el plugin empaqueta un subconjunto curado como redistribuible.
- **`cordillera` vía intérprete del proyecto**: no hay `[build-system]`; el comando stdio usa `python -m ... ` + `PYTHONPATH=src`. Se asume el venv del proyecto activo/deps instaladas (README #11).
- **Verificación del toolset de projects** (criterio del issue "listar items del Project y cambiar un estado"): requiere un token con scope `project`; el `GITHUB_TOKEN` de esta sesión solo tiene `repo`, así que esa verificación en vivo queda fuera de alcance de los archivos de este ticket y se valida con el token adecuado en la sustentación.
- **Fuera de alcance**: README/DECISIONES/videos (#11 entregable); el server `cordillera` ya existe (tickets 002–005).
