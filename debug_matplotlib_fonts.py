#!/usr/bin/env python3
"""
Debug matplotlib fonts para layout handwritten
"""

from src.ePy_docs.core._images import setup_matplotlib_fonts
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

print("=== DEBUG MATPLOTLIB FONTS ===")

# Test font setup for handwritten
layout = "handwritten"
print(f"\n1. Configurando matplotlib para layout: {layout}")
font_list = setup_matplotlib_fonts(layout)
print(f"Lista de fuentes configuradas: {font_list}")

# Check if our custom font is available in matplotlib
print(f"\n2. Verificando disponibilidad de anm_ingenieria_2025:")
available_fonts = [f.name for f in fm.fontManager.ttflist]
custom_font_available = any('anm_ingenieria' in font_name.lower() for font_name in available_fonts)
print(f"Fuente anm_ingenieria_2025 disponible en matplotlib: {custom_font_available}")

# Show matplotlib current font config
print(f"\n3. Configuración actual de matplotlib:")
print(f"font.family: {plt.rcParams['font.family']}")
print(f"font.sans-serif: {plt.rcParams['font.sans-serif']}")

# Test creating a simple plot
print(f"\n4. Creando plot de prueba...")
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([1, 2, 3, 4], [1, 4, 2, 3], 'b-', linewidth=2)
ax.set_title("Test Plot - Fuente Personalizada", fontsize=16)
ax.set_xlabel("X axis", fontsize=12)
ax.set_ylabel("Y axis", fontsize=12)

# Check what font is actually being used
title_font = ax.title.get_fontname()
xlabel_font = ax.xaxis.label.get_fontname()

print(f"Fuente usada en título: {title_font}")
print(f"Fuente usada en labels: {xlabel_font}")

# Save plot for inspection
plt.savefig("results/test_matplotlib_fonts.png", dpi=150, bbox_inches='tight')
plt.close()

print(f"\n✅ Plot guardado en: results/test_matplotlib_fonts.png")
print("=== END DEBUG ===")