import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

# Test específico para tablas con layout corporativo
writer = DocumentWriter(document_type='report', layout_style='corporate')

content = """
# Test de Tablas - Corporate

Este texto normal NO debe estar en negrita.

| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Texto normal en celda | También normal | No debe estar en negrita |
| Segunda fila | Texto normal | Sin negrita |

Más texto normal después de la tabla.

## Subtítulo (debe estar en negrita)

[Este enlace debe ser secondary color](https://example.com)

Párrafo normal que NO debe estar en negrita.
"""

writer.add_content(content)
result = writer.generate(html=True, pdf=False, qmd=False, output_filename="test_tabla_negrita")

print("HTML generado:", result.get('html'))

# Verificar el HTML generado
html_path = result.get('html')
if html_path and os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Buscar patrones problemáticos
    print("\n=== ANÁLISIS HTML ===")
    
    # Buscar font-weight en el HTML
    if 'font-weight:' in html_content:
        print("❌ ENCONTRADO font-weight hardcodeado en HTML:")
        lines = html_content.split('\n')
        for i, line in enumerate(lines):
            if 'font-weight:' in line.lower():
                print(f"  Línea {i+1}: {line.strip()}")
    
    # Buscar estilos inline problemáticos
    if 'bold' in html_content.lower():
        print("❌ ENCONTRADO 'bold' hardcodeado:")
        lines = html_content.split('\n')
        for i, line in enumerate(lines):
            if 'bold' in line.lower() and 'font' in line.lower():
                print(f"  Línea {i+1}: {line.strip()}")
    
    # Buscar clases CSS problemáticas
    if 'class=' in html_content:
        print("\n📋 Clases CSS encontradas:")
        import re
        classes = re.findall(r'class="([^"]*)"', html_content)
        unique_classes = set(classes)
        for cls in sorted(unique_classes):
            if cls:
                print(f"  - {cls}")

print("\n=== VERIFICACIÓN CSS ===")
css_path = "results/report/styles.css"
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # Verificar que el CSS tenga font-weight: normal para elementos de texto
    print("CSS font-weight settings:")
    lines = css_content.split('\n')
    for i, line in enumerate(lines):
        if 'font-weight:' in line:
            print(f"  {line.strip()}")
            
    # Verificar reglas para th y td específicamente
    print("\nReglas específicas para tablas:")
    in_table_rule = False
    for line in lines:
        if line.strip().startswith(('th ', 'td ', 'table')):
            in_table_rule = True
            print(f"  {line.strip()}")
        elif in_table_rule and (line.strip().startswith('}') or line.strip() == ''):
            in_table_rule = False
            print(f"  {line.strip()}")
        elif in_table_rule:
            print(f"  {line.strip()}")