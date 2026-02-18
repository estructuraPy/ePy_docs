---
name: book-generation-pipeline
description: Pipeline maestro que orquestra la creación completa de un libro técnico (Índice -> Contenido -> Imágenes) con confirmación del usuario entre fases.
---

# Instrucciones

Utiliza este skill para ejecutar el flujo completo de creación de un libro técnico. Este pipeline coordina tres sub-skills especializados en secuencia.

## Flujo de Trabajo

### Fase 1: Planificación Técnica
1. **Ejecutar `book-index-creator`**:
   - Procesa las referencias y documentos preexistentes.
   - Genera el índice propuesto en `results/index_proposal/index.qmd`.
   - Crea el archivo `context.md`.
2. **Punto de Control (MANDATORIO)**:
   > [!IMPORTANT]
   > Debes presentar el índice y el contexto al usuario y **solicitar confirmación explícita** para continuar con la redacción del contenido.

### Fase 2: Redacción y Desarrollo de Capítulos
1. **Ejecutar `book-content-generator`**:
   - Solo si la Fase 1 fue aprobada.
   - Genera los archivos `.qmd` de cada capítulo con profundidad técnica y ejemplos de cálculo en LaTeX.
   - Integra contenido preexistente y genera prompts para ilustraciones faltantes.
2. **Punto de Control (MANDATORIO)**:
   > [!IMPORTANT]
   > Debes informar al usuario sobre los capítulos generados y los prompts de imagen creados. **Solicitar confirmación explícita** para proceder a la generación de imágenes.

### Fase 3: Ilustración Técnica Profesional
1. **Ejecutar `image-creator`**:
   - Solo si la Fase 2 fue aprobada.
   - Transforma todos los prompts encontrados en ilustraciones técnicas siguiendo el estilo de ingeniería civil realista.
   - Integra las imágenes en los documentos `.qmd` finales.

## Requisitos de Seguimiento
- Asegurar que no se pierda contenido en las reorganizaciones.
- Mantener la trazabilidad de citas normativas y bibliográficas en todo el pipeline.
- Centralizar todos los resultados en `results/index_proposal/`.

## Output Final
- Un libro técnico completo y estructurado, listo para ser procesado por `ePy_docs` o compilado por Quarto.
