#!/usr/bin/env python3
"""
Test directo para verificar la configuración de fuentes LaTeX generada por el sistema.
"""

from src.ePy_docs.core._config import get_font_latex_config

def test_direct_latex_config():
    """Test directo de la configuración LaTeX para verificar fuentes."""
    print("🔍 Probando configuración LaTeX directa...")
    
    layouts_to_test = ['handwritten', 'corporate', 'classic']
    
    for layout in layouts_to_test:
        print(f"\n--- Layout: {layout} ---")
        try:
            latex_config = get_font_latex_config(layout)
            print(f"Configuración generada:")
            print(latex_config)
            
            # Check for problematic fonts
            if 'anm_ingenieria_2025' in latex_config:
                print("❌ Usa fuente personalizada problemática")
            else:
                print("✅ No usa fuente personalizada problemática")
            
            # Check for system fonts
            if any(font in latex_config for font in ['Latin Modern Roman', 'Segoe Script', 'Arial', 'Times']):
                print("✅ Usa fuente del sistema")
            else:
                print("⚠️  No se detectó fuente del sistema clara")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Configuración LaTeX directa")
    print("=" * 60)
    
    test_direct_latex_config()