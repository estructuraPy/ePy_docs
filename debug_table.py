#!/usr/bin/env python3
"""
Debug simple para verificar problemas en la generación de tablas
"""
from ePy_docs.writers import DocumentWriter
import pandas as pd

def debug_table_generation():
    print("=== DEBUG GENERACION DE TABLAS ===\n")
    
    # Datos simples
    df = pd.DataFrame({
        'A': ['Test1', 'Test2'],
        'B': [1, 2]
    })
    
    try:
        print("1. Creando DocumentWriter...")
        writer = DocumentWriter(layout_style='professional')
        print("✓ DocumentWriter creado")
        
        print("2. Agregando contenido...")
        writer.add_h1("Debug Test")
        writer.add_text("Prueba simple")
        print("✓ Contenido básico agregado")
        
        print("3. Agregando tabla...")
        writer.add_table(df, title="Tabla Debug", show_figure=True)
        print("✓ Tabla agregada")
        
        print("4. Generando documento...")
        result = writer.generate(output_filename="debug_table", html=True, qmd=False, pdf=False)
        print(f"✓ Documento generado: {result}")
        
        print("5. Verificando imágenes generadas...")
        if hasattr(writer, 'generated_images'):
            images = getattr(writer, 'generated_images', [])
            print(f"Imágenes en writer: {images}")
        
    except Exception as e:
        import traceback
        print(f"✗ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_table_generation()