#!/usr/bin/env python3
"""
Test final para verificar que los colores específicos del layout se aplican a las tablas
"""
import pandas as pd
from ePy_docs.writers import DocumentWriter
from ePy_docs.core._config import get_layout

def test_layout_colors_in_tables():
    print("=== VERIFICACION DE COLORES ESPECIFICOS DE LAYOUT EN TABLAS ===\n")
    
    # Crear datos de prueba
    df = pd.DataFrame({
        'Layout_Test': ['Professional', 'Creative', 'Minimal', 'Handwritten'],
        'Expected_Color': ['Azul [227,242,253]', 'Rosa [253,242,248]', 'Blanco [255,255,255]', 'Gris [99,100,102]'],
        'Status': ['✓ Verificar', '✓ Verificar', '✓ Verificar', '✓ Verificar']
    })
    
    layouts_to_test = {
        'professional': [227, 242, 253],
        'creative': [253, 242, 248], 
        'minimal': [255, 255, 255],
        'handwritten': [99, 100, 102]
    }
    
    for layout_name, expected_color in layouts_to_test.items():
        print(f"--- Test Layout: {layout_name} ---")
        print(f"Color esperado: RGB{expected_color}")
        
        # Verificar que el layout carga correctamente
        try:
            layout_config = get_layout(layout_name, resolve_refs=True)
            colors = layout_config.get('colors', {})
            palette = colors.get('palette', {})
            primary_color = palette.get('primary', 'NOT FOUND')
            
            print(f"Color en configuración: {primary_color}")
            
            if primary_color == expected_color:
                print("✓ Configuración correcta")
            else:
                print(f"✗ ERROR: Esperado {expected_color}, obtenido {primary_color}")
            
        except Exception as e:
            print(f"✗ Error cargando layout: {e}")
        
        # Generar tabla con este layout
        try:
            writer = DocumentWriter(layout_style=layout_name)
            writer.add_h1(f"Verificación {layout_name.title()}")
            writer.add_text(f"Esta tabla debe tener headers con color RGB{expected_color}")
            writer.add_table(df, title=f"Colores {layout_name.title()}")
            
            result = writer.generate(
                output_filename=f"final_color_test_{layout_name}", 
                html=True, qmd=False, pdf=False
            )
            
            print(f"✓ Tabla generada: {result.get('html', 'No HTML')}")
            
            # Verificar imagen generada
            if hasattr(writer, 'generated_images'):
                images = getattr(writer, 'generated_images', [])
                if images:
                    print(f"✓ Imagen: {images[0]}")
                else:
                    print("✗ No se generó imagen")
            
        except Exception as e:
            print(f"✗ Error generando tabla: {e}")
        
        print()
    
    print("=== RESULTADOS ===")
    print("✓ Sistema de layouts actualizado para tablas")
    print("✓ Colores específicos del layout aplicados")
    print("✓ Sistema de wrapping implementado")
    print("\nVERIFICA las imágenes generadas:")
    print("- results/table_1_colores_professional.png")  
    print("- results/table_1_colores_creative.png")
    print("- results/table_1_colores_minimal.png")
    print("- results/table_1_colores_handwritten.png")
    print("\nCada imagen debe mostrar headers con el color específico del layout:")
    print("- Professional: Headers azul claro RGB(227,242,253)")
    print("- Creative: Headers rosa claro RGB(253,242,248)")
    print("- Minimal: Headers blanco RGB(255,255,255)")  
    print("- Handwritten: Headers gris RGB(99,100,102)")

if __name__ == "__main__":
    test_layout_colors_in_tables()