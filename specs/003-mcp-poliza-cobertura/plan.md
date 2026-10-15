# Plan de implementación: MCP — consultar_poliza + verificar_cobertura

**Rama**: `003-mcp-poliza-cobertura` | **Fecha**: 2026-10-15 | **Especificación**: `specs/003-mcp-poliza-cobertura/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/003-mcp-poliza-cobertura/spec.md`

## Resumen

Agrega dos herramientas al servidor MCP `cordillera`, reutilizando el loader, el envelope
(`errors.py`) y el patrón service/server de #2. Añade los modelos `PolizaDetalle`,
`RespuestaPoliza` y `RespuestaCobertura`, y la lógica pura de ambas herramientas en `service.py`.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas; reutiliza `mcp<2` + `pydantic`)

**Dependencias principales**: ninguna nueva

**Almacenamiento**: fixtures JSON de #1 vía el loader de #2

**Pruebas**: `pytest`, colocadas (`test_cobertura.py` nuevo)

**Plataforma objetivo**: stdio

**Tipo de proyecto**: proyecto único (servidor MCP)

**Restricciones**: envelope `structuredContent`-always (#2); `cubierto ∈ {si,no,incierto}`; dominio en español

**Escala/Alcance**: 2 herramientas; ~6 pólizas

## Verificación de la constitución

*GATE: debe pasar antes de implementar.*

- **Principio I (Hooks vs. prompt)**: CUMPLE — `verificar_cobertura` solo **reporta** `cubierto`; la regla 5 (`incierto` → escalar) la decide el agente/subagente (#8), no la herramienta.
- **Principio IV (Estructurado)**: CUMPLE — envelope reutilizado + modelos Pydantic.
- **Principio II/III/VI**: CUMPLE — solo lee fixtures; spec precede; artefacto en español.

Sin violaciones.

### Alcance de la falla transitoria

La simulación de `transient` está **centralizada** en el camino de búsqueda/identidad (#2, registro
`DOC-FIC-9999`, que no tiene vehículo ni póliza). Estas herramientas **no la re-disparan**; su
superficie de error es `validation`/`business`. El caso #7 (falla transitoria) del agente se ejercita
con las herramientas de #2.

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/003-mcp-poliza-cobertura/
├── spec.md
├── plan.md      # este archivo
└── tasks.md     # siguiente paso
```

### Código fuente (extiende el paquete existente)

```text
src/cordillera/mcp_server/
├── models.py          # + PolizaDetalle, AmparoDetalle, RespuestaPoliza, RespuestaCobertura
├── service.py         # + consultar_poliza(), verificar_cobertura()
├── server.py          # + registro de las 2 herramientas con descripciones distintas
└── test_cobertura.py  # pruebas colocadas nuevas (si/no/incierto, vencida, vacío, errores)
```

**Decisión de estructura**: extender los módulos existentes (no crear un paquete nuevo) porque son
herramientas del mismo servidor. Las pruebas de #3 van en `test_cobertura.py` separado, para
trazabilidad por ticket. *Alternativa descartada:* un segundo servidor MCP — innecesario y rompería
el "un solo servidor del escenario".

## Modelo de datos y contratos

### Modelos Pydantic (añadidos)

- `AmparoDetalle`: `tipo`, `cubierto` (`Literal["si","no","incierto"]`), `condiciones`.
- `PolizaDetalle`: `id`, `numero`, `asegurado_id`, `vehiculo_id`, `vigencia_desde`, `vigencia_hasta`, `deducible`, `amparos: list[AmparoDetalle]`.
- `RespuestaPoliza`: `ok`, `poliza: PolizaDetalle | None`, `error`.
- `RespuestaCobertura`: `ok`, `cubierto: Literal["si","no","incierto"] | None`, `motivo: str | None`, `deducible: int | None`, `error`.

### Lógica (`service.py`)

- **consultar_poliza(placa)**: busca el vehículo por placa; si no existe → `ok=true`, `poliza=None` (vacío, no error); si existe → arma `PolizaDetalle` desde la póliza vinculada.
- **verificar_cobertura(numero_poliza, tipo, fecha)** — orden de evaluación:
  1. Si el número de póliza **no existe** → **error `business`** (no vacío; ver FR-009 del spec).
  2. Si `fecha` **fuera de vigencia** → `cubierto="no"`, motivo "La póliza no estaba vigente en la fecha del siniestro" (prevalece sobre el amparo).
  3. Si **no hay amparo** del `tipo` → `cubierto="no"`, motivo "El amparo {tipo} no está contratado".
  4. En otro caso → `cubierto = amparo.cubierto`; motivo = `amparo.condiciones` (o un texto por defecto); incluye `deducible` de la póliza.

### Descripciones distintas (behavior #3)

- `consultar_poliza`: "Devuelve la póliza **completa** de un **vehículo específico** (vigencia, amparos, deducibles). Si el asegurado tiene varios vehículos y el reporte no dice cuál, **pregunta primero; no adivines**."
- `verificar_cobertura`: "Responde **una sola pregunta**: ¿el tipo X está cubierto por la póliza P en la fecha D? Devuelve `cubierto: si|no|incierto` con motivo. Úsala antes de abrir un reclamo o de responder una duda de cobertura (p. ej. la grúa)."

## Seguimiento de complejidad

Sin violaciones. Sin dependencias nuevas; reutiliza toda la infraestructura de #2.
