---
description: "Lista de tareas para la capa de pruebas deterministas (consolidación)"
---

# Tareas: Capa de pruebas deterministas (capa 1)

**Entrada**: Documentos de diseño en `specs/011-deterministic-test-layer/`

**Prerrequisitos**: plan.md, spec.md. Depende de #2–#5 y #7 (ya en `main`).

**Pruebas**: INCLUIDAS. **Ticket de consolidación**: el grueso ya existe; net-new mínimo.

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Cerrar el hueco

- [x] T001 [US2] `src/cordillera/mcp_server/test_service.py`: `test_identity_flaky_record_is_transient_error` — `verify_identity("DOC-FIC-9999", ...)` devuelve `transient` con `isRetryable: true` (camino del flaky record que faltaba cubrir).

---

## Fase 2: Consolidación y trazabilidad

- [x] T002 Verificar que las 4 áreas tienen cobertura determinista sin LLM (hooks, `motivos_bloqueo`, tools MCP, esquemas) — ya satisfecho por #2–#5/#7 (ver mapeo en plan.md).
- [x] T003 Comentar en el issue #10 el mapeo criterio↔prueba (trazabilidad para la defensa; Principio V).

---

## Fase N: Pulido

- [x] T004 Ejecutar `pytest` — toda la suite en verde.
- [x] T005 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Notas

- **Decisiones de alcance** (acordadas): sin workflow de CI (las pruebas ya son CI-friendly, sin LLM); sin lever `CORDILLERA_FAULT` (el flaky record ya es el mecanismo de inyección que usa #12).
- La mayor parte de #10 ya se cumplió en tickets previos; este ticket consolida y cierra un único hueco.
- Commits Conventional, sin atribución a IA (Principio V).
