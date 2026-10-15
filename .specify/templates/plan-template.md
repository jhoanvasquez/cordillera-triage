# Plan de implementación: [FUNCIONALIDAD]

**Rama**: `[###-feature-name]` | **Fecha**: [FECHA] | **Especificación**: [enlace]

**Entrada**: Especificación de funcionalidad de `/specs/[###-feature-name]/spec.md`

**Nota**: Este template es completado por el comando `/speckit-plan`; su definición describe el flujo de ejecución.

## Resumen

[Extraer de la especificación de funcionalidad: requisito principal + enfoque técnico derivado de la investigación]

## Contexto técnico

<!--
  ACCIÓN REQUERIDA: Reemplace el contenido de esta sección con los detalles técnicos
  del proyecto. La estructura presentada aquí tiene carácter orientativo para guiar
  el proceso de iteración.
-->

**Lenguaje/Versión**: [p. ej., Python 3.11, Swift 5.9, Rust 1.75 o NEEDS CLARIFICATION]

**Dependencias principales**: [p. ej., FastAPI, UIKit, LLVM o NEEDS CLARIFICATION]

**Almacenamiento**: [si aplica, p. ej., PostgreSQL, CoreData, archivos o N/A]

**Pruebas**: [p. ej., pytest, XCTest, cargo test o NEEDS CLARIFICATION]

**Plataforma destino**: [p. ej., servidor Linux, iOS 15+, WASM o NEEDS CLARIFICATION]

**Tipo de proyecto**: [p. ej., library/cli/web-service/mobile-app/compiler/desktop-app o NEEDS CLARIFICATION]

**Objetivos de rendimiento**: [específicos del dominio, p. ej., 1000 req/s, 10k líneas/seg, 60 fps o NEEDS CLARIFICATION]

**Restricciones**: [específicas del dominio, p. ej., <200ms p95, <100MB memoria, operación sin conexión o NEEDS CLARIFICATION]

**Escala/Alcance**: [específico del dominio, p. ej., 10k usuarios, 1M LOC, 50 pantallas o NEEDS CLARIFICATION]

## Verificación de restricciones

*PUERTA: Debe aprobarse antes de la investigación de la Fase 0. Volver a verificar tras el diseño de la Fase 1.*

[Puertas determinadas según el archivo de restricciones]

## Estructura del proyecto

### Documentación (esta funcionalidad)

```text
specs/[###-feature]/
├── plan.md              # Este archivo (salida del comando /speckit-plan)
├── research.md          # Salida de la Fase 0 (comando /speckit-plan)
├── data-model.md        # Salida de la Fase 1 (comando /speckit-plan)
├── quickstart.md        # Salida de la Fase 1 (comando /speckit-plan)
├── contracts/           # Salida de la Fase 1 (comando /speckit-plan)
└── tasks.md             # Salida de la Fase 2 (comando /speckit-tasks — NO creado por /speckit-plan)
```

### Código fuente (raíz del repositorio)
<!--
  ACCIÓN REQUERIDA: Reemplace el árbol de ejemplo a continuación con la estructura concreta
  para esta funcionalidad. Elimine las opciones que no se utilicen y expanda la estructura
  elegida con rutas reales (p. ej., apps/admin, packages/something). El plan entregado no
  debe incluir etiquetas de Opción.
-->

```text
# [ELIMINAR SI NO SE USA] Opción 1: Proyecto único (PREDETERMINADO)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [ELIMINAR SI NO SE USA] Opción 2: Aplicación web (cuando se detecta "frontend" + "backend")
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [ELIMINAR SI NO SE USA] Opción 3: Móvil + API (cuando se detecta "iOS/Android")
api/
└── [igual que backend arriba]

ios/ or android/
└── [estructura específica de la plataforma: módulos de funcionalidad, flujos de UI, pruebas de plataforma]
```

**Decisión de estructura**: [Documente la estructura seleccionada y referencie los directorios
reales capturados arriba]

## Seguimiento de complejidad

> **Completar SOLO si la Verificación de restricciones tiene violaciones que deban justificarse**

| Violación | Por qué es necesaria | Alternativa más simple descartada porque |
|-----------|----------------------|------------------------------------------|
| [p. ej., 4.° proyecto] | [necesidad actual] | [por qué 3 proyectos son insuficientes] |
| [p. ej., patrón Repository] | [problema específico] | [por qué el acceso directo a BD es insuficiente] |
