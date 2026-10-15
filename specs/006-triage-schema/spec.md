# Especificación de funcionalidad: Esquema de triage + salida estructurada

**Rama de funcionalidad**: `006-triage-schema`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #5. Finaliza el esquema de triage (dueño canónico) y provee el tool
`registrar_triage` de **salida estructurada validada**. El esquema base ya fue sembrado en #4; aquí
se completa y se agrega el mecanismo de producción. El wiring al loop del agente es #6.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Esquema de triage validado (Prioridad: P1)

El triage se representa con un esquema Pydantic: tipo de siniestro, severidad, lesiones, terceros,
fecha, vehículo referido, asuntos del mensaje y datos faltantes. Lo que el reporte no menciona queda
**nulo**.

**Por qué esta prioridad**: Es el contrato de datos del triage (behavior #5); todo lo demás del
agente depende de él.

**Prueba independiente**: Construir un triage con datos parciales → los campos no provistos quedan
`None`; una severidad inválida es rechazada por Pydantic.

**Escenarios de aceptación**:

1. **Dado** datos parciales (solo severidad y fecha), **Cuando** se construye el triage, **Entonces** los demás campos quedan `None` (listas vacías) — el agente no inventa.
2. **Dado** `severity` fuera de `{leve, moderada, grave}` o `claim_type` fuera del enum, **Cuando** se valida, **Entonces** Pydantic lo rechaza.
3. **Dado** un triage, **Entonces** expone `missing_data` (datos faltantes) como lista.

---

### Historia de usuario 2 - Producción por salida estructurada (`registrar_triage`) (Prioridad: P1)

`registrar_triage` produce el triage como **salida estructurada validada**, nunca texto libre. Su
esquema de entrada ES el modelo de triage.

**Por qué esta prioridad**: Behavior #5 exige salida estructurada validada contra un esquema; este
tool es el mecanismo que el agente (#6) usará.

**Prueba independiente**: Llamar `registrar_triage` con datos válidos → devuelve un `Triage`
validado; con datos inválidos → error de validación (no un triage a medias).

**Escenarios de aceptación**:

1. **Dado** datos de triage válidos, **Cuando** se llama `registrar_triage`, **Entonces** devuelve un `Triage` validado.
2. **Dado** datos inválidos (p. ej. severidad inválida), **Cuando** se llama, **Entonces** se devuelve un error de validación.

### Casos límite

- Reporte que no menciona terceros → `third_parties` con campos `None` (no inventar).
- "se fue sin dejar datos" → mapea a `third_parties.present=True`, `identified=False` (lo decide el agente/prompt en #6; el esquema lo soporta).
- Mensaje con varias preocupaciones → `message_topics` con más de un ítem (behavior #6).

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: El esquema `Triage` DEBE tener todos los campos de contenido nulos por defecto (lo no mencionado queda `None`), salvo las listas (`message_topics`, `missing_data`) que por defecto son vacías.
- **FR-002**: `claim_type` DEBE ser un enum `TipoSiniestro` (valores de dominio en español).
- **FR-003**: `severity` DEBE ser `Literal["leve","moderada","grave"] | None` (valores del enunciado).
- **FR-004**: El esquema DEBE incluir `third_parties`, `incident_date`, `referenced_vehicle`, `message_topics`, `missing_data` (behaviors #5, #6, #7).
- **FR-005**: DEBE existir `registrar_triage` que valide la entrada contra el esquema y devuelva un `Triage` validado; entrada inválida → error de validación.
- **FR-006**: El esquema es **dueño canónico** aquí; `abrir_reclamo` (#4) lo consume sin redefinirlo.
- **FR-007**: DEBEN existir pruebas colocadas: nulabilidad, enums, `missing_data`, y `registrar_triage` (válido/ inválido).

### Entidades clave *(include if feature involves data)*

- **TipoSiniestro** (enum, valores español): p. ej. `colision`, `robo`, `incendio`, `vandalismo`, `fenomeno_natural`, `otro`.
- **Triage** / **ThirdParties**: definidos en `models.py` (sembrados en #4); aquí se finalizan.
- **registrar_triage**: función/tool de salida estructurada (paquete `agent/`), backing del tool in-process del SDK.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: Un triage con datos parciales deja en `None` lo no provisto (verificable sin LLM).
- **SC-002**: Valores inválidos de `severity`/`claim_type` son rechazados por el esquema.
- **SC-003**: `registrar_triage` devuelve un `Triage` validado con datos válidos y error con inválidos.
- **SC-004**: La suite de pruebas colocada corre en verde.

## Supuestos

- La regla "lo no mencionado queda nulo" se garantiza por los **defaults del esquema** (`None`) + la **instrucción del prompt** (el prompt es #6).
- El **wiring** de `registrar_triage` como tool in-process del SDK y el loop del agente son **#6**.
- Campos en inglés; valores de enum/estado en español (convención #20).
