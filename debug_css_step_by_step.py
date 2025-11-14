#!/usr/bin/env python3
"""
Debug detallado de get_font_css_config.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def debug_css_config_step_by_step():
    """Debug paso a paso de get_font_css_config."""
    print("🔍 Debuggeando get_font_css_config...")
    
    loader = ModularConfigLoader()
    layout_name = 'handwritten'
    
    print(f"\n1. Cargando configuración completa para {layout_name}...")
    complete_config = loader.load_complete_config(layout_name)
    
    print(f"2. Verificando layout config...")
    layout_config = complete_config.get('layout', {})
    text_config = layout_config.get('text', {})
    font_family_key = text_config.get('font_family', 'sans_technical')
    print(f"   font_family_key: {font_family_key}")
    
    print(f"3. Verificando shared_defaults...")
    shared_defaults = complete_config.get('shared_defaults', {})
    font_families = shared_defaults.get('font_families', {})
    print(f"   font_families keys: {list(font_families.keys())}")
    
    print(f"4. Verificando si {font_family_key} está en font_families...")
    if font_family_key in font_families:
        font_config = font_families[font_family_key]
        print(f"   ✅ Font config encontrado: {font_config}")
        
        primary_font = font_config.get('primary', '')
        print(f"   primary_font: {primary_font}")
        
        if 'font_file_template' in font_config:
            print(f"   ✅ Tiene font_file_template: {font_config['font_file_template']}")
            font_file_template = font_config['font_file_template']
            font_filename = font_file_template.format(font_name=primary_font)
            print(f"   font_filename: {font_filename}")
            
            # Try to find the font file
            try:
                font_path = loader.get_font_path(font_filename)
                print(f"   ✅ Font file found: {font_path}")
                
                # Generate CSS
                css = f"""
@font-face {{
    font-family: '{primary_font}';
    src: url('fonts/{font_filename}') format('opentype');
    font-weight: normal;
    font-style: normal;
}}
"""
                print(f"   CSS generado:")
                print(css)
                
            except FileNotFoundError as e:
                print(f"   ❌ Font file not found: {e}")
        else:
            print(f"   ⚠️  No tiene font_file_template")
    else:
        print(f"   ❌ {font_family_key} no está en font_families")

if __name__ == "__main__":
    print("=" * 60)
    print("DEBUG: get_font_css_config paso a paso")
    print("=" * 60)
    
    debug_css_config_step_by_step()