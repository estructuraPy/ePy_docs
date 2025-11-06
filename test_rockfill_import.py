#!/usr/bin/env python3
"""
Test de importación de tablas desde rockfill.qmd
"""

from src.ePy_docs.writers import DocumentWriter
import pandas as pd

def test_rockfill_table_import():
    """Test de importación del archivo rockfill.qmd"""
    print("=== TEST IMPORTACIÓN ROCKFILL.QMD ===")
    
    # Crear writer
    writer = DocumentWriter(document_type='report', layout_style='professional')
    
    # Intentar importar el archivo
    try:
        writer.add_h1("Test de Importación de Rockfill")
        writer.add_quarto_file("data/user/document/03_geotech/rockfill.qmd", 
                              include_yaml=False, 
                              convert_tables=True)
        
        print("✓ Archivo rockfill.qmd importado sin errores")
        
        # Verificar el contenido
        content = writer.get_content()
        
        # Buscar indicadores de tablas
        if "| Característica" in content:
            print("✓ Primera tabla encontrada en el contenido")
        else:
            print("✗ Primera tabla NO encontrada")
            
        if "| Condición de carga" in content:
            print("✓ Tabla de factores de seguridad encontrada")
        else:
            print("✗ Tabla de factores de seguridad NO encontrada")
            
        if "| Tipo de sitio" in content:
            print("✓ Tabla de coeficientes sísmicos encontrada")
        else:
            print("✗ Tabla de coeficientes sísmicos NO encontrada")
        
        # Contar cuántas tablas hay en el contenido
        table_count = content.count("|")
        print(f"✓ Número de caracteres '|' encontrados: {table_count}")
        
        # Buscar patrones de tablas convertidas
        if "![Table" in content or "table-" in content:
            print("✓ Indicios de tablas convertidas a imágenes encontrados")
        else:
            print("? No se encontraron patrones de tablas convertidas")
            
        return content
        
    except Exception as e:
        print(f"✗ Error al importar rockfill.qmd: {e}")
        import traceback
        traceback.print_exc()
        return None

def debug_table_content(content):
    """Debug del contenido de las tablas"""
    if not content:
        return
        
    print("\n=== DEBUG CONTENIDO TABLAS ===")
    
    # Dividir en líneas y buscar tablas
    lines = content.split('\n')
    in_table = False
    table_lines = []
    table_count = 0
    
    for i, line in enumerate(lines):
        if '|' in line and ':' in line:  # Línea de separador de tabla
            in_table = True
            table_count += 1
            print(f"\n--- TABLA {table_count} (línea {i+1}) ---")
            # Mostrar contexto anterior
            for j in range(max(0, i-2), i):
                print(f"{j+1}: {lines[j]}")
                
        if in_table:
            table_lines.append(line)
            print(f"{i+1}: {line}")
            
        if in_table and line.strip() == "":
            in_table = False
            table_lines = []
            print("--- FIN TABLA ---")

if __name__ == "__main__":
    content = test_rockfill_table_import()
    debug_table_content(content)