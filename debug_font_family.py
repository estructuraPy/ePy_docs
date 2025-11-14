#!/usr/bin/env python3
"""
Test específico para debuggear la resolución de font_family_ref.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def debug_font_family_resolution():
    """Debug específico para resolución de font_family."""
    print("🔍 Debuggeando resolución de font_family...")
    
    loader = ModularConfigLoader()
    
    # Step 1: Load raw layout
    print("\n1. Layout raw:")
    layout = loader.load_layout('handwritten')
    print(f"   font_family_ref: {layout.get('font_family_ref')}")
    print(f"   tiene 'text' section: {'text' in layout}")
    
    # Step 2: Check _merge_layout_config output
    print("\n2. Testing _merge_layout_config:")
    master = loader.load_master()
    layout_merged = loader._merge_layout_config(layout, 'handwritten', master)
    
    text_section = layout_merged.get('text', {})
    print(f"   text section: {text_section}")
    print(f"   font_family in text: {text_section.get('font_family')}")
    
    # Step 3: Check complete config
    print("\n3. Testing complete config:")
    complete = loader.load_complete_config('handwritten')
    complete_layout = complete.get('layout', {})
    complete_text = complete_layout.get('text', {})
    print(f"   complete layout.text: {complete_text}")
    print(f"   complete font_family: {complete_text.get('font_family')}")

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG: Resolución de font_family")
    print("=" * 60)
    
    debug_font_family_resolution()