#!/usr/bin/env python3
"""
Script de testing del bucle de procesamiento QMD corregido
"""

def test_procesamiento_simulado():
    """Simular el bucle de procesamiento exacto que usamos en _quarto.py"""
    
    qmd_content = """# Test

| Nombre | Edad | Ciudad |
|--------|------|--------|
| Juan   | 25   | Madrid |
| María  | 30   | Barcelona |

: Tabla 1: Datos de ejemplo

Texto después.
"""
    
    print("=== SIMULACIÓN BUCLE PROCESAMIENTO ===")
    print("Contenido QMD:")
    print(qmd_content)
    print()
    
    import sys
    sys.path.append('src')
    
    from ePy_docs.core._quarto import _is_table_start, _extract_table_content, _parse_markdown_table
    
    lines = qmd_content.split('\n')
    i = 0
    tablas_procesadas = 0
    
    print("Simulando bucle while corregido:")
    
    while i < len(lines):
        line = lines[i]
        print(f"i={i}: '{line}'")
        
        # Simular lógica de detección de tabla corregida
        if _is_table_start(line, lines, i):
            print(f"  ✅ TABLA DETECTADA en línea {i}")
            
            # Extract tabla
            table_lines, table_caption, next_i = _extract_table_content(lines, i)
            print(f"  📋 Líneas extraídas: {len(table_lines)}")
            for j, tl in enumerate(table_lines):
                print(f"    {j}: '{tl}'")
            print(f"  📝 Caption: {table_caption}")
            print(f"  ⏭️  next_i: {next_i}")
            
            # Parse DataFrame
            df = _parse_markdown_table(table_lines)
            if df is not None:
                print("  ✅ DataFrame creado exitosamente!")
                print(f"    Shape: {df.shape}")
                print(f"    Columnas: {list(df.columns)}")
                tablas_procesadas += 1
            else:
                print("  ❌ Error creando DataFrame")
            
            # CORRECIÓN APLICADA: Actualizar i correctamente
            i = next_i - 1  # Restamos 1 porque i += 1 al final del loop
            print(f"  🔄 Actualizando i a {i} (será {i+1} después de i += 1)")
        
        # Simular i += 1 al final del bucle
        i += 1
        print(f"     → i incrementado a {i}")
        print()
    
    print(f"RESULTADO: {tablas_procesadas} tabla(s) procesada(s) correctamente")
    print("="*50)

def test_con_writer_real():
    """Test con Writer real usando archivo temporal"""
    
    print("=== TEST CON WRITER REAL ===")
    
    import sys
    sys.path.append('src')
    import tempfile
    import os
    
    # Contenido QMD simple
    qmd_content = """# Test Document

## Tabla Simple

| Producto | Precio | Stock |
|----------|--------|-------|
| Laptop   | 800€   | 5     |
| Mouse    | 15€    | 50    |

: Tabla de productos

Más texto aquí.
"""
    
    try:
        from ePy_docs import DocumentWriter
        
        # Archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False, encoding='utf-8') as f:
            f.write(qmd_content)
            temp_file = f.name
        
        print(f"Archivo temporal: {temp_file}")
        
        # Crear writer
        writer = DocumentWriter(layout_style='handwritten')
        
        print("Agregando QMD...")
        writer.add_quarto_file(temp_file, convert_tables=True)
        
        print("Generando documentos...")
        results = writer.generate(html=True, pdf=False, markdown=True)
        
        print(f"Resultados de generación: {list(results.keys())}")
        
        # Verificar si se generó el HTML
        if 'html' in results and results['html']:
            print("✅ HTML generado exitosamente")
            print(f"Archivo HTML: {results['html']}")
            
            # Leer el archivo HTML generado
            try:
                with open(results['html'], 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Buscar tablas
                table_count = html_content.count('<table')
                print(f"Tablas HTML encontradas: {table_count}")
                
                if table_count > 0:
                    print("✅ ¡TABLAS ENCONTRADAS EN HTML!")
                    
                    # Mostrar estructura HTML de tablas
                    import re
                    tables = re.findall(r'<table[^>]*>.*?</table>', html_content, re.DOTALL)
                    for i, table in enumerate(tables):
                        print(f"\nTabla {i+1}:")
                        print(table[:300] + "..." if len(table) > 300 else table)
                else:
                    print("❌ No se encontraron elementos <table>")
                    
                    # Buscar indicadores de tabla
                    if 'Laptop' in html_content:
                        print("✅ Contenido de tabla encontrado")
                    if 'Producto' in html_content:
                        print("✅ Headers de tabla encontrados")
                    
                    # Buscar imágenes (las tablas se convierten en imágenes)
                    img_count = html_content.count('<img')
                    print(f"Imágenes encontradas: {img_count}")
                    
                    if img_count > 0:
                        print("✅ ¡IMÁGENES ENCONTRADAS! (Las tablas se convierten en imágenes)")
                        
                        # Extraer algunas imágenes
                        import re
                        imgs = re.findall(r'<img[^>]*>', html_content)
                        for i, img in enumerate(imgs[:3]):  # Solo las primeras 3
                            print(f"Imagen {i+1}: {img}")
                
            except Exception as e:
                print(f"Error leyendo HTML: {e}")
        
        else:
            print("❌ No se generó HTML")
            print(f"Resultados disponibles: {results}")
        
        # Limpiar
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("="*50)

if __name__ == "__main__":
    test_procesamiento_simulado()
    test_con_writer_real()