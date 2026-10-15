---

description: "Plantilla de lista de tareas para la implementación de funcionalidades"
---

# Tareas: [NOMBRE DE LA FUNCIONALIDAD]

**Entrada**: Documentos de diseño de `/specs/[###-feature-name]/`

**Requisitos previos**: plan.md (obligatorio), spec.md (obligatorio para historias de usuario), research.md, data-model.md, contracts/

**Pruebas**: Los ejemplos a continuación incluyen tareas de prueba. Las pruebas son OPCIONALES — inclúyalas solo si se solicitan explícitamente en la especificación de la funcionalidad.

**Organización**: Las tareas se agrupan por historia de usuario para permitir la implementación y verificación independiente de cada historia.

## Formato: `[ID] [P?] [Story] Descripción`

- **[P]**: Puede ejecutarse en paralelo (archivos distintos, sin dependencias)
- **[Story]**: A qué historia de usuario pertenece esta tarea (p. ej., US1, US2, US3)
- Incluir rutas de archivo exactas en las descripciones

## Convenciones de rutas

- **Proyecto único**: `src/`, `tests/` en la raíz del repositorio
- **Aplicación web**: `backend/src/`, `frontend/src/`
- **Móvil**: `api/src/`, `ios/src/` o `android/src/`
- Las rutas mostradas a continuación asumen proyecto único — ajustar según la estructura en plan.md

<!--
  ============================================================================
  IMPORTANTE: Las tareas a continuación son TAREAS DE EJEMPLO solo con fines ilustrativos.

  El comando /speckit-tasks DEBE reemplazarlas con tareas reales basadas en:
  - Historias de usuario de spec.md (con sus prioridades P1, P2, P3...)
  - Requisitos de funcionalidad de plan.md
  - Entidades de data-model.md
  - Endpoints de contracts/

  Las tareas DEBEN organizarse por historia de usuario para que cada historia pueda:
  - Implementarse de forma independiente
  - Probarse de forma independiente
  - Entregarse como un incremento de MVP

  NO conserve estas tareas de ejemplo en el archivo tasks.md generado.
  ============================================================================
-->

## Fase 1: Configuración (Infraestructura compartida)

**Propósito**: Inicialización del proyecto y estructura básica

- [ ] T001 Crear la estructura del proyecto según el plan de implementación
- [ ] T002 Inicializar el proyecto [language] con las dependencias de [framework]
- [ ] T003 [P] Configurar herramientas de linting y formateo

---

## Fase 2: Fundacional (Requisitos previos bloqueantes)

**Propósito**: Infraestructura central que DEBE estar completa antes de que CUALQUIER historia de usuario pueda implementarse

**⚠️ CRÍTICO**: Ninguna historia de usuario puede iniciarse hasta que esta fase esté completa

Ejemplos de tareas fundacionales (ajustar según el proyecto):

- [ ] T004 Configurar el esquema de base de datos y el framework de migraciones
- [ ] T005 [P] Implementar el framework de autenticación/autorización
- [ ] T006 [P] Configurar el enrutamiento de API y la estructura de middleware
- [ ] T007 Crear los modelos/entidades base de los que dependen todas las historias
- [ ] T008 Configurar la gestión de errores y la infraestructura de logging
- [ ] T009 Configurar la gestión de variables de entorno

**Punto de control**: Fundación lista — la implementación de historias de usuario puede comenzar en paralelo

---

## Fase 3: Historia de usuario 1 - [Título] (Prioridad: P1) 🎯 MVP

**Objetivo**: [Descripción breve de lo que entrega esta historia]

**Prueba independiente**: [Cómo verificar que esta historia funciona por sí sola]

### Pruebas para la Historia de usuario 1 (OPCIONAL — solo si se solicitan pruebas) ⚠️

> **NOTA: Escribir estas pruebas PRIMERO y asegurarse de que FALLEN antes de la implementación**

- [ ] T010 [P] [US1] Prueba de contrato para [endpoint] en tests/contract/test_[name].py
- [ ] T011 [P] [US1] Prueba de integración para [recorrido de usuario] en tests/integration/test_[name].py

### Implementación para la Historia de usuario 1

- [ ] T012 [P] [US1] Crear el modelo [Entity1] en src/models/[entity1].py
- [ ] T013 [P] [US1] Crear el modelo [Entity2] en src/models/[entity2].py
- [ ] T014 [US1] Implementar [Service] en src/services/[service].py (depende de T012, T013)
- [ ] T015 [US1] Implementar [endpoint/feature] en src/[location]/[file].py
- [ ] T016 [US1] Agregar validación y gestión de errores
- [ ] T017 [US1] Agregar logging para las operaciones de la Historia de usuario 1

**Punto de control**: En este punto, la Historia de usuario 1 debe ser completamente funcional y verificable de forma independiente

---

## Fase 4: Historia de usuario 2 - [Título] (Prioridad: P2)

**Objetivo**: [Descripción breve de lo que entrega esta historia]

**Prueba independiente**: [Cómo verificar que esta historia funciona por sí sola]

### Pruebas para la Historia de usuario 2 (OPCIONAL — solo si se solicitan pruebas) ⚠️

- [ ] T018 [P] [US2] Prueba de contrato para [endpoint] en tests/contract/test_[name].py
- [ ] T019 [P] [US2] Prueba de integración para [recorrido de usuario] en tests/integration/test_[name].py

### Implementación para la Historia de usuario 2

- [ ] T020 [P] [US2] Crear el modelo [Entity] en src/models/[entity].py
- [ ] T021 [US2] Implementar [Service] en src/services/[service].py
- [ ] T022 [US2] Implementar [endpoint/feature] en src/[location]/[file].py
- [ ] T023 [US2] Integrar con los componentes de la Historia de usuario 1 (si es necesario)

**Punto de control**: En este punto, las Historias de usuario 1 Y 2 deben funcionar de forma independiente

---

## Fase 5: Historia de usuario 3 - [Título] (Prioridad: P3)

**Objetivo**: [Descripción breve de lo que entrega esta historia]

**Prueba independiente**: [Cómo verificar que esta historia funciona por sí sola]

### Pruebas para la Historia de usuario 3 (OPCIONAL — solo si se solicitan pruebas) ⚠️

- [ ] T024 [P] [US3] Prueba de contrato para [endpoint] en tests/contract/test_[name].py
- [ ] T025 [P] [US3] Prueba de integración para [recorrido de usuario] en tests/integration/test_[name].py

### Implementación para la Historia de usuario 3

- [ ] T026 [P] [US3] Crear el modelo [Entity] en src/models/[entity].py
- [ ] T027 [US3] Implementar [Service] en src/services/[service].py
- [ ] T028 [US3] Implementar [endpoint/feature] en src/[location]/[file].py

**Punto de control**: Todas las historias de usuario deben ser ahora funcionales de forma independiente

---

[Agregar más fases de historias de usuario según sea necesario, siguiendo el mismo patrón]

---

## Fase N: Refinamiento y aspectos transversales

**Propósito**: Mejoras que afectan a múltiples historias de usuario

- [ ] TXXX [P] Actualizaciones de documentación en docs/
- [ ] TXXX Limpieza de código y refactorización
- [ ] TXXX Optimización de rendimiento en todas las historias
- [ ] TXXX [P] Pruebas unitarias adicionales (si se solicitan) en tests/unit/
- [ ] TXXX Refuerzo de seguridad
- [ ] TXXX Ejecutar la validación de quickstart.md

---

## Dependencias y orden de ejecución

### Dependencias entre fases

- **Configuración (Fase 1)**: Sin dependencias — puede iniciarse de inmediato
- **Fundacional (Fase 2)**: Depende de la finalización de la Configuración — BLOQUEA todas las historias de usuario
- **Historias de usuario (Fase 3+)**: Todas dependen de la finalización de la fase Fundacional
  - Las historias de usuario pueden entonces avanzar en paralelo (si hay capacidad de equipo)
  - O de forma secuencial en orden de prioridad (P1 → P2 → P3)
- **Refinamiento (Fase final)**: Depende de que todas las historias de usuario deseadas estén completas

### Dependencias entre historias de usuario

- **Historia de usuario 1 (P1)**: Puede iniciarse tras la fase Fundacional (Fase 2) — Sin dependencias de otras historias
- **Historia de usuario 2 (P2)**: Puede iniciarse tras la fase Fundacional (Fase 2) — Puede integrarse con US1 pero debe ser verificable de forma independiente
- **Historia de usuario 3 (P3)**: Puede iniciarse tras la fase Fundacional (Fase 2) — Puede integrarse con US1/US2 pero debe ser verificable de forma independiente

### Dentro de cada historia de usuario

- Las pruebas (si se incluyen) DEBEN escribirse y FALLAR antes de la implementación
- Modelos antes que servicios
- Servicios antes que endpoints
- Implementación central antes que integración
- Historia completa antes de pasar a la siguiente prioridad

### Oportunidades de paralelismo

- Todas las tareas de Configuración marcadas [P] pueden ejecutarse en paralelo
- Todas las tareas Fundacionales marcadas [P] pueden ejecutarse en paralelo (dentro de la Fase 2)
- Una vez completada la fase Fundacional, todas las historias de usuario pueden iniciarse en paralelo (si la capacidad del equipo lo permite)
- Todas las pruebas de una historia de usuario marcadas [P] pueden ejecutarse en paralelo
- Los modelos dentro de una historia marcados [P] pueden ejecutarse en paralelo
- Distintas historias de usuario pueden trabajarse en paralelo por diferentes miembros del equipo

---

## Ejemplo de paralelismo: Historia de usuario 1

```bash
# Lanzar todas las pruebas de la Historia de usuario 1 juntas (si se solicitan pruebas):
Task: "Contract test for [endpoint] in tests/contract/test_[name].py"
Task: "Integration test for [user journey] in tests/integration/test_[name].py"

# Lanzar todos los modelos de la Historia de usuario 1 juntos:
Task: "Create [Entity1] model in src/models/[entity1].py"
Task: "Create [Entity2] model in src/models/[entity2].py"
```

---

## Estrategia de implementación

### MVP primero (solo Historia de usuario 1)

1. Completar la Fase 1: Configuración
2. Completar la Fase 2: Fundacional (CRÍTICO — bloquea todas las historias)
3. Completar la Fase 3: Historia de usuario 1
4. **DETENER Y VALIDAR**: Probar la Historia de usuario 1 de forma independiente
5. Desplegar/demostrar si está lista

### Entrega incremental

1. Completar Configuración + Fundacional → Fundación lista
2. Agregar Historia de usuario 1 → Probar de forma independiente → Desplegar/Demostrar (¡MVP!)
3. Agregar Historia de usuario 2 → Probar de forma independiente → Desplegar/Demostrar
4. Agregar Historia de usuario 3 → Probar de forma independiente → Desplegar/Demostrar
5. Cada historia agrega valor sin romper las historias anteriores

### Estrategia de equipo en paralelo

Con varios desarrolladores:

1. El equipo completa Configuración + Fundacional en conjunto
2. Una vez finalizada la fase Fundacional:
   - Desarrollador A: Historia de usuario 1
   - Desarrollador B: Historia de usuario 2
   - Desarrollador C: Historia de usuario 3
3. Las historias se completan e integran de forma independiente

---

## Notas

- Las tareas [P] = archivos distintos, sin dependencias
- La etiqueta [Story] vincula la tarea a una historia de usuario específica para trazabilidad
- Cada historia de usuario debe ser completable y verificable de forma independiente
- Verificar que las pruebas fallen antes de implementar
- Hacer commit tras cada tarea o grupo lógico
- Detenerse en cualquier punto de control para validar la historia de forma independiente
- Evitar: tareas vagas, conflictos en el mismo archivo, dependencias entre historias que rompan la independencia
