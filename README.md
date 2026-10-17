# Cordillera Triage — agente de triage de siniestros de auto

Agente de **triage de primer contacto** para siniestros de auto de la aseguradora ficticia
**Cordillera**. A partir del reporte escrito de un asegurado, el agente lo identifica, revisa la póliza y
la cobertura, clasifica el siniestro por severidad, abre los reclamos simples de forma automática y escala
a un ajustador humano cuando corresponde. Construido con el **Claude Agent SDK** y un **servidor MCP** que
simula el core de la aseguradora.

Las reglas de negocio críticas no dependen del prompt: se **garantizan con hooks** del SDK.

## Enlaces

| Recurso | Dónde |
|---|---|
| 🎥 Video de funcionamiento | https://youtu.be/VJD03kaHi1M |
| 📦 Repositorio | https://github.com/jhoanvasquez/cordillera-triage |

## Puesta en marcha (< 5 min)

Requisitos: **Python 3.12+** y autenticación del modelo (`ANTHROPIC_API_KEY` o un `claude` CLI con sesión iniciada).

```bash
# 1. Dependencias (el repo usa uv.lock)
uv sync

# 2. Variables de entorno (no se commitean credenciales)
cp .env.example .env            # completá ANTHROPIC_API_KEY (+ GITHUB_PERSONAL_ACCESS_TOKEN para el MCP de GitHub)

# 3. Correr el chat del agente
PYTHONPATH=src uv run python -m cordillera.agent.chat
```

> **Windows (PowerShell)**: exportá la ruta con `$env:PYTHONPATH="src"` antes de correr el comando.
>
> **Sin uv**: `python -m venv .venv` → activar → `pip install "claude-agent-sdk>=0.2.168" "mcp<2" "pydantic>=2" pytest ruff` → `PYTHONPATH=src python -m cordillera.agent.chat`.

En el chat, escribí el reporte del siniestro como lo haría un asegurado (o `salir` para terminar).

## Tests

```bash
uv run pytest                    # Capa 1 — determinista, sin modelo. 82 passed, 8 skipped
RUN_E2E=1 uv run pytest -m e2e   # Capa 2 — e2e con el modelo real (opt-in; gasta tokens)
```

La capa 1 corre sin red ni modelo: valida reglas, triage, errores del MCP y la interfaz de chat de forma
determinista. La capa 2 (opt-in) corre los escenarios de punta a punta con el modelo real.

## Qué hace el agente

- **Identifica** al asegurado y **verifica identidad + vigencia de póliza** antes de abrir cualquier reclamo.
- **Clasifica** la severidad (leve / moderada / grave) según los criterios del enunciado.
- **Abre el reclamo** automáticamente solo si es leve; **escala a un ajustador** si es moderado/grave, si hay
  lesiones (prioridad alta), si el asegurado pide una persona, o si la póliza no cubre con claridad.
- **Produce un triage estructurado** (tipo, severidad, lesiones, terceros, datos faltantes) validado contra
  un esquema; lo que el reporte no dice queda nulo, no se inventa.
- **Resuelve mensajes con varias preocupaciones** (p. ej. el reporte + la pregunta por la grúa) en una
  respuesta unificada, y **pregunta** ante ambigüedad en lugar de suponer.

## Arquitectura

| Pieza | Rol |
|---|---|
| `src/cordillera/agent/` | Agente (Claude Agent SDK): ciclo agéntico, triage estructurado, chat, subagente de cobertura. |
| `src/cordillera/mcp_server/` | Servidor MCP `cordillera` (stdio): las 6 herramientas del core de la aseguradora. |
| `src/cordillera/data/` | Datos **ficticios** (`DOC-FIC-*`, `FIC-*`): asegurados, pólizas, vehículos. |
| Hooks del SDK (`agent/hooks.py`) | **Garantizan** las reglas de negocio (identidad + póliza, leve-automático, lesiones). |
| `.mcp.json` | Registra 2 servidores MCP: `github` (http) y `cordillera` (stdio). Token por variable de entorno. |

**Las reglas 1 y 2 (y el bloqueo por lesiones de la 3) se hacen cumplir con hooks, no con el prompt.** Una
regla que dependa solo del prompt es una falta grave del enunciado.

## Casos de prueba cubiertos

El mensaje de ejemplo (daño + lesión + pregunta de cobertura) · choque leve con apertura automática ·
pedido de hablar con una persona · asegurado con dos vehículos sin decir cuál · siniestro con póliza vencida ·
intento de abrir reclamo sin identidad verificada (bloqueado) · falla transitoria del MCP · caso que la
póliza no cubre con claridad.

## Ecosistema de Claude Code

El repositorio está parametrizado como lo haría un equipo: jerarquía de `CLAUDE.md`, reglas por ruta en
`.claude/rules/`, subagentes y skills en `.claude/`, hooks deterministas (`.claude/hooks/`), el comando
propio `/ship`, y el plugin reutilizable **`cordillera-devkit`** (`plugins/cordillera-devkit/`) publicado vía
`.claude-plugin/marketplace.json`. El detalle de qué mecanismo resuelve cada necesidad y por qué está en
**`DECISIONES.md`**.

## Datos y seguridad

- **Solo datos ficticios.** Todos los identificadores usan marcadores imposibles por diseño (`DOC-FIC-*`,
  `FIC-*`); un hook PreToolUse (`block_real_ids`) bloquea cualquier valor con forma de documento o placa real.
- **Sin credenciales en el repo.** Los tokens viven en variables de entorno; `.env` está gitignoreado y
  Claude Code tiene denegada la lectura/escritura de archivos de secretos.

## Ciclo de vida (SDD)

Cada ticket implementado tiene su `spec.md`, `plan.md` y `tasks.md` en `specs/<rama>/`, versionados como
evidencia. La constitución del proyecto vive en `.specify/memory/constitution.md`. El backlog y su avance se
gestionan en el GitHub Project.
