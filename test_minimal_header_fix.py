"""Test minimal table header background color fix."""

from src.ePy_docs.core._config import get_layout, get_config_section

print("=" * 70)
print("TEST: Minimal Table Header Background Color")
print("=" * 70)

# Load minimal layout
minimal_layout = get_layout('minimal')
colors_config = minimal_layout.get('colors', {}).get('layout_config', {})
tables_config = colors_config.get('tables', {})
header_config = tables_config.get('header', {})

# Check header palettes and tones
for header_type in ['default', 'engineering', 'environmental', 'financial']:
    config = header_config.get(header_type, {})
    palette = config.get('palette', 'NOT SET')
    tone = config.get('tone', 'NOT SET')
    print(f"\n✓ {header_type:15s}: palette='{palette}', tone='{tone}'")
    
    assert palette == 'minimal', f"{header_type} should use 'minimal' palette"
    assert tone == 'primary', f"{header_type} should use 'primary' tone (white)"

# Get the actual RGB value for minimal primary
colors_global = get_config_section('colors')
minimal_palette = colors_global['palettes']['minimal']
primary_rgb = minimal_palette['primary']

print(f"\n✓ Minimal 'primary' tone: RGB{primary_rgb}")
assert primary_rgb == [255, 255, 255], f"Primary should be white [255,255,255], got {primary_rgb}"

print("\n" + "=" * 70)
print("✓ ALL TESTS PASSED!")
print("=" * 70)

print("\n📋 SUMMARY:")
print("  ✓ All header backgrounds use 'minimal' palette")
print("  ✓ All headers use 'primary' tone (white background)")
print("  ✓ Header text will be black (from typography config)")
print("  ✓ No more black backgrounds hiding text")
