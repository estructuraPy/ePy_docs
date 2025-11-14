#!/usr/bin/env python3
"""
Debug CSS font generation
"""

from src.ePy_docs.core._html import generate_css
from src.ePy_docs.core._config import load_layout, get_config_section

print("=== DEBUG CSS FONT GENERATION ===")

# Test layout loading
layout_name = "handwritten"
print(f"\n1. Loading layout: {layout_name}")
layout = load_layout(layout_name, resolve_refs=True)
print(f"Layout loaded: {layout is not None}")

font_family_key = layout.get('font_family_ref', 'NOT_FOUND')
print(f"Font family key from layout: {font_family_key}")

# Test text config
print(f"\n2. Loading text config")
text_config = get_config_section('text')
print(f"Text config keys: {list(text_config.keys()) if text_config else 'None'}")
print(f"Text config type: {type(text_config)}")

if text_config and 'shared_defaults' in text_config:
    shared_defaults = text_config['shared_defaults']
    font_families = shared_defaults.get('font_families', {})
    print(f"Font families in shared_defaults: {list(font_families.keys())}")
else:
    font_families = text_config.get('font_families', {}) if text_config else {}
    print(f"Font families directly: {list(font_families.keys())}")

print(f"Available font families: {list(font_families.keys())}")

if font_family_key in font_families:
    font_config = font_families[font_family_key]
    primary_font = font_config.get('primary')
    fallback_font = font_config.get('fallback')
    print(f"Primary font: {primary_font}")
    print(f"Fallback font: {fallback_font}")
else:
    print("❌ Font family key not found in font_families")

# Test CSS generation
print(f"\n3. Testing CSS generation")
css_content = generate_css(layout_name)
print(f"CSS generated: {len(css_content)} characters")

# Look for font-family in body
import re
body_match = re.search(r'body\s*{[^}]*font-family:\s*([^;]+);', css_content, re.DOTALL)
if body_match:
    font_family_value = body_match.group(1).strip()
    print(f"Font family in CSS body: {font_family_value}")
else:
    print("❌ No font-family found in body CSS")

print("\n=== END DEBUG ===")