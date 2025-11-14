#!/usr/bin/env python3
"""
Test para verificar la configuración completa del layout handwritten.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def test_layout_configuration():
    """Test para verificar la configuración del layout."""
    print("🔍 Verificando configuración del layout handwritten...")
    
    loader = ModularConfigLoader()
    
    try:
        # Load complete config
        complete_config = loader.load_complete_config('handwritten')
        
        print("📋 Configuración completa cargada")
        
        # Check layout configuration
        layout_config = complete_config.get('layout', {})
        print(f"📄 Layout config keys: {list(layout_config.keys())}")
        
        # Check font family
        font_family_key = layout_config.get('text', {}).get('font_family')
        print(f"🎨 Font family key: {font_family_key}")
        
        # Check shared defaults
        shared_defaults = complete_config.get('shared_defaults', {})
        font_families = shared_defaults.get('font_families', {})
        print(f"📚 Available font families: {list(font_families.keys())}")
        
        if font_family_key in font_families:
            font_config = font_families[font_family_key]
            print(f"🔧 Font config for {font_family_key}:")
            for key, value in font_config.items():
                print(f"   {key}: {value}")
                
            # Check if font file exists
            primary_font = font_config.get('primary')
            font_file_template = font_config.get('font_file_template')
            
            if primary_font and font_file_template:
                font_filename = font_file_template.format(font_name=primary_font)
                print(f"🔍 Looking for font file: {font_filename}")
                
                try:
                    font_path = loader.get_font_path(font_filename)
                    print(f"✅ Font file found: {font_path}")
                except Exception as e:
                    print(f"❌ Font file not found: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Configuración del layout handwritten")
    print("=" * 60)
    
    test_layout_configuration()