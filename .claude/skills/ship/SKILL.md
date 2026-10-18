---
name: ship
description: Orquesta el flujo pre-PR de un ticket — corre la revisión independiente de código y la de cumplimiento, y solo entonces abre el PR y sincroniza el ticket en GitHub.
argument-hint: "<issue-number>"
disable-model-invocation: true
---

Flujo pre-PR de un ticket. Argumento: `<issue-number>`. Ejecutá en orden y **no abras el PR si una
revisión falla**.

## Secuencia

1. **Revisión independiente** (contexto fresco, distinto de la sesión que escribió el código):
   - Lanzá el subagente `code-reviewer` sobre el diff del cambio.
   - Lanzá el subagente `compliance-reviewer` (reglas de negocio 1–5 vs la constitución).
   - Si alguno reporta **CRITICAL** o **NO CUMPLE**: arreglá eso primero y volvé a correr. No sigas al PR.

2. **Abrir el PR** (recién cuando ambas revisiones pasan):
   - Crear el PR con `Closes #<issue-number>` en el cuerpo (referencia y cierra el issue).
   - Resumen: qué se especificó, qué se decidió, qué quedó pendiente.

3. **Sincronizar el ticket** (reusá el skill `ticket-flow <issue-number> pr`):
   - Mover el issue a **In review** en el Project.
   - Comentar el avance en el issue con el enlace al PR.

## Reglas

- Conventional Commits; **sin atribución a IA**; el PR referencia y cierra su issue (Principio V).
- La revisión pre-PR es independiente de la sesión que generó el código (necesidad #8).
- Ninguna credencial en el repo; el token de GitHub vive en el entorno.
