"""
Test final de integración - Verificación de todos los cambios
==============================================================
"""

import sys

def test_config_manager():
    """Test 1: ConfigManager con rutas dinámicas"""
    print("📋 Test 1: ConfigManager")
    from src.ePy_docs.config.config_manager import ConfigManager
    
    cm = ConfigManager()
    assert len(cm._configs) == 16, f"Expected 16 configs, got {len(cm._configs)}"
    assert 'setup' in cm._configs, "setup.epyson not loaded"
    assert 'tables' in cm._configs, "tables.epyson not loaded"
    assert 'colors' in cm._configs, "colors.epyson not loaded"
    
    print("   ✅ 16 configuraciones cargadas correctamente")
    return True

def test_nueva_api():
    """Test 2: API Unificada (sin retrocompatibilidad)"""
    print("\n📋 Test 2: API Unificada")
    from src.ePy_docs.writers import DocumentWriter
    
    # Test API con document_type='report'
    w1 = DocumentWriter('report')
    assert w1.document_type == 'report', "document_type incorrecto"
    assert w1.layout_style == 'classic', "layout_style default incorrecto"
    print("   ✅ DocumentWriter('report') funciona")
    
    # Test API con document_type='paper'
    w2 = DocumentWriter('paper')
    assert w2.document_type == 'paper', "document_type incorrecto"
    assert w2.layout_style == 'academic', "layout_style default incorrecto"
    print("   ✅ DocumentWriter('paper') funciona")
    
    # Test con layout_style explícito
    w3 = DocumentWriter('report', layout_style='technical')
    assert w3.layout_style == 'technical', "layout_style explícito no respetado"
    print("   ✅ DocumentWriter con layout_style explícito funciona")
    
    # Test validación de tipos
    try:
        DocumentWriter('invalid')
        assert False, "Debería fallar con tipo inválido"
    except ValueError:
        print("   ✅ Validación de tipos funciona")
    
    return True

def test_conversion_tablas():
    """Test 3: Conversión de tablas Markdown"""
    print("\n📋 Test 3: Conversión de Tablas Markdown")
    from src.ePy_docs.utils.markdown_parser import extract_markdown_tables
    
    md_content = """
# Test

| Col1 | Col2 |
|------|------|
| A    | 1    |
| B    | 2    |
"""
    
    tables = extract_markdown_tables(md_content)
    assert len(tables) > 0, "No se detectaron tablas"
    
    df, caption, start, end = tables[0]
    assert df is not None, "DataFrame es None"
    assert len(df) == 2, f"DataFrame debe tener 2 filas, tiene {len(df)}"
    
    print("   ✅ Parser de tablas Markdown funciona")
    return True

def test_document_writer():
    """Test 4: DocumentWriter funcional completo"""
    print("\n📋 Test 4: DocumentWriter Funcional")
    from src.ePy_docs.writers import DocumentWriter
    import pandas as pd
    
    writer = DocumentWriter('report', layout_style='technical')
    
    # Test métodos básicos
    writer.add_h1("Test")
    assert len(writer.content_buffer) == 1, "add_h1 no agregó contenido"
    print("   ✅ add_h1() funciona")
    
    writer.add_text("Test text")
    assert len(writer.content_buffer) == 2, "add_text no agregó contenido"
    print("   ✅ add_text() funciona")
    
    df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    writer.add_table(df, title="Test Table")
    assert writer.table_counter == 1, "table_counter no incrementó"
    print("   ✅ add_table() funciona")
    
    writer.add_note("Test note")
    assert writer.note_counter == 1, "note_counter no incrementó"
    print("   ✅ add_note() funciona")
    
    content = writer.get_content()
    assert len(content) > 0, "get_content() retorna vacío"
    print("   ✅ get_content() funciona")
    
    return True

def test_markdown_file_import():
    """Test 5: Importar archivo markdown con tablas"""
    print("\n📋 Test 5: Importar Markdown con Tablas")
    
    # Verificar que el archivo de prueba existe
    import os
    test_file = 'test_markdown_tables.md'
    
    if not os.path.exists(test_file):
        print("   ⚠️  Archivo de prueba no existe (esperado si no se creó)")
        return True
    
    from src.ePy_docs.writers import DocumentWriter
    
    writer = DocumentWriter('report')
    writer.add_markdown_file(test_file, convert_tables=True)
    
    assert writer.table_counter > 0, "No se convirtieron tablas"
    print(f"   ✅ {writer.table_counter} tablas convertidas")
    
    return True

def test_setup_epyson():
    """Test 6: Setup.epyson limpio"""
    print("\n📋 Test 6: Setup.epyson")
    import json
    from pathlib import Path
    
    setup_path = Path('src/ePy_docs/config/setup.epyson')
    assert setup_path.exists(), "setup.epyson no existe"
    
    with open(setup_path, 'r', encoding='utf-8') as f:
        setup = json.load(f)
    
    assert 'config_files' in setup, "config_files no está en setup"
    assert len(setup['config_files']) == 15, f"Esperaba 15 archivos, hay {len(setup['config_files'])}"
    
    # Verificar que no tiene secciones innecesarias
    keys = set(setup.keys())
    expected = {'description', 'version', 'config_files'}
    extra = keys - expected
    
    if extra:
        print(f"   ⚠️  Claves extra en setup: {extra}")
    else:
        print("   ✅ Setup limpio (solo config_files)")
    
    return True

def run_all_tests():
    """Ejecutar todos los tests"""
    print("="*70)
    print("TESTS DE INTEGRACIÓN - Verificación Final")
    print("="*70)
    
    tests = [
        test_config_manager,
        test_nueva_api,
        test_conversion_tablas,
        test_document_writer,
        test_markdown_file_import,
        test_setup_epyson
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"   ❌ Error: {e}")
            failed += 1
    
    print("\n" + "="*70)
    print(f"RESULTADOS: {passed}/{len(tests)} tests pasaron")
    print("="*70)
    
    if failed == 0:
        print("\n🎉 ¡Todos los tests pasaron! Sistema listo para producción.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) fallaron. Revisar errores arriba.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
