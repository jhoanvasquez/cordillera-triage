# Plan de implementación: MCP — buscar_asegurado + verificar_identidad + error envelope

**Rama**: `002-mcp-asegurado-identidad` | **Fecha**: 2026-10-15 | **Especificación**: `specs/002-mcp-asegurado-identidad/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/002-mcp-asegurado-identidad/spec.md`

## Resumen

Diseño del servidor MCP `cordillera` (FastMCP sobre stdio) y sus dos primeras herramientas
(`buscar_asegurado`, `verificar_identidad`) sobre un envelope de respuesta/error compartido,
consumiendo las fixtures de #1. La lógica de las herramientas se separa de la capa MCP para poder
probarla sin levantar el servidor.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12

**Dependencias principales**: `mcp` (FastMCP) + `pydantic` v2 — se agregan a `pyproject.toml` en este ticket

**Almacenamiento**: fixtures JSON de #1 (solo lectura), cargadas por un loader

**Pruebas**: `pytest`, colocadas junto a cada módulo

**Plataforma objetivo**: stdio (el agente lanzará el servidor como subproceso en #6)

**Tipo de proyecto**: proyecto único (biblioteca + servidor MCP)

**Objetivos de rendimiento**: N/A (pocos registros en memoria)

**Restricciones**: forma nativa de MCP; 4 categorías de error; envelope en inglés, valores de dominio en español

**Escala/Alcance**: 2 herramientas; ~6 registros

## Verificación de la constitución

*GATE: debe pasar antes de implementar.*

- **Principio I (Hooks vs. prompt)**: CUMPLE — `verificar_identidad` solo **reporta** (verdadero/falso); la regla 1 (bloquear sin identidad) vive en el hook (#7). Defensa en profundidad server-side es del ticket #4, no de este.
- **Principio IV (Estructurado)**: CUMPLE — envelope MCP nativo + modelos Pydantic.
- **Principio II (Datos ficticios)**: CUMPLE — solo lee fixtures.
- **Principios III/VI**: CUMPLE — el spec precede; artefacto en español; campos de dominio en español, envelope en inglés.

Sin violaciones.

### Decisión del envelope (resuelto tras verificar FastMCP)

Verificación empírica sobre `mcp<2` (FastMCP v1): una herramienta devuelve un valor
(→ `structuredContent`, `isError:false`) **o** lanza una excepción (→ `isError:true`, texto en
`content`, **sin** `structuredContent`). No se pueden combinar `isError:true` + `structuredContent`
por la vía normal.

**Decisión**: `isError` protocolar queda en `false` para resultados de dominio; el estado completo
viaja en `structuredContent` con una bandera `ok`. Así los hooks (#7) leen el resultado de forma
determinista (Principio I) y "vacío no es error" sale natural. Se pina `mcp<2` y `pydantic>=2`; la
versión exacta queda en `uv.lock`. El armado del envelope se encapsula en `errors.py`.

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/002-mcp-asegurado-identidad/
├── spec.md
├── plan.md      # este archivo
└── tasks.md     # siguiente paso
```

### Código fuente (raíz del repositorio)

```text
src/cordillera/mcp_server/
├── __init__.py
├── errors.py          # categorías + helpers ok()/error() con forma MCP (encapsula isError)
├── loader.py          # carga asegurados/vehiculos/polizas desde ../data/
├── models.py          # modelos Pydantic de entrada/salida
├── service.py         # lógica PURA: buscar_asegurado(), verificar_identidad() (testeable sin MCP)
├── server.py          # FastMCP: registra las tools (envuelven service) + entrypoint stdio
├── test_errors.py
├── test_loader.py
└── test_service.py    # 0/1/N coincidencias, identidad ok/mal, cada categoría de error
```

**Decisión de estructura**: separar **lógica pura** (`service.py`) de la **capa MCP** (`server.py`).
Las pruebas golpean `service.py` directo, sin runtime MCP → deterministas y rápidas (alinea con la
capa determinista del ticket #10). *Alternativa descartada:* definir la lógica dentro de los
decoradores de herramienta en `server.py` — se descartó porque obliga a levantar MCP para probar.

## Modelo de datos y contratos

### Envelope (inglés, compartido por todas las herramientas)

`isError` protocolar siempre `false`; el estado va en `structuredContent.ok`.

```jsonc
// Éxito (búsqueda)
{ "isError": false,
  "content": [{ "type": "text", "text": "..." }],
  "structuredContent": { "ok": true, "resultados": [ ... ], "resultCount": N } }

// Error de dominio
{ "isError": false,
  "content": [{ "type": "text", "text": "..." }],
  "structuredContent": { "ok": false,
                         "error": { "errorCategory": "transient|validation|business|permissions",
                                    "isRetryable": true, "description": "..." } } }
```

### Modelos Pydantic (dominio en español)

- `BuscarAseguradoInput`: `criterio: str`, `por: Literal["documento","nombre","placa"] | None`.
- `AseguradoResumen` (salida de búsqueda): `id`, `documento`, `nombre`. **No** incluye `fecha_nacimiento` — es el dato secreto de verificación y no debe filtrarse en la búsqueda.
- `VerificarIdentidadInput`: `documento: str`, `fecha_nacimiento: str`.
- `VerificacionResultado`: `verificado: bool`, `asegurado_id: str | None`.

### Reglas de la lógica (`service.py`)

- **buscar_asegurado**: `por=documento` → match exacto; `por=nombre` → match insensible a mayúsculas (puede devolver varios, p. ej. "María Gómez"); `por=placa` → resuelve el vehículo y devuelve su asegurado; `por=None` → intenta en los tres. Criterio vacío/nulo → error `validation`. Sin coincidencias → `isError:false, resultCount:0`.
- **verificar_identidad**: busca por `documento`; si no existe → error (`validation`/`business`); si existe → `verificado = (fecha_nacimiento coincide)`. Nunca revela la fecha.
- **falla transitoria**: si el `documento` consultado es `DOC-FIC-9999` (registro `flaky`), la lógica devuelve un error `transient` reintentable (simula timeout). Determinista y testeable; da soporte al caso #7.

## Seguimiento de complejidad

> Completar solo si la Verificación de la constitución tiene violaciones que justificar.

Sin violaciones. Se agregan dos dependencias (`mcp`, `pydantic`) justificadas por el enunciado
(servidor MCP + salida estructurada validada).
