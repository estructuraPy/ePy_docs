---
name: book-content-generator
description: Crea capítulos de libros en formato Quarto a partir de un índice, siguiendo estrictas reglas de estilo y compatibilidad con ePy_docs.
---

# Instrucciones

Utiliza este skill para redactar el contenido de los capítulos de un libro técnico basándote en la estructura generada por `book-index-creator`.

## Requisitos de Entrada
Antes de iniciar, verifica que cuentes con:
1. El archivo `index.qmd` ubicado en `results/index_proposal/`.
2. Las referencias procesadas y renombradas por el skill anterior.
3. El skill `epy-qmd-formatter` activo para aplicar los estándares de formato.
**Si falta alguno de estos elementos, debes solicitar al usuario la ubicación o los archivos antes de proceder.**

## Flujo de Trabajo

### 1. Organización de Archivos
- Genera un archivo `.qmd` independiente para cada capítulo definido en el índice.
- Sigue la nomenclatura: `Cap[Número]_[Nombre_Corto].qmd` (ej: `Cap01_Introduccion.qmd`).

### 2. Ingesta y Preservación de Contenido Legado (CRÍTICO)
**Tu prioridad absoluta es mantener y mejorar el contenido existente.**
Antes de escribir cualquier texto nuevo, busca la ruta del archivo legado correspondiente (definida en `index.qmd` o `content_mapping.md`).

1.  **Lectura Obligatoria**: Lee el archivo `.qmd`, `.md` o `.docx` original de `Libro_0_5_0` (o el directorio legado).
2.  **Migración Literal**: Copia el cuerpo técnico principal (ecuaciones, tablas de datos, definiciones, ejemplos resueltos).
3.  **Regla de Volumen ("Content Floor")**: El nuevo capítulo **NUNCA** puede tener menos contenido técnico (texto relevante, no "fluff") que el original. Si el original tenía 10 páginas de derivaciones matemáticas, el nuevo debe tener al menos eso, más las mejoras.
    *   *Incorrecto*: Resumir 5 páginas de teoría en 1 párrafo.
    *   *Correcto*: Mantener las 5 páginas, mejorar el formato, corregir errores y añadir 1 página nueva de referencias actualizadas.

### 3. Redacción y Mejora de Capítulos
Una vez asegurada la base legada, procede a estructurar y enriquecer siguiendo los perfiles:

**Manejo de Imágenes:**
- **Imágenes de Referencia**: Si una referencia tiene una imagen relevante, inclúyela citando la fuente correctamente mediante Quarto (`@fig-id`).
- **Prompts de IA**: Si no hay una imagen disponible o se requiere una nueva, genera un **prompt detallado** para IA.
- **Ubicación del Prompt**: El prompt debe escribirse directamente en el lugar donde debe ir la imagen en el archivo `.qmd`. No lo elimines; servirá de entrada para el skill `image-creator`.

**Requisitos Críticos de Redacción:**
- **Profundidad Técnica**: El contenido debe ser profundo, evitando explicaciones superficiales y centrándose en el rigor de la ingeniería estructural.
- **Ejemplos de Cálculo Obligatorios**: Todo aquello que sea calculable debe incluir ejemplos prácticos detallados.
- **Formato Maestro**: Delega todas las reglas de estética, tablas, figuras y ecuaciones al skill **`epy-qmd-formatter`**. Consulta su `style_guidelines.md` para el cumplimiento estricto.
- **Callouts "Ejemplo"**: Los ejemplos deben encapsularse en bloques de callout de Quarto con el título "Ejemplo" siguiendo la sintaxis de `epy-qmd-formatter`.

- **# [Título del Capítulo]**: Encabezado principal.
- **### Contenido**: Desarrollo profundo y técnico. **Aquí es donde se integra el material legado.** Debe estar respaldado por normativa y organizado lógicamente.
- **### Para estudiantes**: Resumen de conceptos clave y ejemplos paso a paso.
- **### Para profesionales**: Resumen orientado a la aplicación normativa.
- **### Para académicos**: Resumen de fundamentos teóricos.

### 3. Aplicación de Normas de Estilo (ePy_docs Compatibility)
Es obligatorio seguir las reglas de `recursos/style_guidelines.md` para asegurar la compatibilidad con `ePy_docs`:
- **Tablas**: Usa siempre el Div Wrapper `::: {#tbl-id} ... :::` con IDs en `kebab-case`.
- **Referencias Cruzadas**: Usa `@tbl-id`, `@fig-id`, `@eq-id`.
- **Figuras**: Usa atributos extendidos `{#fig-id width="100%"}`.
- **Espaciado**: Líneas en blanco entre bloques.
- **Callouts**: Usa `::: {.callout-note} ... :::`.

## Output Esperado
- Un set de archivos `.qmd` listos para ser procesados por la librería `ePy_docs` y compilados mediante Quarto.
- El contenido debe ser trazable a las referencias originales mediante citas automáticas de Quarto.
