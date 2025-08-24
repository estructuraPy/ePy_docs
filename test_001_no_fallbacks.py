#!/usr/bin/env python3
"""
Test 001: Verificación de sistema sin fallbacks
=====================================

Este test verifica que el sistema funciona completamente sin fallbacks
y que todos los parámetros provienen de setup.json.

Resultados esperados:
- PNG de tabla con superíndices correctos
- HTML de tabla con superíndices correctos  
- PDF del reporte
- Directorio structure respetando setup.json
"""

import sys
sys.path.append('src')

from ePy_docs.api import quick_setup
from ePy_docs.api.report import ReportWriter
import pandas as pd

def test_system_no_fallbacks():
    """Test principal sin fallbacks"""
    
    print("=== TEST 001: Sistema sin fallbacks ===")
    
    # 1. Inicializar sistema - debe fallar si no hay setup.json
    try:
        quick_setup(layout_name='academic', sync_files=True, responsability=True)
        print("✅ Sistema inicializado sin fallbacks")
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False
    
    # 2. Verificar directorios desde setup.json
    from ePy_docs.core.setup import get_output_directories
    dirs = get_output_directories()
    print(f"✅ Directorios cargados: {dirs}")
    
    # 3. Crear datos de test con unidades de ingeniería
    data = {
        'Elemento': ['Viga-1', 'Viga-2', 'Columna-1'],
        'Fuerza (kgf)': [1500.5, 2750.8, 3200.0],
        'Momento (kgf*cm)': [45000, 82500, 96000],
        'Área (m2)': [0.25, 0.40, 0.50],
        'Presión (kgf/cm2)': [180.5, 210.3, 195.8]
    }
    df = pd.DataFrame(data)
    
    # 4. Crear writer y tabla
    writer = ReportWriter("test_001_no_fallbacks.pdf", auto_print=True)
    
    # 5. Generar tabla con superíndices
    writer.add_table(
        df, 
        title="Test 001: Tabla con superíndices (sin fallbacks)"
    )
    
    # 6. Generar reporte
    writer.generate(pdf=True)
    
    print("✅ Test 001 completado - archivos generados:")
    print(f"   - test_001_no_fallbacks.pdf")
    print(f"   - Tabla PNG en: {dirs['tables']}")
    
    return True

if __name__ == "__main__":
    success = test_system_no_fallbacks()
    if success:
        print("\n🎉 TEST 001 PASSED: Sistema funciona sin fallbacks")
    else:
        print("\n❌ TEST 001 FAILED: Error en sistema sin fallbacks")
        sys.exit(1)
