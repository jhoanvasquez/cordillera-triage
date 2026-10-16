# Cordillera Triage — convenciones de equipo

Agente de triage de siniestros de auto (Claude Agent SDK + servidor MCP). Esto es memoria **de
equipo** (versionada). Las preferencias personales van en `CLAUDE.local.md` (gitignorado).

## Convenciones

- **Spec-Driven Development**: no se escribe código de producción en `src/**` sin su `spec.md`,
  `plan.md` y `tasks.md` en `specs/<rama>/`.
- **Idioma**: código, identificadores, campos y claves JSON en **inglés**; dominio y contrato
  (nombres/descripciones de tools, valores de estado, prompts, documentación) en **español**.
- **Reglas de negocio garantizadas por hooks, no por el prompt** (ver abajo). Una regla que dependa
  solo del prompt es falta grave.
- **Tests colocados** junto al código (`test_*.py` en la misma carpeta). Capa 1 determinista (sin LLM);
  capa 2 e2e opt-in (`RUN_E2E=1 pytest -m e2e`). Formateo: `ruff`.
- **Solo datos ficticios** (marcadores `FIC`/`DOC-FIC`); ninguna credencial en el repo.
- **Commits**: Conventional Commits, sin atribución a IA. Cada PR referencia y cierra su issue.

## Reglas de negocio y severidad

@docs/business-rules.md

## Principios del proyecto

La constitución es el dueño de los principios: `.specify/memory/constitution.md`.
