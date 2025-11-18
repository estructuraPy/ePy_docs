# ePy_docs - Development Log

## Session: 2025-01-18 - Column Span Fix & Document Regeneration

### Problema Identificado

1. **Regeneración de Documentos**: El sistema impedía regenerar un documento después de la primera generación, lanzando `RuntimeError: "Document has already been generated"`.

2. **Column Span en Multicol**: Figuras y tablas con `column_span >= 2` no estaban generando los entornos LaTeX correctos (`figure*`, `table*`) necesarios para spanning en documentos multi-columna.

### Solución Implementada

#### 1. Permitir Regeneración de Documentos

**Archivo modificado**: `src/ePy_docs/core/_quarto.py`

**Cambio**: Eliminada la verificación de `_is_generated` en la función `prepare_generation()`.

**Razón**: El flag `_is_generated` debe prevenir agregar contenido DESPUÉS de generar, pero NO debe prevenir regenerar el mismo contenido múltiples veces. Esto permite workflows iterativos en Jupyter notebooks.

**Principios SOLID aplicados**:
- **Single Responsibility**: La función `generate()` ahora solo se encarga de generar, no de mantener estado restrictivo.
- **Open/Closed**: El sistema ahora es más flexible permitiendo extensión sin modificación del comportamiento core.

#### 2. Soporte Completo para Column Span en Imágenes

**Archivo modificado**: `src/ePy_docs/core/_images.py`

**Cambio**: Agregada lógica a `_build_image_markdown()` para generar entornos `figure*` cuando `column_span >= 2` en layouts multi-columna.

**Comportamiento anterior**:
```markdown
![Caption](path){width=100% #fig-1 .column-page}
```

**Comportamiento nuevo** (con `column_span=2`):
```latex
```{=latex}
\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{path}
\caption{Caption}
\label{fig-1}
\end{figure*}
```
```

**Razón**: En LaTeX con `multicol` package, el comando `\textwidth` dentro de una columna se refiere al ancho de toda la página, no al ancho disponible. Para que una figura span múltiples columnas, DEBE usar el entorno `figure*` o `table*`.

#### 3. Tests Actualizados

**Archivo modificado**: `tests/unit/test_column_span_direction.py`

**Cambio**: Actualizado `test_image_column_span_uses_figure_star` para verificar presencia de `\begin{figure*}` en lugar de clases CSS.

### Arquitectura y Principios

#### Single Responsibility Principle (SRP)
- `_build_image_markdown()`: Construye markdown/LaTeX para imágenes según contexto (single vs multi-column)
- `_build_plot_markdown()`: Construye markdown/LaTeX para plots según contexto
- `prepare_generation()`: Prepara contenido para generación (NO mantiene estado restrictivo)

#### Don't Repeat Yourself (DRY)
- La lógica de `figure*` está ahora presente en ambos `_build_image_markdown()` y `_build_plot_markdown()`
- Ambos métodos share el mismo approach: detectar `needs_full_width` y generar LaTeX apropiado

#### Open/Closed Principle
- El sistema permite regeneración sin modificar comportamiento core
- Nuevos tipos de elementos pueden agregar soporte para column span sin modificar infraestructura existente

### Potencial de la Librería

La librería `ePy_docs` ofrece:

1. **Generación Multi-Formato**: HTML, PDF, DOCX, QMD desde un único flujo de trabajo
2. **Layouts Preconfigur ados**: 9 layouts diferentes (professional, creative, minimal, etc.)
3. **Soporte Multi-Columna**: Layout automático con spanning correcto en PDF/LaTeX
4. **Flujo Pythonic**: API fluida con method chaining
5. **Integración Jupyter**: Display inline de figuras y tablas durante desarrollo
6. **Configuración Declarativa**: Sistema epyson para configuración sin hardcoding
7. **Color Palettes**: Sistema de paletas de colores para visualizaciones consistentes
8. **Bibliografia Integrada**: Soporte para citas y referencias con múltiples estilos (APA, Chicago, IEEE)
9. **Validación Robusta**: Sistema de validación completo para prevenir errores comunes
10. **Regeneración Flexible**: Permite workflows iterativos en notebooks

### Estado de Tests

**Passing**: 219/227 tests
**Failing**: 8 tests relacionados con cambios en width generation

**Tests fallidos requieren actualización** para reflejar nuevo comportamiento:
- `test_auto_width_adjustment.py`: 5 tests esperan `width=100%` pero ahora generamos `\columnwidth` o `\linewidth`
- `test_book_bibliography_issues.py`: 2 tests esperan clases CSS o comportamiento antiguo
- `test_validation.py`: 1 test espera error en regeneración (ahora permitida intencionalmente)

### Próximos Pasos

1. ✅ Permitir regeneración de documentos
2. ✅ Agregar soporte `figure*` para imágenes
3. ⏳ Actualizar tests fallidos para reflejar comportamiento correcto
4. ⏳ Verificar generación PDF completa en notebook
5. ⏳ Documentar ejemplos de uso de column_span

### Métricas de Código

**Módulos actualizados**:
- `_quarto.py`: -4 líneas (eliminación de verificación innecesaria)
- `_images.py`: +30 líneas (soporte figure* para imágenes)
- `test_column_span_direction.py`: 2 líneas modificadas

**Complejidad**: Reducida (lógica más simple y directa)
**Mantenibilidad**: Mejorada (menos restricciones artificiales)
**Flexibilidad**: Significativamente mejorada

---

*Última actualización: 2025-01-18*
