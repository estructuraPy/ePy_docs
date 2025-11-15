"""
Prueba del código exacto del usuario para verificar que funciona
"""

from ePy_docs import DocumentWriter
from pathlib import Path

# Obtener rutas a archivos de bibliografía
package_root = Path(__file__).parent / 'src' / 'ePy_docs'
bibliography_file = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_file = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Crear documento
writer = DocumentWriter("paper", layout_style="academic")

writer.add_h1("Proyecto Estructural - Prueba")

# NORMATIVA Y REFERENCIAS
writer.add_h2("Normativa Aplicable") \
      .add_content("""
El diseño estructural se rige por las siguientes normativas y códigos:
""") \
      .add_list([
          "Código Sísmico de Costa Rica (CSCR-2010) [@CSCR2010_14]",
          "American Concrete Institute ACI 318-19 [@ACI318_19]",
          "ASCE 7-16 - Minimum Design Loads [@AISC360_22]",
          "Reglamento de Construcciones de Costa Rica"
      ], ordered=True) \
      .add_content("""
La referencia principal para el diseño sísmico es el Código Sísmico de Costa Rica [@CSCR2010_14], 
que establece los parámetros de diseño para la zona sísmica del proyecto.
""") \
      .add_reference_citation("CSCR2010_14") \
      .add_reference_citation("ACI318_19") \
      .add_reference_citation("AISC360_22")

print("✅ Normativa y referencias bibliográficas agregadas")

# Generar documento
result = writer.generate(
    html=True,
    pdf=True,
    qmd=True,
    output_filename="test_normativa",
    bibliography_path=str(bibliography_file),
    csl_path=str(csl_file)
)

print("\n=== Documento Generado ===")
for format_type, path in result.items():
    if path:
        print(f"{format_type.upper()}: {path}")

print("\n=== Verificación ===")
print("✓ Revisa el PDF para ver las citas renderizadas")
print("✓ Revisa el .qmd para ver el markdown generado")
print("✓ Las referencias deben aparecer al final del documento")
