"""Test completo de fuentes y colores después de migración."""

import pandas as pd
from ePy_docs.writers import DocumentWriter
from ePy_docs.core._config import get_font_latex_config, get_layout_colors

# Test 1: Verificar generación de fuentes LaTeX
print("="*60)
print("TEST 1: Generación de configuración de fuentes LaTeX")
print("="*60)

layouts_to_test = ['professional', 'corporate', 'handwritten']
for layout in layouts_to_test:
    print(f"\n--- {layout.upper()} ---")
    config = get_font_latex_config(layout)
    if config:
        # Mostrar solo las primeras líneas
        lines = config.strip().split('\n')
        print(f"✅ Fuente configurada: {lines[1] if len(lines) > 1 else 'N/A'}")
    else:
        print("❌ Sin configuración")

# Test 2: Verificar carga de colores
print("\n" + "="*60)
print("TEST 2: Carga de colores del layout")
print("="*60)

for layout in layouts_to_test:
    print(f"\n--- {layout.upper()} ---")
    colors = get_layout_colors(layout)
    print(f"✅ Colores cargados: {len(colors)} colores")
    print(f"   Primary: {colors.get('primary', 'N/A')}")
    print(f"   Secondary: {colors.get('secondary', 'N/A')}")

# Test 3: Crear documento y verificar que no hay errores
print("\n" + "="*60)
print("TEST 3: Creación de DocumentWriter")
print("="*60)

for layout in ['professional', 'corporate']:
    try:
        writer = DocumentWriter('report', layout, 'es')
        print(f"✅ {layout}: DocumentWriter creado exitosamente")
    except Exception as e:
        print(f"❌ {layout}: Error - {e}")

# Test 4: Crear tabla con colores (sin guardar para speed)
print("\n" + "="*60)
print("TEST 4: Validación de estructura colors_config en tablas")
print("="*60)

# Simular lo que hace _tables.py
from ePy_docs.core._config import get_layout, get_config_section

layout_style = 'professional'
layout_config = get_layout(layout_style)

# Aplicar nueva lógica de colores
colors_config = {}
if 'palette' in layout_config:
    embedded_palette = layout_config['palette']
    if 'colors' in embedded_palette:
        colors_config['palettes'] = {
            layout_style: embedded_palette['colors']
        }
        colors_config['palette'] = embedded_palette['colors']

# Agregar color_palettes
colors_data = get_config_section('colors')
if 'color_palettes' in colors_data:
    colors_config['palettes'].update(colors_data['color_palettes'])

print(f"✅ colors_config['palettes'] tiene {len(colors_config['palettes'])} palettes")
print(f"   Palettes disponibles: {', '.join(list(colors_config['palettes'].keys())[:5])}...")

# Verificar que se puede acceder al palette del layout
palette_name = layout_style
if palette_name in colors_config['palettes']:
    palette = colors_config['palettes'][palette_name]
    print(f"✅ Palette '{palette_name}' accesible con {len(palette)} colores")
else:
    print(f"❌ Palette '{palette_name}' no encontrado")

print("\n" + "="*60)
print("RESUMEN: Todos los tests completados")
print("="*60)
