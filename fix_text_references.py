"""
Script para eliminar referencias obsoletas a text.epyson que fue eliminado en migraciones previas.

Cambios:
1. core.epyson: Eliminar "text": "config/text.epyson" de config_modules
2. corporate.epyson: Eliminar "text_ref": "text.default"
"""

import json
from pathlib import Path

def fix_core_epyson():
    """Elimina referencia a text.epyson de core.epyson"""
    core_path = Path("src/ePy_docs/config/core.epyson")
    
    with open(core_path, 'r', encoding='utf-8') as f:
        core = json.load(f)
    
    # Eliminar text de config_modules
    if 'config_modules' in core and 'text' in core['config_modules']:
        del core['config_modules']['text']
        print("✅ Eliminado 'text' de config_modules en core.epyson")
    else:
        print("⚠️ 'text' no encontrado en config_modules (ya eliminado)")
    
    # Guardar con formato bonito
    with open(core_path, 'w', encoding='utf-8') as f:
        json.dump(core, f, indent=2, ensure_ascii=False)
    
    print(f"✅ core.epyson actualizado")

def fix_corporate_layout():
    """Elimina text_ref de corporate.epyson"""
    corporate_path = Path("src/ePy_docs/config/layouts/corporate.epyson")
    
    with open(corporate_path, 'r', encoding='utf-8') as f:
        corporate = json.load(f)
    
    # Eliminar text_ref
    if 'text_ref' in corporate:
        del corporate['text_ref']
        print("✅ Eliminado 'text_ref' de corporate.epyson")
    else:
        print("⚠️ 'text_ref' no encontrado en corporate.epyson (ya eliminado)")
    
    # Guardar con formato bonito
    with open(corporate_path, 'w', encoding='utf-8') as f:
        json.dump(corporate, f, indent=2, ensure_ascii=False)
    
    print(f"✅ corporate.epyson actualizado")

def verify_other_layouts():
    """Verifica que otros layouts no tengan text_ref"""
    layouts_dir = Path("src/ePy_docs/config/layouts")
    layouts_with_text_ref = []
    
    for layout_file in layouts_dir.glob("*.epyson"):
        with open(layout_file, 'r', encoding='utf-8') as f:
            layout = json.load(f)
        
        if 'text_ref' in layout:
            layouts_with_text_ref.append(layout_file.stem)
    
    if layouts_with_text_ref:
        print(f"\n⚠️ ADVERTENCIA: Los siguientes layouts aún tienen 'text_ref':")
        for layout_name in layouts_with_text_ref:
            print(f"   - {layout_name}")
        return False
    else:
        print(f"\n✅ Ningún layout tiene 'text_ref'")
        return True

def main():
    print("🔧 CORRIGIENDO REFERENCIAS A text.epyson\n")
    print("="*60)
    
    try:
        fix_core_epyson()
        print()
        fix_corporate_layout()
        print()
        all_clean = verify_other_layouts()
        
        print("\n" + "="*60)
        if all_clean:
            print("✅ CORRECCIÓN COMPLETADA")
            print("\nSe eliminaron todas las referencias a text.epyson")
            print("El sistema ahora debería funcionar correctamente.")
        else:
            print("⚠️ CORRECCIÓN PARCIAL")
            print("\nSe corrigieron core.epyson y corporate.epyson,")
            print("pero algunos layouts aún tienen text_ref.")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
