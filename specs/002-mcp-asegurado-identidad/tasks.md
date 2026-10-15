---
description: "Lista de tareas para MCP buscar_asegurado + verificar_identidad + error envelope"
---

# Tareas: MCP — buscar_asegurado + verificar_identidad + error envelope

**Entrada**: Documentos de diseño en `specs/002-mcp-asegurado-identidad/`

**Prerrequisitos**: plan.md (requerido), spec.md (requerido para las historias de usuario)

**Pruebas**: INCLUIDAS (el spec las exige: SC-005 y las pruebas independientes de cada historia).

**Organización**: Tareas agrupadas por historia de usuario.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Historia]**: US1, US2, US3

## Convenciones de rutas

- Código y pruebas colocadas bajo `src/cordillera/mcp_server/`

---

## Fase 1: Configuración

- [x] T001 Agregar dependencias `mcp` (FastMCP) y `pydantic` a `pyproject.toml` y sincronizar el entorno (`uv`); registrar la versión usada.
- [x] T002 Crear la estructura del paquete `src/cordillera/mcp_server/` con `__init__.py`.

---

## Fase 2: Fundacional (prerrequisitos bloqueantes)

**Propósito**: Infra central de la que dependen TODAS las herramientas. Debe completarse antes de las historias.

- [x] T003 Implementar `src/cordillera/mcp_server/loader.py`: carga `asegurados/vehiculos/polizas` desde `../data/` + `test_loader.py` (carga correcta, conteos esperados).
- [x] T004 Implementar `src/cordillera/mcp_server/errors.py`: categorías `transient|validation|business|permissions`, helpers `ok()` / `error()` con la forma nativa de MCP (`isError`/`content`/`structuredContent`). **Verificar contra la versión instalada de FastMCP** el mecanismo para `isError`. + `test_errors.py` (forma del envelope por categoría, `isRetryable`).
- [x] T005 [P] Implementar `src/cordillera/mcp_server/models.py` (Pydantic): `BuscarAseguradoInput`, `AseguradoResumen` (sin `fecha_nacimiento`), `VerificarIdentidadInput`, `VerificacionResultado`.

**Punto de control**: loader, envelope y modelos listos y probados.

---

## Fase 3: Historia de usuario 1 - Localizar al asegurado (Prioridad: P1) 🎯 MVP

**Objetivo**: `buscar_asegurado` por documento/nombre/placa con múltiples coincidencias y vacío sin error.

### Implementación

- [x] T006 [US1] `service.buscar_asegurado()` en `service.py`: match por `documento` (exacto), `nombre` (insensible, múltiple), `placa` (vía vehículo); criterio vacío → `validation`; sin coincidencias → `ok` con `resultCount: 0`; documento `DOC-FIC-9999` → `transient`.
- [x] T007 [US1] Registrar la herramienta `buscar_asegurado` en `server.py` (envuelve `service` + envelope).

### Pruebas

- [x] T008 [US1] `test_service.py`: coincidencia única (documento), múltiple (nombre "María Gómez"), vacía (sin error), por placa `FIC-01A`, criterio vacío (`validation`).

**Punto de control**: `buscar_asegurado` devuelve 0/1/N y maneja vacío como no-error.

---

## Fase 4: Historia de usuario 2 - Verificar la identidad (Prioridad: P1)

**Objetivo**: `verificar_identidad` con segundo dato, sin filtrar el secreto.

### Implementación

- [x] T009 [US2] `service.verificar_identidad()` en `service.py`: busca por `documento`; compara `fecha_nacimiento`; documento inexistente → error; nunca revela la fecha.
- [x] T010 [US2] Registrar la herramienta `verificar_identidad` en `server.py`.

### Pruebas

- [x] T011 [US2] `test_service.py`: dato correcto → `verificado=true`; incorrecto → `verificado=false`; documento inexistente → error de categoría apropiada.

**Punto de control**: la identidad se distingue correctamente; la salida la puede consumir el hook (#7).

---

## Fase 5: Historia de usuario 3 - Errores estructurados y resultados vacíos (Prioridad: P1)

**Objetivo**: Las 4 categorías + `isRetryable`; búsqueda vacía no es error.

### Pruebas

- [x] T012 [US3] `test_service.py` / `test_errors.py`: `transient` (flaky `DOC-FIC-9999`, `isRetryable=true`), `validation` (criterio vacío, `isRetryable=false`), y búsqueda vacía (`isError:false`, `resultCount:0`).

**Punto de control**: cada categoría se provoca y se refleja con el `isRetryable` correcto.

---

## Fase 6: Entrypoint del servidor

- [x] T013 Implementar el entrypoint stdio en `server.py` (función `main` que corre el servidor FastMCP) + prueba ligera `test_server.py` (importa y confirma que las 2 herramientas quedan registradas).

---

## Fase N: Pulido y aspectos transversales

- [x] T014 Ejecutar `pytest` — toda la suite colocada en verde.
- [x] T015 [P] Ejecutar `ruff format` y `ruff check` sobre `src/cordillera/mcp_server/`.

---

## Dependencias y orden de ejecución

- **Configuración (Fase 1)**: primero.
- **Fundacional (Fase 2)**: depende de Configuración; BLOQUEA todas las historias. T005 `[P]` respecto a T003/T004.
- **US1 / US2 (Fases 3–4)**: dependen de la Fundacional; comparten `service.py` y `server.py`, así que van en orden (no en paralelo sobre el mismo archivo).
- **US3 (Fase 5)**: pruebas sobre la lógica ya construida; tras US1/US2.
- **Entrypoint (Fase 6)**: tras registrar ambas herramientas.
- **Pulido (Fase N)**: al final.

## Notas

- `service.py` y `server.py` son archivos compartidos por US1 y US2 → esas tareas NO son `[P]` entre sí.
- El loader, el envelope y los modelos son prerrequisitos reales (Fundacional), no parte de una sola historia.
- Las herramientas de póliza/cobertura y abrir/escalar son de #3 y #4.
