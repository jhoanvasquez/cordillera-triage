---
description: "Lista de tareas para Fixtures de datos ficticios"
---

# Tareas: Fixtures de datos ficticios

**Entrada**: Documentos de diseño en `specs/001-fictitious-data-fixtures/`

**Prerrequisitos**: plan.md (requerido), spec.md (requerido para las historias de usuario)

**Pruebas**: INCLUIDAS. El spec las exige explícitamente (SC-002 y las pruebas independientes de cada historia).

**Organización**: Las tareas se agrupan por historia de usuario para permitir implementación y prueba independientes.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Historia]**: A qué historia de usuario pertenece (US1, US2, US3, US4)

## Convenciones de rutas

- Proyecto único: datos y pruebas colocadas bajo `src/cordillera/data/`

---

## Fase 1: Configuración (infraestructura compartida)

**Propósito**: Inicialización mínima del proyecto para que las fixtures y su prueba existan y se ejecuten. Infra compartida creada aquí por ser el primer ticket que la necesita.

- [x] T001 Crear la estructura de paquete: `src/cordillera/__init__.py` y `src/cordillera/data/__init__.py`
- [x] T002 [P] Crear `pyproject.toml` mínimo en la raíz (Python 3.12, `pytest`, `ruff`; configuración de descubrimiento de tests)

---

## Fase 2: Fundacional (prerrequisitos bloqueantes)

**Propósito**: Infraestructura central previa a cualquier historia.

N/A — esta funcionalidad no tiene prerrequisitos bloqueantes más allá de la Configuración.

---

## Fase 3: Historia de usuario 1 - Datos para los 8 casos (Prioridad: P1) 🎯 MVP

**Objetivo**: Un conjunto de datos del que se derivan los 8 escenarios obligatorios.

**Prueba independiente**: Leyendo solo los JSON, cada caso tiene sus registros con los atributos requeridos.

### Implementación de la Historia de usuario 1

- [x] T003 [US1] Crear `src/cordillera/data/asegurados.json` con los 6 asegurados del roster (A1–A5 + registro flaky `DOC-FIC-9999`): `documento` (`DOC-FIC-####`), `nombre`, `fecha_nacimiento`. A2 y A5 comparten nombre "María Gómez".
- [x] T004 [US1] Crear `src/cordillera/data/vehiculos.json` (placas `FIC-01A`…`FIC-06F`), `uso` (A4 = `particular`), y vínculos `asegurado_id` / `poliza_id`.
- [x] T005 [US1] Crear `src/cordillera/data/polizas.json` (`POL-FIC-####`): vigencias alrededor de **2026-10-10** (POL-FIC-0004 vencida hasta 2025-01-01), `deducible`, y `amparos` anidados (grúa `si` en A1; amparo con `condiciones` de uso en A4 → `incierto`).

### Pruebas de la Historia de usuario 1

- [x] T006 [US1] Prueba `test_cobertura_casos` en `src/cordillera/data/test_fixtures.py`: cada uno de los 8 casos tiene registros con los atributos requeridos.
- [x] T007 [US1] Prueba `test_integridad_referencial`: cada `asegurado_id`/`poliza_id`/`vehiculo_id` resuelve a un registro existente.

**Punto de control**: Los datos existen y cubren los 8 casos de forma verificable.

---

## Fase 4: Historia de usuario 2 - Datos inequívocamente ficticios (Prioridad: P1)

**Objetivo**: Ningún valor con forma real en ningún archivo.

**Prueba independiente**: Un barrido por regex no encuentra formas reales.

### Pruebas de la Historia de usuario 2

- [x] T008 [US2] Prueba `test_formatos_ficticios`: todo `documento` ∈ `DOC-FIC-####`, `placa` ∈ `FIC-##X`, `numero` de póliza ∈ `POL-FIC-####`.
- [x] T009 [US2] Prueba `test_sin_datos_reales`: barrido sobre todos los `.json` de `data/` que FALLA si algún valor coincide con una forma real (cédula de 8–10 dígitos o placa de 3 letras + 3 dígitos).

**Punto de control**: El barrido de datos reales da cero coincidencias.

---

## Fase 5: Historia de usuario 3 - Búsqueda y verificación de identidad (Prioridad: P2)

**Objetivo**: Soportar varias coincidencias y un segundo dato de identidad.

### Pruebas de la Historia de usuario 3

- [x] T010 [US3] Prueba `test_coincidencias_multiples`: existen dos asegurados con el nombre "María Gómez" y documentos distintos.
- [x] T011 [US3] Prueba `test_segundo_dato_identidad`: cada asegurado tiene `fecha_nacimiento` no vacío.

**Punto de control**: La búsqueda por nombre puede devolver 1 o varios; cada asegurado es verificable.

---

## Fase 6: Historia de usuario 4 - Falla transitoria (Prioridad: P3)

**Objetivo**: Un registro reservado identificable para simular la falla.

### Pruebas de la Historia de usuario 4

- [x] T012 [US4] Prueba `test_registro_flaky_presente`: existe el asegurado `DOC-FIC-9999` reservado para la simulación de falla transitoria.

**Punto de control**: El registro flaky es identificable en los datos.

---

## Fase N: Pulido y aspectos transversales

- [x] T013 Ejecutar `pytest` — toda la suite colocada en verde.
- [x] T014 [P] Ejecutar `ruff format` y `ruff check` sobre `src/cordillera/data/`.

---

## Dependencias y orden de ejecución

- **Configuración (Fase 1)**: sin dependencias — primero.
- **Fundacional (Fase 2)**: N/A.
- **US1 (Fase 3)**: depende de Configuración. Crea los 3 JSON de los que dependen el resto de las historias.
- **US2 / US3 / US4 (Fases 4–6)**: dependen de los JSON de US1; entre sí pueden ir en paralelo (son pruebas sobre los mismos datos).
- **Pulido (Fase N)**: depende de todas las anteriores.

### Oportunidades de paralelismo

- T001 y T002 marcadas según corresponda; T002 `[P]`.
- Una vez creados los 3 JSON (T003–T005), las pruebas de US2/US3/US4 (T008–T012) pueden escribirse en paralelo.

## Notas

- `[P]` = archivos distintos, sin dependencias.
- `[Historia]` mapea cada tarea a su historia de usuario para trazabilidad.
- El loader de datos y el mecanismo de falla transitoria NO son de este ticket (viven en #2–#4).
- Commit por tarea o grupo lógico; la prueba colocada acompaña a los datos (necesidad #3).
