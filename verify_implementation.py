"""
Verificación de implementación: Descubrimiento dinámico de layouts.

Este script se puede ejecutar para validar que:
1. core.epyson tiene solo los campos necesarios
2. Los layouts se descubren dinámicamente
3. validation.allowed_languages funciona
"""

import json
from pathlib import Path

def verify_core_epyson():
    """Verifica que core.epyson esté limpio."""
    print("\n" + "="*70)
    print("1. VERIFICANDO core.epyson")
    print("="*70)
    
    core_path = Path("src/ePy_docs/config/core.epyson")
    with open(core_path, 'r', encoding='utf-8') as f:
        core = json.load(f)
    
    # Verificar campos eliminados
    assert 'project_config' not in core, "❌ project_config debería estar eliminado"
    print("✅ project_config eliminado correctamente")
    
    layouts = core.get('layouts', {})
    assert 'available' not in layouts, "❌ layouts.available debería estar eliminado"
    print("✅ layouts.available eliminado correctamente")
    
    assert 'config_path' not in layouts, "❌ layouts.config_path debería estar eliminado"
    print("✅ layouts.config_path eliminado correctamente")
    
    # Verificar campos mantenidos
    assert 'default' in layouts, "❌ layouts.default debe existir"
    assert layouts['default'] == 'classic', "❌ default debería ser 'classic'"
    print(f"✅ layouts.default = '{layouts['default']}'")
    
    assert 'config_modules' in core, "❌ config_modules debe existir"
    print(f"✅ config_modules tiene {len(core['config_modules'])} módulos")
    
    assert core['last_updated'] == '2025-11-22', "❌ Fecha no actualizada"
    print(f"✅ last_updated = {core['last_updated']}")

def verify_layouts_filesystem():
    """Verifica layouts en el filesystem."""
    print("\n" + "="*70)
    print("2. VERIFICANDO LAYOUTS EN FILESYSTEM")
    print("="*70)
    
    layouts_dir = Path("src/ePy_docs/config/layouts")
    layout_files = sorted([f.stem for f in layouts_dir.glob('*.epyson')])
    
    expected = ["academic", "classic", "corporate", "creative", 
                "handwritten", "minimal", "professional", "scientific", "technical"]
    
    print(f"✅ Encontrados {len(layout_files)} layouts:")
    for layout in layout_files:
        marker = "✅" if layout in expected else "⚠️"
        print(f"   {marker} {layout}")
    
    for exp in expected:
        assert exp in layout_files, f"❌ Falta layout esperado: {exp}"
    
    print(f"✅ Todos los layouts esperados están presentes")

def verify_allowed_languages():
    """Verifica validation.allowed_languages."""
    print("\n" + "="*70)
    print("3. VERIFICANDO validation.allowed_languages")
    print("="*70)
    
    code_path = Path("src/ePy_docs/config/code.epyson")
    with open(code_path, 'r', encoding='utf-8') as f:
        code_config = json.load(f)
    
    validation = code_config.get('validation', {})
    allowed = validation.get('allowed_languages', [])
    
    assert len(allowed) > 0, "❌ allowed_languages no puede estar vacío"
    print(f"✅ allowed_languages tiene {len(allowed)} lenguajes")
    print(f"   Lenguajes: {', '.join(allowed[:5])}...")
    
    # Verificar que tiene los básicos
    basics = ['python', 'javascript', 'html', 'css', 'sql']
    for lang in basics:
        assert lang in allowed, f"❌ Falta lenguaje básico: {lang}"
    print(f"✅ Lenguajes básicos presentes")

def verify_config_code():
    """Verifica cambios en _config.py."""
    print("\n" + "="*70)
    print("4. VERIFICANDO CAMBIOS EN _config.py")
    print("="*70)
    
    config_path = Path("src/ePy_docs/core/_config.py")
    with open(config_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar que usa list_layouts()
    assert "self.list_layouts()" in content, "❌ No usa list_layouts()"
    print("✅ load_layout() usa list_layouts() para validación dinámica")
    
    # Verificar que get_available_layouts() usa list_layouts()
    assert "return sorted(self.list_layouts())" in content, "❌ get_available_layouts() no usa list_layouts()"
    print("✅ get_available_layouts() retorna sorted(list_layouts())")
    
    # Verificar que NO lee 'available' de master
    assert "get('available'" not in content or content.count("get('available'") == 0, "⚠️ Aún puede estar leyendo 'available'"
    print("✅ No lee campo 'available' de core.epyson")

def verify_document_configs():
    """Verifica que documentos tengan lof/lot."""
    print("\n" + "="*70)
    print("5. VERIFICANDO CONFIGURACIONES DE DOCUMENTOS")
    print("="*70)
    
    docs_dir = Path("src/ePy_docs/config/documents")
    
    # book.epyson debe tener lof=true, lot=true
    with open(docs_dir / "book.epyson", 'r', encoding='utf-8') as f:
        book = json.load(f)
    
    qc = book.get('quarto_common', {})
    assert qc.get('lof') == True, "❌ book.epyson debe tener lof=true"
    assert qc.get('lot') == True, "❌ book.epyson debe tener lot=true"
    print("✅ book.epyson: lof=true, lot=true")
    
    # Otros deben tener lof=false, lot=false
    for doc_type in ['paper', 'report', 'notebook']:
        with open(docs_dir / f"{doc_type}.epyson", 'r', encoding='utf-8') as f:
            doc = json.load(f)
        
        qc = doc.get('quarto_common', {})
        assert qc.get('lof') == False, f"❌ {doc_type}.epyson debe tener lof=false"
        assert qc.get('lot') == False, f"❌ {doc_type}.epyson debe tener lot=false"
        print(f"✅ {doc_type}.epyson: lof=false, lot=false")

def main():
    """Ejecuta todas las verificaciones."""
    print("\n" + "🔍 VERIFICACIÓN DE IMPLEMENTACIÓN".center(70))
    
    try:
        verify_core_epyson()
        verify_layouts_filesystem()
        verify_allowed_languages()
        verify_config_code()
        verify_document_configs()
        
        print("\n" + "="*70)
        print("✅ TODAS LAS VERIFICACIONES PASARON".center(70))
        print("="*70)
        print("\nResumen de cambios implementados:")
        print("  • core.epyson: Eliminados campos no usados (available, config_path, project_config)")
        print("  • _config.py: Descubrimiento dinámico de layouts desde filesystem")
        print("  • documents/*.epyson: Agregados atributos lof/lot")
        print("  • _quarto.py: Corregida lógica de ejecución para respetar doc_type_config")
        print("\n✨ El sistema ahora descubre layouts automáticamente.")
        print("   Para agregar un nuevo layout, solo crea {name}.epyson en config/layouts/\n")
        
    except AssertionError as e:
        print(f"\n❌ ERROR: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
