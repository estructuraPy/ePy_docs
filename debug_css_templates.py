import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ePy_docs.core._config import get_config_section

# Debug HTML config section
html_config = get_config_section('html')
print("HTML config keys:", list(html_config.keys()))

css_templates = html_config.get('css_templates', {})
print("CSS templates keys:", list(css_templates.keys()))

for key, template in css_templates.items():
    print(f"\n{key}:")
    print(f"  {template[:100]}..." if len(template) > 100 else f"  {template}")