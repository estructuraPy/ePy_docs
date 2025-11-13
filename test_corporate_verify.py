import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

# Test solo corporate para verificar sus colores
writer = DocumentWriter(document_type='report', layout_style='corporate')

content = """
# Corporate Test

[Link de prueba](https://example.com) - debe ser secondary color

## Subtítulo

Texto normal.
"""

writer.add_content(content)
result = writer.generate(html=True, pdf=False, qmd=False, output_filename="test_corporate_only")

print("Corporate HTML:", result.get('html'))

# Verificar CSS corporativo
if os.path.exists("results/report/styles.css"):
    with open("results/report/styles.css", 'r', encoding='utf-8') as f:
        css = f.read()
        print("\nCSS Corporate contiene:")
        print(f"- Layout: {'corporate' in css}")
        print(f"- Helvetica: {'helvetica_lt_std_compressed' in css}")
        print(f"- Color rojo corporativo: {'#C6123C' in css}")
        print(f"- Color azul navy: {'#00217E' in css}")
        print(f"- Texto negro: {'#000000' in css}")
        print(f"- Links secondary: {'color: #00217E' in css}")
        
        # Mostrar la sección de links
        if 'color: #00217E' in css:
            lines = css.split('\n')
            for i, line in enumerate(lines):
                if '#00217E' in line:
                    print(f"\nContexto del link color:")
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        print(f"  {lines[j]}")
                    break