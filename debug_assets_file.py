import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.core._config import get_loader

# Test with detailed debugging
loader = get_loader()

print(f"Config dir: {loader.config_dir}")
print(f"Assets path: {loader.config_dir / 'assets.epyson'}")
print(f"Assets exists: {os.path.exists(loader.config_dir / 'assets.epyson')}")

# Check what files are in config dir
config_files = list(loader.config_dir.glob('*.epyson'))
print(f"Config files: {[f.name for f in config_files]}")

# Try to load assets directly
try:
    external_path = loader.config_dir / "assets.epyson"
    print(f"Trying to load: {external_path}")
    with open(external_path, 'r', encoding='utf-8') as f:
        import json
        content = f.read()
        print(f"File content length: {len(content)}")
        # Try to parse JSON
        data = json.loads(content)
        print(f"JSON parsed successfully")
        print(f"Keys: {list(data.keys())}")
        if "palettes" in data:
            palettes = data["palettes"]
            print(f"Palettes: {list(palettes.keys())}")
        else:
            print("No palettes in JSON")
except Exception as e:
    print(f"Error loading file: {e}")