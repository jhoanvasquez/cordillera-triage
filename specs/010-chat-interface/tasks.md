---
description: "Lista de tareas para la interfaz de chat de consola"
---

# Tareas: Interfaz de chat (consola)

**Entrada**: Documentos de diseño en `specs/010-chat-interface/`

**Prerrequisitos**: plan.md, spec.md. Depende de #6, #7 y #8 (ya en `main`).

**Pruebas**: INCLUIDAS, deterministas sin LLM (SC-001..004, FR-007).

**Organización**: por historia de usuario. El renderer y la detección de eventos son el núcleo testeable; el loop vivo es #12.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: puede ejecutarse en paralelo (archivo distinto, sin dependencias)

---

## Fase 3: Historia de usuario 1 - Conversación turno a turno legible (Prioridad: P1)

### Implementación

- [x] T001 [US1] `agent/chat.py`: `render_insured(text) -> str` y `render_agent(text) -> str` (lógica pura) con etiquetas de rol claramente distinguibles (p. ej. `Asegurado:` / `Agente:`). Etiquetas de cara al usuario en español; código en inglés.

### Pruebas

- [x] T002 [P] [US1] `agent/test_chat.py`: `render_insured`/`render_agent` producen líneas con etiqueta de rol distinguible (una no se confunde con la otra).

**Punto de control**: los turnos de asegurado y agente son legibles y distinguibles.

---

## Fase 4: Historia de usuario 2 - Acciones evidentes: reclamo / escalamiento (Prioridad: P1) 🎯

### Implementación

- [x] T003 [US2] `agent/state.py`: agregar `claim_id: str | None`, `escalation_id: str | None`, `escalation_priority: str | None` + `record_claim(resp)` (si `ok`, guarda `claim_id` de `ClaimResponse`) y `record_escalation(resp)` (si `ok`, guarda `escalation_id`/`priority` de `EscalationResponse`). No altera `motivos_bloqueo()`.
- [x] T004 [US2] `agent/hooks.py`: `make_post_tool_use` enruta `abrir_reclamo`→`record_claim` y `escalar_a_ajustador`→`record_escalation` (Principio I: desde el resultado). (depende de T003)
- [x] T005 [US2] `agent/chat.py`: `render_claim_opened(claim_id) -> str` y `render_escalation(escalation_id, priority) -> str` (líneas evidentes con indicador, distintas de un turno de chat; incluyen el id y la prioridad).

### Pruebas

- [x] T006 [P] [US2] `agent/test_chat.py`: `render_claim_opened` incluye el `claim_id` y un indicador evidente; `render_escalation` incluye la prioridad (`alta`) y es distinta de un turno de chat. `state.record_claim`/`record_escalation` contra `tool_response` sintéticos → guardan los campos; `ok=false` no marca. El dispatch de `make_post_tool_use` enruta ambas tools a sus recorders.

**Punto de control**: abrir reclamo y escalar quedan evidentes, derivados de resultados de herramientas.

---

## Fase 5: Historia de usuario 3 - Ejecutable en terminal (Prioridad: P1)

### Implementación

- [x] T007 [US3] `agent/chat.py`: `run_chat(input_stream, output)` — crea un `SessionState` y un `ClaudeSDKClient(build_options(state=...))` persistentes; por cada mensaje: `render_insured` → `query` → `consume` (reusa #6) → `render_agent` → renderiza los eventos nuevos del estado (reclamo/escalamiento no renderizados aún). EOF/comando de salida termina limpio; `ClaudeSDKError` se reporta claro. Bloque `__main__` para `python -m cordillera.agent.chat`. (depende de T001, T005, T003)

### Pruebas

- [x] T008 [P] [US3] `agent/test_chat.py`: la selección de "eventos nuevos" emite exactamente un evento cuando el estado pasa de sin-reclamo a con-reclamo (no re-renderiza); el módulo `cordillera.agent.chat` es importable y expone el punto de entrada. (El loop vivo con modelo es #12.)

**Punto de control**: hay un chat de terminal ejecutable que presenta la conversación y las acciones.

---

## Fase N: Pulido

- [x] T009 Ejecutar `pytest` — toda la suite en verde.
- [x] T010 [P] `ruff format` + `ruff check` sobre `src/`.

---

## Dependencias y orden

- **T001** (render turnos) y **T003→T004** (estado/dispatch de eventos) son independientes; **T005** (render eventos) depende solo de sí mismo.
- **T007** (`run_chat`) depende de T001, T005 y T003.
- US1 (T001→T002), US2 (T003→T004→T005→T006), US3 (T007→T008); pulido (T009–T010) al final.

## Notas

- El chat **solo presenta**; las reglas las garantizan los hooks (#7) y el prompt (#6/#8). Reusa `run`/`consume`/`build_options`.
- Eventos de acción derivados de **resultados de herramientas** (Principio I), reusando el dispatch PostToolUse de #7 — sin un segundo mecanismo. Extender `SessionState` es aditivo (no toca `motivos_bloqueo()`).
- Sin dependencias web; texto plano (Rich opcional, no se agrega).
- A confirmar en runtime (#12): contexto conversacional entre `query()` sucesivos; forma de `tool_response` (aislada en `extract_structured`); ver los casos de prueba en la interfaz.
- Commits Conventional, sin atribución a IA (Principio V).
