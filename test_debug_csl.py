"""
Test con debugging para verificar el flujo completo de CSL
"""

from ePy_docs import DocumentWriter
from pathlib import Path

# Crear documento
writer = DocumentWriter("paper", layout_style="technical")

# Verificar atributos del writer
print(f"Layout name: {writer.layout_name}")

# Agregar debug a la carga de CSL
from ePy_docs.core._config import get_loader
loader = get_loader()
if loader:
    layout = loader.load_layout(writer.layout_name)
    csl_style = layout.get('citation_style')
    print(f"Citation style desde layout: {csl_style}")
    
    package_root = Path(__file__).parent / 'src' / 'ePy_docs'
    default_csl = package_root / 'config' / 'assets' / 'csl' / f'{csl_style}.csl'
    print(f"Ruta CSL: {default_csl}")
    print(f"¿Existe?: {default_csl.exists()}")

writer.add_h1("Test")
writer.add_text("Cita: [@CSCR2010_14]")

# Generar
result = writer.generate(html=True, pdf=False, qmd=True, output_filename="test_debug")

print(f"\n QMD: {result['qmd']}")
