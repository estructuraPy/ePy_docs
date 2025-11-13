"""
RESUMEN DE CORRECCIONES PARA RENDERIZADO DE QMD
================================================

## Problema Original
El contenido de archivos QMD (Quarto Markdown) no se renderizaba correctamente.
Las referencias cruzadas (@fig-xxx, @tbl-xxx) y los atributos de figuras/tablas
({#fig-xxx}, {#tbl-xxx}) se estaban eliminando durante el procesamiento.

## Solución Implementada

### 1. Preservar Referencias Cruzadas de Quarto
**Archivo**: src/ePy_docs/core/_quarto.py
**Líneas 1064-1068**: Se eliminaron las siguientes líneas que removían referencias:
- content = re.sub(r'@fig-[\w-]+', '[Figure]', content)
- content = re.sub(r'@tbl-[\w-]+', '[Table]', content)
- content = re.sub(r'@eq-[\w-]+', '[Equation]', content)

**Razón**: Quarto necesita estas referencias para generar links automáticos entre
el texto y las figuras/tablas/ecuaciones.

### 2. Preservar Atributos de Identificación
**Archivo**: src/ePy_docs/core/_quarto.py
**Líneas 1070-1082**: Se eliminó el código que limpiaba atributos {#xxx}

**Razón**: Los atributos {#fig-xxx}, {#tbl-xxx} son necesarios para que Quarto
pueda identificar y referenciar elementos.

## Resultado

Ahora el sistema preserva correctamente:
✅ Referencias cruzadas: @fig-xxx, @tbl-xxx, @eq-xxx
✅ Referencias bibliográficas: @CSCR2010_14, @LDpV2023, etc.
✅ Atributos de identificación: {#fig-xxx}, {#tbl-xxx}
✅ LaTeX matemático: $\phi M_{n} = 584.20 kgf \cdot m$
✅ Tablas Markdown con captions
✅ Listas y texto normal
✅ Todos los niveles de encabezados

## Verificación

Para verificar que funciona correctamente:
```python
from src.ePy_docs.writers import DocumentWriter

writer = DocumentWriter(layout_style='corporate')
writer.add_quarto_file('tu_archivo.qmd', fix_image_paths=True)
result = writer.generate()
```

El QMD generado preservará todas las referencias y atributos de Quarto,
permitiendo que Quarto genere correctamente el PDF con referencias cruzadas
funcionando.
"""
print(__doc__)
