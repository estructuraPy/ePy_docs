"""Simple test to verify corporate palette colors."""

import json

# Read assets.epyson directly
with open('src/ePy_docs/config/assets.epyson', 'r', encoding='utf-8') as f:
    assets = json.load(f)

corporate_palette = assets.get('palettes', {}).get('corporate', {})

print("=" * 60)
print("Corporate Palette Colors (from assets.epyson)")
print("=" * 60)

expected = {
    'page_background': (255, 255, 255),
    'primary': (198, 18, 60),
    'secondary': (0, 33, 126),
    'tertiary': (99, 100, 102),
    'quaternary': (0, 0, 0),
    'quinary': (157, 159, 162),
    'senary': (202, 154, 36)
}

print("\nActual values:")
for key, value in corporate_palette.items():
    if isinstance(value, list):
        color_tuple = tuple(value)
        print(f"  {key:20s}: RGB{color_tuple}")
        if key in expected and color_tuple == expected[key]:
            print(f"                        ✅ Correct")
        elif key in expected:
            print(f"                        ❌ Expected: RGB{expected[key]}")
    else:
        print(f"  {key:20s}: {value}")

# Read corporate layout
with open('src/ePy_docs/config/layouts/corporate.epyson', 'r', encoding='utf-8') as f:
    layout = json.load(f)

print("\n" + "=" * 60)
print("Heading Color Tones (from corporate.epyson)")
print("=" * 60)

typography = layout.get('colors', {}).get('layout_config', {}).get('typography', {})

heading_mapping = {
    'h1': ('primary', (198, 18, 60)),
    'h2': ('secondary', (0, 33, 126)),
    'h3': ('tertiary', (99, 100, 102)),
    'h4': ('quaternary', (0, 0, 0)),
    'h5': ('quaternary', (0, 0, 0)),
    'h6': ('quaternary', (0, 0, 0))
}

for heading, (expected_tone, expected_color) in heading_mapping.items():
    h_config = typography.get(heading, {})
    actual_tone = h_config.get('tone', 'N/A')
    
    if actual_tone == expected_tone:
        print(f"  {heading}: tone={actual_tone:15s} → RGB{expected_color} ✅")
    else:
        print(f"  {heading}: tone={actual_tone:15s} → Expected: {expected_tone} ❌")

# Table colors
print("\n" + "=" * 60)
print("Table Color Configuration")
print("=" * 60)

tables_config = layout.get('colors', {}).get('layout_config', {}).get('tables', {})

# Header
header_config = tables_config.get('header', {}).get('default', {})
header_tone = header_config.get('tone', 'N/A')
expected_header_tone = 'senary'
expected_header_color = (202, 154, 36)

if header_tone == expected_header_tone:
    print(f"  Table Header: tone={header_tone:15s} → RGB{expected_header_color} ✅")
else:
    print(f"  Table Header: tone={header_tone:15s} → Expected: {expected_header_tone} ❌")

# Alt row
alt_row_config = tables_config.get('alt_row', {})
alt_row_tone = alt_row_config.get('tone', 'N/A')
expected_alt_row_tone = 'quinary'
expected_alt_row_color = (157, 159, 162)

if alt_row_tone == expected_alt_row_tone:
    print(f"  Alt Row:      tone={alt_row_tone:15s} → RGB{expected_alt_row_color} ✅")
else:
    print(f"  Alt Row:      tone={alt_row_tone:15s} → Expected: {expected_alt_row_tone} ❌")

print("\n" + "=" * 60)
print("Summary - Expected Configuration")
print("=" * 60)
print("  H1: RGB(198, 18, 60)   - carmesí (primary)")
print("  H2: RGB(0, 33, 126)    - azul marino (secondary)")
print("  H3: RGB(99, 100, 102)  - gris medio (tertiary)")
print("  H4-H6: RGB(0, 0, 0)    - negro (quaternary)")
print("  Table Header: RGB(202, 154, 36)  - dorado (senary)")
print("  Table Alt Row: RGB(157, 159, 162) - gris claro (quinary)")
print("  Page Background: RGB(255, 255, 255) - blanco")
print("=" * 60)
