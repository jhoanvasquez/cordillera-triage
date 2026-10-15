---
description: "Lista de tareas para esquema de triage + registrar_triage"
---

# Tareas: Esquema de triage + salida estructurada

**Entrada**: Documentos de diseño en `specs/006-triage-schema/`

**Prerrequisitos**: plan.md, spec.md

**Pruebas**: INCLUIDAS (SC-001..004).

**Organización**: por historia de usuario.

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 1: Configuración

- [x] T001 Crear el paquete `src/cordillera/agent/` con `__init__.py`.

---

## Fase 3: Historia de usuario 1 - Esquema de triage validado (Prioridad: P1)

### Pruebas (el esquema ya existe en #4; se confirma su contrato)

- [x] T002 [US1] `agent/test_triage.py`: datos parciales → campos no provistos quedan `None`, listas vacías; `severity` inválida → `ValidationError`; `claim_type` libre acepta cualquier string; `missing_data` funciona.

**Punto de control**: el esquema cumple el contrato (nulabilidad, severidad cerrada, claim_type libre).

---

## Fase 4: Historia de usuario 2 - Producción por salida estructurada (Prioridad: P1)

### Implementación

- [x] T003 [US2] `agent/triage.py`: `TriageResult` (ok/triage/error, reutiliza `ErrorInfo`) + `registrar_triage(data)` que valida con Pydantic (éxito → Triage; `ValidationError` → error `validation`).

### Pruebas

- [x] T004 [US2] `agent/test_triage.py`: `registrar_triage` con datos válidos → `ok` con `Triage`; con severidad inválida → `ok=False` con error `validation`.

**Punto de control**: `registrar_triage` produce triage validado o un error estructurado.

---

## Fase N: Pulido

- [x] T005 Ejecutar `pytest` — toda la suite en verde.
- [x] T006 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- T001 primero; T002/T003 dependen del paquete; T004 depende de T003; pulido al final.

## Notas

- El esquema `Triage` NO cambia (verificado contra la fuente de verdad: `severity` cerrado, `claim_type` libre).
- El wiring de `registrar_triage` como tool in-process del SDK y el loop del agente son **#6**.
