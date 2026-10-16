# Paquete `agent/` — convenciones

Núcleo del agente (Claude Agent SDK). Esta memoria se carga al editar archivos de esta carpeta.

- **Estado desde resultados, nunca texto del modelo** (Principio I): `SessionState` se puebla con
  hooks PostToolUse que leen el **resultado** de las tools (`extract_structured`). Nada se deriva de lo
  que dice el modelo.
- **Reglas por hooks**: `guard_abrir_reclamo` (PreToolUse) niega apertura según `state.motivos_bloqueo()`
  (reglas 1, 2 y bloqueo por lesiones de la 3); `force_priority_on_injuries` fuerza `prioridad=alta`.
  Las reglas 4 y 5 son juicios → system prompt (y subagente `revisor-cobertura` para la 5).
- **Prompts versionados** como artefactos: `system_prompt.md`, `coverage_reviewer_prompt.md`. El loader
  (`prompt.py`) es la fuente única; no armar prompts inline.
- **Ciclo agéntico**: el loop (`consume`) termina por la señal de resultado del SDK (`ResultMessage`),
  nunca por conteo de iteraciones ni matching de palabras clave.
- **Salida estructurada**: el triage se produce con `registrar_triage` (validado), nunca texto libre.
- **Idioma**: identificadores/código en inglés; prompts y valores de dominio en español.
