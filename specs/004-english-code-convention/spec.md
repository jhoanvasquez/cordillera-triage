# Especificación de funcionalidad: Convención de idioma del código (inglés)

**Rama de funcionalidad**: `004-english-code-convention`

**Creado**: 2026-10-15

**Estado**: Borrador

**Entrada**: Issue de GitHub #20. Adoptar la convención "código en inglés, dominio en español" en
todo el repositorio y documentarla en la constitución. Refactor sin cambio de comportamiento.

## Escenarios de usuario y pruebas *(obligatorio)*

### Historia de usuario 1 - Identificadores de código en inglés (Prioridad: P1)

Todo el código interno usa identificadores en inglés: variables, funciones internas, clases,
nombres de campo Pydantic, **claves JSON**, nombres de archivo de datos, comentarios y docstrings
internos.

**Por qué esta prioridad**: Es la convención profesional acordada; un código mitad-español
mitad-inglés es difícil de mantener y de defender.

**Prueba independiente**: Revisar `src/cordillera/` — ningún identificador de dominio en español
salvo las excepciones permitidas; las pruebas siguen en verde.

**Escenarios de aceptación**:

1. **Dado** los modelos y el servicio, **Cuando** se revisan, **Entonces** los campos y funciones internas están en inglés (`document`, `plate`, `valid_from`, `search_insured`, …).
2. **Dado** los archivos de fixtures, **Cuando** se revisan, **Entonces** las claves JSON y los nombres de archivo están en inglés (`insured.json`, `vehicles.json`, `policies.json`).

---

### Historia de usuario 2 - El contrato de dominio permanece en español (Prioridad: P1)

Lo que es contrato externo o vocabulario de dominio NO cambia.

**Por qué esta prioridad**: Los nombres de herramientas los fija el enunciado; los valores de
estado y las reglas son dominio y no se negocian.

**Prueba independiente**: Las 6 herramientas conservan su nombre español; los valores de estado y
las descripciones de herramientas siguen en español.

**Escenarios de aceptación**:

1. **Dado** las herramientas MCP, **Entonces** sus **nombres** (`buscar_asegurado`, `consultar_poliza`, …), sus **parámetros** (`documento`, `placa`, `fecha`, …) y sus **descripciones** permanecen en español (contrato agent-facing del enunciado).
2. **Dado** los valores de estado, **Entonces** `cubierto ∈ {si, no, incierto}` y `severidad ∈ {leve, moderada, grave}` permanecen en español (cambia el nombre del campo, no el valor).

---

### Historia de usuario 3 - Comportamiento preservado (Prioridad: P1)

El refactor no cambia el comportamiento: toda la suite de pruebas pasa igual.

**Por qué esta prioridad**: Un refactor que rompe algo no es un refactor.

**Prueba independiente**: `pytest` en verde antes y después; mismas aserciones de resultado (solo
cambian los nombres de campo/acceso).

**Escenarios de aceptación**:

1. **Dado** la suite completa, **Cuando** se corre tras el refactor, **Entonces** pasa sin fallos.
2. **Dado** una llamada a `buscar_asegurado` por nombre homónimo, **Entonces** sigue devolviendo varias coincidencias (comportamiento idéntico).

### Casos límite

- Un campo que es a la vez dato de dominio y clave JSON (`cubierto`) → la **clave** pasa a inglés (`covered`), el **valor** sigue en español (`si|no|incierto`).
- Parámetros de herramienta vs. parámetros de función interna → los de herramienta (contrato) quedan en español; los de `service.py` pueden ir en inglés.

## Requisitos *(obligatorio)*

### Requisitos funcionales

- **FR-001**: Los identificadores de código interno (variables, funciones internas, clases, campos Pydantic) DEBEN estar en inglés.
- **FR-002**: Las claves JSON y los nombres de archivo de fixtures DEBEN estar en inglés.
- **FR-003**: Los comentarios y docstrings internos DEBEN estar en inglés.
- **FR-004**: Los **nombres** de las 6 herramientas MCP DEBEN permanecer en español (contrato del enunciado).
- **FR-005**: Los **parámetros** y las **descripciones** de las herramientas MCP DEBEN permanecer en español (contrato agent-facing).
- **FR-006**: Los **valores** de estado (`si|no|incierto`, `leve|moderada|grave`) y las reglas de negocio DEBEN permanecer en español.
- **FR-007**: El refactor NO DEBE cambiar el comportamiento; la suite de pruebas DEBE quedar en verde.
- **FR-008**: La constitución (Principio VI) DEBE actualizarse con esta convención.

### Entidades clave — mapeo de renombres (referencia de implementación)

| Español (actual) | Inglés (nuevo) |
|---|---|
| `asegurados.json` / `vehiculos.json` / `polizas.json` | `insured.json` / `vehicles.json` / `policies.json` |
| `documento`, `nombre`, `fecha_nacimiento` | `document`, `name`, `birth_date` |
| `placa`, `marca`, `modelo`, `uso` | `plate`, `make`, `model`, `use` |
| `asegurado_id`, `poliza_id`, `vehiculo_id` | `insured_id`, `policy_id`, `vehicle_id` |
| `numero`, `vigencia_desde`, `vigencia_hasta`, `deducible`, `amparos` | `number`, `valid_from`, `valid_to`, `deductible`, `coverages` |
| `tipo`, `cubierto` (clave), `condiciones` | `type`, `covered` (clave; valor sigue `si/no/incierto`), `conditions` |
| `cargar_asegurados/vehiculos/polizas` | `load_insured/vehicles/policies` |
| `AseguradoResumen`, `PolizaDetalle`, `AmparoDetalle` | `InsuredSummary`, `PolicyDetail`, `CoverageDetail` |
| `RespuestaBusqueda/Verificacion/Poliza/Cobertura` | `SearchResponse`, `VerificationResponse`, `PolicyResponse`, `CoverageResponse` |
| `resultados`, `verificado`, `motivo` | `results`, `verified`, `reason` |
| `CategoriaError`, `_coincidencias`, `DOCUMENTO_FLAKY` | `ErrorCategory`, `_matches`, `FLAKY_DOCUMENT` |

## Criterios de éxito *(obligatorio)*

### Resultados medibles

- **SC-001**: `src/cordillera/` no contiene identificadores de dominio en español salvo las excepciones de FR-004/005/006.
- **SC-002**: La suite de pruebas pasa en verde tras el refactor (comportamiento idéntico).
- **SC-003**: La constitución refleja la convención (Principio VI).

## Supuestos

- Es un refactor interno; no agrega ni quita funcionalidad.
- Las herramientas MCP mantienen su contrato externo (nombres, parámetros, descripciones) en español.
- Afecta las funcionalidades #1, #2 y #3 (ya mergeadas); se hace de una sola vez para consistencia.
