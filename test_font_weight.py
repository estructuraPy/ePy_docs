import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

# Crear el writer con layout corporativo
writer = DocumentWriter(document_type='report', layout_style='corporate')

# Agregar contenido con texto normal y encabezados
content = """
# Encabezado 1 (debe estar en negrita)

Este párrafo de texto normal no debe estar en negrita. Solo los encabezados deben tener font-weight bold.

## Encabezado 2 (debe estar en negrita)

Más texto normal que debe aparecer con peso de fuente normal, no en negrita.

### Encabezado 3 (debe estar en negrita)

- Este elemento de lista no debe estar en negrita
- Este tampoco debe estar en negrita

#### Encabezado 4 (debe estar en negrita)

| Columna 1 | Columna 2 |
|-----------|-----------|
| Texto normal en tabla | También normal |

##### Encabezado 5 (debe estar en negrita)

Este es texto normal después del encabezado 5.

###### Encabezado 6 (debe estar en negrita)

Y este es el último párrafo de texto normal.
"""

writer.add_content(content)

# Generar solo HTML
result = writer.generate(html=True, pdf=False, qmd=False, output_filename="test_font_weight_output")
html_path = result.get('html', 'test_font_weight_output.html')

print(f"HTML generado en: {html_path}")

# Mostrar parte del HTML generado para verificar los estilos
if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Buscar la sección de estilos
    if "<style>" in html_content:
        start_idx = html_content.find("<style>")
        end_idx = html_content.find("</style>") + 8
        styles_section = html_content[start_idx:end_idx]
        print("\nEstilos CSS aplicados:")
        print("=" * 50)
        print(styles_section)
    
    print("\nPrimeras líneas del body:")
    print("=" * 50)
    if "<body>" in html_content:
        body_start = html_content.find("<body>")
        body_content = html_content[body_start:body_start+500]
        print(body_content)