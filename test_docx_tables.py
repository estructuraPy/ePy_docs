#!/usr/bin/env python3
"""
Test para verificar generación DOCX con tablas como imágenes
"""
from ePy_docs.writers import DocumentWriter
import pandas as pd
import os

def test_docx_generation():
    print("=== TEST GENERACIÓN DOCX CON TABLAS ===\n")
    
    # Crear datos de prueba
    data = {
        'Columna_Larga_Para_Test_Wrap': ['Texto largo que debe hacer wrap', 'Otro texto', 'Tercero'],
        'Valores': [100, 200, 300],
        'Estado': ['Activo', 'Inactivo', 'Pendiente']
    }
    
    df = pd.DataFrame(data)
    
    # Test con handwritten para verificar colores
    print("--- Generando documento DOCX con tabla handwritten ---")
    writer = DocumentWriter(layout_style='handwritten')
    writer.add_h1("Test DOCX con Tabla")
    writer.add_text("Este documento contiene una tabla que debe aparecer como imagen en Word.")
    writer.add_text("La tabla debe tener headers grises [99,100,102] y texto bien envuelto.")
    writer.add_table(df, title="Tabla_Test_DOCX_Handwritten")
    writer.add_text("Fin del documento.")
    
    # Generar DOCX
    try:
        result = writer.generate(
            output_filename="test_docx_table", 
            html=False, 
            pdf=False, 
            qmd=True,
            docx=True
        )
        
        print(f"✓ Resultado generación: {result}")
        
        # Verificar archivos
        if 'docx' in result and result['docx']:
            docx_path = result['docx']
            print(f"✓ DOCX generado: {docx_path}")
            
            if os.path.exists(str(docx_path)):
                size = os.path.getsize(str(docx_path))
                print(f"✓ Archivo DOCX existe: {size} bytes")
            else:
                print(f"✗ Archivo DOCX no encontrado: {docx_path}")
        else:
            print("✗ No se generó archivo DOCX")
            
        # Verificar imagen de tabla
        if hasattr(writer, 'generated_images'):
            images = getattr(writer, 'generated_images', [])
            if images:
                print(f"✓ Imagen de tabla generada: {images[0]}")
                if os.path.exists(images[0]):
                    img_size = os.path.getsize(images[0])
                    print(f"✓ Imagen existe: {img_size} bytes")
                else:
                    print(f"✗ Imagen no encontrada: {images[0]}")
            else:
                print("✗ No se generaron imágenes de tabla")
        
    except Exception as e:
        import traceback
        print(f"✗ Error generando DOCX: {e}")
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n=== INSTRUCCIONES VERIFICACIÓN ===")
    print("1. Abrir el archivo .docx generado en Word")
    print("2. Verificar que la tabla aparece como IMAGEN (no como tabla editable)")
    print("3. Verificar que headers tienen color gris oscuro")
    print("4. Verificar que texto largo está en múltiples líneas")
    print("5. Verificar que no hay desbordamiento de texto")

if __name__ == "__main__":
    test_docx_generation()