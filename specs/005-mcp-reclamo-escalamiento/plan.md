# Plan de implementación: MCP — abrir_reclamo + escalar_a_ajustador

**Rama**: `005-mcp-reclamo-escalamiento` | **Fecha**: 2026-10-15 | **Especificación**: `specs/005-mcp-reclamo-escalamiento/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/005-mcp-reclamo-escalamiento/spec.md`

## Resumen

Agrega las dos herramientas de escritura, sus esquemas (triage y handoff) y el estado en memoria del
servidor (registro de verificación + almacén de reclamos). Reutiliza loader/envelope de #2/#3 y la
lógica de vigencia de #3. `verificar_identidad` pasa a registrar la verificación; `abrir_reclamo`
aplica la defensa en profundidad de la regla 1 (identidad + vigencia).

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas)

**Almacenamiento**: fixtures de #1 (lectura) + estado en memoria del proceso (verificación, reclamos)

**Pruebas**: `pytest`, colocadas (`test_claims.py`)

**Restricciones**: envelope de #2; valores de estado/enum en español; campos en inglés (convención #20)

## Verificación de la constitución

- **Principio I**: la defensa server-side es **defensa en profundidad**, NO el enforcement principal de las reglas (eso es el hook #7). `abrir_reclamo` respalda la regla 1; no implementa la regla 2 (queda al hook). CUMPLE.
- **Principio IV**: esquemas Pydantic + envelope estructurado. CUMPLE.
- **Principio VI**: código inglés; tool names/params/descripciones + valores de enum en español. CUMPLE.

Sin violaciones.

## Estructura del proyecto (extiende `mcp_server/`)

```text
src/cordillera/mcp_server/
├── models.py        # + Triage, ThirdParties, Handoff, ClaimResponse, EscalationResponse, enums
├── state.py         # NUEVO: VerificationRegistry + ClaimStore (en memoria, inyectables)
├── service.py       # + open_claim(), escalate_to_adjuster(); verify_identity registra la verificación
├── server.py        # + tools abrir_reclamo, escalar_a_ajustador (firma española -> service inglés)
└── test_claims.py   # pruebas colocadas nuevas
```

## Modelo de datos y contratos

### Esquemas (campos en inglés; valores en español)

- `ThirdParties`: `present: bool | None`, `identified: bool | None`, `description: str | None`.
- `Triage`: `claim_type: str | None`, `severity: Literal["leve","moderada","grave"] | None`, `injuries_reported: bool | None`, `injury_description: str | None`, `third_parties: ThirdParties`, `incident_date: str | None`, `referenced_vehicle: str | None`, `message_topics: list[str] = []`, `missing_data: list[str] = []`. **Propiedad canónica de #5** (ver spec).
- `EscalationCause` (enum, valores español): `solicitud_asegurado|severidad|lesiones|cobertura_incierta|falla_tecnica`.
- `Handoff`: `insured_id`, `policy_number: str | None`, `triage: Triage`, `actions_taken: list[str]`, `escalation_cause: EscalationCause`, `priority: Literal["alta","media","baja"]`, `recommended_action: str`.
- `ClaimResponse`: `ok`, `claim_id: str | None`, `error`.
- `EscalationResponse`: `ok`, `escalation_id: str | None`, `priority: str | None`, `error`.

### Estado en memoria (`state.py`)

- `VerificationRegistry`: `mark_verified(document)`, `is_verified(document) -> bool`, `reset()`. Singleton de módulo `verification_registry`.
- `ClaimStore`: `open(insured_id, policy_number, triage) -> claim_id` (ids `RCL-0001…`), lista interna; singleton `claim_store`.
- Inyectables: las funciones de `service` aceptan `registry`/`store` opcionales (default singleton) para aislar en tests.

### Lógica (`service.py`)

- `verify_identity(...)`: al verificar con éxito, `registry.mark_verified(document)` (cambio menor; param `registry` opcional).
- `open_claim(insured_document, policy_number, triage, *, registry, policies, store)`:
  1. **Regla 1a**: `not registry.is_verified(insured_document)` → `business` ("identidad no verificada").
  2. **Regla 1b**: póliza inexistente → `business`; póliza no vigente en `triage.incident_date` → `business` ("póliza no vigente en la fecha del siniestro"). Reutiliza la verificación de vigencia de #3.
  3. Éxito → `store.open(...)` → `ClaimResponse(ok=True, claim_id=...)`.
- `escalate_to_adjuster(handoff, *, store)`: registra el handoff → `EscalationResponse(ok=True, escalation_id, priority=handoff.priority)`.

### Validación: estructural vs. dominio (decisión)

La validación **estructural** la hacen Pydantic/FastMCP a partir de los tipos de las herramientas
(esquema expuesto al agente; entrada malformada → falla de validación de FastMCP). El **envelope**
(`ok=false` + `error`) se reserva para los **resultados de dominio**: identidad no verificada, póliza
no vigente, asegurado/póliza inexistentes. Así el agente obtiene un esquema rico y los hooks (#7)
leen los resultados de dominio de forma determinista.

## Seguimiento de complejidad

`verify_identity` pasa a tener efecto (registra verificación) → se mitiga con inyección de un
`VerificationRegistry` fresco en los tests para aislar. Sin dependencias nuevas.
