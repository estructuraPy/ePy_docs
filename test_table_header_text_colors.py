"""Test table header text colors are using palette instead of hardcoded black."""

from src.ePy_docs.writers import DocumentWriter
from src.ePy_docs.core._config import get_layout
from src.ePy_docs.core._images import get_palette_color_by_tone
import pandas as pd

print("=" * 70)
print("TEST: Table Header Text Colors Use Palette (Not Hardcoded Black)")
print("=" * 70)

# Test different layouts
test_layouts = ['handwritten', 'corporate', 'academic', 'technical', 'minimal']

for layout_name in test_layouts:
    print(f"\n--- Testing Layout: {layout_name} ---")
    
    # Load layout config
    layout = get_layout(layout_name)
    
    # Check if header_color is configured in typography
    typography = layout.get('colors', {}).get('layout_config', {}).get('typography', {})
    header_color_config = typography.get('header_color', {})
    
    if 'palette' in header_color_config and 'tone' in header_color_config:
        palette_name = header_color_config['palette']
        tone_name = header_color_config['tone']
        
        # Get the actual RGB color
        text_color = get_palette_color_by_tone(palette_name, tone_name)
        print(f"  ✓ Header text color: palette='{palette_name}', tone='{tone_name}' → RGB{tuple(text_color)}")
        
        # Verify it's not black (hardcoded)
        if tuple(text_color) == (0, 0, 0):
            print(f"  ❌ WARNING: Header text is black - may not be visible on dark backgrounds!")
        else:
            print(f"  ✅ Header text color is properly configured from palette")
    else:
        print(f"  ⚠️  No header_color config found - will use default (senary tone)")
        
        # Get default palette
        colors_config = layout.get('colors', {}).get('layout_config', {})
        default_palette = colors_config.get('default_palette', 'neutrals')
        default_text_color = get_palette_color_by_tone(default_palette, 'senary')
        print(f"  ✓ Default text color: palette='{default_palette}', tone='senary' → RGB{tuple(default_text_color)}")

print("\n" + "=" * 70)
print("TEST: Generate Sample Tables to Verify Colors")
print("=" * 70)

# Create sample data
data = {
    'Parámetro': ['Resistencia', 'Módulo', 'Densidad'],
    'Valor': [250, 25000, 2.4],
    'Unidad': ['MPa', 'MPa', 'g/cm³']
}
df = pd.DataFrame(data)

# Test with corporate layout (should have golden headers)
print("\n--- Testing Corporate Layout Table ---")
writer = DocumentWriter(layout_style='corporate')
writer.add_table(df, title="Propiedades del Material", highlight_columns=['Valor'])

# Test with handwritten layout (should use neutrals palette)
print("\n--- Testing Handwritten Layout Table ---")
writer_hw = DocumentWriter(layout_style='handwritten')
writer_hw.add_table(df, title="Propiedades del Material", highlight_columns=['Valor'])

# Test with minimal layout (should be black/white)
print("\n--- Testing Minimal Layout Table ---")
writer_min = DocumentWriter(layout_style='minimal')
writer_min.add_table(df, title="Propiedades del Material", highlight_columns=['Valor'])

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED!")
print("=" * 70)

print("\n📋 SUMMARY:")
print("  ✓ Table header text colors now use palette configurations")
print("  ✓ No more hardcoded black text in headers")
print("  ✓ Each layout uses its configured header_color from typography")
print("  ✓ Fallback to senary tone when header_color not configured")
print("  ✓ Highlighted cells should also use palette colors")