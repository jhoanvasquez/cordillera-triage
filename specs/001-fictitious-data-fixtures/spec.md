# Especificación de funcionalidad: Fixtures de datos ficticios

**Rama de funcionalidad**: `001-fictitious-data-fixtures`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #1 — "Fictitious data fixtures". El conjunto de datos respalda el
servidor MCP `cordillera` y todos los escenarios de triage posteriores, usando identificadores
ficticios imposibles por diseño.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Todos los escenarios obligatorios de triage tienen datos de respaldo (Prioridad: P1)

El agente de triage y sus pruebas deben reproducir los 8 escenarios obligatorios de forma
determinista. Los fixtures proveen, para cada escenario, registros concretos de
asegurado/vehículo/póliza cuyos atributos determinan el camino de triage esperado.

**Por qué esta prioridad**: Sin estos datos, ninguna herramienta, prueba o demo puede ejecutarse.
Es la base de la que dependen todos los demás tickets.

**Prueba independiente**: Para cada uno de los 8 casos, confirmar que existen los registros que
necesita con los atributos requeridos (póliza vigente vs. vencida, cobertura de grúa, dos
vehículos, vehículo de uso particular, etc.) — verificable leyendo solo los datos, sin necesidad
del agente.

**Escenarios de aceptación**:

1. **Dado** el caso del mensaje de ejemplo, **Cuando** se busca al asegurado, **Entonces** existe un asegurado con un vehículo, una póliza vigente en la fecha del siniestro y cobertura de grúa, consistente con un reporte de lesión y un tercero que se fue sin dejar datos.
2. **Dado** el caso del choque leve, **Cuando** se consultan póliza y cobertura, **Entonces** existe un asegurado cuya póliza vigente y daño leve permiten la apertura automática del reclamo.
3. **Dado** el caso de póliza vencida, **Entonces** existe un asegurado cuya póliza NO estaba vigente en la fecha del siniestro.
4. **Dado** el caso de dos vehículos, **Entonces** existe un asegurado con dos vehículos, ambos con pólizas vigentes.
5. **Dado** el caso de cobertura no clara, **Entonces** existe un asegurado con un vehículo de uso particular cuya actividad reportada (domicilios) hace que la cobertura sea `incierto`.

---

### Historia de usuario 2 - Todos los datos son inequívocamente ficticios (Prioridad: P1)

Ningún valor en ningún lugar puede confundirse con un documento de identidad o una placa de
vehículo colombianos reales — ni en fixtures, ni en logs, ni en configuración.

**Por qué esta prioridad**: Un dato con forma real es una falta grave según el enunciado, sin
importar el resto de la entrega.

**Prueba independiente**: Un barrido por expresiones regulares sobre todos los archivos de
fixtures encuentra cero valores que coincidan con formas reales de documento/placa; cada
identificador lleva un marcador ficticio reservado.

**Escenarios de aceptación**:

1. **Dado** el conjunto completo de archivos de fixtures, **Cuando** se barre buscando patrones reales de documento/placa, **Entonces** no se encuentran coincidencias.
2. **Dado** cualquier asegurado o vehículo, **Entonces** su documento/placa usa un formato ficticio reservado (p. ej. `DOC-FIC-0001`, placa `FIC-01A`).

---

### Historia de usuario 3 - Soporta la búsqueda y verificación de identidad (Prioridad: P2)

`buscar_asegurado` puede devolver varias coincidencias; `verificar_identidad` necesita un segundo
dato para confirmar la identidad.

**Por qué esta prioridad**: Requerido por los contratos de las herramientas MCP y por los
comportamientos de "dos vehículos / varias coincidencias", pero solo después de que existan los
datos P1.

**Prueba independiente**: Al menos un criterio de búsqueda devuelve más de un asegurado; cada
asegurado lleva un atributo verificable adicional, distinto de la clave de búsqueda.

**Escenarios de aceptación**:

1. **Dado** dos asegurados que comparten un nombre, **Cuando** se busca por ese nombre, **Entonces** se devuelven ambos.
2. **Dado** un asegurado, **Entonces** existe un segundo dato ficticio (p. ej. fecha de nacimiento) para confirmar la identidad.

---

### Historia de usuario 4 - Soporta el escenario de falla transitoria (Prioridad: P3)

El conjunto de datos reserva un registro o condición que el servidor MCP puede usar para simular
una falla transitoria de forma determinista.

**Por qué esta prioridad**: Necesario para uno de los 8 casos, pero el mecanismo de la falla vive
en la funcionalidad del servidor MCP.

**Prueba independiente**: El registro/flag reservado es identificable en los datos.

**Escenarios de aceptación**:

1. **Dado** el escenario de falla transitoria, **Entonces** existe un registro o flag designado para que el servidor dispare un error transitorio reintentable.

### Casos límite

- Un asegurado sin póliza, o una póliza sin vehículo asociado → las herramientas deben poder devolver un resultado vacío (no un error).
- Una fecha de siniestro exactamente en el límite de inicio o fin de una póliza → la vigencia debe ser inequívoca a partir de los datos.
- Un vehículo cuyo uso declarado (particular) entra en conflicto con la actividad reportada (domicilios) → los datos deben soportar un resultado `cubierto: incierto`.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: El conjunto de datos DEBE incluir asegurados, vehículos y pólizas suficientes para reproducir los 8 escenarios obligatorios del enunciado.
- **FR-002**: Todo identificador (documento, placa, número de póliza) DEBE usar un formato ficticio imposible por diseño que no pueda coincidir con un documento o placa colombianos reales, con un marcador reservado (p. ej. `FIC` / `DOC-FIC`).
- **FR-003**: Ningún valor de los fixtures (nombres, números, fechas, notas de texto libre) PUEDE parecerse a datos personales reales, en ningún lugar — incluidos los comentarios.
- **FR-004**: Al menos una póliza DEBE estar vigente en la fecha del siniestro de su escenario, y al menos una DEBE estar vencida antes de esa fecha.
- **FR-005**: Al menos un asegurado DEBE tener dos vehículos, ambos con pólizas vigentes.
- **FR-006**: Al menos una póliza DEBE incluir cobertura de grúa; al menos un vehículo DEBE ser de uso particular con una actividad reportada que haga la cobertura `incierto`.
- **FR-007**: Los datos DEBEN soportar varias coincidencias para `buscar_asegurado`, y cada asegurado DEBE llevar un segundo dato para `verificar_identidad`.
- **FR-008**: El conjunto de datos DEBE reservar un registro o condición para el escenario de falla transitoria (el mecanismo lo define la funcionalidad del servidor MCP).
- **FR-009**: El resultado de triage esperado de cada escenario DEBE poder derivarse únicamente de los datos (insumos de severidad, presencia de lesiones, presencia de terceros, vigencia de la póliza, cobertura).

### Entidades clave *(incluir si la funcionalidad involucra datos)*

- **Asegurado**: persona ficticia — documento ficticio, nombre ficticio, un segundo dato de verificación; posee uno o más vehículos.
- **Vehículo**: placa ficticia, uso declarado (p. ej. particular), vinculado a un asegurado y a una póliza.
- **Póliza**: número ficticio, ventana de vigencia (desde/hasta), vehículo vinculado, amparos contratados y deducibles.
- **Amparo (cobertura)**: tipo (p. ej. grúa, daños), cubierto sí/no, y condiciones que pueden dar `incierto`.
- **Marcador de falla**: un registro o flag designado que habilita el escenario de falla transitoria.

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: Los 8 escenarios obligatorios tienen registros de respaldo concretos con los atributos que cada uno requiere (100% de cobertura de escenarios).
- **SC-002**: Un barrido buscando documentos/placas con forma real sobre todo el repositorio devuelve cero coincidencias.
- **SC-003**: Teniendo solo los fixtures, una persona revisora puede predecir el camino de triage esperado para cada uno de los 8 casos.
- **SC-004**: `buscar_asegurado` puede ejercitarse contra los datos para devolver tanto un resultado de coincidencia única como uno de varias coincidencias.

## Supuestos

- Los datos viven como archivos JSON locales (sin base de datos real); el layout exacto de archivos y el esquema son decisiones de diseño que se difieren a `plan.md`.
- El mecanismo de la falla transitoria (variable de entorno vs. registro "flaky") lo define la funcionalidad del servidor MCP; esta funcionalidad solo garantiza el dato/registro que ese mecanismo necesita.
- "Con forma real" se juzga contra las formas colombianas (cédula de 8 a 10 dígitos; placa de 3 letras + 3 dígitos); los ficticios NO DEBEN coincidir con estas.
- Los valores de dominio permanecen en español según la constitución (`severidad`, `cubierto`, etc.).
