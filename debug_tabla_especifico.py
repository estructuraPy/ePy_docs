#!/usr/bin/env python3
"""
Script de debugging específico para tablas markdown
"""

def test_tabla_simple():
    """Test parsing de tabla markdown simple"""
    
    # Contenido de tabla simple
    tabla_content = """| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Valor 1   | Valor 2   | Valor 3   |
| Dato A    | Dato B    | Dato C    |"""
    
    print("=== TEST TABLA SIMPLE ===")
    print("Contenido de tabla:")
    print(tabla_content)
    print()
    
    # Test de detección
    lines = tabla_content.split('\n')
    
    # Importar funciones
    import sys
    sys.path.append('src')
    
    from ePy_docs.core._quarto import _is_table_start, _extract_table_content, _parse_markdown_table
    
    # Test 1: Detección de inicio de tabla
    print("Test 1: _is_table_start")
    is_table = _is_table_start(lines[0], lines, 0)
    print(f"¿Es inicio de tabla? {is_table}")
    print()
    
    if is_table:
        # Test 2: Extracción de contenido
        print("Test 2: _extract_table_content")
        table_lines, caption, next_i = _extract_table_content(lines, 0)
        print(f"Líneas de tabla extraídas: {len(table_lines)}")
        for i, line in enumerate(table_lines):
            print(f"  {i}: '{line}'")
        print(f"Caption: {caption}")
        print(f"Next index: {next_i}")
        print()
        
        # Test 3: Parsing a DataFrame
        print("Test 3: _parse_markdown_table")
        try:
            df = _parse_markdown_table(table_lines)
            if df is not None:
                print("✅ DataFrame creado exitosamente!")
                print("Shape:", df.shape)
                print("Columnas:", list(df.columns))
                print("DataFrame:")
                print(df)
            else:
                print("❌ Failed to parse - df is None")
        except Exception as e:
            print(f"❌ Error parsing tabla: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*50)
    
def test_qmd_completo():
    """Test con archivo QMD completo simulado"""
    
    qmd_content = """---
title: "Test Document"
---

# Introducción

Esto es texto normal.

## Tabla de ejemplo

| Nombre | Edad | Ciudad |
|--------|------|--------|
| Juan   | 25   | Madrid |
| María  | 30   | Barcelona |

: Tabla 1: Datos de ejemplo

Más texto después de la tabla.
"""
    
    print("=== TEST QMD COMPLETO ===")
    print("Contenido QMD:")
    print(qmd_content)
    print()
    
    # Simular procesamiento completo
    import sys
    sys.path.append('src')
    
    from ePy_docs.core._quarto import _is_table_start, _extract_table_content, _parse_markdown_table
    
    lines = qmd_content.split('\n')
    
    print("Procesando línea por línea:")
    for i, line in enumerate(lines):
        print(f"Línea {i}: '{line}'")
        if _is_table_start(line, lines, i):
            print(f"  ✅ TABLA DETECTADA en línea {i}")
            
            table_lines, caption, next_i = _extract_table_content(lines, i)
            print(f"  📋 Líneas extraídas: {len(table_lines)}")
            for j, tl in enumerate(table_lines):
                print(f"    {j}: '{tl}'")
            print(f"  📝 Caption: {caption}")
            
            df = _parse_markdown_table(table_lines)
            if df is not None:
                print("  ✅ DataFrame creado!")
                print(f"    Shape: {df.shape}")
                print(f"    Columnas: {list(df.columns)}")
            else:
                print("  ❌ DataFrame failed")
            
            # Saltar las líneas procesadas
            i = next_i - 1
    
    print("\n" + "="*50)

def test_writer_integration():
    """Test integración con Writer"""
    
    print("=== TEST WRITER INTEGRATION ===")
    
    import sys
    sys.path.append('src')
    import tempfile
    import os
    
    # Crear archivo QMD temporal
    qmd_content = """# Test Tables

| Producto | Precio | Stock |
|----------|--------|-------|
| Laptop   | 800€   | 5     |
| Mouse    | 15€    | 50    |

: Tabla de productos

Texto después de la tabla.
"""
    
    try:
        from ePy_docs import DocumentWriter
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.qmd', delete=False, encoding='utf-8') as f:
            f.write(qmd_content)
            temp_file = f.name
        
        print(f"Archivo temporal creado: {temp_file}")
        
        # Crear writer y procesar
        writer = DocumentWriter(layout_style='handwritten')
        
        print("Agregando archivo QMD al writer...")
        writer.add_quarto_file(temp_file, convert_tables=True)
        
        # Generar HTML para ver resultado
        print("Generando HTML...")
        html_output = writer.render_html()
        
        print("HTML generado. Buscando tablas...")
        if '<table' in html_output:
            print("✅ ¡TABLA ENCONTRADA EN HTML!")
            # Extraer tabla
            start = html_output.find('<table')
            end = html_output.find('</table>') + 8
            if start != -1 and end != -1:
                table_html = html_output[start:end]
                print("Contenido de tabla:")
                print(table_html[:500] + "..." if len(table_html) > 500 else table_html)
        else:
            print("❌ No se encontraron tablas en HTML")
            
            # Mostrar parte del HTML para debug
            print("Primeros 1000 caracteres del HTML:")
            print(html_output[:1000])
        
        # Limpiar
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ Error en test de integración: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*50)

if __name__ == "__main__":
    test_tabla_simple()
    test_qmd_completo()
    test_writer_integration()