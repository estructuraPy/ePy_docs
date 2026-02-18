---
name: epy-qmd-formatter
description: Centraliza y aplica los estándares de formato, estética y estructura para documentos Quarto (.qmd) y Markdown (.md) en todo el ecosistema ePy Suite.
---

# Instrucciones

Utiliza este skill como el motor de formato maestro para cualquier documento técnico generado o auditado. Asegura que la estética sea "premium" y cumpla con las reglas de compilación de Quarto.

## Reglas de Formato Maestras
Para una descripción detallada, consulta `recursos/style_guidelines.md`.

### 1. Tablas y Figuras
- **Tablas Nativas**: Markdown nativo (`|...|`) seguido de leyenda (`: Título {#tbl-id}`). NO usar envoltorios Div (`:::`).
- **Tablas como Imagen** (generadas por `ePy_docs`): La imagen va dentro de una celda de tabla Markdown (`| ![](...){width=100%} |`), seguida del separador `|---|` y la leyenda (`: Título {#tbl-id}`). Esto garantiza que Quarto las numere como Tablas, no como Figuras.
- **Títulos Mandatorios**: Todas las tablas deben tener un título inferior con su respectivo ID.
- **IDs**: Siempre en kebab-case y con el prefijo `tbl-`. No usar guiones bajos.

### 2. Ecuaciones y Cálculos
- **LaTeX**: Uso mandatorio para todas las fórmulas.
- **Bloques**: Separación clara con líneas en blanco.

### 3. Callouts y Estructura
- **Callouts Profesionales**: Usa `callout-note` para avisos y `callout-tip` para ejemplos de cálculo.
- **Ejemplos**: Título mandatorio "Ejemplo" para bloques de cálculo.
- **Espaciado**: Línea en blanco antes y después de cada bloque de código, tabla o figura.

### 4. Referencias Cruzadas
- Usa `@tbl-id`, `@fig-id` y `@eq-id` para citar elementos en el texto.

### 5. Tono Pedagógico y Precisión Técnica
- **Sin Memorización**: PROHIBIDO usar verbos como "memorizar". Utiliza "comprender", "identificar", "aplicar" o "conocer".
- **Conceptos Estructurales**: Asegura que conceptos como el principio "Columna Fuerte - Viga Débil" se describan con precisión (ej: las rótulas plásticas deben ocurrir en las vigas, nunca en las columnas o nudos).
- **Consistencia**: Mantén el nivel de detalle adecuado para los tres perfiles (Estudiantes, Profesionales, Académicos).

## Integración
Este skill debe ser llamado por:
- `book-content-generator`: Durante la redacción de capítulos.
- `epy-validation-audit`: Durante la auditoría de formato de cuadernos de validación.

## Output Esperado
Documentos con formato impecable, listos para ser renderizados a PDF o HTML sin errores de parsing.
