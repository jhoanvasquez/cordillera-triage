# DECISIONES.md — mecanismos del ecosistema de Claude Code

Para cada necesidad del enunciado: **qué mecanismo elegí** y **por qué** (con la alternativa descartada).
El criterio transversal: *las reglas que no se negocian se garantizan con hooks deterministas; los juicios van
en instrucciones.* Una línea bien ubicada vale más que diez de `CLAUDE.md`.

## Necesidades del ecosistema

| # | Necesidad | Mecanismo elegido | Por qué / alternativa descartada |
|---|---|---|---|
| 1 | Quien clona recibe las convenciones sin configurar nada | `CLAUDE.md` + todo `.claude/`, `.mcp.json` y el plugin **versionados** (en settings: `enabledPlugins`, `extraKnownMarketplaces`) | Viaja con el repo, cero setup. Descarté documentar en wiki/README: exige leerlo y no lo aplica el agente. |
| 2 | Las preferencias personales no afectan a los compañeros | Separación **equipo vs personal**: `CLAUDE.md` + `.claude/settings.json` (versionados) frente a `CLAUDE.local.md` + `.claude/settings.local.json` (gitignored) | Jerarquía nativa de Claude Code. Descarté un único archivo: mezcla lo personal con lo del equipo. |
| 3 | Los tests viven junto al código, en muchas carpetas, con las mismas convenciones | Tests **colocados** (`test_*.py` en la misma carpeta) + regla por ruta `.claude/rules/tests.md` (`paths` + glob) + `pytest` (`testpaths=src`, `python_files=test_*`) | La convención se aplica donde está el código. Descarté una carpeta `tests/` espejo: se desincroniza del código que prueba. |
| 4 | No se escribe código de un ticket sin su especificación en `specs/` | Hook **PreToolUse `require_spec`**: bloquea escrituras en `src/**` salvo que exista `specs/<rama>/spec.md` | Garantía determinista. Descarté una instrucción en el prompt: es sugerencia, el modelo puede ignorarla. |
| 5 | Ningún archivo con forma de documento o placa real | Hook **PreToolUse `block_real_ids`** (match por *contexto de identidad*, repo-wide) + marcadores ficticios imposibles por diseño (`FIC`/`DOC-FIC`) + check de CI | Match por contexto de identidad porque un patrón "3 letras + 3 dígitos" u "8–11 dígitos" a secas colisiona con IDs de código, montos o timestamps (falsos positivos). Descarté revisión manual: no determinista. |
| 6 | Los secretos y variables de entorno no se leen ni modifican desde Claude Code | `.claude/settings.json` → `permissions.deny` sobre `.env*`, `**/secrets/**`, `*.pem`, `*.key` + `.gitignore` del `.env` | Barrera de permisos nativa, no criterio del modelo. Descarté confiar en el prompt: frágil ante un error. |
| 7 | El código queda formateado después de cada edición | Hook **PostToolUse `format`** → `ruff format` sobre el `.py` editado | Corre dentro del flujo de edición de Claude Code. Descarté un pre-commit de git: no actúa durante la sesión, solo al commitear. |
| 8 | Antes del PR, revisión independiente de la sesión que generó el código | Subagente **`code-reviewer`** (contexto fresco) orquestado por el comando **`/ship`** | El contexto fresco evita el sesgo de quien escribió el código. Descarté el self-review en la misma sesión: no es independiente. |
| 9 | Una revisión de cumplimiento verifica que las reglas de negocio estén implementadas como se especificaron | Subagente **`compliance-reviewer`**: checklist regla por regla contra la constitución y el enunciado (vía `/ship`) | Verifica *conformidad con la spec*, no solo que el código corra. Descarté dejarlo a los tests unitarios: no contrastan contra la constitución. |
| 10 | El estado de los tickets se mantiene sincronizado sin intervención manual | Skill **`ticket-flow`** + comando **`/ship`** sobre el **MCP de GitHub** (toolset `projects` habilitado por header) | El avance se arrastra desde el código (PR → In review; `Closes #N` → Done). Descarté mover tarjetas a mano: el enunciado lo prohíbe. |
| 11 | Otro equipo puede instalar tus piezas reutilizables | Plugin **`cordillera-devkit`** + `.claude-plugin/marketplace.json` (repo instalable); dog-fooding desde `settings.json` | Empaquetado nativo e instalable (`/plugin install`). Descarté copiar archivos a mano entre repos: no versionable ni actualizable. |

## Mínimos de componentes (todos cumplidos)

| Componente | Entregado |
|---|---|
| CLAUDE.md jerárquico | Raíz + `src/cordillera/agent/CLAUDE.md` (subdir), con `@import` de las reglas de negocio |
| Reglas en `.claude/rules/` (≥2, por ruta) | `tests.md`, `mcp-tools.md` (con `paths` + glob) |
| Subagentes (≥2, herramientas por rol) | `code-reviewer`, `compliance-reviewer` (read-only) |
| Skills (≥2; `context: fork`, `allowed-tools`, `argument-hint`) | `ship`, `ticket-flow`, `design-review` |
| Hooks (≥2; 1 bloqueante + 1 post-edición) | `require_spec`, `block_real_ids` (PreToolUse) + `format` (PostToolUse) |
| Comando propio (≥1, versionado) | `/ship <issue>` |
| Servidores MCP (2, sin credenciales) | `github` (http) + `cordillera` (stdio); token por `${GITHUB_PERSONAL_ACCESS_TOKEN}` |
| Plugin (≥1 subagente + skill + hook) | `cordillera-devkit` (code-reviewer + design-review + format) |

## Decisiones de diseño destacadas

- **Reglas por hooks, no por prompt (Principio I).** Las reglas 1, 2 y el bloqueo por lesiones de la 3 se hacen
  cumplir con hooks del SDK (`guard_abrir_reclamo`, `force_priority_on_injuries`); el chat lee los eventos desde
  los resultados de las tools (`SessionState`), nunca del texto del modelo. Las reglas 4 y 5 (juicios) van en
  instrucciones, apoyadas por el subagente `revisor-cobertura`.
- **Plugin: paquete aparte con copias curadas (no referencia in-place ni mover todo).** Elegido para no
  provocar **doble registro** con la config nativa y para no romper la **trazabilidad** de las specs previas;
  el hook empaquetado (`format`) es idempotente y un script de equivalencia guarda contra la deriva de las copias.
- **`cordillera` vía wrapper de venv.** El `python` del sistema no tiene `mcp`; el launcher elige el intérprete
  del venv y fija `PYTHONPATH=src`, para que el server no falle en silencio al arrancar sin el venv activo.

> Verificado-en-sustentación: la prueba en vivo de listar y mover items del Project vía el MCP de GitHub
> requiere un token con scope `project` (el de desarrollo tenía solo `repo`). El diseño —toolset `projects`
> declarado, token por variable de entorno, cero credenciales en el repo— está completo.
