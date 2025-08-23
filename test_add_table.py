#!/usr/bin/env python3
# Test rápido para verificar add_table

import sys
import os
import pandas as pd
sys.path.insert(0, 'src')

def test_add_table():
    """Probar la función add_table."""
    print("🧪 Test de add_table...")
    
    try:
        # Inicializar sistema
        from ePy_docs.api.quick_setup import quick_setup
        print("📋 Inicializando sistema...")
        result = quick_setup(layout='academic', sync_files=False, responsability=False)
        
        # Obtener writer
        import builtins
        writer = builtins.writer
        
        # Crear datos de prueba
        sample_data = pd.DataFrame({
            'Node': [1, 2, 3],
            'X (m)': [0, 5, 10],
            'Y (m)': [0, 0, 0], 
            'Force (kN)': [100, 200, 150]
        })
        
        # Probar add_table
        print("📊 Probando add_table...")
        writer.add_table(sample_data, title="Sample structural data")
        print("✅ add_table ejecutado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_add_table()
    if success:
        print("🎉 TEST EXITOSO: add_table funciona correctamente")
    else:
        print("❌ TEST FALLIDO: Requiere más correcciones")
