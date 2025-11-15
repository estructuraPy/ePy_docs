"""
Test para verificar que column_span ajusta correctamente el ancho de imágenes y plots
"""

from ePy_docs import DocumentWriter
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Crear documento con 2 columnas
writer = DocumentWriter("paper", layout_style="academic", columns=2)

writer.add_h1("Prueba de Column Span en Imágenes")

# Test 1: Plot sin column_span (debe usar 1 columna por defecto)
writer.add_h2("1. Plot sin column_span (1 columna)")
fig1, ax1 = plt.subplots(figsize=(6, 4))
x = np.linspace(0, 10, 100)
ax1.plot(x, np.sin(x))
ax1.set_title("Sine Wave")
writer.add_plot(fig1, title="Plot de 1 Columna", caption="Sin column_span especificado")

# Test 2: Plot con column_span=1 (explícito)
writer.add_h2("2. Plot con column_span=1 (1 columna)")
fig2, ax2 = plt.subplots(figsize=(6, 4))
ax2.plot(x, np.cos(x))
ax2.set_title("Cosine Wave")
writer.add_plot(fig2, title="Plot de 1 Columna Explícito", caption="column_span=1", column_span=1)

# Test 3: Plot con column_span=2 (ancho completo)
writer.add_h2("3. Plot con column_span=2 (ancho completo)")
fig3, ax3 = plt.subplots(figsize=(8, 5))
ax3.plot(x, np.sin(x) * np.cos(x))
ax3.set_title("Combined Wave")
writer.add_plot(fig3, title="Plot de Ancho Completo", caption="column_span=2 (debe abarcar 2 columnas)", column_span=2)

# Test 4: Imagen con column_span (si tienes una imagen disponible)
writer.add_h2("4. Notas sobre Ancho")
writer.add_text("""
Con layout de 2 columnas en paper:
- column_span=1 debería resultar en width ≈ 3.1in
- column_span=2 debería resultar en width ≈ 6.5in

El ancho ahora se calcula automáticamente usando ColumnWidthCalculator
basado en el column_span especificado.
""")

# Generar solo QMD para revisar el YAML y el markdown
result = writer.generate(
    html=False,
    pdf=False,
    qmd=True,
    output_filename="column_span_test"
)

print("\nDocumento generado:")
print(f"QMD: {result['qmd']}")

# Leer y mostrar contenido para verificar los anchos
qmd_path = result['qmd']
with open(qmd_path, 'r', encoding='utf-8') as f:
    content = f.read()

print("\n=== Verificando anchos en el QMD ===")
import re
# Buscar todas las líneas con width=
width_lines = re.findall(r'!\[.*?\]\(.*?\)\{width=([^}]+)[^}]*\}', content)
for i, width in enumerate(width_lines, 1):
    print(f"Figura {i}: width={width}")

print("\nSi ves:")
print("  - width=3.1in o similar para column_span=1 ✓")
print("  - width=6.5in para column_span=2 ✓")
print("Entonces column_span está funcionando correctamente!")
