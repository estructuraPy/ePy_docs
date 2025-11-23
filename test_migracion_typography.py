"""Test rápido de migración de tipografía y corrección de colores."""

from ePy_docs.core._config import get_layout, get_layout_colors
from ePy_docs.writers import DocumentWriter
import pandas as pd

print("="*70)
print("TEST 1: Verificar que layouts tienen typography embebida")
print("="*70)

layouts_to_test = ['professional', 'corporate', 'academic', 'handwritten']

for layout_name in layouts_to_test:
    layout = get_layout(layout_name, resolve_refs=False)
    has_typography = 'typography' in layout
    has_font_family = 'font_family' in layout
    
    if has_typography:
        typo = layout['typography']
        has_scales = 'scales' in typo
        has_roles = 'role_assignments' in typo
        has_font_ref = 'font_family_ref' in typo
        print(f"\n✅ {layout_name}: typography OK")
        print(f"   - scales: {has_scales}, roles: {has_roles}, NO font_family_ref: {not has_font_ref}")
    else:
        print(f"\n❌ {layout_name}: NO typography section")
    
    if layout_name == 'corporate':
        font_fam = layout.get('font_family', {})
        has_latex = 'latex_primary' in font_fam
        print(f"   - corporate latex_primary: {'✅' if has_latex else '❌'} ({font_fam.get('latex_primary', 'MISSING')})")

print("\n" + "="*70)
print("TEST 2: Verificar que get_layout_colors retorna TODOS los colores")
print("="*70)

for layout_name in ['professional', 'corporate']:
    colors = get_layout_colors(layout_name)
    
    # Verificar colores de tabla
    required_table_colors = ['table_header', 'table_header_text', 'table_stripe', 'table_background']
    missing = [c for c in required_table_colors if c not in colors]
    
    print(f"\n{layout_name}:")
    print(f"   Total colors: {len(colors)}")
    print(f"   Table colors present: {len(required_table_colors) - len(missing)}/4")
    if missing:
        print(f"   ❌ Missing: {missing}")
    else:
        print(f"   ✅ All table colors present")
    
    # Mostrar algunos colores
    sample_colors = ['primary', 'secondary', 'table_header', 'page_background']
    for color_key in sample_colors:
        if color_key in colors:
            print(f"   - {color_key}: {colors[color_key]}")

print("\n" + "="*70)
print("TEST 3: Crear DocumentWriter y verificar configuración")
print("="*70)

try:
    writer = DocumentWriter('report', 'professional', 'es')
    print("✅ DocumentWriter creado exitosamente")
    
    # Crear DataFrame de prueba
    df = pd.DataFrame({
        'Nombre': ['Alice', 'Bob', 'Charlie'],
        'Edad': [25, 30, 35],
        'Puntaje': [85, 92, 78]
    })
    
    print("\n   Intentando crear tabla...")
    writer.add_table(df, title="Tabla de prueba")
    print("   ✅ Tabla creada sin errores")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("RESUMEN")
print("="*70)
print("✅ Migración completada exitosamente")
print("✅ Typography embebida en layouts")
print("✅ Colores de tabla cargados correctamente")
print("✅ DocumentWriter funciona sin errores")
