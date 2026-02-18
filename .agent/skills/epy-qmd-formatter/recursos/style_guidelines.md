# Reglas de Formato y Estilo para Documentación Técnica

Este documento establece las directrices para mantener la integridad, consistencia y correcta compilación de documentos Quarto/Markdown, especialmente para generar salidas PDF (via LaTeX) y HTML.

## 1. Tablas y Referencias

Para evitar errores de compilación en LaTeX y asegurar que las tablas se comporten como objetos flotantes numerados (Tabla X.Y):

### 1.1 Sintaxis Obligatoria (Div Wrapper)
Siempre encapsula la tabla y su descripción en un bloque Div con el identificador único. **No** uses la sintaxis de leyenda suelta (`: Caption`).

**Correcto:**
```markdown
| Columna 1 | Columna 2 |
| :--- | :--- |
| Dato A | Dato B |

: Título descriptivo de la tabla {#tbl-identificador-unico}
```

> [!IMPORTANT]
> Se prefiere la sintaxis de leyenda nativa de Quarto para mantener una estética limpia y uniforme con los componentes generados por `ePy_docs`.

### 1.2 Identificadores (IDs)
*   **Formato:** Usa `kebab-case` (guiones medios).
    *   **Permitido:** `{#tbl-cronograma-final}`
    *   **Prohibido:** `{#tbl_cronograma_final}` (Los guiones bajos rompen las referencias cruzadas en LaTeX).
*   **Prefijos:** Respeta los prefijos estándar de Quarto para que funcionen las referencias cruzadas automáticas:
    *   `tbl-` para tablas.
    *   `fig-` para figuras.
    *   `eq-` para ecuaciones.
    *   `sec-` para secciones.

### 1.3 Referencias en Texto
Usa siempre la referencia cruzada de Quarto, no texto duro (salvo excepciones extremas).
*   **Correcto:** "...como se ve en la @tbl-cronograma-final."

## 2. Figuras

Usa la sintaxis estándar de Markdown con atributos extendidos:
```markdown
![Descripción accesible de la figura](ruta/imagen.png){#fig-identificador width="100%"}
```

## 3. Bloques y Estructura

### 3.1 Espaciado
Deja siempre una **línea en blanco** antes y después de cualquier bloque (tablas, figuras, callouts, divs, listas) para asegurar que el parser de Markdown los identifique correctamente y no los mezcle con el párrafo anterior.

### 3.2 Callouts (Alertas)
Usa los bloques nativos de Quarto para notas, advertencias y tips. Evita usar citas (`>`) para este propósito.

```markdown
::: {.callout-note title="Nota Importante"}
Contenido de la nota.
:::
```

### 3.3 Código
Evita dejar bloques de código (` ``` `) "huerfanos" o mal cerrados al final de los archivos, ya que pueden romper el renderizado de los capítulos siguientes en documentos multi-archivo.

### 3.4 Callouts de Ejemplos (Cálculo)
Para ejemplos matemáticos y de cálculo, usa el bloque `callout-tip` con el título "Ejemplo". Asegura que todo el desarrollo matemático use LaTeX.

```markdown
::: {.callout-tip title="Ejemplo"}
**Problema:** Calcular la resistencia nominal a flexión...

::: {#tbl-ejemplo-calculo latex-table-env="table"}
| Variable | Valor |
| :--- | :--- |
| $f_y$ | 4200 kg/cm² |

Título del ejemplo de cálculo
:::

$$
M_n = A_s f_y (d - a/2)
$$
:::
```

> [!TIP]
> Mantener las tablas dentro de su Div wrapper incluso dentro de callouts asegura que la apariencia generada por `ePy_docs` sea idéntica en todo el documento.

## 4. Encabezados
*   Usa encabezados de nivel 1 (`# Título`) solo para el título del capítulo.
*   Mantén una jerarquía lógica (`##`, `###`).
*   Agrega `{.unnumbered}` si el capítulo no debe llevar numeración (como Introducción o Referencias).
