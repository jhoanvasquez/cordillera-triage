# Especificación de funcionalidad: MCP — abrir_reclamo + escalar_a_ajustador

**Rama de funcionalidad**: `005-mcp-reclamo-escalamiento`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #4. Las dos herramientas de **escritura** del servidor MCP: abrir un
reclamo con el triage estructurado y escalar a un ajustador con un resumen de handoff. Define los
esquemas de **triage** y **handoff** como contrato de entrada; la producción agent-side del triage
es #5.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Abrir un reclamo (Prioridad: P1)

`abrir_reclamo` valida el triage estructurado y abre un reclamo, devolviendo un identificador.

**Por qué esta prioridad**: Es la acción final del flujo "resolver"; sin ella el agente no puede
materializar un reclamo simple.

**Prueba independiente**: Con un triage válido y una identidad previamente verificada, devuelve un
reclamo con id; con un triage malformado, devuelve `validation`.

**Escenarios de aceptación**:

1. **Dado** un triage válido y la identidad del asegurado verificada, **Cuando** se abre el reclamo, **Entonces** se devuelve `ok=true` con un `claim_id`.
2. **Dado** un triage que no cumple el esquema (p. ej. `severity` inválida), **Cuando** se abre, **Entonces** se devuelve un error `validation`.

---

### Historia de usuario 2 - Defensa server-side de la regla 1 (Prioridad: P1)

`abrir_reclamo` rechaza abrir si NO se cumplen las **dos** condiciones de la regla 1: (a) identidad
del asegurado verificada en la sesión **Y** (b) póliza vigente en la fecha del siniestro. Defensa en
profundidad, respaldo del hook (#7), no en su lugar.

**Por qué esta prioridad**: La regla 1 del enunciado (pág. 3) es textual: "Ningún reclamo se abre
sin identidad verificada del asegurado y sin confirmar que la póliza estaba vigente en la fecha del
siniestro." El servidor no debe abrir un reclamo que viole **cualquiera** de las dos, aun si el hook
se omitiera.

**Prueba independiente**: Sin verificación previa → `business`; con póliza no vigente en la fecha del
triage → `business`; con ambas condiciones cumplidas → permite abrir.

**Escenarios de aceptación**:

1. **Dado** un asegurado cuya identidad NO fue verificada, **Cuando** se intenta abrir un reclamo, **Entonces** se devuelve `business` ("identidad no verificada").
2. **Dado** identidad verificada pero la póliza NO vigente en la fecha del siniestro, **Cuando** se intenta abrir, **Entonces** se devuelve `business` ("póliza no vigente en la fecha del siniestro").
3. **Dado** identidad verificada **y** póliza vigente en la fecha, **Cuando** se abre el reclamo, **Entonces** no se bloquea por la regla 1.

---

### Historia de usuario 3 - Escalar a un ajustador (Prioridad: P1)

`escalar_a_ajustador` valida el resumen de handoff y lo registra, devolviendo confirmación y
prioridad. El resumen debe permitir a un ajustador **sin acceso a la conversación** actuar.

**Por qué esta prioridad**: Cierra el flujo "escalar" (reglas 3, 4, 5); el handoff es evaluado
(behavior #9).

**Prueba independiente**: Un handoff completo válido → `ok=true` con confirmación; un handoff sin
campos obligatorios → `validation`.

**Escenarios de aceptación**:

1. **Dado** un handoff con asegurado, póliza, triage, acciones, causa, prioridad y acción recomendada, **Cuando** se escala, **Entonces** se devuelve `ok=true` con confirmación y `priority`.
2. **Dado** un handoff al que le falta la causa de escalamiento, **Cuando** se escala, **Entonces** se devuelve un error `validation`.

### Casos límite

- Triage con campos nulos permitidos (lo que el reporte no menciona es `None`) → válido, no error.
- `escalation_cause` fuera del enum → `validation`.
- Abrir reclamo para un asegurado inexistente → `business`.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: DEBE existir un esquema de **triage** (Pydantic) con campos nulos permitidos: tipo de siniestro, severidad (`leve|moderada|grave`), lesiones reportadas, terceros, fecha, vehículo referido, asuntos del mensaje, datos faltantes.
- **FR-002**: `abrir_reclamo` DEBE recibir referencia del asegurado y de la póliza más el triage, y validar el triage contra su esquema; entrada inválida → `validation`.
- **FR-003**: `abrir_reclamo` DEBE rechazar con `business` si NO se cumple la regla 1 completa: (a) la identidad del asegurado no fue verificada en la sesión (registro en memoria poblado por `verificar_identidad`), **O** (b) la póliza no estaba vigente en la fecha del siniestro (reutiliza la lógica de vigencia de #3). Es defensa en profundidad del hook (#7), no su reemplazo.
- **FR-004**: `abrir_reclamo` DEBE devolver un `claim_id` en caso de éxito.
- **FR-005**: DEBE existir un esquema de **handoff** con: asegurado, póliza, triage, acciones realizadas, causa de escalamiento (enum `solicitud_asegurado|severidad|lesiones|cobertura_incierta|falla_tecnica`), prioridad (`alta|media|baja`) y acción recomendada.
- **FR-006**: `escalar_a_ajustador` DEBE validar el handoff y devolver confirmación + `priority`; handoff incompleto → `validation`.
- **FR-007**: Ambas herramientas DEBEN usar el envelope estructurado de #2.
- **FR-008**: DEBEN existir pruebas colocadas: abrir con/ sin identidad, triage inválido, handoff válido/incompleto, causa fuera de enum.

### Entidades clave *(include if feature involves data)*

- **Triage**: `claim_type`, `severity` (`leve|moderada|grave`), `injuries_reported`, `injury_description`, `third_parties`, `incident_date`, `referenced_vehicle`, `message_topics`, `missing_data` (campos nulos permitidos salvo las listas).
- **ThirdParties**: `present`, `identified`, `description`.
- **Handoff**: `insured_id`, `policy_number`, `triage`, `actions_taken`, `escalation_cause` (enum), `priority` (`alta|media|baja`), `recommended_action`.
- **VerificationRegistry**: estado en memoria del servidor; `verificar_identidad` marca verificado, `abrir_reclamo` lo consulta.
- **ClaimResponse / EscalationResponse**: envelope con `ok`, id de resultado y `error`.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: `abrir_reclamo` abre un reclamo con triage válido + identidad verificada, y lo rechaza (`business`) sin verificación.
- **SC-002**: Un triage malformado produce `validation`; un triage con nulos permitidos es válido.
- **SC-003**: `escalar_a_ajustador` acepta un handoff completo y rechaza uno incompleto.
- **SC-004**: La suite de pruebas colocada corre en verde.

## Supuestos

- Reutiliza el loader, el envelope y los modelos base de #2/#3.
- Los **valores** de estado y de enum van en español (`leve|moderada|grave`, causas de escalamiento); los **nombres de campo** en inglés (convención #20).
- Las reglas de negocio garantizadas por hooks (reglas 1-3) son del ticket #7; aquí solo está la **defensa en profundidad** server-side de identidad, no el hook principal.
- **El esquema de triage es propiedad canónica de #5** (behavior #5), incluida la regla "lo que el reporte no menciona queda nulo". Aquí se define/consume como contrato de entrada de `abrir_reclamo`; #5 debe reusar este modelo, no redefinir uno divergente. Si hay conflicto, manda #5.
