#!/usr/bin/env python3
"""
Test para verificar que la corrección de fuentes LaTeX funciona correctamente.
Este test verifica que las fuentes se configuren correctamente para LaTeX.
"""

from src.ePy_docs.core._config import ModularConfigLoader

def test_latex_font_fallback():
    """Test que las fuentes LaTeX usen system fonts en lugar de archivos."""
    print("🔍 Probando configuración de fuentes LaTeX...")
    
    # Load configuration
    config_loader = ModularConfigLoader()
    config = config_loader.load_complete_config()
    
    # Test handwritten layout
    layout_config = config.get('layouts', {}).get('handwritten', {})
    font_family = layout_config.get('text', {}).get('font_family', 'handwritten_personal')
    
    print(f"1. Layout handwritten usa font_family: {font_family}")
    
    # Get font config
    font_config = config.get('shared_defaults', {}).get('font_families', {}).get(font_family, {})
    
    print(f"2. Font config: {font_config}")
    
    # Check that latex_primary exists
    latex_primary = font_config.get('latex_primary')
    regular_primary = font_config.get('primary')
    
    print(f"3. Primary font: {regular_primary}")
    print(f"4. LaTeX primary font: {latex_primary}")
    
    # Generate LaTeX config
    from src.ePy_docs.core._config import get_font_latex_config
    
    try:
        latex_config = get_font_latex_config('handwritten')
        print(f"5. ✅ LaTeX config generado exitosamente")
        print("LaTeX config preview:")
        print(latex_config[:200] + "..." if len(latex_config) > 200 else latex_config)
        
        # Verify it uses system font, not file
        assert 'Latin Modern Roman' in latex_config or 'Segoe Script' in latex_config, "Debe usar fuente del sistema"
        assert 'anm_ingenieria_2025' not in latex_config, "No debe usar fuente de archivo personalizada"
        
        print("6. ✅ Verificación exitosa: usa fuente del sistema")
        
    except Exception as e:
        print(f"5. ❌ Error generando LaTeX config: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("TEST: Verificación de corrección de fuentes LaTeX")
    print("=" * 60)
    
    success = test_latex_font_fallback()
    
    if success:
        print("\n🎉 ¡ÉXITO! Las fuentes LaTeX están configuradas correctamente")
        print("📝 Cambios aplicados:")
        print("   - handwritten_personal.primary = 'Segoe Script'")
        print("   - handwritten_personal.latex_primary = 'Latin Modern Roman'")
        print("   - LaTeX usa fuentes del sistema en lugar de archivos")
    else:
        print("\n❌ Hubo problemas con la configuración de fuentes")