# Plan de implementación: Convención de idioma del código (inglés)

**Rama**: `004-english-code-convention` | **Fecha**: 2026-10-15 | **Especificación**: `specs/004-english-code-convention/spec.md`

**Entrada**: Especificación de funcionalidad de `specs/004-english-code-convention/spec.md`

## Resumen

Refactor mecánico, sin cambio de comportamiento. Aplica la tabla de renombres del spec en un orden
seguro (de los datos hacia arriba) para que cada capa compile contra la anterior, corriendo `pytest`
al final. Actualiza la constitución (Principio VI).

## Contexto técnico

**Lenguaje/Versión**: Python 3.12 (sin dependencias nuevas)

**Almacenamiento**: fixtures JSON (se renombran archivos y claves)

**Pruebas**: `pytest` (mismas aserciones; cambian nombres de campo/acceso)

**Restricciones**: comportamiento idéntico; contrato MCP (nombres/params/descripciones) en español; valores de estado en español

**Escala/Alcance**: ~11 archivos de `src/cordillera/` + la constitución

## Verificación de la constitución

- **Principio VI (Idioma)**: este ticket lo **redefine** — código en inglés, dominio (estados/reglas/contrato MCP) en español. Se actualiza el texto del principio.
- **Comportamiento**: preservado y verificado con `pytest`.

Sin violaciones.

## Estructura del proyecto — orden de ejecución seguro

```text
1. Datos      src/cordillera/data/*.json   → git mv a inglés + claves en inglés
              src/cordillera/data/test_fixtures.py → referencias nuevas
2. Loader     loader.py (load_insured/vehicles/policies + rutas) + test_loader.py
3. Modelos    models.py (clases + campos en inglés)
4. Servicio   service.py (funciones internas, variables, constantes, acceso a claves)
5. Servidor   server.py (los wrappers @mcp.tool llaman a las funciones renombradas;
              los NOMBRES, PARÁMETROS y DESCRIPCIONES de las tools quedan en español)
6. Pruebas    test_service.py, test_cobertura.py, test_errors.py, test_server.py
7. Constitución  .specify/memory/constitution.md (Principio VI)
```

**Decisión de diseño (contrato vs. implementación)**: los wrappers de herramienta en `server.py`
conservan firma española (`buscar_asegurado(criterio, por)`) y llaman **posicionalmente** a las
funciones de `service.py` con firma inglesa (`search_insured(query, by)`). Como la llamada es
posicional, no hay conflicto de nombres. `tipo` (builtin-safe) se mapea a `coverage_type` en el
servicio.

## Mapeo de nombres (referencia)

Ver la tabla de "Entidades clave" en el spec. Además, funciones de servicio:
`buscar_asegurado→search_insured`, `verificar_identidad→verify_identity`,
`consultar_poliza→get_policy`, `verificar_cobertura→check_coverage`.

## Seguimiento de complejidad

Riesgo: un rename incompleto rompe imports/accesos. Mitigación: `pytest` + `ruff` al final;
el orden datos→servidor asegura que cada capa ya ve a la anterior renombrada.
