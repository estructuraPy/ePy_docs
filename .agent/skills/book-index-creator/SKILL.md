---
name: book-index-creator
description: Genera un índice de contenidos en formato Quarto optimizado para ingenieros estructurales, docentes e investigadores, procesando referencias externas.
---

# Instrucciones

Utiliza este skill para crear un índice de contenidos para un libro técnico, integrando componentes de ingeniería estructural, docencia e investigación.

## Perfil del Usuario
El usuario es:
- **Ingeniero Estructural**: Enfoque en normativa (CSCR, LRFD), diseño, análisis y práctica profesional.
- **Docente**: Enfoque en pedagogía, ejemplos paso a paso y claridad conceptual para estudiantes.
- **Investigador**: Enfoque en estado del arte, validación científica y trazabilidad de fuentes.

## Requisitos Transversales
Independientemente del perfil, el índice debe cumplir con:
- **Respaldo Normativo**: Todo contenido técnico debe estar claramente vinculado a la normativa vigente (CSCR, LRFD, ACI, etc.).
- **Estructura Lógica de "Estudio"**: Organización progresiva del contenido para permitir una comprensión acumulativa y facilitar la ubicación del lector en el mapa temático del libro.

## Requisitos de Entrada
Antes de iniciar, verifica que cuentes con:
1. **Información Básica**: Título del libro, autor, y descripción general del nivel o alcance (si no se proporciona, **debes preguntar al usuario**).
2. **Carpeta de Referencias**: Directorio con los documentos a procesar.

## Flujo de Trabajo

### 1. Procesamiento de Referencias
Antes de generar el índice, debes procesar los documentos en la carpeta de referencias proporcionada:
1. **Lectura**: Intenta leer cada archivo (PDF, DOCX, etc.) para extraer autor, año y título.
2. **Documentos Preexistentes**: Si existe una subcarpeta (por ejemplo, `preexisting` o `conservar`) dentro de la carpeta de referencias, lee estos documentos con prioridad. Estos archivos representan contenido que el usuario ya tiene y desea mantener.
3. **Renombrado**: Renombra cada archivo (excepto los preexistentes si ya tienen un formato válido) siguiendo el estándar: `año_autor-título_corto_representativo.extension`.
   - *Ejemplo*: `2024_McCormac-Diseño_Acero_LRFD.pdf`
4. **Clasificación**: Si un archivo no puede ser leído o está corrupto, muévelo a una subcarpeta llamada `unreadable` dentro del mismo directorio.
5. **Inventario**: Crea una lista de las referencias procesadas con un breve resumen de qué contenido aporta cada una al libro. Evita duplicar temas que ya estén cubiertos por documentos preexistentes.


### 2. Integración de Contenido Legado (CRÍTICO)
**El objetivo principal es EVITAR LA PÉRDIDA DE INFORMACIÓN.**
Antes de generar el índice, debes analizar la estructura del libro anterior (por defecto `C:\Users\ingah\pyTEC\Libro_0_5_0` o el directorio indicado).

1.  **Mapeo Obligatorio**: Identifica las carpetas o capítulos existentes en la versión anterior (ej: `PARTE_III_CIMENTACIONES`, `PARTE_IV_CONCRETO`).
2.  **Preservación Estructural**: El nuevo índice DEBE incluir, como mínimo, todos los temas macro que existían en el libro anterior. No se permite eliminar secciones enteras sin una instrucción explícita del usuario.
3.  **Prioridad de Origen**:
    *   **Prioridad 1 (Máxima)**: Contenido del `LegacyContentDir` (`Libro_0_5_0`). Este es el "esqueleto" y la "carne" base del nuevo libro.
    *   **Prioridad 2**: Referencias procesadas (`Libro_CEC_0_0_1\referencias`). Estas sirven para *complementar*, *actualizar* o *profundizar*, pero NO para reemplazar el volumen de contenido técnico ya existente.

### 3. Generación del Índice (Formato Quarto)
Crea la estructura del índice. Por cada capítulo o temática principal, debes incluir obligatoriamente el bloque general de contenido seguido de los resúmenes orientados:

- **### Contenido**: Descripción del contenido base. **DEBES ESPECIFICAR EXPLÍCITAMENTE qué archivo(s) del "Legacy Content" alimentarán este capítulo.** (Ej: "Basado en `Libro_0_5_0\PARTE_IV_CONCRETO\CAPITULO 1...`").
- **### Para estudiantes**: Resumen de lo que este perfil debe estudiar con más detalle dentro del capítulo (conceptos, ejemplos paso a paso).
- **### Para profesionales**: Resumen orientado a la práctica profesional (normativa, optimización, casos reales).
- **### Para académicos**: Resumen orientado a la investigación (teoría avanzada, validación, estado del arte).

**Reglas de Formato:**
- Usa encabezados de nivel 1 (`#`) para Partes y nivel 2 (`##`) para Capítulos.
- Las secciones de perfil y contenido deben ser nivel 3 (`###`).
- No es necesario incluir YAML frontmatter (esto se maneja externamente).
- Asegura la trazabilidad mediante citaciones si se dispone de las referencias procesadas.

### 3. Informe Final
Entrega los resultados en la carpeta `results/index_proposal/` dentro del directorio base del proyecto:
1. El archivo `index.qmd` generado.
2. El archivo `context.md`: Un detalle de consideraciones críticas, hitos de desarrollo y puntos clave para la evolución del libro.
3. El informe de referencias procesadas (qué se tomó de cada una).
4. **Tabla de Mapeo de Contenido**: Un archivo `content_mapping.md` que liste: `Nuevo Capítulo` <-> `Archivo Legado de Origen`.
5. Confirmación de archivos renombrados y movidos a `unreadable`.
