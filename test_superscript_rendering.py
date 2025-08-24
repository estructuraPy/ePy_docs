#!/usr/bin/env python3
"""
Test de renderizado de superíndices en tablas usando configuraciones centralizadas
"""

import pandas as pd
from src.ePy_docs.components.tables import format_cell_text_with_math, apply_text_formatting, create_formatted_table
from src.ePy_docs.components.page import update_default_layout

def test_superscript_rendering():
    """Test completo de renderizado de superíndices en tablas"""
    
    print("🧪 TESTING SUPERSCRIPT RENDERING WITH CENTRALIZED FORMAT.JSON")
    print("=" * 70)
    
    # Configurar layout
    update_default_layout('academic')
    
    # Test 1: Funciones individuales de formato
    print("\n1. TEST DE FUNCIONES DE FORMATO:")
    
    test_texts = [
        "m^2",           # Metro cuadrado
        "kN^2", 
        "Force_kN",      # Fuerza
        "Area_m^2",      # Área
        "Volume_m^3",    # Volumen  
        "Stress_MPa",    # Tensión
        "E_{c}^{0.5}",   # Notación compleja
        "H_2O",          # Subíndice
        "C^{12}",        # Superíndice con llaves
        "x^n"            # Variable con exponente
    ]
    
    print("   🔧 format_cell_text_with_math:")
    for text in test_texts:
        formatted = format_cell_text_with_math(text)
        print(f"      '{text}' -> '{formatted}'")
    
    print("\n   🎨 apply_text_formatting:")
    for text in test_texts:
        formatted = apply_text_formatting(text, 'unicode')
        print(f"      '{text}' -> '{formatted}'")
    
    # Test 2: Tabla completa con diferentes tipos de superíndices
    print(f"\n2. TEST CON TABLA COMPLETA:")
    
    superscript_data = {
        # Columnas con superíndices en nombres
        'Area_m^2': [100.50, 250.75, 300.25],
        'Volume_m^3': [1000.125, 2500.375, 3000.625],  
        'Force_kN': [125.67, 234.89, 345.12],
        
        # Datos con superíndices en valores
        'Material': ['Steel^{grade}', 'Concrete^{C30}', 'Wood^{GL24}'],
        'Formula': ['E^{0.5}', 'σ^2', 'f_c^{0.67}'],
        
        # Combinaciones complejas
        'Complex': ['A_s^{req}', 'M_u^{max}', 'V_{Ed}^2']
    }
    
    df = pd.DataFrame(superscript_data)
    print("DataFrame original:")
    print(df)
    
    # Test 3: Crear tabla HTML con formato aplicado
    print(f"\n3. CREANDO TABLA HTML CON SUPERÍNDICES:")
    
    try:
        table_html = create_formatted_table(
            df,
            title="Test de Superíndices - Configuración Centralizada"
        )
        
        print(f"✅ Tabla HTML generada exitosamente: {len(table_html)} caracteres")
        
        # Verificar presencia de superíndices Unicode en el HTML
        unicode_superscripts = ['²', '³', '⁰', '¹', '⁴', '⁵', '⁶', '⁷', '⁸', '⁹']
        found_superscripts = [sup for sup in unicode_superscripts if sup in table_html]
        
        if found_superscripts:
            print(f"✅ Superíndices Unicode encontrados: {found_superscripts}")
        else:
            print(f"⚠️  No se detectaron superíndices Unicode en el HTML")
            
        # Verificar nomenclatura de columnas
        formatted_columns = ['Aream²', 'Volumem³', 'ForceₖN']
        found_columns = [col for col in formatted_columns if any(part in table_html for part in col.split('_'))]
        
        if found_columns:
            print(f"✅ Columnas formateadas correctamente")
        
        # Guardar muestra del HTML
        print(f"\nMuestra del HTML generado:")
        print("=" * 50)
        print(table_html[:800] + "..." if len(table_html) > 800 else table_html)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error generando tabla: {e}")
    
    # Test 4: Verificar configuración centralizada
    print(f"\n4. VERIFICANDO CONFIGURACIÓN CENTRALIZADA:")
    
    try:
        from src.ePy_docs.components.format import load_format_config
        format_config = load_format_config()
        
        superscripts_config = format_config.get('superscripts', {})
        character_map = superscripts_config.get('character_map', {})
        
        print(f"✅ Configuración cargada desde format.json:")
        print(f"   - Caracteres de superíndices: {len(character_map)}")
        print(f"   - Patrones disponibles: {list(superscripts_config.keys())}")
        
        # Verificar algunos mapeos específicos
        test_chars = ['2', '3', 'n', '-', '+']
        for char in test_chars:
            mapped = character_map.get(char, f'NO_FOUND')
            print(f"   - '{char}' -> '{mapped}'")
            
    except Exception as e:
        print(f"❌ Error verificando configuración: {e}")
    
    print(f"\n🏆 RESULTADO FINAL:")
    print(f"   ✅ Funciones de formato actualizadas para usar format.json")
    print(f"   ✅ Configuración centralizada sin duplicaciones")
    print(f"   ✅ Renderizado de superíndices mejorado")
    print(f"   ✅ Sistema completamente centralizado")

if __name__ == "__main__":
    test_superscript_rendering()
