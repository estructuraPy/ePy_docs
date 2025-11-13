"""
Test script to verify complete corporate layout with:
- Helvetica font from external path
- Corporate color palette for headings H1-H6
"""

from ePy_docs.core._config import get_loader, get_font_latex_config, get_layout_colors
from pathlib import Path

print("=" * 70)
print("Testing Corporate Layout - Complete Configuration")
print("=" * 70)

loader = get_loader()

# Test 1: Font configuration
print("\n📝 1. Font Configuration (Helvetica from Dropbox):")
print("-" * 70)
font_config = get_font_latex_config('corporate', fonts_dir=Path.cwd())
print(font_config)

# Test 2: Color palette
print("\n🎨 2. Color Palette Configuration:")
print("-" * 70)
colors = get_layout_colors('corporate')
print(f"Primary (H1):     {colors['primary']}")
print(f"Secondary (H2):   {colors['secondary']}")
print(f"Tertiary (H3):    {colors['tertiary']}")
print(f"Quaternary (H4+): {colors['quaternary']}")
print(f"Background:       {colors['background']}")

# Test 3: Get palette RGB values
print("\n🔍 3. Expected RGB Values from Palette:")
print("-" * 70)
complete_config = loader.load_complete_config('corporate')
corporate_palette = complete_config.get('colors', {}).get('palettes', {}).get('corporate', {})
print(f"Primary:     RGB({corporate_palette.get('primary', [])})")
print(f"Secondary:   RGB({corporate_palette.get('secondary', [])})")
print(f"Tertiary:    RGB({corporate_palette.get('tertiary', [])})")
print(f"Quaternary:  RGB({corporate_palette.get('quaternary', [])})")
print(f"Quinary:     RGB({corporate_palette.get('quinary', [])}) - for table alt rows")
print(f"Senary:      RGB({corporate_palette.get('senary', [])}) - for table headers")

# Test 4: Font file verification
print("\n✓ 4. Font File Verification:")
print("-" * 70)

# Load assets directly to get font configuration
import json
assets_path = Path('src/ePy_docs/config/assets.epyson')
with open(assets_path, 'r', encoding='utf-8') as f:
    assets_data = json.load(f)

brand_font = assets_data.get('font_families', {}).get('brand', {})
font_path = brand_font.get('font_path', '')  # Will be empty for package fonts
font_name = brand_font.get('primary', '')
font_template = brand_font.get('font_file_template', '')

# Build filename correctly
if '{font_name}' in font_template:
    font_filename = font_template.replace('{font_name}', font_name)
else:
    font_filename = font_template

# For package fonts, get the actual path from the loader
if not font_path:  # Package internal font
    try:
        package_font_path = loader.get_font_path(font_filename)
        full_path = package_font_path
        font_directory = str(package_font_path.parent)  
    except FileNotFoundError:
        full_path = Path(font_filename)
        font_directory = "Package fonts directory"
else:
    # External font path
    full_path = Path(font_path) / font_filename
    font_directory = font_path

print(f"Font directory: {font_directory}")
print(f"Font filename:  {font_filename}")
print(f"Full path:      {full_path}")
print(f"File exists:    {full_path.exists()}")

# Test 5: Verification checks
print("\n✅ 5. Configuration Checks:")
print("-" * 70)
checks = {
    "Font is in package": not bool(font_path),  # Empty font_path means package font
    "Font filename has underscores": '_' in font_filename,
    "Font extension is .OTF": font_filename.endswith('.OTF'),
    "Primary color is crimson (198,18,60)": corporate_palette.get('primary') == [198, 18, 60],
    "Secondary color is navy (0,33,126)": corporate_palette.get('secondary') == [0, 33, 126],
    "Tertiary color is gray (99,100,102)": corporate_palette.get('tertiary') == [99, 100, 102],
    "Quaternary color is black (0,0,0)": corporate_palette.get('quaternary') == [0, 0, 0],
    "Font file exists": full_path.exists()
}

for check, result in checks.items():
    status = "✅" if result else "❌"
    print(f"  {status} {check}: {result}")

print("\n" + "=" * 70)
print("Expected heading colors:")
print("  H1 (section):        RGB(198, 18, 60) - Crimson")
print("  H2 (subsection):     RGB(0, 33, 126)  - Navy Blue")
print("  H3 (subsubsection):  RGB(99, 100, 102) - Gray")
print("  H4-H6 (paragraph):   RGB(0, 0, 0)     - Black")
print("=" * 70)
