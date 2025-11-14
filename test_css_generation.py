#!/usr/bin/env python3
"""
Test para verificar que generate_css incluya fuentes personalizadas.
"""

from src.ePy_docs.core._html import generate_css

def test_css_generation_with_fonts():
    """Test para verificar que generate_css incluya fuentes."""
    print("🔍 Probando generación de CSS con fuentes...")
    
    layouts = ['handwritten', 'corporate', 'classic']
    
    for layout in layouts:
        print(f"\n--- Layout: {layout} ---")
        try:
            css_content = generate_css(layout)
            
            if '@font-face' in css_content:
                print("✅ CSS contiene @font-face")
                # Extract @font-face section
                lines = css_content.split('\n')
                in_font_face = False
                for line in lines:
                    if '@font-face' in line:
                        in_font_face = True
                    if in_font_face:
                        print(f"   {line}")
                        if '}' in line and 'font-face' not in line:
                            in_font_face = False
                            break
            else:
                print("⚠️  CSS no contiene @font-face")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Generación de CSS con fuentes")
    print("=" * 60)
    
    test_css_generation_with_fonts()