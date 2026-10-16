# Especificación de funcionalidad: Ecosistema — jerarquía de CLAUDE.md + reglas path-scoped + settings

**Rama de funcionalidad**: `014-ecosystem-claude-md`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #13. Ecosistema de Claude Code (parte 1/4): jerarquía de memoria del
proyecto, settings de equipo y reglas con alcance por ruta. Resuelve las necesidades del enunciado #1
(convenciones al clonar), #2 (preferencias personales aisladas), #3 (tests colocados, mismas
convenciones) y #6 (secretos no se leen/modifican desde Claude Code). Los comandos de Spec Kit NO
cuentan para los mínimos del ecosistema.

**Formatos confirmados como nativos** (vía documentación de Claude Code): CLAUDE.md raíz + subdir (lazy),
`@path` imports (relativos al archivo), `CLAUDE.local.md` y `.claude/settings.local.json` (gitignore),
`.claude/rules/*.md` con frontmatter `paths:` (carga on-demand), `settings.json` `permissions.deny`.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Convenciones de equipo al clonar, sin configurar nada (Prioridad: P1)

Quien clona el repo recibe las convenciones del equipo automáticamente: un `CLAUDE.md` raíz **corto**
con las convenciones y un `@import` a un documento breve de reglas de negocio (detalle donde es
relevante, raíz chica). Las reglas de negocio citables viven en `docs/business-rules.md`.

**Por qué esta prioridad**: Necesidad #1 del enunciado; base del ecosistema.

**Prueba independiente**: Clonar/abrir el repo → `CLAUDE.md` raíz existe, es corto, e importa
`docs/business-rules.md` (que contiene las 5 reglas + criterios de severidad, textuales del enunciado).

**Escenarios de aceptación**:

1. **Dado** el repo, **Entonces** existe `CLAUDE.md` en la raíz con convenciones de equipo y un `@import` a `docs/business-rules.md`.
2. **Dado** `docs/business-rules.md`, **Entonces** contiene las reglas 1–5 y los criterios de severidad textuales.

---

### Historia de usuario 2 - Preferencias personales aisladas (Prioridad: P1)

Las preferencias personales no afectan a los compañeros: `CLAUDE.local.md` (memoria personal del
proyecto) y `.claude/settings.local.json` (settings personales) están **gitignorados**; las convenciones
y settings de equipo (`CLAUDE.md`, `.claude/settings.json`) se versionan.

**Por qué esta prioridad**: Necesidad #2 del enunciado.

**Prueba independiente**: `git check-ignore CLAUDE.local.md` y `.claude/settings.local.json` → ignorados; `CLAUDE.md` y `.claude/settings.json` → versionados.

**Escenarios de aceptación**:

1. **Dado** `.gitignore`, **Entonces** `CLAUDE.local.md` y `.claude/settings.local.json` están ignorados.
2. **Dado** el repo, **Entonces** `.claude/settings.json` (equipo) está versionado.

---

### Historia de usuario 3 - Reglas con alcance por ruta (Prioridad: P1)

Dos reglas path-scoped en `.claude/rules/` cargan solo al tocar los archivos que matchean (ahorra
contexto): una para tests (colocados, mismas convenciones — necesidad #3) y una para las tools MCP.

**Por qué esta prioridad**: El enunciado exige ≥2 reglas con alcance por ruta (paths + glob).

**Prueba independiente**: `.claude/rules/tests.md` tiene `paths: ["**/test_*.py"]`; `.claude/rules/mcp-tools.md` tiene `paths: ["src/cordillera/mcp_server/**/*.py"]`.

**Escenarios de aceptación**:

1. **Dado** `.claude/rules/tests.md`, **Entonces** su frontmatter tiene `paths: ["**/test_*.py"]` y convenciones de testing.
2. **Dado** `.claude/rules/mcp-tools.md`, **Entonces** su frontmatter tiene `paths: ["src/cordillera/mcp_server/**/*.py"]` y convenciones de tools (categorías de error, `isRetryable`, nombres/valores español).

---

### Historia de usuario 4 - Secretos protegidos + subdir CLAUDE.md (Prioridad: P1)

`.claude/settings.json` (equipo) deniega leer/editar secretos (necesidad #6). Un `CLAUDE.md` de
subdirectorio en `src/cordillera/agent/` (lazy) da orientación de arquitectura del agente al editar ahí.

**Prueba independiente**: `settings.json` contiene `permissions.deny` para `.env`/secretos; existe `src/cordillera/agent/CLAUDE.md`.

**Escenarios de aceptación**:

1. **Dado** `.claude/settings.json`, **Entonces** `permissions.deny` incluye `Read(.env)`, `Read(.env.*)`, `Edit(.env)`, `Edit(.env.*)`, `Read(**/secrets/**)`, `Edit(**/secrets/**)` (y afines).
2. **Dado** `src/cordillera/agent/CLAUDE.md`, **Entonces** documenta las convenciones del agente (estado desde resultados — Principio I; prompts versionados; hooks imponen reglas, el prompt guía; código inglés / prompts español).

### Casos límite

- El subdir CLAUDE.md (`agent/`) y la regla `mcp-tools.md` scopean a **directorios distintos** → sin solapamiento.
- `@import` relativo se resuelve respecto al archivo que importa (raíz → `docs/business-rules.md`).
- `settings.json` debe ser JSON válido (sin comentarios).

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: `CLAUDE.md` raíz (versionado), corto, con convenciones de equipo + `@import` a `docs/business-rules.md`.
- **FR-002**: `docs/business-rules.md` con las reglas 1–5 y los criterios de severidad textuales (enunciado).
- **FR-003**: `CLAUDE.local.md` y `.claude/settings.local.json` gitignorados; `CLAUDE.md` y `.claude/settings.json` versionados.
- **FR-004**: `.claude/rules/tests.md` con `paths: ["**/test_*.py"]` y convenciones de testing.
- **FR-005**: `.claude/rules/mcp-tools.md` con `paths: ["src/cordillera/mcp_server/**/*.py"]` y convenciones de tools.
- **FR-006**: `.claude/settings.json` con `permissions.deny` para `.env*` y `**/secrets/**` (necesidad #6).
- **FR-007**: `src/cordillera/agent/CLAUDE.md` (subdir, lazy) con convenciones del agente.
- **FR-008**: Todos los artefactos con formato nativo correcto (frontmatter YAML válido; `settings.json` JSON válido).

### Entidades clave

- **Jerarquía de memoria**: raíz `CLAUDE.md` (sesión) + subdir `agent/CLAUDE.md` (lazy) + `CLAUDE.local.md` (personal); `@import` a `docs/business-rules.md`.
- **Reglas path-scoped**: `.claude/rules/{tests,mcp-tools}.md`.
- **Settings**: `.claude/settings.json` (equipo) vs `.claude/settings.local.json` (personal, gitignore).

## Criterios de éxito *(obligatorio)*

- **SC-001**: `CLAUDE.md` raíz importa `docs/business-rules.md`; la raíz es corta.
- **SC-002**: `CLAUDE.local.md` y `.claude/settings.local.json` están gitignorados; `.claude/settings.json` versionado.
- **SC-003**: Las dos reglas tienen el frontmatter `paths` correcto; scopean a targets distintos del subdir CLAUDE.md.
- **SC-004**: `settings.json` deniega secretos y es JSON válido.
- **SC-005**: La suite de tests del proyecto sigue en verde (no se tocó código).

## Supuestos

- **Plugin enablement diferido a #16**: el issue menciona "plugin enablement" en `settings.json`, pero el plugin/marketplace es #16. Habilitar un plugin inexistente sería inerte; en #13 va el `permissions.deny` real y la estructura de settings. La habilitación (`enabledPlugins`/`extraKnownMarketplaces`) aterriza en #16.
- **Subdir CLAUDE.md en `agent/` (no `mcp_server/`)**: para no solapar con la regla path-scoped `mcp-tools.md` (que ya cubre `mcp_server/`). El criterio "subdir CLAUDE.md O @import" se satisface con ambos a targets distintos.
- **No es `src/**` de producción**: el `require_spec` hook (cuando exista, #15) protege `src/**`; igual este ticket tiene spec/plan/tasks (Principio III).
- **Fuera de alcance**: subagentes/skills de Claude Code (#14); hooks + `/ship` (#15); plugin + marketplace (#16).
