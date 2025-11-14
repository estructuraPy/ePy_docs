#!/usr/bin/env python3
"""
Test para verificar la generación de CSS de fuentes.
"""

from src.ePy_docs.core._config import get_font_css_config

def test_font_css_generation():
    """Test para verificar si se genera CSS para fuentes personalizadas."""
    print("🔍 Verificando generación de CSS para fuentes...")
    
    layouts = ['handwritten', 'corporate', 'classic']
    
    for layout in layouts:
        print(f"\n--- Layout: {layout} ---")
        try:
            css_config = get_font_css_config(layout)
            
            if css_config.strip():
                print("✅ CSS generado:")
                print(css_config)
                
                # Check for custom font references
                if 'anm_ingenieria_2025' in css_config:
                    print("🎯 Incluye fuente personalizada anm_ingenieria_2025")
                if 'helvetica' in css_config.lower():
                    print("🎯 Incluye fuente helvetica")
                    
            else:
                print("⚠️  No se generó CSS personalizado")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Generación de CSS para fuentes")
    print("=" * 60)
    
    test_font_css_generation()