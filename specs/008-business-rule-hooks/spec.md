# Especificación de funcionalidad: Hooks de reglas de negocio (reglas 1 y 2, +3)

**Rama de funcionalidad**: `008-business-rule-hooks`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #7. Es la pieza crítica: las reglas de negocio se hacen cumplir con
**hooks del SDK**, no con el prompt (imponerlas solo por prompt es condición de fallo automático —
Principio I de la constitución). Construye sobre el núcleo del agente (#6 / spec 007), que ya expone
las seis tools de negocio del servidor `cordillera`, `registrar_triage` in-process y el loop. Aquí se
agrega el **estado de sesión derivado de resultados de herramientas** y los **hooks PreToolUse /
PostToolUse** que garantizan las reglas 1, 2 y la parte determinista de la 3.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Estado de sesión desde resultados de herramientas (Prioridad: P1)

El estado de la sesión se construye **únicamente a partir de los resultados de las herramientas**,
nunca del texto del modelo (Principio I). Hooks **PostToolUse** observan los resultados de
`verificar_identidad`, `consultar_poliza` / `verificar_cobertura` y `registrar_triage`, y registran:
identidad verificada, vigencia de póliza en la fecha del siniestro, cobertura (`si|no|incierto`) y el
triage validado (severidad, lesiones).

**Por qué esta prioridad**: Es la base de todos los hooks. Si el estado se contaminara con texto del
modelo, las reglas dejarían de ser garantías. Todo lo demás del #7 depende de este estado.

**Prueba independiente**: Alimentar al estado con resultados de herramientas simulados → los campos
quedan derivados de esos resultados; nada se toma de texto libre del modelo.

**Escenarios de aceptación**:

1. **Dado** un resultado de `verificar_identidad` con `verified=true`, **Cuando** el hook PostToolUse lo procesa, **Entonces** el estado marca identidad verificada (y el `insured_id`).
2. **Dado** un resultado de `verificar_cobertura` con `covered="si"`, **Cuando** el hook lo procesa, **Entonces** el estado registra cobertura `si`; análogo para `no`/`incierto`.
3. **Dado** un resultado de `registrar_triage` válido, **Cuando** el hook lo procesa, **Entonces** el estado guarda el triage validado (severidad, lesiones) — tomado del resultado, no del texto del modelo.

---

### Historia de usuario 2 - `guard_abrir_reclamo` niega por defecto (reglas 1, 2 y 3) (Prioridad: P1)

Un hook **PreToolUse** sobre `abrir_reclamo` **NIEGA** la apertura salvo que se cumplan TODAS las
condiciones: identidad verificada **y** póliza vigente en la fecha del siniestro **y** severidad
`leve` **y** sin lesiones **y** la cobertura no es `no`. El motivo del rechazo le indica al modelo
que **escale**. La decisión se toma con `state.motivos_bloqueo()`, una **función pura** sobre el
estado. (La cobertura `incierto` o sin verificar NO bloquea: la regla 5 es un juicio del prompt;
solo un `no` afirmativo —reclamo claramente no cubierto— impide la apertura automática.)

**Por qué esta prioridad**: Es el corazón del cumplimiento (reglas 1 y 2, y el bloqueo por lesiones de
la regla 3). Imponerlo por prompt sería fallo automático; debe ser un hook determinista.

**Prueba independiente**: Llamar al hook/`motivos_bloqueo()` con estados construidos a mano → sin
identidad, bloquea con el motivo correspondiente; con todo en orden y severidad `leve`, permite.

**Escenarios de aceptación**:

1. **Dado** un estado sin identidad verificada, **Cuando** se evalúa `guard_abrir_reclamo`, **Entonces** NIEGA con un motivo que menciona la identidad y sugiere escalar.
2. **Dado** identidad verificada pero póliza no vigente en la fecha del siniestro, **Entonces** NIEGA (regla 1).
3. **Dado** severidad `moderada` o `grave`, **Entonces** NIEGA e indica escalar a un ajustador humano (regla 2).
4. **Dado** lesiones reportadas, **Entonces** NIEGA e indica escalar (regla 3).
5. **Dado** cobertura `no` (reclamo claramente no cubierto), **Entonces** NIEGA e indica escalar.
6. **Dado** cobertura `incierto` o sin verificar, **Entonces** NO bloquea por cobertura (la regla 5 la decide el prompt).
7. **Dado** identidad verificada, póliza vigente en la fecha, severidad `leve`, sin lesiones y cobertura no `no`, **Entonces** PERMITE la apertura (incl. el caso leve de apertura automática aunque no se haya corrido `verificar_cobertura`).

---

### Historia de usuario 3 - `escalar_a_ajustador` fuerza prioridad alta con lesiones (Prioridad: P1)

Un hook **PreToolUse** sobre `escalar_a_ajustador` **fuerza** `prioridad=alta` cuando hay lesiones
reportadas en el estado, sin importar lo que haya puesto el modelo (regla 3).

**Por qué esta prioridad**: La regla 3 exige prioridad alta ante lesiones de forma determinista; no
puede depender de que el modelo recuerde ponerla.

**Prueba independiente**: Invocar el hook con un escalamiento de `prioridad=media` y estado con
lesiones → la entrada efectiva queda con `prioridad=alta`.

**Escenarios de aceptación**:

1. **Dado** lesiones reportadas y un escalamiento con `prioridad=media`, **Cuando** el hook PreToolUse lo procesa, **Entonces** la prioridad efectiva es `alta`.
2. **Dado** sin lesiones, **Entonces** el hook no altera la prioridad elegida.

### Casos límite

- Resultado de herramienta con `ok=false` (error de negocio/validación) → el estado NO marca el hecho como logrado (p. ej. identidad no verificada si `verified=false`).
- El modelo intenta `abrir_reclamo` antes de verificar identidad o cobertura → el guard niega; el estado simplemente no tiene esos hechos.
- Varias verificaciones de cobertura en la sesión → el estado refleja la cobertura del vehículo/póliza pertinente al reclamo en curso.
- "se fue sin dejar datos" u otra señal de lesiones ambigua → las lesiones se derivan del triage validado (resultado de `registrar_triage`), no del texto.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: El estado de sesión DEBE construirse SOLO a partir de resultados de herramientas (Principio I); ningún campo se deriva de texto libre del modelo.
- **FR-002**: Hooks **PostToolUse** DEBEN registrar en el estado: identidad verificada (de `verificar_identidad`), vigencia de póliza en la fecha y/o cobertura (de `consultar_poliza` / `verificar_cobertura`) y el triage validado (de `registrar_triage`).
- **FR-003**: DEBE existir `state.motivos_bloqueo()` como **función pura** sobre el estado que devuelva la lista de motivos por los que no se puede abrir un reclamo (vacía ⇒ se puede).
- **FR-004**: Un hook **PreToolUse** `guard_abrir_reclamo` DEBE NEGAR la apertura salvo que se cumplan TODAS: identidad verificada ∧ póliza vigente en la fecha ∧ severidad `leve` ∧ sin lesiones ∧ la cobertura no es `no`. El motivo del rechazo DEBE indicar al modelo que escale. La cobertura `incierto`/sin verificar NO bloquea (regla 5 = juicio del prompt); solo un `no` afirmativo impide la apertura automática. Esto mantiene el caso obligatorio "leve → apertura automática" (enunciado) sin falso-bloqueo.
- **FR-005**: Un hook **PreToolUse** sobre `escalar_a_ajustador` DEBE forzar `prioridad=alta` cuando el estado indica lesiones (regla 3), sobrescribiendo lo que haya puesto el modelo.
- **FR-006**: Los hooks DEBEN cablearse en las opciones del agente (#6, `build_options`) sin romper el loop ni la conexión MCP.
- **FR-007**: DEBEN existir pruebas deterministas (sin LLM): `motivos_bloqueo()` con estados construidos a mano (incl. "bloqueado sin identidad" llamando al hook directamente), el guard permite/niega por caso, y el forzado de prioridad por lesiones.
- **FR-008**: Las reglas 4 y 5 **siguen siendo instrucciones del prompt** (#6), NO hooks. El guard solo agrega una red determinista contra auto-abrir un reclamo con cobertura `no` afirmativa (no la regla 5 completa, que es el juicio sobre `incierto`).

### Entidades clave *(include if feature involves data)*

- **SessionState**: estado derivado de resultados de herramientas — identidad verificada (+`insured_id`), vigencia de póliza en la fecha, cobertura (`si|no|incierto`), triage validado (severidad, lesiones). Campos en inglés; valores de dominio en español.
- **`motivos_bloqueo()`**: función pura `SessionState -> list[str]` (motivos de bloqueo del reclamo).
- **Hooks**: `guard_abrir_reclamo` (PreToolUse), el forzado de prioridad en `escalar_a_ajustador` (PreToolUse), y los PostToolUse que pueblan el estado.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: El estado se deriva solo de resultados de herramientas (verificable sin LLM con resultados simulados).
- **SC-002**: `motivos_bloqueo()` es pura y determinista: sin identidad → bloquea; todo en orden + `leve` → vacía.
- **SC-003**: `guard_abrir_reclamo` niega en cada caso de bloqueo (identidad, póliza, severidad, lesiones, cobertura `no`) con un motivo que sugiere escalar, permite cuando se cumplen todas las condiciones, y NO bloquea por cobertura `incierto`/sin verificar.
- **SC-004**: El hook de `escalar_a_ajustador` fuerza `prioridad=alta` ante lesiones.
- **SC-005**: La suite de pruebas deterministas colocada corre en verde.

## Supuestos

- **Dependencia de #6**: los hooks se cablean en `build_options` (#6). Este ticket asume que #6 ya está en `main`.
- **Defensa en profundidad**: el servidor MCP (#4) ya valida identidad/póliza en `abrir_reclamo`; el guard del agente es una segunda barrera determinista del lado del agente (Principio I). No se elimina la validación del servidor.
- **Cobertura en el guard** (decisión revisada contra el enunciado, fuente de verdad): el enunciado exige hooks solo para las reglas 1 y 2; la cobertura es regla 5 (juicio). Por eso el guard solo bloquea ante cobertura `no` afirmativa (red determinista contra auto-abrir un reclamo no cubierto) y NO ante `incierto`/sin verificar — así no falso-bloquea el caso obligatorio "leve → apertura automática". La regla 5 completa ("cobertura incierta → escalar") sigue siendo instrucción del prompt (#6) y, más adelante, el subagente `revisor-cobertura` (#8). El issue #7 pedía `cobertura si`; se ajustó por fidelidad al enunciado.
- **Vigencia vs. cobertura**: `verificar_cobertura` ya considera la fecha del siniestro; la "vigencia en la fecha" se deriva de los resultados de `consultar_poliza` (`valid_from`/`valid_to`) y/o de que la cobertura sea `si`. El plan fija el mecanismo exacto.
- **Convención de idioma**: identificadores/campos en inglés; valores de dominio y motivos de cara al modelo en español (Principios IV/VI). `motivos_bloqueo` conserva su nombre en español por ser el contrato citado en el issue.
- **Fuera de alcance**: subagente `revisor-cobertura` (#8), interfaz de chat (#9), pruebas con modelo real (#12).
