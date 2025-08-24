#!/usr/bin/env python3
"""
Test 003: Verificación de fallas sin fallbacks
=============================================

Este test verifica que el sistema falle correctamente cuando
faltan configuraciones requeridas, sin usar fallbacks.

Resultados esperados:
- Error claro cuando falta setup.json
- Error claro cuando faltan archivos de configuración
- Sin resultados artificiales o fallbacks silenciosos
"""

import sys
import os
import shutil
sys.path.append('src')

def test_no_fallbacks_failures():
    """Test que verifica fallas correctas sin fallbacks"""
    
    print("=== TEST 003: Verificación de fallas sin fallbacks ===")
    
    # Backup del archivo setup.json
    setup_file = "src/ePy_docs/core/setup.json"
    backup_file = "src/ePy_docs/core/setup.json.backup"
    
    if os.path.exists(setup_file):
        shutil.copy2(setup_file, backup_file)
        os.remove(setup_file)
    
    try:
        # 1. Test: Sistema debe fallar sin setup.json
        print("1. Testando falla sin setup.json...")
        try:
            from ePy_docs.api import quick_setup
            quick_setup(layout_name='academic', sync_files=True, responsability=True)
            print("❌ ERROR: Sistema debería haber fallado sin setup.json")
            return False
        except Exception as e:
            print(f"✅ Sistema falló correctamente sin setup.json: {e}")
        
        # 2. Restaurar setup.json para otros tests
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, setup_file)
            os.remove(backup_file)
        
        # 3. Test: Sistema debe funcionar con setup.json restaurado
        print("2. Testando funcionamiento con setup.json restaurado...")
        try:
            # Limpiar módulos cacheados
            if 'ePy_docs.api.quick_setup' in sys.modules:
                del sys.modules['ePy_docs.api.quick_setup']
            if 'ePy_docs.core.setup' in sys.modules:
                del sys.modules['ePy_docs.core.setup']
                
            from ePy_docs.api import quick_setup
            quick_setup(layout_name='academic', sync_files=True, responsability=True)
            print("✅ Sistema funciona correctamente con setup.json")
        except Exception as e:
            print(f"❌ ERROR: Sistema falló con setup.json válido: {e}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ ERROR en test: {e}")
        return False
    finally:
        # Asegurar que setup.json siempre se restaure
        if os.path.exists(backup_file):
            shutil.copy2(backup_file, setup_file)
            os.remove(backup_file)

def test_configuration_strictness():
    """Test que verifica strictness en configuraciones"""
    
    print("3. Testando strictness en configuraciones...")
    
    try:
        from ePy_docs.components.tables import _load_table_config
        
        # El sistema debe cargar sin problemas con archivos existentes
        config = _load_table_config()
        print("✅ Configuración de tablas cargada correctamente")
        
        # Verificar que todas las secciones requeridas están presentes
        required_sections = ['display', 'pagination', 'default_header_color']
        
        for section in required_sections:
            if section not in config:
                print(f"❌ ERROR: Sección requerida '{section}' no encontrada")
                return False
            else:
                print(f"✅ Sección '{section}' presente")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR en configuración: {e}")
        return False

if __name__ == "__main__":
    print("Ejecutando tests de verificación sin fallbacks...\n")
    
    success1 = test_no_fallbacks_failures()
    success2 = test_configuration_strictness()
    
    if success1 and success2:
        print("\n🎉 TEST 003 PASSED: Sistema funciona sin fallbacks y falla correctamente")
    else:
        print("\n❌ TEST 003 FAILED: Problemas en sistema sin fallbacks")
        sys.exit(1)
