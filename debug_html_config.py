import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.core._config import get_loader

# Test HTML config loading
loader = get_loader()

try:
    html_path = loader.config_dir / 'html.epyson'
    print(f"HTML config path: {html_path}")
    print(f"HTML config exists: {os.path.exists(html_path)}")
    
    with open(html_path, 'r', encoding='utf-8') as f:
        import json
        content = f.read()
        print(f"File content length: {len(content)}")
        
        # Try to parse JSON
        data = json.loads(content)
        print(f"JSON parsed successfully")
        print(f"Keys: {list(data.keys())}")
        
        if "css_templates" in data:
            css_templates = data["css_templates"]
            print(f"CSS templates keys: {list(css_templates.keys())}")
        else:
            print("No css_templates in JSON")
            
except Exception as e:
    print(f"Error loading HTML config: {e}")

# Also test via get_config_section
print("\n=== Testing get_config_section ===")
try:
    html_config = loader.get_config_section('html')
    print(f"HTML config via loader: {list(html_config.keys())}")
except Exception as e:
    print(f"Error with get_config_section: {e}")