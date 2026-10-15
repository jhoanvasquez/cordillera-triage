# Plan de implementación: Fixtures de datos ficticios

**Rama**: `001-fictitious-data-fixtures` | **Fecha**: 2026-10-15 | **Especificación**: `specs/001-fictitious-data-fixtures/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/001-fictitious-data-fixtures/spec.md`

## Resumen

Diseño del conjunto de datos ficticios (JSON locales) que respalda el servidor MCP `cordillera`.
Define el layout de archivos, el esquema de cada entidad, el roster concreto de registros con su
mapeo a los 8 casos de prueba obligatorios, y las convenciones de formatos ficticios imposibles
por diseño. No incluye el servidor ni las herramientas (eso vive en los tickets #2–#4); esta
funcionalidad entrega solo los datos y una prueba determinista que valida formatos y cobertura.

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (los datos son JSON puro; se consumirán con Pydantic v2 en #2–#4)

**Dependencias principales**: ninguna para los datos; `pytest` para la prueba de validación

**Almacenamiento**: archivos JSON locales bajo `src/cordillera/data/` (sin base de datos)

**Pruebas**: `pytest`; una prueba determinista colocada que valida formatos ficticios, integridad referencial y cobertura de los 8 casos

**Plataforma objetivo**: local (el servidor MCP corre por stdio)

**Tipo de proyecto**: proyecto único (biblioteca/CLI)

**Objetivos de rendimiento**: N/A (pocos registros, en memoria)

**Restricciones**: cero valores con forma real; formatos imposibles por diseño; valores de dominio en español

**Escala/Alcance**: ~6 asegurados, ~6 vehículos, ~6 pólizas — el mínimo para cubrir los 8 casos

## Verificación de la constitución

*GATE: debe pasar antes de implementar.*

- **Principio II (Solo datos ficticios)**: CUMPLE — es el objetivo del ticket; todo identificador usa `DOC-FIC-####` / placa `FIC-##X` / `POL-FIC-####`, imposibles de confundir con formatos colombianos reales.
- **Principio III (SDD)**: CUMPLE — este plan precede al código; `spec.md` ya existe.
- **Principio IV (Estructurado)**: CUMPLE — los JSON se alinean con los futuros esquemas Pydantic; los valores de dominio van en español.
- **Principio VI (Idioma)**: CUMPLE con una aclaración de diseño (ver abajo): los **nombres de campo del modelo de dominio van en español** (son vocabulario de dominio, como `severidad`/`cubierto`), mientras que el envelope de transporte MCP permanece en inglés.

Sin violaciones.

### Decisión de idioma de los campos

Los nombres de campo de las entidades de dominio (`documento`, `placa`, `vigencia_desde`,
`amparos`, `cubierto`, …) se escriben en **español**, de forma coherente con los nombres de
herramientas del enunciado (`buscar_asegurado`, `consultar_poliza`) y con el esquema de triage.
Esto es dominio, no un identificador técnico neutro. El envelope de transporte/errores de MCP
(`isError`, `errorCategory`, `isRetryable`, `resultCount`) permanece en inglés (Principio IV).

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/001-fictitious-data-fixtures/
├── spec.md       # El QUÉ y el PORQUÉ
├── plan.md       # Este archivo
└── tasks.md      # Lista de tareas (siguiente paso)
```

### Código fuente (raíz del repositorio)

```text
src/cordillera/
└── data/
    ├── __init__.py        # marca el paquete (el loader vive en el ticket del MCP)
    ├── asegurados.json    # personas aseguradas
    ├── vehiculos.json     # vehículos, vinculados a asegurado y póliza
    ├── polizas.json       # pólizas con amparos anidados
    └── test_fixtures.py   # prueba determinista colocada (formatos + integridad + cobertura)
```

**Decisión de estructura**: tres archivos JSON **normalizados** (asegurados / vehículos / pólizas),
enlazados por IDs. Refleja el core de la aseguradora y mapea 1:1 con las herramientas
(`buscar_asegurado`→asegurados, `consultar_poliza`→pólizas). *Alternativa descartada:* un único
`fixtures.json` — se descartó porque oscurece el mapeo a herramientas y dificulta razonar sobre la
integridad referencial. La prueba se coloca junto a los datos (necesidad #3 del enunciado).

## Modelo de datos

Esquema conceptual (los tipos finales se formalizan con Pydantic en #2–#4):

- **Asegurado**: `id`, `documento` (`DOC-FIC-####`), `nombre`, `fecha_nacimiento` (segundo dato para `verificar_identidad`).
- **Vehículo**: `id`, `placa` (`FIC-##X`), `marca`, `modelo`, `uso` (`particular`), `asegurado_id`, `poliza_id`.
- **Póliza**: `id`, `numero` (`POL-FIC-####`), `asegurado_id`, `vehiculo_id`, `vigencia_desde`, `vigencia_hasta`, `deducible`, `amparos: [{ tipo, cubierto, condiciones }]`.
- **Amparo**: `tipo` (p. ej. `grua`, `danos`), `cubierto` (`si|no|incierto`), `condiciones` (texto que explica el `incierto`).

Convenciones de formato ficticio (imposibles contra formas reales colombianas):
- Documento: `DOC-FIC-0001` (real: 8–10 dígitos → no coincide).
- Placa: `FIC-01A` (real: 3 letras + 3 dígitos → no coincide).
- Póliza: `POL-FIC-0001`.
- Fecha de referencia del escenario: **2026-10-10** (fecha del siniestro usada por los casos con fecha).

## Roster de registros y mapeo a los 8 casos

| Registro | Datos clave | Sirve al caso |
|---|---|---|
| Asegurado A1 (`DOC-FIC-0001`) + Vehículo `FIC-01A` + Póliza `POL-FIC-0001` **vigente**, amparo `grua: si` | 1 vehículo, póliza vigente en 2026-10-10, cubre grúa | #1 mensaje de ejemplo (lesión + pregunta grúa), #2 choque leve (apertura automática), #3 "hablar con persona", #6 abrir sin identidad (bloqueado por hook) |
| Asegurado A2 (`DOC-FIC-0002`, "María Gómez") + Vehículos `FIC-02B` y `FIC-03C` + Pólizas `POL-FIC-0002/0003` **vigentes** | 2 vehículos, ambos vigentes | #4 dos vehículos sin especificar |
| Asegurado A3 (`DOC-FIC-0003`) + Vehículo `FIC-04D` + Póliza `POL-FIC-0004` **vencida** (hasta 2025-01-01) | póliza no vigente en 2026-10-10 | #5 póliza vencida |
| Asegurado A4 (`DOC-FIC-0004`) + Vehículo `FIC-05E` `uso: particular` + Póliza `POL-FIC-0005` vigente, amparo con `condiciones` de uso | actividad reportada: domicilios → `cubierto: incierto` | #8 cobertura no clara |
| Asegurado A5 (`DOC-FIC-0005`, "María Gómez") + Vehículo `FIC-06F` + Póliza `POL-FIC-0006` vigente | **homónimo** de A2 | US3: `buscar_asegurado` por "María Gómez" devuelve varias coincidencias |
| Registro marcado `DOC-FIC-9999` ("flaky") | reservado para simular falla transitoria | #7 falla transitoria del MCP (mecanismo en #2–#4) |

Notas de cobertura:
- #3 y #6 son de comportamiento (no requieren datos propios): usan A1 como asegurado localizable; el bloqueo de #6 lo garantiza el hook `abrir_reclamo`, no los datos.
- Cada caso con fecha usa el siniestro en **2026-10-10**; las vigencias se definen alrededor de esa fecha para que vigente/vencida sea inequívoco.

## Seguimiento de complejidad

> Completar solo si la Verificación de la constitución tiene violaciones que justificar.

Sin violaciones. Diseño mínimo: 3 archivos JSON normalizados + 1 prueba colocada; sin dependencias nuevas más allá de `pytest`.
