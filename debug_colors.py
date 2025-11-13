import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.core._config import get_layout_colors

# Test the get_layout_colors function
colors = get_layout_colors('corporate')
print("Colores obtenidos para 'corporate':")
for key, value in colors.items():
    print(f"  {key}: {value}")

# También probemos con otros layouts para comparar
print("\nColores para 'classic':")
classic_colors = get_layout_colors('classic')
for key, value in classic_colors.items():
    print(f"  {key}: {value}")