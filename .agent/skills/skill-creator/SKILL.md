---
name: skill-creator
description: Framework estandarizado para crear y estructurar nuevas skills en Antigravity.
---

# Instrucciones

Utiliza este skill para crear nuevas skills para Antigravity. Sigue rigurosamente el siguiente flujo de trabajo y reglas de creación.

## 1. Entender el Objetivo
**Antes de crear nada, asegúrate de tener la siguiente información:**
- **Identidad**: ¿Qué problema resuelve el skill? ¿Cuál es su objetivo principal?
- **Nombre**: Debe ser en `kebab-case`, corto (máx 40 caracteres). Ej: `planificar-video`, `refactorizar-python`.
- **Descripción**: En tercera persona, explicando QUÉ hace y CUÁNDO se usa.
- **Instrucciones**: Lógica detallada, pasos a seguir, o el prompt complejo que se quiere convertir en procedimiento.
- **Archivos Adicionales**: Guías, templates, ejemplos, PDFs, imágenes, etc.

## 2. Definir el Nivel de Libertad
Determina el tipo de skill según su naturaleza:
- **Alto (Heurísticas)**: Para brainstorming o tareas creativas.
- **Medio (Plantillas)**: Para la creación de documentos y textos estructurados.
- **Bajo (Pasos Exactos)**: Para scripts, migraciones y operaciones delicadas.

## 3. Estructurar el Output
Genera la estructura de carpetas y archivos obligatoria:

`.agent/skills/<nombre-del-skill>/`

### 3.1. Archivo Principal (Obligatorio)
Crea el archivo `.agent/skills/<nombre-del-skill>/SKILL.md` con el siguiente formato YAML frontmatter y contenido:

```markdown
---
name: <nombre-del-skill>
description: <descripción>
---

# Instrucciones

<instrucciones detalladas y reglas del skill>
```

**Reglas para el contenido del SKILL.md:**
- **Sin Relleno**: Es un manual de ejecución. Usa reglas cortas y directas.
- **Separación de Responsabilidades**: Incluye solo la lógica y los pasos en `SKILL.md`. Mueve estilos, datos grandes y ejemplos a la carpeta `recursos/`.
- **Inputs Explícitos**: Si un dato es crítico, el skill debe pedirlo explícitamente.
- **Output Estandarizado**: Define qué formato debe devolver el skill (Tabla, Markdown, JSON, etc.).

### 3.2. Carpetas de Soporte (Opcionales pero recomendadas)
Crea las siguientes subcarpetas si el skill lo requiere:

- **`recursos/`**:
  - Almacena aquí guías, templates, JSONs de configuración, y cualquier archivo adicional (PDF, DOCX, MD, imágenes, etc.) que el skill necesite consultar o usar.
- **`scripts/`**:
  - Almacena aquí utilidades técnicas, scripts de Python (`.py`), JavaScript (`.js`), etc., que el skill deba ejecutar.
- **`ejemplos/`**:
  - Almacena aquí referencias del output ideal o casos de uso.

## 4. Revisión y Confirmación
1.  Verifica que el nombre del directorio y del archivo `SKILL.md` coincidan y sean válidos.
2.  Confirma al usuario que el skill ha sido creado exitosamente indicando la ruta: `.agent/skills/<nombre-del-skill>/SKILL.md`.
