---
paths:
  - "src/cordillera/mcp_server/**/*.py"
---

# Convenciones del servidor MCP y sus tools

- **Capa delgada**: `server.py` solo registra las tools de FastMCP; la lógica pura vive en `service.py`
  (testeable sin levantar el servidor).
- **Contrato agent-facing en español**: nombres de las tools y sus descripciones/parámetros en español
  (los fija el enunciado). Las descripciones deben dejar claro cuándo usar `consultar_poliza` vs
  `verificar_cobertura` y qué hacer ante varios vehículos.
- **Salida estructurada**: las tools devuelven modelos Pydantic; FastMCP los expone como
  `structuredContent`. Campos en inglés, valores de dominio en español (`severidad`, `cubierto: si|no|incierto`).
- **Envelope de error estructurado**: los errores llevan `errorCategory ∈ {transient, validation,
  business, permissions}` e `isRetryable` (solo `transient` es reintentable). Una **búsqueda sin
  resultados NO es un error** (`ok=true`, `resultCount=0`).
- **Reglas de negocio**: las hace cumplir el agente (hooks). El servidor mantiene defensa en profundidad
  donde corresponde (p. ej. `abrir_reclamo` revalida identidad + vigencia de póliza), sin reemplazar al hook.
- **Solo datos ficticios** (`FIC`/`DOC-FIC`); ninguna credencial.
