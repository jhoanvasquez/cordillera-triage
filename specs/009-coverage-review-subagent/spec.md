# Especificación de funcionalidad: Subagente de revisión de cobertura (`revisor-cobertura`)

**Rama de funcionalidad**: `009-coverage-review-subagent`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #8. Define el subagente `revisor-cobertura` vía la opción `agents` del
Claude Agent SDK (`AgentDefinition`), con herramientas restringidas a póliza/cobertura. Cumple el
comportamiento obligatorio #10 del enunciado ("al menos un subagente; el agente delega una parte del
trabajo pasando el contexto de forma explícita") y cierra la **regla 5** de verdad: el subagente
produce un veredicto de cobertura y, ante `incierto`, el caso se escala. Construye sobre el núcleo del
agente (#6) y convive con los hooks (#7).

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Subagente con herramientas restringidas (Prioridad: P1)

`revisor-cobertura` se define como `AgentDefinition` (opción `agents` del SDK) con un prompt versionado
y herramientas **restringidas** a `consultar_poliza` y `verificar_cobertura` — no puede abrir reclamos
ni escalar ni registrar triage. Se registra en las opciones del agente (#6, `build_options`).

**Por qué esta prioridad**: El enunciado exige un subagente con herramientas limitadas a su rol; es la
base del comportamiento #10.

**Prueba independiente**: Inspeccionar la `AgentDefinition` construida → sus `tools` son exactamente
las dos de cobertura y queda registrada bajo `agents["revisor-cobertura"]`.

**Escenarios de aceptación**:

1. **Dado** el agente iniciado, **Cuando** se construyen las opciones, **Entonces** existe `agents["revisor-cobertura"]` con `tools` = [`mcp__cordillera__consultar_poliza`, `mcp__cordillera__verificar_cobertura`] y ninguna otra.
2. **Dado** el subagente, **Entonces** su prompt está versionado bajo `src/cordillera/agent/` (fuente única), como el system prompt principal.

---

### Historia de usuario 2 - Veredicto de cobertura estructurado (Prioridad: P1)

El subagente produce un **veredicto estructurado** validable: `covered` (`si|no|incierto`),
`coverage_type`, `deductible`, `tow_covered`, `reason`. Existe un esquema Pydantic `CoverageVerdict`
y un parser que lo valida; el `incierto` es un valor de primera clase.

**Por qué esta prioridad**: El issue exige un veredicto estructurado que incluya `incierto`; es el dato
sobre el que el agente decide escalar (regla 5).

**Prueba independiente**: Parsear un veredicto válido → `CoverageVerdict`; uno inválido → error; un
veredicto con `covered="incierto"` se representa correctamente.

**Escenarios de aceptación**:

1. **Dado** un veredicto válido (incl. `covered="incierto"`), **Cuando** se parsea, **Entonces** devuelve un `CoverageVerdict` validado.
2. **Dado** un `covered` fuera de `{si, no, incierto}`, **Cuando** se valida, **Entonces** se rechaza.
3. **Dado** un reporte que no menciona la grúa, **Entonces** `tow_covered` queda nulo (no se inventa).

---

### Historia de usuario 3 - Delegación con contexto explícito + escalar ante `incierto` (Prioridad: P1)

El agente principal delega la revisión de cobertura pasando el contexto **explícitamente** (número de
póliza, fecha del siniestro, tipo de siniestro, uso del vehículo, pregunta del asegurado). Si el
veredicto es `incierto`, el agente **escala** en lugar de improvisar (regla 5).

**Por qué esta prioridad**: El enunciado pide delegación con contexto explícito (#10) y escalamiento
ante cobertura no clara (regla 5 / comportamiento #8).

**Prueba independiente**: Verificar en el prompt del agente principal la instrucción de delegar con el
contexto enumerado y de escalar ante `incierto` (behavior guiado; la ejecución real es #12).

**Escenarios de aceptación**:

1. **Dado** el system prompt principal, **Entonces** instruye delegar la cobertura en `revisor-cobertura` pasando póliza, fecha, tipo, uso del vehículo y la pregunta del asegurado.
2. **Dado** un veredicto `incierto` (p. ej. vehículo particular que hacía domicilios), **Entonces** el prompt indica escalar a un ajustador.

### Casos límite

- El subagente no puede abrir reclamos ni escalar (sus tools lo impiden); solo evalúa cobertura.
- Pregunta específica por la grúa → `tow_covered` responde ese asunto por separado (behavior #6: varias preocupaciones).
- Veredicto `no` (p. ej. póliza vencida en la fecha) → el agente no auto-abre; el guard de #7 ya bloquea un `no` afirmativo.
- Datos insuficientes para decidir cobertura → `covered="incierto"` con `reason`.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: DEBE existir `revisor-cobertura` como `AgentDefinition` registrada en `agents` (SDK), con `tools` restringidas EXACTAMENTE a `consultar_poliza` y `verificar_cobertura`.
- **FR-002**: El prompt del subagente DEBE estar versionado bajo `src/cordillera/agent/` (fuente única).
- **FR-003**: DEBE existir un esquema `CoverageVerdict` (Pydantic) con `covered: Literal["si","no","incierto"]`, `coverage_type`, `deductible`, `tow_covered`, `reason`; lo no mencionado queda nulo. Convención VI: claves en inglés, valores de dominio en español. (Mapeo al issue: `cubierto→covered`, `amparo→coverage_type`, `grua_cubierta→tow_covered`, `motivo→reason`.)
- **FR-004**: DEBE existir un parser que valide un veredicto contra `CoverageVerdict`; entrada inválida → error de validación (no un veredicto a medias).
- **FR-005**: El system prompt principal (#6) DEBE instruir: delegar la cobertura en `revisor-cobertura` pasando contexto explícito (póliza, fecha, tipo, uso del vehículo, pregunta); y escalar ante `incierto` (regla 5).
- **FR-006**: El subagente DEBE cablearse en `build_options` (#6) sin romper el loop, los hooks (#7) ni la conexión MCP.
- **FR-007**: DEBEN existir pruebas deterministas (sin LLM): la `AgentDefinition` tiene las tools correctas y queda registrada; `CoverageVerdict`/parser (válido, inválido, `incierto`, nulabilidad de `tow_covered`).

### Entidades clave *(include if feature involves data)*

- **`revisor-cobertura`**: `AgentDefinition` (description, prompt versionado, `tools` restringidas).
- **CoverageVerdict**: esquema del veredicto (`covered`, `coverage_type`, `deductible`, `tow_covered`, `reason`).
- **Prompt del subagente**: artefacto versionado bajo `agent/`.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: `agents["revisor-cobertura"]` existe con exactamente las dos tools de cobertura (verificable sin LLM).
- **SC-002**: `CoverageVerdict` valida un veredicto correcto (incl. `incierto`) y rechaza uno inválido.
- **SC-003**: El system prompt principal contiene la guía de delegación con contexto explícito y de escalar ante `incierto`.
- **SC-004**: Los hooks (#7) y el loop (#6) siguen funcionando con el subagente cableado (suite en verde).

## Supuestos

- **Dependencia de #6/#7**: el subagente se registra en `build_options` junto al system prompt, las tools y los hooks. Asume #6 y #7 en `main`.
- **Veredicto por salida del subagente**: un subagente del SDK devuelve texto; el veredicto estructurado se logra instruyendo al subagente a emitir JSON conforme a `CoverageVerdict`, y validándolo con el parser (patrón análogo a `registrar_triage`). El esquema es la fuente de forma; el prompt, el productor.
- **Regla 5**: el escalamiento ante `incierto` es una **instrucción** (regla 5 = juicio, como se fijó en #7); no es un hook. El subagente aporta el veredicto; el agente principal decide con su prompt.
- **Idioma**: claves de `CoverageVerdict` en inglés, valores en español (convención VI); el prompt del subagente es contenido de producto en español neutro.
- **Dos clases de subagente**: este es el subagente del **Agent SDK** (delegación del agente, behavior #10). Los subagentes de **Claude Code** (`code-reviewer`, `compliance-reviewer`) del ecosistema son #14, distintos.
- **Fuera de alcance**: ejecución real de la delegación con modelo (que el agente efectivamente llame al subagente y escale) es #12; la interfaz de chat es #9.
