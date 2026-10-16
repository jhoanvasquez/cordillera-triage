# Plan de implementación: Capa de pruebas deterministas (capa 1)

**Rama**: `011-deterministic-test-layer` | **Fecha**: 2026-10-16 | **Especificación**: `specs/011-deterministic-test-layer/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/011-deterministic-test-layer/spec.md`

## Resumen

Ticket de **consolidación**. La capa determinista ya existe (81 pruebas de #2–#5/#7). El net-new es:
(1) cerrar el hueco de `verificar_identidad` con el flaky record, y (2) documentar el mapeo criterio↔
prueba en el issue #10 (trazabilidad). Sin workflow de CI y sin lever `CORDILLERA_FAULT` (decisiones de
alcance).

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas). **Pruebas**: `pytest`, colocadas.

## Verificación de la constitución

- **Principio I / IV**: las garantías duras (reglas por hooks, salida estructurada, errores categorizados) ya están probadas sin LLM. CUMPLE.
- **Principio III (SDD)**: este ticket tiene spec/plan/tasks pese a ser chico. CUMPLE.
- **Principio V (trazabilidad)**: el mapeo criterio↔prueba se comenta en el issue #10. CUMPLE.

Sin violaciones.

## Decisiones técnicas

- **No se agrega nada de producción**: solo una prueba (`verificar_identidad` flaky) y documentación. El flaky record (`service.py:FLAKY_DOCUMENT`) ya existe y maneja ambas tools; faltaba la prueba del camino `verificar_identidad`.
- **No CI / no lever** (alcance acordado): las pruebas ya corren con `.venv/Scripts/python.exe -m pytest -q` sin LLM.

## Modelo de datos y contratos

Sin cambios de modelo. Reutiliza `verify_identity`/`FLAKY_DOCUMENT`/`ErrorInfo` existentes.

## Estrategia de pruebas

- `test_service.py::test_identity_flaky_record_is_transient_error`: `verify_identity("DOC-FIC-9999", ...)` → `transient`/`isRetryable: true`.
- Regresión: toda la suite en verde.

## Mapeo criterio↔prueba (para el comentario en #10)

| Criterio #10 | Prueba que lo cubre |
|---|---|
| Unit tests (hooks, `motivos_bloqueo`, tools MCP, esquemas) | `test_hooks.py`, `test_service.py`, `test_claims.py`, `test_cobertura.py`, `test_triage.py`, `test_coverage.py`, `test_errors.py` |
| Abrir reclamo sin identidad vía hook directo | `test_hooks.py::test_guard_denies_without_identity` |
| Falla transitoria `transient`/`reintentable: true` | `test_service.py::test_flaky_record_is_transient_error` (+ `::test_identity_flaky_record_is_transient_error`, nuevo) |
| Todo verde en CI | `pytest` sin LLM, CI-friendly |

## Seguimiento de complejidad

Sin violaciones. Ticket deliberadamente mínimo: una prueba + documentación. Lo demás ya estaba.
