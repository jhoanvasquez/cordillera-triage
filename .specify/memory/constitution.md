# Constitución de Cordillera Triage

Agente de triage de primer contacto para siniestros de auto de *Aseguradora Cordillera*,
construido con el Claude Agent SDK y un servidor MCP del escenario. Esta constitución recoge
los principios que todo ticket debe respetar. Las reglas de negocio y los criterios de
severidad se citan **textualmente** porque el enunciado los declara no negociables.

## Principios fundamentales

### I. Reglas de negocio garantizadas por hooks, no por el prompt (NO NEGOCIABLE)
Todo aquello cuya violación constituya una falla de negocio, seguridad o cumplimiento se hace
cumplir con un **hook** (del SDK o de Claude Code); las cuestiones de estilo y de criterio van
en **instrucciones**. Una regla de negocio que dependa solo del prompt es una falta grave.
- El estado de la sesión se construye **únicamente a partir de resultados de herramientas**,
  nunca de lo que dice el modelo.
- Las reglas 1 y 2 (y la parte determinista de la regla 3) son **hooks del SDK**. Las reglas 4
  y 5 son juicios → instrucciones + el subagente de cobertura.
- Determinar la severidad es un juicio (prompt + esquema); actuar sobre la severidad es una
  regla (hook).

### II. Solo datos ficticios (NO NEGOCIABLE)
Ningún valor con forma de dato real en todo el repositorio — ni en fixtures, ni en logs, ni en
configuración.
- Los identificadores ficticios usan formas imposibles por diseño que no pueden coincidir con
  formatos reales colombianos: documentos como `DOC-FIC-0001`, placas como `FIC-01A`. El
  marcador reservado `FIC`/`DOC-FIC` es obligatorio.
- Un hook PreToolUse (`block_real_ids`) y una verificación en CI/pre-commit rechazan cualquier
  cosa con forma de documento o placa real antes de que el archivo exista.

### III. Desarrollo guiado por especificaciones (NO NEGOCIABLE)
No se escribe código de producción en `src/**` sin su `spec.md`, `plan.md` y `tasks.md`.
- Un hook PreToolUse (`require_spec`) bloquea escrituras en `src/**` salvo que exista
  `specs/<rama-actual>/spec.md`. Los tickets de configuración no producen código de producción,
  por lo que el hook solo protege `src/**`.
- Los requisitos funcionales viven en `spec.md`; las decisiones de arquitectura/técnicas en
  `plan.md`; los principios del proyecto, aquí; las decisiones de mecanismo del ecosistema en
  `DECISIONES.md`. La separación es por artefacto, no una división posterior.
- Los artefactos de Spec Kit se versionan; son evidencia revisada en la sustentación.

### IV. Estructurado antes que texto libre
El triage y la E/S de las herramientas se validan contra esquemas, nunca texto libre.
- El triage se produce como salida estructurada (Pydantic): tipo de siniestro, severidad,
  lesiones reportadas, terceros y datos faltantes. **Lo que el reporte no menciona queda nulo;
  el agente no lo inventa.**
- Las herramientas devuelven la forma nativa de MCP (`isError`, `content`, `structuredContent`).
  Los errores llevan `errorCategory` en `transient | validation | business | permissions` e
  `isRetryable`. **Una búsqueda sin resultados no es un error** (`isError: false`,
  `resultCount: 0`).
- Convención: el envelope de transporte/errores de MCP en inglés; los valores de dominio en
  español (`severidad: leve|moderada|grave`, `cubierto: si|no|incierto`).

### V. Trazabilidad autónoma
El GitHub Project y los issues son la única fuente de verdad y se actualizan solos.
- Los tickets pasan Todo → In progress (inicio) → In review (PR) → Done (merge) sin edición
  manual.
- Cada PR referencia y cierra su issue; cada issue recibe comentarios de avance.
- Los commits siguen Conventional Commits (`<tipo>(<alcance>): <asunto>`), sin atribución a IA.
  Un evaluador debe poder reconstruir el proyecto solo mirando GitHub.

### VI. Idioma de los artefactos
Los artefactos de proyecto y la documentación se redactan en **español neutro/profesional**:
esta constitución, las specs, los planes, las tareas y los documentos (`DECISIONES.md`,
`README.md`).
- Permanecen en **inglés**: los identificadores de código, los nombres de archivos y rutas, y
  el envelope de transporte/errores de MCP (Principio IV).
- Permanecen **textuales en español**: las reglas de negocio y los criterios de severidad del
  enunciado.

## Reglas de negocio y criterios de severidad (textual — no se negocian)

**Criterios de severidad de la aseguradora:**
- **Leve**: Daños en piezas exteriores. El vehículo puede seguir circulando.
- **Moderada**: Daños que impiden circular o que afectan partes mecánicas o eléctricas.
- **Grave**: Posible pérdida total, incendio o volcamiento.

**Reglas de negocio de la aseguradora, que tu solución debe respetar:**
1. Ningún reclamo se abre sin identidad verificada del asegurado y sin confirmar que la póliza estaba vigente en la fecha del siniestro.
2. Un siniestro de severidad leve puede abrirse como reclamo de forma automática. Uno de severidad moderada o grave requiere un ajustador humano.
3. Si el reporte menciona lesiones a personas, el caso se escala a un ajustador con prioridad alta, sin importar la severidad del daño.
4. Si el asegurado pide explícitamente hablar con una persona, se escala de inmediato, sin investigar primero.
5. Si la póliza no cubre el caso con claridad, por ejemplo un vehículo particular que estaba haciendo domicilios, el agente escala en lugar de improvisar.

**Mapeo de aplicación (hooks vs instrucciones):**

| Regla | Mecanismo | Dónde |
|---|---|---|
| 1 — identidad + póliza vigente | **Hook** | PreToolUse `abrir_reclamo` niega salvo identidad verificada Y póliza vigente en la fecha del siniestro |
| 2 — leve automático, moderada/grave humano | **Hook** | PreToolUse `abrir_reclamo` niega salvo severidad `leve`; en otro caso, escala |
| 3 — lesiones → escalar, prioridad alta | **Hook** | PreToolUse `escalar_a_ajustador` fuerza `prioridad = alta`; `abrir_reclamo` se niega si hay lesiones |
| 4 — pide hablar con una persona → escalar ya | Instrucción | System prompt; sin investigar primero |
| 5 — cobertura no clara → escalar | Instrucción + subagente | `revisor-cobertura`; `incierto` → escalar |

## Seguridad, secretos y controles de calidad

- Los **secretos** nunca se leen ni se modifican desde Claude Code: `permissions.deny` sobre
  `Read/Edit` de `.env*` y `**/secrets/**`. Ninguna credencial, `.env` ni token en el
  repositorio o en el `.zip` de entrega — la historia de git no se puede reescribir, así que
  una filtración es permanente.
- El **formateo** corre después de cada edición: hook PostToolUse → `ruff format` sobre el
  archivo editado.
- **Revisión independiente antes del PR**: un subagente `code-reviewer` (contexto fresco, solo
  lectura) y un subagente `compliance-reviewer` (reglas de negocio 1–5 contra esta
  constitución) corren antes de abrir un PR, orquestados por `/ship`.
- **Ciclo agéntico correcto**: el loop termina según la razón de parada del modelo — nunca por
  un número de iteraciones ni por buscar palabras en el texto.

## Gobernanza

Esta constitución prevalece sobre otras prácticas en este repositorio. Las reglas de negocio y
los criterios de severidad están fijados por el enunciado de la prueba y NO DEBEN alterarse.
Los demás principios pueden enmendarse actualizando este archivo con un incremento de versión y
una línea de justificación; las enmiendas deben mantener el repositorio consistente con el
enunciado. Toda spec, plan y revisión verifica el cumplimiento de estos principios; cualquier
complejidad añadida debe responder a una necesidad real o eliminarse.

**Version**: 1.1.0 | **Ratified**: 2026-10-14 | **Last Amended**: 2026-10-15
