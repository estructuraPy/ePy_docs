# Corrección: Manejo de Citas y Referencias Bibliográficas

## Problema Identificado

Las citas y referencias bibliográficas no se manejaban adecuadamente en Quarto. Los archivos `.bib` (bibliografía) y `.csl` (estilo de citas) estaban ubicados en el directorio `assets` de la librería, pero **no se copiaban** al directorio de salida donde se genera el documento `.qmd`.

Esto causaba que Quarto no pudiera encontrar los archivos durante el proceso de renderizado, resultando en citas y referencias no procesadas correctamente.

## Solución Implementada

### 1. Nueva Función de Copia de Archivos (`_copy_bibliography_files_to_output`)

Se agregó una función en `_quarto.py` que:
- Copia el archivo `.bib` al directorio de salida
- Copia el archivo `.csl` al directorio de salida  
- Devuelve las rutas relativas (solo nombres de archivo) para usar en la configuración YAML

```python
def _copy_bibliography_files_to_output(
    bibliography_path: Optional[str],
    csl_path: Optional[str],
    output_dir: Path
) -> Tuple[Optional[str], Optional[str]]:
    """
    Copia archivos de bibliografía y CSL al directorio de salida.
    Quarto espera que estos archivos estén en el mismo directorio que el .qmd.
    """
```

### 2. Modificación de `create_and_render`

La función ahora:
1. **Primero** copia los archivos `.bib` y `.csl` al directorio de salida
2. **Luego** genera la configuración YAML con las rutas relativas (solo nombres de archivo)
3. Finalmente crea el `.qmd` y renderiza los formatos solicitados

```python
# Copiar archivos al directorio de salida
output_dir = output_path.parent
bib_relative, csl_relative = _copy_bibliography_files_to_output(
    bibliography_path, csl_path, output_dir
)

# Generar YAML con rutas relativas
yaml_config = generate_quarto_yaml(
    ...
    bibliography_path=bib_relative,  # Solo el nombre del archivo
    csl_path=csl_relative,           # Solo el nombre del archivo
    ...
)
```

### 3. Simplificación de `generate_quarto_yaml`

Se eliminó la conversión de backslashes (`\` a `/`) ya que ahora solo se usan nombres de archivo (rutas relativas simples):

```python
# Antes:
yaml_config['bibliography'] = str(bibliography_path).replace('\\', '/')

# Ahora:
yaml_config['bibliography'] = bibliography_path  # Solo nombre de archivo
```

## Archivos Modificados

1. **`src/ePy_docs/core/_quarto.py`**
   - Agregada función `_copy_bibliography_files_to_output`
   - Modificada función `create_and_render`
   - Simplificada función `generate_quarto_yaml`

2. **`src/ePy_docs/writers.py`**
   - Actualizada documentación del método `generate` para aclarar que los archivos se copian automáticamente

3. **`examples/bibliography_example.py`** (nuevo)
   - Ejemplo completo de uso de bibliografía y citas

## Uso

### Archivos Incluidos con la Librería

La librería incluye archivos predeterminados en `config/assets/`:
- **Bibliografía**: `bibliography/references.bib`
- **Estilos CSL**: `csl/ieee.csl`, `csl/apa.csl`, `csl/chicago.csl`

### Ejemplo Básico

```python
from ePy_docs import DocumentWriter
from pathlib import Path

# Rutas a archivos incluidos con la librería
package_root = Path(__file__).parent.parent / 'src' / 'ePy_docs'
bibliography = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_style = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Crear documento
writer = DocumentWriter("paper", layout_style="academic")

# Agregar contenido con citas
# Cita entre paréntesis
writer.add_text("El código sísmico [@CSCR2002] establece...")

# Cita narrativa (en el texto)
writer.add_text("Según @ASCE7, el diseño debe considerar...")

# Generar con bibliografía
result = writer.generate(
    pdf=True,
    html=True,
    bibliography_path=str(bibliography),  # Se copiará automáticamente
    csl_path=str(csl_style)              # Se copiará automáticamente
)
```

### Sintaxis de Citas

Quarto/Pandoc soporta dos formas principales de citar:

**Citas entre paréntesis** (con corchetes):
- **Cita simple**: `[@citation_key]` → (Author, Year)
- **Múltiples citas**: `[@key1; @key2]` → (Author1, Year1; Author2, Year2)
- **Con página**: `[@key, p. 42]` → (Author, Year, p. 42)

**Citas narrativas** (sin corchetes, en el flujo del texto):
- **En el texto**: `@citation_key` → Author (Year)
- **Ejemplo**: "Según @ASCE7, el diseño sísmico..." → "Según ASCE (2022), el diseño sísmico..."
- **Con sufijo**: `@key [p. 42]` → Author (Year, p. 42)

## Comportamiento

1. Cuando se llama a `generate()` con `bibliography_path` y/o `csl_path`:
   - Los archivos se copian al directorio de salida (ej: `results/paper/`)
   - El YAML del `.qmd` referencia los archivos usando solo el nombre (ej: `references.bib`)
   - Quarto encuentra los archivos porque están en el mismo directorio
   - Las citas se procesan correctamente en HTML y PDF

2. Si no se proporciona `bibliography_path`:
   - No se configura bibliografía
   - Las referencias `[@key]` aparecen como texto literal

## Beneficios

✅ **Portabilidad**: El directorio de salida contiene todos los archivos necesarios  
✅ **Simplicidad**: Funciona automáticamente, sin configuración manual  
✅ **Flexibilidad**: Se pueden usar rutas absolutas o relativas  
✅ **Compatibilidad**: Funciona con cualquier archivo `.bib` y `.csl` estándar

## Archivos de Salida

Después de generar un documento con bibliografía, el directorio de salida contendrá:

```
results/paper/
├── Document.qmd          # Archivo Quarto con referencias
├── Document.pdf          # PDF renderizado con bibliografía
├── Document.html         # HTML renderizado con bibliografía
├── references.bib        # Copia del archivo de bibliografía
├── ieee.csl             # Copia del estilo CSL
├── styles.css
├── figures/
└── tables/
```

## Referencias

- [Quarto Citations](https://quarto.org/docs/authoring/footnotes-and-citations.html)
- [BibTeX Format](http://www.bibtex.org/)
- [Citation Style Language (CSL)](https://citationstyles.org/)
