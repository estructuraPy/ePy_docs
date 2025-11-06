#!/usr/bin/env python3
"""
Test rápido de los nuevos métodos estáticos de DocumentWriter
"""

from src.ePy_docs.writers import DocumentWriter
import pandas as pd

def test_new_static_methods():
    """Test de los nuevos métodos estáticos"""
    print("=== TESTING NEW STATIC METHODS ===")
    
    # Test get_available_document_types
    print("\n1. Testing get_available_document_types()")
    doc_types = DocumentWriter.get_available_document_types()
    assert isinstance(doc_types, dict)
    assert len(doc_types) > 0
    assert 'paper' in doc_types
    assert 'report' in doc_types
    print(f"   ✓ Found {len(doc_types)} document types: {list(doc_types.keys())}")
    
    # Test get_available_layouts
    print("\n2. Testing get_available_layouts()")
    layouts = DocumentWriter.get_available_layouts()
    assert isinstance(layouts, dict)
    assert len(layouts) > 0
    assert 'creative' in layouts
    assert 'professional' in layouts
    print(f"   ✓ Found {len(layouts)} layouts: {list(layouts.keys())}")
    
    # Test get_available_palettes
    print("\n3. Testing get_available_palettes()")
    palettes = DocumentWriter.get_available_palettes()
    assert isinstance(palettes, dict)
    assert len(palettes) > 0
    assert 'reds' in palettes
    assert 'blues' in palettes
    print(f"   ✓ Found {len(palettes)} palettes including: reds, blues, greens, oranges, purples")
    
    print("\n✓ All new static methods work correctly!")

def test_palette_name_parameter():
    """Test del parámetro palette_name en add_colored_table"""
    print("\n=== TESTING PALETTE_NAME PARAMETER ===")
    
    # Crear datos de prueba
    df = pd.DataFrame({
        'Esfuerzo': [100, 200, 300, 400, 500],
        'Deformación': [0.001, 0.002, 0.003, 0.004, 0.005],
        'Tipo': ['A', 'B', 'C', 'D', 'E']
    })
    
    # Crear writer
    writer = DocumentWriter(document_type='report', layout_style='professional')
    
    # Test con palette_name (correcto)
    try:
        writer.add_colored_table(
            df,
            title="Tabla con palette_name correcto",
            show_figure=False,  # No mostrar en test
            palette_name='reds',  # Parámetro correcto
            highlight_columns=['Esfuerzo', 'Deformación']
        )
        print("   ✓ palette_name='reds' funciona correctamente")
    except Exception as e:
        print(f"   ✗ Error con palette_name: {e}")
        raise
    
    # Test que pallete_name (incorrecto) falle
    try:
        writer.add_colored_table(
            df,
            title="Tabla con pallete_name incorrecto",
            show_figure=False,
            pallete_name='blues'  # Parámetro incorrecto
        )
        print("   ✗ pallete_name NO debería funcionar")
        assert False, "pallete_name no debería ser aceptado"
    except TypeError as e:
        if "unexpected keyword argument 'pallete_name'" in str(e):
            print("   ✓ pallete_name correctamente rechazado (TypeError esperado)")
        else:
            raise
    
    print("\n✓ Parameter palette_name works correctly!")

def show_usage_examples():
    """Mostrar ejemplos de uso"""
    print("\n=== USAGE EXAMPLES ===")
    
    print("\n1. Ver tipos de documento disponibles:")
    print("   doc_types = DocumentWriter.get_available_document_types()")
    doc_types = DocumentWriter.get_available_document_types()
    for name, desc in list(doc_types.items())[:3]:
        print(f"   {name}: {desc}")
    
    print("\n2. Ver layouts disponibles:")
    print("   layouts = DocumentWriter.get_available_layouts()")
    layouts = DocumentWriter.get_available_layouts()
    for name, desc in list(layouts.items())[:3]:
        print(f"   {name}: {desc[:50]}...")
    
    print("\n3. Ver paletas disponibles:")
    print("   palettes = DocumentWriter.get_available_palettes()")
    palettes = DocumentWriter.get_available_palettes()
    color_palettes = [name for name in palettes.keys() if name in ['blues', 'reds', 'greens', 'oranges', 'purples']]
    print(f"   Principales: {', '.join(color_palettes)}")
    
    print("\n4. Uso correcto de add_colored_table:")
    print("   writer.add_colored_table(")
    print("       df,")
    print("       title='Tabla de Esfuerzos',")
    print("       palette_name='reds',  # ← Correcto: una 'l'")
    print("       highlight_columns=['Esfuerzo', 'Deformación']")
    print("   )")

if __name__ == "__main__":
    test_new_static_methods()
    test_palette_name_parameter() 
    show_usage_examples()
    print("\n🎉 All tests passed! New methods are working correctly.")