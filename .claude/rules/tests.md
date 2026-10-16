---
paths:
  - "**/test_*.py"
---

# Convenciones de tests

- **Colocados**: los tests viven junto al código que prueban (`test_*.py` en la misma carpeta), con las
  mismas convenciones en todas las carpetas.
- **Capa 1 — determinista (sin LLM, CI-friendly)**: hooks, máquina de estado (`motivos_bloqueo`), tools
  MCP, esquemas Pydantic. Corre con `pytest`. Las garantías duras se prueban acá, independientes del
  modelo (p. ej. "abrir reclamo sin identidad" se prueba llamando al hook PreToolUse directamente).
- **Capa 2 — e2e (modelo real, opt-in)**: `@pytest.mark.e2e` + `skipif(not RUN_E2E)`. Se corre con
  `RUN_E2E=1 pytest -m e2e`; la suite por defecto los saltea. Asertar sobre el **trace de tool-calls y
  el `SessionState`** (comportamiento), nunca sobre el wording del modelo.
- **Datos ficticios**: usar marcadores `FIC`/`DOC-FIC`; nunca algo con forma de documento o placa real.
- **Formateo/lint**: `ruff format` + `ruff check` después de editar.
