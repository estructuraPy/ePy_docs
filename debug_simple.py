import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

# Test simple con una tabla que sabemos que falla
test_table = """
# Test

| Condición de análisis | Riesgo de daños económicos y ambientales | Riesgo de pérdida de vidas |
| :-------------------- | :------------------------------------- | :------------------------ |
|                       |                                        | Bajo    | Medio   | Alto   |
| Estática              | Bajo                                    | 1,20    | 1,30    | 1,40   |

Fin del test.
"""

print("Creando writer...")
writer = DocumentWriter(document_type='report', layout_style='minimal')

print("Agregando contenido con tabla...")
writer.add_content(test_table)

content = writer.get_content()
print(f"\nResultado final ({len(content)} chars):")
print("=" * 50)
print(content)
print("=" * 50)

if "![" in content:
    print("\n✓ TABLA CONVERTIDA A IMAGEN")
elif "|" in content:
    print("\n✗ TABLA SIGUE EN MARKDOWN")
else:
    print("\n? NO SE DETECTÓ TABLA")