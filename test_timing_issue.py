"""
Test crítico: Verificar si el problema es el timing de aplicación de fuentes.
"""

import matplotlib.pyplot as plt
import numpy as np
from ePy_docs import setup_matplotlib_fonts, apply_fonts_to_plot

# Caso 1: Aplicar fuentes ANTES de tight_layout
print("="*70)
print("CASO 1: Fuentes ANTES de tight_layout")
print("="*70)

font_list = setup_matplotlib_fonts('handwritten')
print(f"Font list: {font_list}")

fig1, ax1 = plt.subplots(figsize=(10, 6))
ax1.plot([0, 1, 2], [0, 1, 4])
ax1.set_xlabel('Test (0123) [ABC]')
ax1.set_title('Before tight_layout')

# Aplicar fuentes ANTES
apply_fonts_to_plot(ax1, font_list)
print("✓ Fuentes aplicadas")

# DESPUÉS hacer tight_layout
plt.tight_layout()
print("✓ tight_layout llamado")

fig1.savefig('results/report/test_before_tight_layout.png', dpi=150, bbox_inches='tight')
print("✓ Guardado: test_before_tight_layout.png\n")
plt.close(fig1)

# Caso 2: Aplicar fuentes DESPUÉS de tight_layout (como hace writer.add_plot ahora)
print("="*70)
print("CASO 2: Fuentes DESPUÉS de tight_layout (situación actual)")
print("="*70)

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot([0, 1, 2], [0, 1, 4])
ax2.set_xlabel('Test (0123) [ABC]')
ax2.set_title('After tight_layout')

# PRIMERO tight_layout
plt.tight_layout()
print("✓ tight_layout llamado")

# DESPUÉS aplicar fuentes (esto es lo que hace writer.add_plot)
apply_fonts_to_plot(ax2, font_list)
print("✓ Fuentes aplicadas")

fig2.savefig('results/report/test_after_tight_layout.png', dpi=150, bbox_inches='tight')
print("✓ Guardado: test_after_tight_layout.png\n")
plt.close(fig2)

# Caso 3: Aplicar fuentes y forzar re-render llamando draw
print("="*70)
print("CASO 3: Fuentes DESPUÉS + canvas.draw() para forzar re-render")
print("="*70)

fig3, ax3 = plt.subplots(figsize=(10, 6))
ax3.plot([0, 1, 2], [0, 1, 4])
ax3.set_xlabel('Test (0123) [ABC]')
ax3.set_title('After with draw()')

plt.tight_layout()
print("✓ tight_layout llamado")

apply_fonts_to_plot(ax3, font_list)
print("✓ Fuentes aplicadas")

# Forzar re-render
fig3.canvas.draw()
print("✓ canvas.draw() llamado para forzar re-render")

fig3.savefig('results/report/test_with_canvas_draw.png', dpi=150, bbox_inches='tight')
print("✓ Guardado: test_with_canvas_draw.png\n")
plt.close(fig3)

print("="*70)
print("ANÁLISIS:")
print("="*70)
print("Compara los 3 archivos generados:")
print("  1. test_before_tight_layout.png")
print("  2. test_after_tight_layout.png  ← Situación actual de writer.add_plot")
print("  3. test_with_canvas_draw.png    ← Posible solución")
print()
print("Si SOLO el caso 1 o 3 muestran fallbacks correctos,")
print("entonces el problema es el TIMING de aplicación de fuentes.")
