---
description: "Lista de tareas para el refactor de convención de idioma del código"
---

# Tareas: Convención de idioma del código (inglés)

**Entrada**: Documentos de diseño en `specs/004-english-code-convention/`

**Prerrequisitos**: plan.md, spec.md (tabla de renombres)

**Pruebas**: se reutilizan las existentes; deben quedar en verde tras el refactor (SC-002).

**Organización**: por capa, en orden seguro de datos hacia arriba. Todas contribuyen a un único
cambio de comportamiento-neutro.

## Formato: `[ID] [P?] Descripción`

---

## Fase 1: Datos

- [x] T001 `git mv` de los fixtures a inglés (`insured.json`, `vehicles.json`, `policies.json`) y renombrar sus claves a inglés (`document`, `plate`, `valid_from`, `coverages`, `covered` [valor sigue `si/no/incierto`], …).
- [x] T002 Actualizar `src/cordillera/data/test_fixtures.py` a los nuevos archivos y claves.

## Fase 2: Loader

- [x] T003 `loader.py`: `load_insured/vehicles/policies` + rutas a los archivos renombrados; actualizar `test_loader.py`.

## Fase 3: Modelos

- [x] T004 `models.py`: clases (`InsuredSummary`, `PolicyDetail`, `CoverageDetail`, `SearchResponse`, `VerificationResponse`, `PolicyResponse`, `CoverageResponse`) y campos en inglés.

## Fase 4: Servicio

- [x] T005 `service.py`: funciones internas (`search_insured`, `verify_identity`, `get_policy`, `check_coverage`), variables, constantes (`FLAKY_DOCUMENT`), helper (`_matches`), y acceso a claves en inglés. `errors.py`: `ErrorCategory`, `_RETRYABLE`.

## Fase 5: Servidor

- [x] T006 `server.py`: los wrappers `@mcp.tool` conservan nombre/parámetros/descripción en español y llaman posicionalmente a las funciones inglesas de `service.py`; imports actualizados.

## Fase 6: Pruebas

- [x] T007 Actualizar `test_service.py`, `test_cobertura.py`, `test_errors.py`, `test_server.py` a los nuevos nombres y claves.

## Fase 7: Constitución

- [x] T008 Actualizar `.specify/memory/constitution.md` (Principio VI) con la convención final.

## Fase N: Verificación

- [x] T009 `pytest` en verde (comportamiento idéntico).
- [x] T010 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden de ejecución

Estrictamente secuencial por capa (datos → loader → modelos → servicio → servidor → pruebas →
constitución), porque cada capa referencia a la anterior ya renombrada. La verificación cierra.

## Notas

- Es un único cambio lógico (un commit `refactor:`), no features nuevas.
- Lo que NO cambia: nombres/parámetros/descripciones de las 6 herramientas, valores de estado, reglas.
