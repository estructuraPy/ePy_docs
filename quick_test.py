import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.writers import DocumentWriter

print("Creando DocumentWriter...")
writer = DocumentWriter(document_type='report', layout_style='minimal')

print("Procesando archivo rockfill.qmd...")
writer.add_quarto_file(r"data\user\document\03_geotech\rockfill.qmd", convert_tables=True)

content = writer.get_content()
print(f"Contenido generado: {len(content)} caracteres")

# Verificar si las tablas se convirtieron
if "![" in content and "Table" in content:
    print("✓ TABLAS CONVERTIDAS A IMÁGENES")
elif "|" in content:
    print("✗ TABLAS AÚN EN FORMATO MARKDOWN")
else:
    print("? NO HAY TABLAS DETECTADAS")

# Verificar LaTeX
if "\\frac" in content:
    print("✓ LATEX PRESERVADO")
else:
    print("✗ LATEX NO ENCONTRADO")

print("LISTO!")