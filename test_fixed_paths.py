#!/usr/bin/env python3
"""
Test para verificar rutas de imagen corregidas en DOCX
"""
from ePy_docs.writers import DocumentWriter
import pandas as pd
import os

def test_fixed_docx_paths():
    print("=== TEST RUTAS CORREGIDAS PARA DOCX ===\n")
    
    # Datos de prueba más simples
    data = {
        'Test': ['A', 'B'],
        'Value': [1, 2]
    }
    
    df = pd.DataFrame(data)
    
    print("--- Generando DOCX con rutas corregidas ---")
    writer = DocumentWriter(layout_style='professional')
    writer.add_h1("Test Rutas Corregidas")
    writer.add_text("Esta tabla debe aparecer correctamente en el DOCX.")
    writer.add_table(df, title="Tabla_Con_Rutas_Corregidas")
    
    try:
        result = writer.generate(
            output_filename="test_fixed_paths", 
            html=False, 
            pdf=False, 
            qmd=True,
            docx=True
        )
        
        print(f"✓ Resultado: {result}")
        
        # Verificar QMD generado
        if 'qmd' in result and result['qmd']:
            qmd_path = result['qmd']
            print(f"✓ QMD: {qmd_path}")
            
            # Leer contenido del QMD
            with open(qmd_path, 'r', encoding='utf-8') as f:
                qmd_content = f.read()
            
            print("--- Contenido QMD ---")
            print(qmd_content)
            
            # Verificar si la ruta de imagen es correcta
            if '../table_' in qmd_content:
                print("✓ Ruta de imagen corregida encontrada (../table_...)")
            elif 'results/table_' in qmd_content:
                print("⚠ Ruta de imagen antigua encontrada (results/table_...)")
            else:
                print("? Ruta de imagen no identificada en el contenido")
        
        # Verificar DOCX
        if 'docx' in result and result['docx']:
            docx_path = result['docx']
            print(f"✓ DOCX: {docx_path}")
            
            if os.path.exists(str(docx_path)):
                size = os.path.getsize(str(docx_path))
                print(f"✓ DOCX existe: {size} bytes")
            else:
                print(f"✗ DOCX no encontrado: {docx_path}")
        
    except Exception as e:
        import traceback
        print(f"✗ Error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
    
    print("\n=== VERIFICACIÓN ===")
    print("1. Abrir el archivo DOCX generado")
    print("2. La tabla debe aparecer como imagen")
    print("3. Si no aparece, revisar las rutas en el archivo QMD")

if __name__ == "__main__":
    test_fixed_docx_paths()