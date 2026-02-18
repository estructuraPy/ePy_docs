---
name: image-creator
description: Genera ilustraciones técnicas de ingeniería civil de alta calidad basadas en prompts de IA, integrándolas en documentos Quarto con su debida citación.
---

# Instrucciones

Utiliza este skill para transformar los prompts de imagen generados en los capítulos del libro en ilustraciones técnicas profesionales.

## Estilo Visual Obligatorio
Todas las imágenes generadas deben seguir el estilo definido en `recursos/image_style.md`:
- **Estética**: Realista con trazos limpios de boceto técnico.
- **Paleta**: Gris concreto, azul acero, beige papel, amarillo seguridad.
- **Detalles**: Etiquetas de texto en español con líneas indicadoras finas.
- **Calidad**: Alta calidad técnica, fondo neutro limpio, pero optimizada para no ser excesivamente pesada.

## Flujo de Trabajo

### 1. Extracción de Prompts
- Lee los archivos `.qmd` generados por `book-content-generator`.
- Identifica los bloques de texto que contienen prompts de IA para imágenes.

### 2. Generación Masiva
- Utiliza la herramienta de generación de imágenes (`generate_image`) para cada prompt encontrado.
- **Importante**: No modifiques el prompt original del usuario, simplemente combínalo con el estilo general de ingeniería civil definido en los recursos.

### 3. Integración en el Documento
- Inserta la imagen generada en la ubicación del prompt en el archivo `.qmd`.
- **Regla de Trazabilidad**: No elimines el prompt original. Coloca la imagen debajo o encima de él.
- **Citación**: Asegúrate de que la imagen esté debidamente citada en el texto (ej: "Como se ilustra en la @fig-detalle-tecnico") y que tenga un pie de figura descriptivo.

### 4. Organización de Resultados
- Guarda las imágenes en una subcarpeta `results/index_proposal/assets/` para mantener el proyecto organizado.
- Actualiza los paths en los archivos `.qmd` para que apunten a este directorio.

## Output Esperado
- Documentos `.qmd` actualizados con imágenes integradas.
- Carpeta de assets con las ilustraciones técnicas en alta resolución.
