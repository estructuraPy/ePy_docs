#!/usr/bin/env python3
"""
Test para verificar si se puede cargar la configuración de texto directamente.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def test_direct_text_loading():
    """Test para cargar configuración de texto directamente."""
    print("🔍 Intentando cargar configuración de texto directamente...")
    
    loader = ModularConfigLoader()
    
    try:
        # Try loading text config directly
        text_config = loader.load_external('text')
        print("✅ Configuración de texto cargada directamente")
        print(f"📄 Keys: {list(text_config.keys())}")
        
        if 'shared_defaults' in text_config:
            shared = text_config['shared_defaults']
            print(f"📚 shared_defaults keys: {list(shared.keys())}")
            
            if 'font_families' in shared:
                font_families = shared['font_families']
                print(f"🎨 Font families: {list(font_families.keys())}")
                
                if 'handwritten_personal' in font_families:
                    hp = font_families['handwritten_personal']
                    print(f"✍️ handwritten_personal: {hp}")
        
    except Exception as e:
        print(f"❌ Error cargando texto: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Carga directa de configuración de texto")
    print("=" * 60)
    
    test_direct_text_loading()