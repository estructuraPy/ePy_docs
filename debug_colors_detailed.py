import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.core._config import get_loader

# Test with detailed debugging
loader = get_loader()

print("=== Debug get_layout_colors ===")

# Load the corporate layout
layout = loader.load_layout('corporate')
print(f"Layout loaded: {layout.get('layout_name', 'UNKNOWN')}")

# Check colors config
colors_config = layout.get('colors', {}).get('layout_config', {})
print(f"Colors config: {colors_config}")

default_palette = colors_config.get('default_palette', 'academic')
print(f"Default palette: {default_palette}")

# Load complete config for palettes
complete_config = loader.load_complete_config('corporate')
palettes = complete_config.get('colors', {}).get('palettes', {})
print(f"Available palettes: {list(palettes.keys())}")

if default_palette in palettes:
    palette = palettes[default_palette]
    print(f"Corporate palette: {palette}")
else:
    print(f"ERROR: Default palette '{default_palette}' not found in palettes!")

# Test the actual function
colors = loader.get_layout_colors('corporate')
print(f"\nFinal colors: {colors}")