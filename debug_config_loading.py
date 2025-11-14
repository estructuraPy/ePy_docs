#!/usr/bin/env python3
"""
Test para debuggear la carga de configuración paso a paso.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def debug_config_loading():
    """Debug paso a paso de la carga de configuración."""
    print("🔍 Debuggeando carga de configuración...")
    
    loader = ModularConfigLoader()
    
    # Step 1: Load layout
    print("\n1. Cargando layout handwritten...")
    layout = loader.load_layout('handwritten')
    print(f"   Keys: {list(layout.keys())}")
    print(f"   font_family_ref: {layout.get('font_family_ref')}")
    
    # Step 2: Load master config
    print("\n2. Cargando configuración master...")
    master = loader.load_master()
    print(f"   Keys: {list(master.keys())}")
    
    # Step 3: Check if text config is loaded
    if 'shared_defaults' in master:
        shared = master['shared_defaults']
        print(f"   shared_defaults keys: {list(shared.keys())}")
        
        if 'font_families' in shared:
            font_families = shared['font_families']
            print(f"   font_families keys: {list(font_families.keys())}")
            
            if 'handwritten_personal' in font_families:
                hp_config = font_families['handwritten_personal']
                print(f"   handwritten_personal config: {hp_config}")
    
    # Step 4: Try complete config loading
    print("\n3. Cargando configuración completa...")
    complete = loader.load_complete_config('handwritten')
    
    print(f"   complete config keys: {list(complete.keys())}")
    
    # Check shared_defaults
    if 'shared_defaults' in complete:
        shared = complete['shared_defaults']
        print(f"   shared_defaults loaded: {list(shared.keys())}")
        if 'font_families' in shared:
            print(f"   font_families available: {list(shared['font_families'].keys())}")
    
    # Check the resolution process
    if 'layout' in complete:
        layout_resolved = complete['layout']
        text_config = layout_resolved.get('text', {})
        print(f"   layout.text keys: {list(text_config.keys())}")
        print(f"   layout.text.font_family: {text_config.get('font_family')}")

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG: Carga de configuración paso a paso")
    print("=" * 60)
    
    debug_config_loading()