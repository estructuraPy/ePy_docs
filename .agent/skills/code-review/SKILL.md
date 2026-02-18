---
name: code-review
description: Garantiza que el código cumple con los estándares de calidad, diseño y estilo definidos en code_review_guidelines.md.
---

# Instrucciones

Utiliza este skill para auditar y asegurar la calidad del código según los estándares del proyecto.

## 1. Identificar el Alcance de la Revisión
Determina qué tipo de archivo o código se está revisando:
- **Código Python**: Lógica, Clases, Funciones.
- **Configuración**: JSON, Epyson, Epyx.
- **Tests**: Pruebas unitarias o de integración.
- **Documentación**: README.md.

## 2. Consultar los Estándares
Lee y utiliza como referencia obligatoria el archivo `recursos/code_review_guidelines.md` que se encuentra en este directorio.

## 3. Ejecutar la Revisión
Para cada archivo analizado, verifica punto por punto los items de la lista de verificación correspondiente en `code_review_guidelines.md`.

### Estándares Críticos (Resumen de code_review_guidelines.md)
*   **Python**:
    *   Principios SOLID y Responsabilidad Única.
    *   Módulos < 1000 líneas.
    *   Docstrings y Type Hints presentes con todos los parámetros explícitos.
    *   Sin duplicación de código.
    *   Sin valores hardcodeados innecesarios.
    *   Sin código muerto, ni harcoded (todos los valores provienen de archivos de configuración JSON/Epyson), ni legacy, ni backward compability.
    *   Los módulos tendrán nombres representativos, simples y con máximo dos palabras.
*   **JSON/Epyson**:
    *   Estructura lógica, sin duplicados.
    *   Organización alfanumérica y horizontal (donde aplique).
    *   Sin valores hardcodeados innecesarios.
*   **Tests**:
    *   Cobertura de casos borde.
    *   Nombres descriptivos.
    *   Independencia de datos externos (fixtures en el mismo módulo).
    *   Hay un módulo de tests por cada módulo de código.
    *   Hay un método de test por cada método de código.
    *   Hay un archivo markdown por cada módulo de código con los cálculos manuales de validación para cada test. Estos archivos se depositan en otra carpeta llamada tests_validation.


## 4. Generar Reporte
El output de este skill debe ser un reporte detallado (en Markdown) que incluya:

1.  **Archivo Analizado**: Ruta y nombre.
2.  **Estado General**: Aprobado / Requiere Cambios.
3.  **Hallazgos**:
    *   Lista de items que **NO** se cumplen (marcar con `[ ]` y explicar el porqué).
    *   Lista de items que **SÍ** se cumplen (marcar con `[x]`).
4.  **Recomendaciones Específicas**: Sugerencias de refactorización o corrección para cada hallazgo negativo, incluyendo ejemplos de código si es necesario.

## 5. Corrección (Opcional)
Si el usuario lo solicita explícitamente, aplica las correcciones necesarias para cumplir con los estándares, pero prioriza siempre la generación del reporte primero.
