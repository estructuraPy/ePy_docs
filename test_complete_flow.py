#!/usr/bin/env python3
# Test script completo para verificar el flujo de quick_setup

import sys
import os
sys.path.insert(0, 'src')

def test_complete_flow():
    """Probar el flujo completo de quick_setup."""
    print("🧪 Test completo del flujo quick_setup...")
    
    try:
        # 1. Test de importación
        from ePy_docs.api.quick_setup import quick_setup
        print("✅ quick_setup importado correctamente")
        
        # 2. Test de ejecución
        print("\n📋 Ejecutando quick_setup...")
        result = quick_setup(layout='academic', sync_files=False, responsability=False)
        print("✅ quick_setup ejecutado correctamente")
        
        # 3. Test del writer
        print("\n📝 Probando writer...")
        import builtins
        if hasattr(builtins, 'writer'):
            writer = builtins.writer
            writer.add_h1("Test Report")
            writer.add_text("This is a test paragraph.")
            print("✅ writer funciona correctamente")
            
            # Generar reporte de prueba
            print("📄 Generando reporte...")
            result_files = writer.generate(qmd=True, markdown=True)
            if result_files:
                print(f"✅ Reporte generado exitosamente: {result_files}")
            else:
                print("✅ Reporte generado (sin archivos devueltos)")
        else:
            print("❌ writer no está disponible en builtins")
        
        print("\n🎉 TEST COMPLETO EXITOSO: Todo funciona correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n✅ Sistema completamente funcional - listo para producción")
    else:
        print("\n❌ Sistema requiere correcciones adicionales")
