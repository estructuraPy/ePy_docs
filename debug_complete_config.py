import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.core._config import get_loader

# Test with detailed debugging
loader = get_loader()

print("=== Debug load_complete_config ===")

# Load assets directly
try:
    assets_data = loader.load_external("assets")
    print(f"Assets loaded successfully")
    print(f"Assets keys: {list(assets_data.keys())}")
    if "palettes" in assets_data:
        palettes = assets_data["palettes"]
        print(f"Palettes in assets: {list(palettes.keys())}")
        if "corporate" in palettes:
            print(f"Corporate palette: {palettes['corporate']}")
        else:
            print("ERROR: 'corporate' palette not found in assets!")
    else:
        print("ERROR: No 'palettes' in assets data!")
except Exception as e:
    print(f"ERROR loading assets: {e}")

print("\n=== Debug complete_config ===")
# Load complete config
complete_config = loader.load_complete_config('corporate')
print(f"Complete config keys: {list(complete_config.keys())}")
if "colors" in complete_config:
    colors = complete_config["colors"]
    print(f"Colors keys: {list(colors.keys())}")
    if "palettes" in colors:
        palettes = colors["palettes"]
        print(f"Palettes in complete config: {list(palettes.keys())}")
    else:
        print("ERROR: No palettes in complete config colors!")
else:
    print("ERROR: No colors in complete config!")