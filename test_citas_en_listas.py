"""
Test para verificar si las citas bibliográficas funcionan en listas y add_content
"""

from ePy_docs import DocumentWriter
from pathlib import Path

# Obtener rutas a archivos de bibliografía
package_root = Path(__file__).parent / 'src' / 'ePy_docs'
bibliography_file = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_file = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Crear documento
writer = DocumentWriter("paper", layout_style="minimal")

writer.add_h1("Test de Citas en Listas y add_content")

# Test 1: Citas en add_text (ESTO FUNCIONA)
writer.add_h2("1. Citas en add_text (Funciona)")
writer.add_text("El código sísmico [@CSCR2010_14] establece los requisitos de diseño.")

# Test 2: Citas en add_content
writer.add_h2("2. Citas en add_content")
writer.add_content("""
La referencia principal para el diseño sísmico es el Código Sísmico de Costa Rica [@CSCR2010_14], 
que establece los parámetros de diseño para la zona sísmica del proyecto.
También se considera [@ACI318_19] para el diseño de concreto.
""")

# Test 3: Citas en add_list con ordered=True
writer.add_h2("3. Citas en add_list (Ordenada)")
writer.add_list([
    "Código Sísmico de Costa Rica (CSCR-2010) [@CSCR2010_14]",
    "American Concrete Institute ACI 318-19 [@ACI318_19]",
    "ASCE 7-16 - Minimum Design Loads [@ASCE7_16]",
    "AISC 360-22 - Steel Construction Manual [@AISC360_22]"
], ordered=True)

# Test 4: Citas en add_list sin ordenar
writer.add_h2("4. Citas en add_list (No ordenada)")
writer.add_list([
    "Código de viento [@LDpV2023]",
    "Código de cimentaciones [@CCCR2009]",
    "Norma ACI [@ACI318_19]"
], ordered=False)

# Test 5: Combinación con add_text
writer.add_h2("5. Lista seguida de texto con cita")
writer.add_list([
    "Elemento 1 con cita [@CSCR2010_14]",
    "Elemento 2 con cita [@ACI318_19]"
], ordered=True)
writer.add_text("Después de la lista, referenciamos [@AISC360_22] en el texto normal.")

# Test 6: Sintaxis @ sin corchetes en listas
writer.add_h2("6. Sintaxis narrativa en listas")
writer.add_list([
    "Según @CSCR2010_14, el diseño sísmico debe considerar factores regionales",
    "El trabajo de @ACI318_19 establece las bases del diseño en concreto"
], ordered=False)

# Generar documento
result = writer.generate(
    html=True,
    pdf=True,
    qmd=True,
    output_filename="test_citas_listas",
    bibliography_path=str(bibliography_file),
    csl_path=str(csl_file)
)

print("\n=== Documento Generado ===")
for format_type, path in result.items():
    if path:
        print(f"{format_type.upper()}: {path}")

print("\n=== Instrucciones ===")
print("1. Abre el archivo .qmd para ver el markdown crudo")
print("2. Abre el PDF para verificar si las citas se renderizaron")
print("3. Busca las referencias al final del documento")
