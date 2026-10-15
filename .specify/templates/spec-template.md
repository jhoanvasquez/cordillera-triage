# Especificación de funcionalidad: [NOMBRE DE LA FUNCIONALIDAD]

**Rama de funcionalidad**: `[###-feature-name]`

**Creado**: [FECHA]

**Estado**: Borrador

**Entrada**: Descripción del usuario: "$ARGUMENTS"

## Escenarios de usuario y pruebas *(obligatorio)*

<!--
  IMPORTANTE: Las historias de usuario deben estar PRIORIZADAS como recorridos de usuario ordenados por importancia.
  Cada historia/recorrido de usuario debe ser VERIFICABLE DE FORMA INDEPENDIENTE — es decir, si se implementa
  solamente UNA de ellas, debe existir un MVP (Producto Mínimo Viable) funcional que entregue valor.

  Asigne prioridades (P1, P2, P3, etc.) a cada historia, donde P1 es la más crítica.
  Piense en cada historia como una porción autónoma de funcionalidad que puede:
  - Desarrollarse de forma independiente
  - Probarse de forma independiente
  - Desplegarse de forma independiente
  - Demostrarse a los usuarios de forma independiente
-->

### Historia de usuario 1 - [Título breve] (Prioridad: P1)

[Describe este recorrido de usuario en lenguaje claro]

**Por qué esta prioridad**: [Explica el valor y la razón de este nivel de prioridad]

**Prueba independiente**: [Describe cómo puede probarse de forma independiente — p. ej., "Puede verificarse completamente mediante [acción específica] y entrega [valor específico]"]

**Escenarios de aceptación**:

1. **Dado** [estado inicial], **Cuando** [acción], **Entonces** [resultado esperado]
2. **Dado** [estado inicial], **Cuando** [acción], **Entonces** [resultado esperado]

---

### Historia de usuario 2 - [Título breve] (Prioridad: P2)

[Describe este recorrido de usuario en lenguaje claro]

**Por qué esta prioridad**: [Explica el valor y la razón de este nivel de prioridad]

**Prueba independiente**: [Describe cómo puede probarse de forma independiente]

**Escenarios de aceptación**:

1. **Dado** [estado inicial], **Cuando** [acción], **Entonces** [resultado esperado]

---

### Historia de usuario 3 - [Título breve] (Prioridad: P3)

[Describe este recorrido de usuario en lenguaje claro]

**Por qué esta prioridad**: [Explica el valor y la razón de este nivel de prioridad]

**Prueba independiente**: [Describe cómo puede probarse de forma independiente]

**Escenarios de aceptación**:

1. **Dado** [estado inicial], **Cuando** [acción], **Entonces** [resultado esperado]

---

[Agregar más historias de usuario según sea necesario, cada una con una prioridad asignada]

### Casos límite

<!--
  ACCIÓN REQUERIDA: El contenido de esta sección representa valores de ejemplo.
  Complételo con los casos límite correctos.
-->

- ¿Qué ocurre cuando [condición límite]?
- ¿Cómo gestiona el sistema [escenario de error]?

## Requisitos *(obligatorio)*

<!--
  ACCIÓN REQUERIDA: El contenido de esta sección representa valores de ejemplo.
  Complételo con los requisitos funcionales correctos.
-->

### Requisitos funcionales

- **FR-001**: El sistema DEBE [capacidad específica, p. ej., "permitir a los usuarios crear cuentas"]
- **FR-002**: El sistema DEBE [capacidad específica, p. ej., "validar direcciones de correo electrónico"]
- **FR-003**: Los usuarios DEBEN poder [interacción clave, p. ej., "restablecer su contraseña"]
- **FR-004**: El sistema DEBE [requisito de datos, p. ej., "persistir las preferencias del usuario"]
- **FR-005**: El sistema DEBE [comportamiento, p. ej., "registrar todos los eventos de seguridad"]

*Ejemplo de cómo marcar requisitos poco claros:*

- **FR-006**: El sistema DEBE autenticar a los usuarios mediante [NEEDS CLARIFICATION: método de autenticación no especificado — correo/contraseña, SSO, OAuth?]
- **FR-007**: El sistema DEBE conservar los datos del usuario durante [NEEDS CLARIFICATION: período de retención no especificado]

### Entidades clave *(incluir si la funcionalidad involucra datos)*

- **[Entidad 1]**: [Qué representa, atributos clave sin detalles de implementación]
- **[Entidad 2]**: [Qué representa, relaciones con otras entidades]

## Criterios de éxito *(obligatorio)*

<!--
  ACCIÓN REQUERIDA: Defina criterios de éxito medibles.
  Deben ser independientes de la tecnología y cuantificables.
-->

### Resultados medibles

- **SC-001**: [Métrica cuantificable, p. ej., "Los usuarios pueden completar la creación de cuenta en menos de 2 minutos"]
- **SC-002**: [Métrica cuantificable, p. ej., "El sistema soporta 1000 usuarios concurrentes sin degradación"]
- **SC-003**: [Métrica de satisfacción del usuario, p. ej., "El 90% de los usuarios completa la tarea principal en el primer intento"]
- **SC-004**: [Métrica de negocio, p. ej., "Reducir los tickets de soporte relacionados con [X] en un 50%"]

## Supuestos

<!--
  ACCIÓN REQUERIDA: El contenido de esta sección representa valores de ejemplo.
  Complételo con los supuestos correctos basados en valores predeterminados razonables
  elegidos cuando la descripción de la funcionalidad no especificó ciertos detalles.
-->

- [Supuesto sobre los usuarios objetivo, p. ej., "Los usuarios tienen conectividad a internet estable"]
- [Supuesto sobre los límites del alcance, p. ej., "El soporte móvil está fuera del alcance para v1"]
- [Supuesto sobre datos/entorno, p. ej., "Se reutilizará el sistema de autenticación existente"]
- [Dependencia de un sistema/servicio existente, p. ej., "Requiere acceso a la API de perfil de usuario existente"]
