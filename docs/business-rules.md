# Reglas de negocio y criterios de severidad (Aseguradora Cordillera)

Textuales del enunciado de la prueba. **No se negocian.** La constitución
(`.specify/memory/constitution.md`) define cuáles se hacen cumplir con hooks y cuáles con instrucciones.

## Criterios de severidad

| Severidad | Criterio |
|---|---|
| **Leve** | Daños en piezas exteriores. El vehículo puede seguir circulando. |
| **Moderada** | Daños que impiden circular o que afectan partes mecánicas o eléctricas. |
| **Grave** | Posible pérdida total, incendio o volcamiento. |

## Reglas de negocio

1. Ningún reclamo se abre sin identidad verificada del asegurado y sin confirmar que la póliza estaba
   vigente en la fecha del siniestro.
2. Un siniestro de severidad leve puede abrirse como reclamo de forma automática. Uno de severidad
   moderada o grave requiere un ajustador humano.
3. Si el reporte menciona lesiones a personas, el caso se escala a un ajustador con prioridad alta, sin
   importar la severidad del daño.
4. Si el asegurado pide explícitamente hablar con una persona, se escala de inmediato, sin investigar
   primero.
5. Si la póliza no cubre el caso con claridad, por ejemplo un vehículo particular que estaba haciendo
   domicilios, el agente escala en lugar de improvisar.

## Cómo se hacen cumplir (resumen; detalle en la constitución)

- **Reglas 1, 2 y el bloqueo por lesiones de la 3**: hooks del SDK (`guard_abrir_reclamo`, PreToolUse) —
  garantizadas, no sugeridas. Una regla que dependa solo del prompt es falta grave.
- **Prioridad alta ante lesiones (regla 3)**: hook PreToolUse que fuerza `prioridad=alta` en `escalar_a_ajustador`.
- **Reglas 4 y 5**: instrucciones del system prompt (son juicios); la 5 se apoya además en el subagente `revisor-cobertura`.
