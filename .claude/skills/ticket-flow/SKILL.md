---
name: ticket-flow
description: Coreografía del GitHub Project de un ticket — mover su estado, comentar avance, y abrir/cerrar el PR en los momentos correctos. Mantiene el Project sincronizado con el avance real.
argument-hint: "<issue-number> start|pr|done"
allowed-tools: mcp__github__*
disable-model-invocation: true
---

Mantené el GitHub Project sincronizado con el avance real, sin intervención manual. Argumentos:
`<issue-number>` y una fase: `start`, `pr` o `done`. Usá el servidor MCP de GitHub (issues, projects,
pull requests).

## Fases

- **`start`** (al empezar el ticket):
  - Mover el issue a **In progress** en el Project.
  - Comentar en el issue qué se va a especificar/implementar (insumo de `/speckit.specify`).

- **`pr`** (al abrir el pull request):
  - Abrir el PR con `Closes #<issue-number>` en el cuerpo (referencia y cierra el issue).
  - Mover el issue a **In review** en el Project.
  - Comentar en el issue el enlace al PR y un resumen de lo que se decidió.

- **`done`** (al mergear):
  - Confirmar que el merge cerró el issue; mover el ítem a **Done** en el Project.

## Reglas

- El historial del Project y de los issues es evidencia: cada transición queda registrada.
- Conventional Commits en el PR; **sin atribución a IA**; el PR referencia y cierra su issue.
- Nunca editar estado a mano fuera de este flujo; el estado se arrastra desde el ticket.
- Ninguna credencial en el repo; el token del MCP de GitHub vive en el entorno, no versionado.
