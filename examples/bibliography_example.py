"""
Ejemplo de uso de bibliografía y citas en ePy_docs

Este ejemplo demuestra cómo usar archivos .bib y .csl para citas bibliográficas.
Los archivos se copian automáticamente al directorio de salida durante la generación.
"""

from ePy_docs import DocumentWriter
from pathlib import Path

# Obtener rutas a los archivos de bibliografía y CSL incluidos con la librería
package_root = Path(__file__).parent.parent / 'src' / 'ePy_docs'
bibliography_file = package_root / 'config' / 'assets' / 'bibliography' / 'references.bib'
csl_file = package_root / 'config' / 'assets' / 'csl' / 'ieee.csl'

# Verificar que los archivos existen
print(f"Bibliography file exists: {bibliography_file.exists()}")
print(f"CSL file exists: {csl_file.exists()}")

# Crear documento
writer = DocumentWriter("paper", layout_style="academic")

# Agregar título y contenido
writer.add_h1("Documento con Referencias Bibliográficas")

writer.add_text("""
Este documento demuestra el uso de citas bibliográficas en ePy_docs.
Las citas se pueden incluir usando la sintaxis de Pandoc [@citation_key].
""")

writer.add_h2("Ejemplo de Citas Entre Paréntesis")

writer.add_text("""
Los códigos sísmicos son fundamentales para el diseño estructural [@CSCR2002].
Además, el diseño por viento debe considerarse en zonas expuestas [@LDpV2023].
""")

writer.add_text("""
Múltiples referencias pueden citarse simultáneamente [@CSCR2010_14; @ACI318_19].
Para cimentaciones, se debe consultar el código correspondiente [@CCCR2009].
""")

writer.add_h2("Ejemplo de Citas Narrativas")

writer.add_text("""
Según @CSCR2002, los requisitos sísmicos han evolucionado significativamente.
El trabajo de @ACI318_19 establece los criterios para diseño de concreto.
Como menciona @AISC360_22, las estructuras de acero requieren consideraciones especiales.
""")

writer.add_h2("Estructura de Acero")

writer.add_text("""
El diseño de estructuras de acero debe seguir las especificaciones AISC [@AISC360_22].
Para zonas sísmicas, se aplican provisiones especiales [@AISC341_22].
""")

# Generar documento con bibliografía
# Los archivos .bib y .csl se copiarán automáticamente al directorio de salida
result = writer.generate(
    html=True,
    pdf=True,
    qmd=True,
    output_filename="bibliography_example",
    bibliography_path=str(bibliography_file),
    csl_path=str(csl_file)
)

print("\nDocumento generado exitosamente:")
for format_type, path in result.items():
    if path:
        print(f"  {format_type}: {path}")

print("\nNOTA: Los archivos references.bib e ieee.csl fueron copiados automáticamente")
print("al directorio de salida para que Quarto pueda procesarlos correctamente.")
