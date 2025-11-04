"""
Verificación de anchos uniformes y captions correctos
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from ePy_docs import DocumentWriter

print("🔍 VERIFICACIÓN DE ANCHOS Y CAPTIONS")
print("=" * 70)

# Crear writer
writer = DocumentWriter("report", "handwritten")

writer.add_h1("Prueba de Uniformidad de Anchos y Captions")

# Tabla 1
df1 = pd.DataFrame({
    'Elemento': ['V-1', 'V-2', 'V-3'],
    'Carga (kN)': [150, 230, 180],
    'Deflexión (mm)': [2.3, 4.1, 3.2]
})

print("✓ Agregando tabla 1...")
writer.add_table(df1, title="Primera tabla", show_figure=True)

# Figura 1
x = np.linspace(0, 10, 50)
y = np.sin(x)

fig1, ax1 = plt.subplots(figsize=(6.5, 4))
ax1.plot(x, y, 'b-', linewidth=2)
ax1.set_xlabel('x')
ax1.set_ylabel('sin(x)')
ax1.set_title('Función Seno')
ax1.grid(True, alpha=0.3)
plt.tight_layout()

print("✓ Agregando figura 1 con caption...")
writer.add_plot(fig1, caption="Gráfica de la función seno")
plt.close()

# Tabla 2
df2 = pd.DataFrame({
    'Muestra': ['M-1', 'M-2', 'M-3', 'M-4'],
    'pH': [7.2, 6.8, 7.5, 7.0],
    'Temperatura (°C)': [22.5, 24.1, 23.8, 21.9]
})

print("✓ Agregando tabla 2...")
writer.add_table(df2, title="Segunda tabla", show_figure=True)

# Figura 2
categories = ['A', 'B', 'C', 'D']
values = [23, 45, 56, 32]

fig2, ax2 = plt.subplots(figsize=(6.5, 4))
ax2.bar(categories, values, color='steelblue', alpha=0.7)
ax2.set_xlabel('Categoría')
ax2.set_ylabel('Valor')
ax2.set_title('Datos por Categoría')
ax2.grid(True, axis='y', alpha=0.3)
plt.tight_layout()

print("✓ Agregando figura 2 con caption...")
writer.add_plot(fig2, caption="Gráfica de barras comparativa")
plt.close()

# Generar documento
print("\n📝 Generando documento...")
writer.generate(html=True, pdf=False)

print("\n✅ Documento generado: results/report/Document.html")

# Verificar el markdown generado
print("\n🔍 VERIFICANDO MARKDOWN GENERADO:")
print("-" * 70)

with open("results/report/Document.qmd", "r", encoding="utf-8") as f:
    content = f.read()

# Buscar todas las líneas con imágenes
import re
image_lines = [line for line in content.split('\n') if '![' in line and '](' in line]

print(f"\n📊 IMÁGENES ENCONTRADAS: {len(image_lines)}")
for i, line in enumerate(image_lines, 1):
    print(f"\n{i}. {line[:100]}...")
    
    # Verificar ancho
    width_match = re.search(r'\{width=([^}]+)\}', line)
    if width_match:
        print(f"   ✓ Ancho: {width_match.group(1)}")
    else:
        print(f"   ⚠️ Sin especificación de ancho")
    
    # Verificar ID
    id_match = re.search(r'\{#([^}]+)\}', line)
    if id_match:
        print(f"   ✓ ID: {id_match.group(1)}")
    else:
        print(f"   ⚠️ Sin ID")
    
    # Verificar si el ID aparece pegado al ancho
    if '}{#' in line:
        print(f"   ⚠️ PROBLEMA: ID pegado al ancho (sin espacio)")
    elif '} {#' in line:
        print(f"   ✓ Espacio correcto entre ancho e ID")

# Buscar captions
caption_lines = [line for line in content.split('\n') if line.startswith('**Figure') or line.startswith('**Figura')]
print(f"\n📝 CAPTIONS ENCONTRADOS: {len(caption_lines)}")
for i, line in enumerate(caption_lines, 1):
    print(f"{i}. {line[:80]}...")

# Verificar anchos de tablas
table_lines = [line for line in content.split('\n') if 'table_' in line.lower() and '![' in line]
print(f"\n📋 TABLAS ENCONTRADAS: {len(table_lines)}")
for i, line in enumerate(table_lines, 1):
    width_match = re.search(r'\{width=([^}]+)\}', line)
    if width_match:
        print(f"{i}. Ancho tabla: {width_match.group(1)}")

print("\n" + "=" * 70)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 70)
