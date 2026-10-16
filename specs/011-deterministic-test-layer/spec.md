# Especificación de funcionalidad: Capa de pruebas deterministas (capa 1)

**Rama de funcionalidad**: `011-deterministic-test-layer`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #10. La capa de pruebas deterministas corre en CI **sin** el modelo y
sostiene las garantías duras con independencia del no-determinismo del LLM; además provee el mecanismo
de inyección de falla transitoria del que depende la capa e2e (#12).

**Naturaleza del ticket (consolidación)**: el grueso de esta capa **ya fue construido** incrementalmente
en #2–#5 y #7 (81 pruebas deterministas, sin LLM, en verde). Este ticket **consolida** esa capa,
documenta el mapeo criterio↔prueba y **cierra un único hueco** detectado. Alcance acordado: **sin un
workflow de CI** nuevo (las pruebas ya son CI-friendly: sin LLM, corren con `pytest`); **sin** el lever
`CORDILLERA_FAULT` (el flaky record ya es el mecanismo de inyección).

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Garantías duras probadas sin el modelo (Prioridad: P1)

Las garantías de negocio se prueban determinísticamente (sin LLM), de modo que valen aunque el modelo
sea no-determinista. En particular, "abrir un reclamo sin identidad verificada" se prueba llamando al
hook PreToolUse directamente.

**Prueba independiente**: `pytest` corre toda la suite sin red ni modelo y queda en verde.

**Escenarios de aceptación**:

1. **Dado** un estado sin identidad, **Cuando** se llama `guard_abrir_reclamo` directo, **Entonces** niega (ya cubierto por `test_hooks.py::test_guard_denies_without_identity`).
2. **Dado** `motivos_bloqueo()`, **Entonces** sus casos están cubiertos sin LLM (`test_hooks.py`).
3. **Dado** las tools MCP y los esquemas Pydantic, **Entonces** están cubiertos (`test_service.py`, `test_claims.py`, `test_cobertura.py`, `test_triage.py`, `test_coverage.py`, `test_errors.py`).

---

### Historia de usuario 2 - Inyección de falla transitoria (Prioridad: P1)

El mecanismo de inyección de falla transitoria (flaky record `DOC-FIC-9999`) hace que la tool MCP
devuelva un error `transient` **reintentable** (`isRetryable: true`), y queda cubierto en ambas puertas
de entrada que lo consultan (`buscar_asegurado` y `verificar_identidad`).

**Prueba independiente**: consultar el flaky record en cada tool → error `transient` con `isRetryable: true`.

**Escenarios de aceptación**:

1. **Dado** `DOC-FIC-9999` en `buscar_asegurado`, **Entonces** error `transient` con `isRetryable: true` (ya cubierto, `test_service.py::test_flaky_record_is_transient_error`).
2. **Dado** `DOC-FIC-9999` en `verificar_identidad`, **Entonces** error `transient` con `isRetryable: true` (**hueco cerrado por este ticket**).

### Casos límite

- Una búsqueda sin resultados NO es un error (ya cubierto).
- Otras categorías de error (`validation`/`business`/`permissions`) NO son reintentables (ya cubierto, `test_errors.py`).

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: Deben existir pruebas deterministas (sin LLM) de las 4 áreas: hooks, máquina de estado (`motivos_bloqueo`), tools MCP y esquemas Pydantic. (Ya satisfecho por #2–#5/#7.)
- **FR-002**: "Abrir reclamo sin identidad" DEBE probarse llamando al hook PreToolUse directamente. (Ya satisfecho, `test_hooks.py`.)
- **FR-003**: El mecanismo de inyección de falla transitoria DEBE estar implementado y probado: la tool devuelve `transient` con `isRetryable: true`. (Satisfecho para `buscar_asegurado`; este ticket lo extiende a `verificar_identidad`.)
- **FR-004**: Toda la suite determinista corre en verde con `pytest` (sin LLM, CI-friendly).

### Entidades clave

- **Capa determinista (capa 1)**: el conjunto de `test_*.py` colocados que corren sin modelo. Contrasta con la capa e2e (#12), que usa modelo real.
- **Flaky record (`DOC-FIC-9999`)**: el mecanismo de inyección de falla transitoria que #12 usa.

## Criterios de éxito *(obligatorio)*

- **SC-001**: `pytest` corre toda la suite sin modelo y queda en verde.
- **SC-002**: La falla transitoria devuelve `transient`/`isRetryable: true` en `buscar_asegurado` **y** `verificar_identidad`.
- **SC-003**: El issue #10 queda con un comentario que mapea cada criterio a la prueba que lo cubre (trazabilidad para la defensa).

## Supuestos

- **Ya construido**: la mayor parte de #10 se cumplió en tickets previos; este ticket consolida y cierra el hueco de `verificar_identidad`.
- **Sin CI nuevo** (decisión de alcance): "corre en CI" se interpreta como "las pruebas son CI-friendly (sin LLM)", que ya se cumple; no se agrega un workflow de GitHub Actions.
- **Flaky record como mecanismo** (decisión de alcance): no se agrega el lever `CORDILLERA_FAULT`; el flaky record ya satisface el criterio y lo usa #12.
- **Fuera de alcance**: capa e2e con modelo real (#12); cualquier pipeline de CI.
