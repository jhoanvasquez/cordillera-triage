---
description: "Lista de tareas para MCP consultar_poliza + verificar_cobertura"
---

# Tareas: MCP — consultar_poliza + verificar_cobertura

**Entrada**: Documentos de diseño en `specs/003-mcp-poliza-cobertura/`

**Prerrequisitos**: plan.md (requerido), spec.md (requerido para las historias)

**Pruebas**: INCLUIDAS (el spec las exige: SC-004 y las pruebas independientes).

**Organización**: Tareas agrupadas por historia de usuario.

## Formato: `[ID] [P?] [Historia] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Historia]**: US1, US2, US3

## Convenciones de rutas

- Extiende `src/cordillera/mcp_server/`; pruebas nuevas en `test_cobertura.py`

---

## Fase 1: Configuración

N/A — reutiliza las dependencias y la infraestructura (loader, envelope) de la funcionalidad #2.

---

## Fase 2: Fundacional (prerrequisitos bloqueantes)

- [ ] T001 Añadir a `models.py`: `AmparoDetalle`, `PolizaDetalle`, `RespuestaPoliza`, `RespuestaCobertura` (Pydantic).

**Punto de control**: los modelos de salida existen.

---

## Fase 3: Historia de usuario 1 - Consultar la póliza de un vehículo (Prioridad: P1) 🎯 MVP

### Implementación

- [ ] T002 [US1] `service.consultar_poliza(placa)` en `service.py`: resuelve el vehículo por placa; si no existe → `ok=true` con `poliza=None` (vacío, no error); si existe → arma `PolizaDetalle`.
- [ ] T003 [US1] Registrar la herramienta `consultar_poliza` en `server.py` con su descripción distintiva (incluye la guía multi-vehículo).

### Pruebas

- [ ] T004 [US1] `test_cobertura.py`: placa `FIC-01A` → póliza con amparo `grua`; placa inexistente → vacío sin error.

**Punto de control**: `consultar_poliza` devuelve la póliza completa y maneja vacío como no-error.

---

## Fase 4: Historia de usuario 2 - Verificar la cobertura (Prioridad: P1)

### Implementación

- [ ] T005 [US2] `service.verificar_cobertura(numero_poliza, tipo, fecha)` en `service.py`, con el orden: póliza inexistente → error `business`; fecha fuera de vigencia → `no`; sin amparo del tipo → `no`; si no → `amparo.cubierto` + motivo + deducible.
- [ ] T006 [US2] Registrar la herramienta `verificar_cobertura` en `server.py` con su descripción distintiva.

### Pruebas

- [ ] T007 [US2] `test_cobertura.py`: `POL-FIC-0001`+`grua` → `si`; `POL-FIC-0005`+`danos` → `incierto` (motivo domicilios); `POL-FIC-0004` (vencida) → `no`; póliza inexistente → error `business` (NO vacío).

**Punto de control**: `cubierto` distingue si/no/incierto; vencida → no; inexistente → error.

---

## Fase 5: Historia de usuario 3 - Descripciones que evitan confusión (Prioridad: P1)

### Implementación + Pruebas

- [ ] T008 [US3] Redactar las descripciones distintas y no solapadas de ambas herramientas en `server.py` (ya reflejadas en el plan).
- [ ] T009 [US3] `test_cobertura.py`: las descripciones de las dos herramientas son distintas y la de `consultar_poliza` contiene la guía multi-vehículo (p. ej. "pregunta" / "cuál vehículo").

**Punto de control**: las descripciones no se solapan.

---

## Fase N: Pulido y aspectos transversales

- [ ] T010 Ejecutar `pytest` — toda la suite verde.
- [ ] T011 [P] Ejecutar `ruff format` y `ruff check` sobre `src/cordillera/mcp_server/`.

---

## Dependencias y orden de ejecución

- **Fundacional (T001)**: primero; BLOQUEA las historias.
- **US1 / US2 / US3**: dependen de T001; comparten `service.py`/`server.py` → en orden, no en paralelo sobre el mismo archivo.
- **Pulido (Fase N)**: al final.

## Notas

- Las descripciones de las herramientas (US3) se evalúan explícitamente (behavior #3).
- `verificar_cobertura` solo reporta `cubierto`; la regla 5 (`incierto` → escalar) la decide el agente (#8).
- `abrir_reclamo` / `escalar_a_ajustador` son del ticket #4.
