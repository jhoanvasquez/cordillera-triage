# Plan de implementación: Esquema de triage + salida estructurada

**Rama**: `006-triage-schema` | **Fecha**: 2026-10-15 | **Especificación**: `specs/006-triage-schema/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/006-triage-schema/spec.md`

## Resumen

El esquema `Triage` ya existe (sembrado en #4) y, tras la verificación contra la fuente de verdad,
**no requiere cambios** (`severity` Literal cerrado; `claim_type` libre). Este ticket agrega el
paquete `agent/` y el tool `registrar_triage` (salida estructurada validada) más sus pruebas. El
loop del agente y el wiring del tool al SDK son #6.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas)

**Pruebas**: `pytest`, colocadas (`agent/test_triage.py`)

**Restricciones**: salida estructurada validada; `severity` cerrado, `claim_type` libre (fuente de verdad); campos inglés, valores español

## Verificación de la constitución

- **Principio IV (Estructurado)**: `registrar_triage` produce salida estructurada validada, nunca texto libre. CUMPLE.
- **Principio I**: `registrar_triage` solo valida/produce; no decide escalar/abrir. CUMPLE.
- **Principio VI**: código inglés; valores de dominio español. CUMPLE.

Sin violaciones.

## Estructura del proyecto (paquete `agent/` nuevo)

```text
src/cordillera/agent/
├── __init__.py
├── triage.py        # TriageResult + registrar_triage(data) -> TriageResult
└── test_triage.py   # nulabilidad, severidad inválida, missing_data, registrar válido/ inválido
```

## Modelo de datos y contratos

- Reutiliza `Triage` / `ThirdParties` de `mcp_server/models.py` (esquema de dominio compartido).
- `TriageResult` (nuevo, en `agent/triage.py`): `ok: bool`, `triage: Triage | None`, `error: ErrorInfo | None` (reutiliza el `ErrorInfo`/`ErrorCategory` de `mcp_server/errors.py`).

### Lógica (`agent/triage.py`)

```text
registrar_triage(data: dict) -> TriageResult:
  - intenta construir Triage(**data); Pydantic valida.
  - ValidationError -> TriageResult(ok=False, error=validation).
  - éxito -> TriageResult(ok=True, triage=...).
```

**Decisión de capas**: `agent/` importa el esquema `Triage` desde `mcp_server/models` (contrato de
dominio compartido). Es aceptable: se importa el modelo de datos, no la lógica del servidor. Una
extracción a un módulo `schemas` compartido se puede hacer luego si crece el acoplamiento.

## Seguimiento de complejidad

Sin violaciones. Ticket deliberadamente chico: el grueso del esquema ya estaba; aquí va el mecanismo
de producción estructurada + pruebas.
