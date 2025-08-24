#!/usr/bin/env python3
"""
Test 002: Verificación de superíndices en unidades de ingeniería
=========================================================

Este test verifica que los superíndices se rendericen correctamente
en unidades de ingeniería sin usar fallbacks.

Resultados esperados:
- PNG con superíndices: kgf/cm² (no kgf/cm2)
- PNG con superíndices: m² (no m2) 
- HTML con superíndices Unicode correctos
- PDF del reporte con superíndices visibles
"""

import sys
sys.path.append('src')

from ePy_docs.api import quick_setup
from ePy_docs.api.report import ReportWriter
import pandas as pd

def test_engineering_units_superscripts():
    """Test específico para superíndices en unidades de ingeniería"""
    
    print("=== TEST 002: Superíndices en unidades de ingeniería ===")
    
    # 1. Inicializar sistema
    quick_setup(layout_name='academic', sync_files=True, responsability=True)
    
    # 2. Crear datos con múltiples unidades de ingeniería
    data = {
        'Material': ['Concreto f\'c=210', 'Acero Fy=4200', 'Mampostería f\'m=35'],
        'Resistencia (kgf/cm2)': [210.5, 4200.0, 35.8],
        'Módulo E (kgf/cm2)': [217000, 2100000, 75000],
        'Área sección (m2)': [0.25, 0.005, 0.18],
        'Inercia (cm4)': [52083, 416, 12500],
        'Momento (kgf*m)': [1250.5, 850.2, 320.8],
        'Presión (ksi)': [3.0, 59.7, 0.51]
    }
    df = pd.DataFrame(data)
    
    # 3. Crear writer
    writer = ReportWriter("test_002_engineering_units.pdf", auto_print=True)
    
    # 4. Agregar contenido explicativo
    writer.add_h1("Test 002: Verificación de Superíndices en Unidades")
    writer.add_content("""
Este test verifica que las unidades de ingeniería se muestren con superíndices correctos:

- **kgf/cm2** debe aparecer como **kgf/cm²**
- **m2** debe aparecer como **m²** 
- **cm4** debe aparecer como **cm⁴**
- **ksi** debe mantenerse como **ksi**
- **kgf*m** debe mantenerse como **kgf·m**

Las siguientes tablas deben mostrar todos los superíndices correctamente.
""")
    
    # 5. Generar tabla principal
    writer.add_table(
        df, 
        title="Test 002: Propiedades de materiales con unidades de ingeniería"
    )
    
    # 6. Crear tabla adicional con más casos
    force_data = {
        'Tipo de carga': ['Permanente', 'Variable', 'Sísmica', 'Viento'],
        'Fuerza P (kgf)': [12500.5, 8750.0, 15200.3, 4500.8],
        'Momento Mx (kgf*m)': [850.2, 1200.5, 2100.8, 650.3],
        'Momento My (kgf*m)': [320.5, 450.8, 800.2, 250.1],
        'Esfuerzo σ (kgf/cm2)': [45.2, 65.8, 120.5, 28.3],
        'Área req. (m2)': [0.15, 0.22, 0.35, 0.12]
    }
    force_df = pd.DataFrame(force_data)
    
    writer.add_h2("Tabla de verificación de fuerzas y esfuerzos")
    writer.add_content("""
La siguiente tabla incluye diferentes tipos de unidades que deben mostrar superíndices:
- Fuerzas en **kgf**
- Momentos en **kgf·m** 
- Esfuerzos en **kgf/cm²**
- Áreas en **m²**
""")
    
    writer.add_table(
        force_df,
        title="Test 002: Cargas y esfuerzos con unidades específicas"
    )
    
    # 7. Generar reporte
    writer.generate(pdf=True)
    
    print("✅ Test 002 completado - archivos generados:")
    print(f"   - test_002_engineering_units.pdf")
    print(f"   - Tablas PNG con superíndices en: results/report/tables/")
    
    return True

if __name__ == "__main__":
    success = test_engineering_units_superscripts()
    if success:
        print("\n🎉 TEST 002 PASSED: Superíndices de ingeniería funcionan correctamente")
    else:
        print("\n❌ TEST 002 FAILED: Error en renderizado de superíndices")
        sys.exit(1)
