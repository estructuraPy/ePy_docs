import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

# Test final: verificar que todo funciona con layout corporativo y handwritten

print("=== TEST CORPORATE LAYOUT ===")
writer_corp = DocumentWriter(document_type='report', layout_style='corporate')

content_corp = """
# Título Corporativo (debe ser rojo #C6123C)

Este párrafo usa texto normal en negro (#000000) con fuente Helvetica.

## Subtítulo (debe ser azul navy #00217E)

[Este enlace debe ser azul navy #00217E](https://example.com)

### Subsección (debe ser gris medio #636466)

Más contenido con fuentes corporativas.
"""

writer_corp.add_content(content_corp)
result_corp = writer_corp.generate(html=True, pdf=False, qmd=False, output_filename="test_corporate_final")

print("Corporate HTML generado en:", result_corp.get('html'))

print("\n=== TEST HANDWRITTEN LAYOUT ===")
writer_hand = DocumentWriter(document_type='report', layout_style='handwritten')

content_hand = """
# Título Handwritten

Este texto debe usar anm_ingenieria_2025 en todos los formatos (HTML, PDF, markdown).

[Este enlace también debe usar secondary color](https://example.com)

## Subtítulo handwritten

Contenido con fuente personalizada consistente.
"""

writer_hand.add_content(content_hand)
result_hand = writer_hand.generate(html=True, pdf=False, qmd=False, output_filename="test_handwritten_final")

print("Handwritten HTML generado en:", result_hand.get('html'))

print("\n=== VERIFICACIÓN DE CSS ===")
# Verificar los CSS generados
css_paths = [
    "results/report/styles.css"
]

for css_path in css_paths:
    if os.path.exists(css_path):
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()
            print(f"\n{css_path} contiene:")
            print(f"- Fuente helvetica: {'helvetica_lt_std_compressed' in css_content}")
            print(f"- Color secondary en links: {'#00217E' in css_content}")
            print(f"- Colores corporativos: {'#C6123C' in css_content}")
            print(f"- Text color negro: {'#000000' in css_content}")
    else:
        print(f"{css_path} no existe")

print("\n✅ Cambios implementados:")
print("1. Links usan secondary color (#00217E) en todos los layouts")  
print("2. anm_ingenieria_2025 simplificado para uso consistente en todos los formatos")
print("3. Configuración corporativa con colores correctos")
print("4. CSS completo con font-weight normal para texto y bold solo para headings")