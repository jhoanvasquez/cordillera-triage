---
description: "Lista de tareas para MCP abrir_reclamo + escalar_a_ajustador"
---

# Tareas: MCP — abrir_reclamo + escalar_a_ajustador

**Entrada**: Documentos de diseño en `specs/005-mcp-reclamo-escalamiento/`

**Prerrequisitos**: plan.md, spec.md

**Pruebas**: INCLUIDAS (SC-004 y las pruebas independientes).

**Organización**: por historia de usuario.

## Formato: `[ID] [P?] [Historia] Descripción`

---

## Fase 2: Fundacional (prerrequisitos bloqueantes)

- [x] T001 `models.py`: + `ThirdParties`, `Triage`, `EscalationCause` (enum), `Handoff`, `ClaimResponse`, `EscalationResponse` (campos inglés; valores de enum/estado en español).
- [x] T002 `state.py` (nuevo): `VerificationRegistry` (`mark_verified`/`is_verified`/`reset`) + `ClaimStore` (`open`→`RCL-####`); singletons de módulo, inyectables.

**Punto de control**: esquemas y estado listos.

---

## Fase 3: Historia de usuario 1 + 2 - Abrir reclamo con defensa de la regla 1 (Prioridad: P1) 🎯 MVP

### Implementación

- [x] T003 [US2] `service.verify_identity`: al verificar con éxito, registra el documento en `VerificationRegistry` (param `registry` opcional; default singleton).
- [x] T004 [US1][US2] `service.open_claim(insured_document, policy_number, triage, *, registry, policies, store)`: regla 1a (identidad no verificada → `business`), regla 1b (póliza inexistente / no vigente en `triage.incident_date` → `business`, reutiliza vigencia de #3), éxito → `store.open` + `claim_id`.
- [x] T005 [US1] Registrar la herramienta `abrir_reclamo` en `server.py` (firma española → `service.open_claim` posicional).

### Pruebas

- [x] T006 [US1][US2] `test_claims.py`: identidad verificada + póliza vigente → `ok` con `claim_id`; sin identidad → `business`; póliza no vigente en la fecha → `business`. Usa un `VerificationRegistry`/`ClaimStore` frescos (aislamiento).

**Punto de control**: `abrir_reclamo` abre solo si se cumple la regla 1 completa.

---

## Fase 4: Historia de usuario 3 - Escalar a un ajustador (Prioridad: P1)

### Implementación

- [x] T007 [US3] `service.escalate_to_adjuster(handoff, *, store)` + registrar la herramienta `escalar_a_ajustador` en `server.py`.

### Pruebas

- [x] T008 [US3] `test_claims.py`: handoff completo válido → `ok` con `escalation_id` + `priority`; handoff con causa fuera del enum / campos faltantes → rechazado por el esquema (Pydantic).

**Punto de control**: el handoff válido se registra; el inválido se rechaza.

---

## Fase N: Pulido

- [x] T009 Ejecutar `pytest` — toda la suite en verde.
- [x] T010 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- Fundacional (T001-T002) primero; bloquea todo.
- US1+US2 (T003-T006) antes que US3; comparten `service.py`/`server.py` → secuencial.
- Pulido al final.

## Notas

- `verify_identity` ahora tiene efecto (registra) → los tests inyectan estado fresco.
- La regla 2 (severidad) NO se implementa aquí: es del hook #7. Aquí solo la defensa de la regla 1.
- Validación estructural = Pydantic/FastMCP; resultados de dominio = envelope.
