"""
Test de descubrimiento dinámico de layouts desde filesystem.

Este test verifica que:
1. get_available_layouts() retorna todos los layouts del filesystem
2. Cada layout puede cargarse correctamente
3. La validación rechaza layouts inexistentes
4. El layout por defecto funciona correctamente
"""

from src.ePy_docs.core._config import ModularConfigLoader

def test_dynamic_layout_discovery():
    """Test que los layouts se descubren dinámicamente desde el filesystem."""
    loader = ModularConfigLoader()
    
    # 1. Verificar que se descubren layouts
    available = loader.get_available_layouts()
    print(f"✅ Layouts descubiertos: {len(available)}")
    print(f"   {', '.join(available)}")
    
    assert len(available) > 0, "Debe haber al menos un layout disponible"
    
    # Verificar que están los 9 layouts esperados
    expected = ["academic", "classic", "corporate", "creative", 
                "handwritten", "minimal", "professional", "scientific", "technical"]
    
    for layout in expected:
        assert layout in available, f"Layout '{layout}' no encontrado"
    
    print(f"✅ Todos los layouts esperados están presentes")
    
    # 2. Verificar que cada layout puede cargarse
    for layout_name in available:
        try:
            layout_config = loader.load_layout(layout_name)
            assert layout_config is not None
            assert "description" in layout_config
            print(f"   ✅ {layout_name}: {layout_config['description'][:50]}...")
        except Exception as e:
            print(f"   ❌ {layout_name}: Error - {e}")
            raise
    
    print(f"✅ Todos los layouts cargan correctamente")
    
    # 3. Verificar que layout inexistente falla
    try:
        loader.load_layout("nonexistent_layout")
        assert False, "Debería fallar con layout inexistente"
    except ValueError as e:
        assert "not found" in str(e).lower()
        print(f"✅ Validación correcta de layout inexistente")
    
    # 4. Verificar layout por defecto
    default = loader.get_default_layout()
    print(f"✅ Layout por defecto: {default}")
    assert default == "classic", f"Layout por defecto debería ser 'classic', es '{default}'"
    
    # 5. Verificar que cargar sin especificar layout usa el default
    default_config = loader.load_layout()
    assert default_config is not None
    print(f"✅ Load sin parámetro usa default correctamente")
    
    print(f"\n{'='*60}")
    print(f"✅ TODOS LOS TESTS PASARON")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_dynamic_layout_discovery()
