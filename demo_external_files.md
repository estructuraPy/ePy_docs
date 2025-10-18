# Demostración: Incluir Archivos Externos

Este notebook muestra cómo incluir archivos **Markdown** (.md) y **Quarto** (.qmd) externos en el flujo de generación de documentos con ePy_docs.

## Métodos disponibles

### 1. `add_markdown_file(file_path, fix_image_paths=True)`

Incluye archivos `.md` estándar al documento.

**Parámetros:**
- `file_path`: Ruta al archivo .md
- `fix_image_paths`: Corrige rutas de imágenes relativas (default: True)

### 2. `add_quarto_file(file_path, include_yaml=False, fix_image_paths=True)`

Incluye archivos `.qmd` de Quarto con sintaxis avanzada.

**Parámetros:**
- `file_path`: Ruta al archivo .qmd
- `include_yaml`: Incluir metadata YAML del frontmatter (default: False)
- `fix_image_paths`: Corrige rutas de imágenes (default: True)

---

## Ejemplo de uso

```python
from ePy_docs import ReportWriter

# Crear writer
writer = ReportWriter(layout_style='classic')

# Agregar contenido manual
writer.add_h1("Documento con Secciones Externas") \\
      .add_content("Este documento combina contenido generado y archivos externos.")

# Incluir archivo Markdown
writer.add_h2("Sección desde Markdown") \\
      .add_markdown_file("data/user/document/sample_section.md")

# Incluir archivo Quarto (sin YAML)
writer.add_h2("Sección desde Quarto") \\
      .add_quarto_file("data/user/document/sample_quarto.qmd", include_yaml=False)

# Más contenido manual
writer.add_h2("Conclusiones") \\
      .add_content("Las secciones externas se integran perfectamente al documento.")

# Generar
results = writer.generate(html=True, pdf=True)
print("✅ Documento generado con secciones externas")
```

## Casos de uso

1. **Separación de contenido**: Mantener secciones complejas en archivos individuales
2. **Reutilización**: Compartir secciones entre múltiples reportes
3. **Colaboración**: Diferentes autores editan secciones independientes
4. **Templates**: Usar plantillas predefinidas (introducción, metodología, etc.)
5. **Documentación técnica**: Incluir especificaciones desde archivos separados

## Ventajas

✅ **Method chaining**: Se integra con el patrón fluido de ePy_docs  
✅ **Compatibilidad**: Acepta rutas absolutas o relativas  
✅ **Procesamiento automático**: Manejo de imágenes y rutas  
✅ **Flexibilidad**: Combina contenido programático y archivos externos  
✅ **Sin duplicación**: Mantén contenido reutilizable en un solo lugar  

---

**Nota:** Los archivos externos se insertan en el orden que los agregas al writer, permitiendo control total sobre la estructura del documento.
