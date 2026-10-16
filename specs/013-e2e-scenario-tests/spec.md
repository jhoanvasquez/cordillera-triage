# Especificación de funcionalidad: Capa de pruebas de escenario e2e (modelo real)

**Rama de funcionalidad**: `013-e2e-scenario-tests`

**Creado**: 2026-10-16

**Estado**: Borrador

**Entrada**: Issue de GitHub #12. Capa de pruebas de escenario que corre el **modelo real** de punta a
punta. Los 8 casos obligatorios del enunciado, como guiones de conversación, corribles con
`pytest -m e2e`. Cada test aserta sobre el **trace de tool-calls + el resultado** (reclamo abierto /
escalado / pregunta hecha), **no** sobre el wording. Construye sobre #6–#10.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Los 8 casos obligatorios corren e2e y asertan comportamiento (Prioridad: P1)

Los 8 casos del enunciado existen como guiones de conversación, marcados `e2e`, y asertan sobre el
comportamiento observable (qué tools se llamaron, qué resultado se produjo), robusto al no-determinismo
del modelo.

**Por qué esta prioridad**: Es *el* ticket que valida el agente completo end-to-end; lo que el video de
funcionamiento demuestra. Cierra los seams que quedaron "a confirmar" (forma de `tool_response`,
delegación real con la tool `Agent`, contexto multi-turno).

**Prueba independiente**: `pytest -m e2e` (con auth del modelo) corre los 8 casos; cada uno aserta sobre
el trace/outcome. `pytest` por defecto los **excluye** (la capa determinista sigue verde sin modelo).

**Los 8 casos (1:1 con el enunciado, datos ficticios existentes)**:

1. **Mensaje de ejemplo** (daño + lesión + pregunta de grúa) — `DOC-FIC-0001` (Juan Pérez), placa `FIC-01A`, póliza con grúa `si`. **Aserción**: hay lesión ⇒ se **escala** (prioridad `alta`); se revisa cobertura (delegación a `revisor-cobertura` / `verificar_cobertura` en el trace); NO se abre reclamo automático.
2. **Choque leve sin heridos** — `DOC-FIC-0001`, daño leve, sin lesiones, cobertura `si`. **Aserción**: `abrir_reclamo` en el trace y `claim_id` seteado; sin escalamiento.
3. **Pide hablar con una persona** (desde el primer mensaje). **Aserción**: se **escala** de inmediato (`escalar_a_ajustador` / `escalation_id`), sin abrir reclamo; sin investigación previa extensa (regla 4).
4. **Dos vehículos, no dice cuál** — `DOC-FIC-0002` (María Gómez, vehículos `FIC-02B` y `FIC-03C`). **Aserción**: el agente **pregunta** cuál vehículo; no abre reclamo ni adivina (sin `abrir_reclamo`, sin `claim_id`); la respuesta es una pregunta.
5. **Siniestro con póliza vencida** — `DOC-FIC-0003` (Carlos), póliza `POL-FIC-0004` vigente 2024–2025, siniestro en 2026. **Aserción**: NO se abre reclamo (`claim_id` nulo); cobertura `no` / se escala o se reporta no cubierto.
6. **Intento de abrir reclamo sin identidad verificada** — el asegurado se niega a dar su fecha de nacimiento y empuja a abrir. **Aserción**: el guard (#7) **bloquea**: `claim_id` nulo (invariante: si hay `claim_id`, hubo identidad verificada).
7. **Falla transitoria del servidor MCP** — `DOC-FIC-9999` (flaky record). **Aserción**: el agente maneja el error `transient` con gracia (reintenta y/o escala / da un mensaje claro), sin crashear; el run completa.
8. **Cobertura no clara (reparto/domicilios)** — `DOC-FIC-0004` (Ana), póliza `POL-FIC-0005` con `danos: incierto` (vehículo particular haciendo domicilios). **Aserción**: cobertura `incierto` ⇒ se **escala** (regla 5); no se abre reclamo automático.

**Escenarios de aceptación**:

1. **Dado** auth del modelo, **Cuando** se corre `pytest -m e2e`, **Entonces** los 8 casos corren y asertan sobre trace/outcome.
2. **Dado** sin auth, **Cuando** se corre `pytest` (por defecto), **Entonces** los e2e se excluyen/saltean y la capa determinista queda verde.
3. **Dado** cualquier caso, **Entonces** la aserción es sobre comportamiento (tools llamadas, `claim_id`/`escalation`/pregunta), NO sobre el texto exacto.

---

### Historia de usuario 2 - Caso de falla transitoria con manejo con gracia (Prioridad: P1)

El caso de falla transitoria usa el mecanismo de inyección de #10 (flaky record): el agente recibe un
error `transient` (reintentable) y responde con gracia (reintenta y luego escala / mensaje claro), sin
crashear.

**Prueba independiente**: correr el caso 7 → el run completa; el agente no se cuelga ante el error transitorio.

**Escenarios de aceptación**:

1. **Dado** `DOC-FIC-9999`, **Cuando** el agente consulta, **Entonces** recibe un error `transient` y maneja el caso con gracia (no excepción no manejada).

### Casos límite

- Sin auth ni opt-in → los e2e se saltean (no fallan), para no romper la suite por defecto ni CI.
- No-determinismo del modelo → las aserciones son sobre comportamiento, tolerantes a variaciones de redacción y de orden no esencial.
- Costo de tokens → los e2e corren solo bajo pedido explícito (`-m e2e` + opt-in), nunca en la suite por defecto.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: DEBEN existir los **8 casos** como guiones de conversación, marcados `@pytest.mark.e2e`, corribles con `pytest -m e2e`.
- **FR-002**: Cada test DEBE asertar sobre el **trace de tool-calls + el resultado** (`claim_id`/`escalation`/pregunta), NO sobre el wording.
- **FR-003**: El caso de falla transitoria DEBE usar el mecanismo de #10 (flaky record) y verificar manejo con gracia.
- **FR-004**: La suite **por defecto** (`pytest`) DEBE **excluir** los e2e, de modo que la capa determinista (#10) siga verde sin modelo.
- **FR-005**: Los e2e DEBEN **saltearse** (no fallar) cuando no hay auth/opt-in, para no romper la suite ni CI.
- **FR-006**: DEBE existir un **harness** que corra un guion (lista de mensajes del asegurado) contra el agente real y capture el trace de tools + el `SessionState` final + el texto, reusando #6–#9.

### Entidades clave

- **Harness de escenario**: `run_scenario(messages) -> ScenarioResult` (trace de tools, `SessionState`, texto final).
- **Marcador `e2e`**: separa la capa 2 (modelo real) de la capa 1 (determinista, #10).

## Criterios de éxito *(obligatorio)*

- **SC-001**: `pytest` (por defecto) NO corre los e2e; la capa determinista sigue en verde.
- **SC-002**: `pytest -m e2e` (con auth) corre los 8 casos; cada uno aserta sobre trace/outcome, mapeados 1:1 al enunciado.
- **SC-003**: Sin auth/opt-in, los e2e se saltean con un mensaje claro (no fallan).
- **SC-004**: El caso de falla transitoria verifica manejo con gracia.

## Supuestos

- **Requiere modelo real**: los e2e necesitan `ANTHROPIC_API_KEY` o el `claude` CLI logueado, y el runtime del Claude Agent CLI (Node). Gastan tokens; corren bajo pedido (para el video), no en la suite por defecto.
- **Aserción sobre comportamiento, no wording**: por el no-determinismo del modelo. El trace de tools y el `SessionState` (que se puebla de resultados de tools, Principio I) son la base de las aserciones.
- **Opt-in explícito**: los e2e se saltean salvo opt-in (p. ej. `RUN_E2E=1`) para evitar gasto accidental de tokens.
- **Esta especificación no garantiza "verde" en este entorno**: el repositorio incluye los tests y son corribles; el verde depende de la auth del evaluador (y de la no-determinación del modelo). Un smoke-test en vivo valida el harness.
- **Alcance de cambios al agente**: el e2e NO cambia las **reglas** (siguen en los hooks de #6–#8). Sí incluye dos arreglos que el smoke-test en vivo destapó (ver `plan.md` → Hallazgos): el fix crítico de `extract_structured` (forma real de `tool_response`) y una guía de prompt para verificar cobertura contra los amparos contratados. Ninguno toca una regla de negocio.
- **Fuera de alcance**: workflow de CI (#10 / decisión de alcance); nuevas reglas o herramientas.
