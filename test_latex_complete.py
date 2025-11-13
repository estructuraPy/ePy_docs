"""
Test para verificar la configuración completa de LaTeX para texto normal
"""
from ePy_docs.core._config import get_font_latex_config
from ePy_docs.core._pdf import get_pdf_header_config

print("=" * 70)
print("Configuración completa de LaTeX para layout corporate")
print("=" * 70)

# Configuración de fuentes
print("\n📝 1. Configuración de Fuentes:")
print("-" * 50)
font_config = get_font_latex_config('corporate')
print(font_config)

# Configuración completa del header PDF
print("\n📋 2. Configuración Completa del Header PDF:")
print("-" * 50)
header_config = get_pdf_header_config('corporate')
print(header_config)