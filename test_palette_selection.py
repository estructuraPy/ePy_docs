"""
Test para verificar la selección de paletas en tablas y plots
"""
import sys
sys.path.append('src')

from ePy_docs import DocumentWriter
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

print("=== Test: Selección de Paletas ===\n")

# Crear documento con layout minimal
doc = DocumentWriter('report', layout_style='minimal')

# 1. Test de tabla con paleta 'reds'
print("1. Creando tabla con paleta 'reds'...")
data_stress = pd.DataFrame({
    'Material': ['Acero', 'Concreto', 'Madera', 'Aluminio'],
    'Esfuerzo': [250, 180, 120, 200],
    'Deformación': [0.002, 0.001, 0.003, 0.0025],
    'Factor': [1.5, 1.8, 2.0, 1.6]
})

# Test con 'palette_name'
doc.add_colored_table(
    data_stress,
    title="Tabla con paleta 'reds' - usando palette_name",
    show_figure=True,
    palette_name='reds',
    highlight_columns='Esfuerzo'
)

# Test con 'pallete_name' (typo común)
doc.add_colored_table(
    data_stress,
    title="Tabla con paleta 'greens' - usando pallete_name (typo)",
    show_figure=True,
    pallete_name='greens',  # Nota: typo intencional para probar alias
    highlight_columns='Deformación'
)

# 2. Test de plot con paleta específica
print("2. Creando plots con diferentes paletas...")

# Plot con paleta 'blues'
x = np.linspace(0, 10, 100)
fig1, ax1 = plt.subplots(figsize=(8, 4))
for i in range(4):
    ax1.plot(x, np.sin(x + i), label=f'Serie {i+1}')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('Plot con paleta Blues')
ax1.legend()
ax1.grid(True, alpha=0.3)

doc.add_plot(fig1, title="Gráfico con paleta 'blues'", palette_name='blues')
plt.close(fig1)

# Plot con paleta 'reds'
fig2, ax2 = plt.subplots(figsize=(8, 4))
for i in range(4):
    ax2.plot(x, np.cos(x + i), label=f'Serie {i+1}')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_title('Plot con paleta Reds')
ax2.legend()
ax2.grid(True, alpha=0.3)

doc.add_plot(fig2, title="Gráfico con paleta 'reds'", palette_name='reds')
plt.close(fig2)

# Plot con paleta 'minimal' (solo blanco y negro)
fig3, ax3 = plt.subplots(figsize=(8, 4))
for i in range(3):
    ax3.plot(x, np.exp(-x/5) * np.sin(x + i), label=f'Serie {i+1}')
ax3.set_xlabel('X')
ax3.set_ylabel('Y')
ax3.set_title('Plot con paleta Minimal (B&W)')
ax3.legend()
ax3.grid(True, alpha=0.3)

doc.add_plot(fig3, title="Gráfico con paleta 'minimal' (blanco y negro)", palette_name='minimal')
plt.close(fig3)

# Plot sin especificar paleta (usa defaults de matplotlib)
fig4, ax4 = plt.subplots(figsize=(8, 4))
for i in range(4):
    ax4.scatter(x[::10], np.random.randn(10) + i, label=f'Serie {i+1}', alpha=0.6)
ax4.set_xlabel('X')
ax4.set_ylabel('Y')
ax4.set_title('Plot sin paleta específica (default)')
ax4.legend()
ax4.grid(True, alpha=0.3)

doc.add_plot(fig4, title="Gráfico sin paleta (default matplotlib)")
plt.close(fig4)

print("\n3. Generando reporte...")
result = doc.generate(output_filename='Test_Palette_Selection', html=True)

print(f"\n✓ Reporte generado: {result['html']}")
print("\nVerificar que:")
print("  - Tablas usan las paletas especificadas para highlighting")
print("  - Plots usan los colores de las paletas seleccionadas")
print("  - La paleta 'minimal' solo usa blanco y negro")
print("  - El plot sin paleta usa colores default de matplotlib")
