"""Test corporate layout color configuration."""

from src.ePy_docs.writers import DocumentWriter
from src.ePy_docs.core._config import get_loader

# Test 1: Verify palette colors
print("=" * 60)
print("TEST 1: Corporate Palette Colors")
print("=" * 60)

loader = get_loader()
complete_config = loader.load_complete_config('corporate')
corporate_palette = complete_config.get('format', {}).get('palettes', {}).get('corporate', {})

print("\nCorporate Palette:")
for key, value in corporate_palette.items():
    if isinstance(value, list):
        print(f"  {key:20s}: RGB{tuple(value)}")
    else:
        print(f"  {key:20s}: {value}")

# Test 2: Verify heading color mapping
print("\n" + "=" * 60)
print("TEST 2: Heading Color Mapping")
print("=" * 60)

layout = loader.load_layout('corporate')
typography = layout.get('colors', {}).get('layout_config', {}).get('typography', {})

for i in range(1, 7):
    h_key = f"h{i}"
    h_config = typography.get(h_key, {})
    tone = h_config.get('tone', 'N/A')
    palette_name = h_config.get('palette', 'N/A')
    if tone != 'N/A' and tone in corporate_palette:
        color = corporate_palette[tone]
        print(f"  h{i}: tone={tone:15s} → RGB{tuple(color)}")
    else:
        print(f"  h{i}: tone={tone:15s} → Color not mapped")

# Test 3: Verify table colors
print("\n" + "=" * 60)
print("TEST 3: Table Color Configuration")
print("=" * 60)

tables_config = layout.get('colors', {}).get('layout_config', {}).get('tables', {})

# Header color
header_config = tables_config.get('header', {}).get('default', {})
header_tone = header_config.get('tone', 'N/A')
if header_tone in corporate_palette:
    header_color = corporate_palette[header_tone]
    print(f"  Table Header: tone={header_tone:15s} → RGB{tuple(header_color)}")

# Alt row color
alt_row_config = tables_config.get('alt_row', {})
alt_row_tone = alt_row_config.get('tone', 'N/A')
if alt_row_tone in corporate_palette:
    alt_row_color = corporate_palette[alt_row_tone]
    print(f"  Alt Row:      tone={alt_row_tone:15s} → RGB{tuple(alt_row_color)}")

# Page background
page_bg = corporate_palette.get('page_background', [255, 255, 255])
print(f"  Page BG:      tone={'page_background':15s} → RGB{tuple(page_bg)}")

# Test 4: Generate sample document
print("\n" + "=" * 60)
print("TEST 4: Generating Sample Document")
print("=" * 60)

writer = DocumentWriter(layout_style='corporate')

# Add headings
writer.add_content("# Título Nivel 1 (H1)")
writer.add_content("Debe ser RGB(198, 18, 60) - carmesí\n")

writer.add_content("## Título Nivel 2 (H2)")
writer.add_content("Debe ser RGB(0, 33, 126) - azul marino\n")

writer.add_content("### Título Nivel 3 (H3)")
writer.add_content("Debe ser RGB(99, 100, 102) - gris medio\n")

writer.add_content("#### Título Nivel 4 (H4)")
writer.add_content("Debe ser RGB(0, 0, 0) - negro\n")

writer.add_content("##### Título Nivel 5 (H5)")
writer.add_content("Debe ser RGB(0, 0, 0) - negro\n")

writer.add_content("###### Título Nivel 6 (H6)")
writer.add_content("Debe ser RGB(0, 0, 0) - negro\n")

# Add table
writer.add_content("## Tabla de Prueba\n")

import pandas as pd
df = pd.DataFrame({
    'Elemento': ['Columna 1', 'Columna 2', 'Columna 3'],
    'Valor': [100, 200, 300],
    'Estado': ['OK', 'Pendiente', 'Revisión']
})

writer.add_table(df, title="Tabla con colores corporativos")

# Generate
result = writer.generate()
print(f"\n✅ Document generated!")
print(f"📄 QMD: {result.get('qmd')}")
print(f"📝 HTML: {result.get('html')}")

print("\n" + "=" * 60)
print("Expected Colors Summary:")
print("=" * 60)
print("  H1: RGB(198, 18, 60)   - carmesí")
print("  H2: RGB(0, 33, 126)    - azul marino")
print("  H3: RGB(99, 100, 102)  - gris medio")
print("  H4-H6: RGB(0, 0, 0)    - negro")
print("  Table Header: RGB(202, 154, 36)  - dorado")
print("  Table Alt Row: RGB(157, 159, 162) - gris claro")
print("  Page Background: RGB(255, 255, 255) - blanco")
print("=" * 60)
