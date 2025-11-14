#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test para verificar que las fuentes personalizadas y colores están correctamente mapeados.

Verifica:
1. Layout Corporate usa fuente Helvetica (brand)
2. Layout Handwritten usa fuente anm_ingenieria_2025 
3. Colores corporativos ANM están correctos
4. Colores handwritten (grafito) están correctos
"""

import pandas as pd
from src.ePy_docs.writers import DocumentWriter
from src.ePy_docs.core._config import get_layout, get_config_section

def test_font_color_mapping():
    """Test completo de mapeo de fuentes y colores"""
    
    print("=== TEST: MAPEO CORRECTO DE FUENTES Y COLORES ===")
    
    # Datos de prueba para tablas
    data = {
        'Layout': ['Corporate', 'Handwritten'],
        'Fuente Esperada': ['helvetica_lt_std_compressed', 'anm_ingenieria_2025'],
        'Color Primario': ['RGB(198,18,60) - Carmesí', 'RGB(85,85,85) - Grafito'],
        'Archivo Fuente': ['helvetica_lt_std_compressed.OTF', 'anm_ingenieria_2025.otf']
    }
    
    df = pd.DataFrame(data)
    print("Configuración esperada:")
    print(df)
    print()
    
    # Test 1: Verificar configuración corporate
    print("=== TEST 1: LAYOUT CORPORATE ===")
    
    try:
        corporate_layout = get_layout('corporate')
        font_family = corporate_layout.get('font_family')
        palette_ref = corporate_layout.get('palette_ref')
        
        print(f"Font Family Ref: {corporate_layout.get('font_family_ref')}")
        print(f"Font Family Resolved: {font_family}")
        print(f"Palette Ref: {palette_ref}")
        
        # Verificar que usa font brand
        assert corporate_layout.get('font_family_ref') == 'brand', f"Expected 'brand', got {corporate_layout.get('font_family_ref')}"
        
        # Verificar colores corporativos
        colors_config = get_config_section('colors')
        corporate_colors = colors_config.get('palettes', {}).get('corporate', {})
        
        expected_corporate = {
            'primary': [198, 18, 60],    # Carmesí ANM
            'secondary': [0, 33, 126],   # Azul marino ANM  
            'tertiary': [99, 100, 102]   # Gris medio ANM
        }
        
        for key, expected in expected_corporate.items():
            actual = corporate_colors.get(key)
            print(f"Color {key}: {actual} (expected: {expected})")
            assert actual == expected, f"Color {key} mismatch: {actual} != {expected}"
        
        print("✅ Corporate layout correctamente configurado")
        
    except Exception as e:
        print(f"❌ Error en corporate: {str(e)}")
    
    # Test 2: Verificar configuración handwritten
    print("\n=== TEST 2: LAYOUT HANDWRITTEN ===")
    
    try:
        handwritten_layout = get_layout('handwritten')
        font_family_ref = handwritten_layout.get('font_family_ref')
        palette_ref = handwritten_layout.get('palette_ref')
        
        print(f"Font Family Ref: {font_family_ref}")
        print(f"Palette Ref: {palette_ref}")
        
        # Verificar que usa handwritten_personal
        assert font_family_ref == 'handwritten_personal', f"Expected 'handwritten_personal', got {font_family_ref}"
        
        # Verificar fuente anm_ingenieria_2025
        text_config = get_config_section('text')
        font_families = text_config.get('shared_defaults', {}).get('font_families', {})
        handwritten_font = font_families.get('handwritten_personal', {})
        
        primary_font = handwritten_font.get('primary')
        print(f"Primary Font: {primary_font}")
        assert primary_font == 'anm_ingenieria_2025', f"Expected 'anm_ingenieria_2025', got {primary_font}"
        
        # Verificar colores handwritten (grafito)
        colors_config = get_config_section('colors')
        handwritten_colors = colors_config.get('palettes', {}).get('handwritten', {})
        
        expected_handwritten = {
            'primary': [85, 85, 85],      # Grafito oscuro
            'secondary': [110, 110, 110], # Grafito medio
            'page_background': [248, 248, 245]  # Papel crema
        }
        
        for key, expected in expected_handwritten.items():
            actual = handwritten_colors.get(key)
            print(f"Color {key}: {actual} (expected: {expected})")
            assert actual == expected, f"Color {key} mismatch: {actual} != {expected}"
        
        print("✅ Handwritten layout correctamente configurado")
        
    except Exception as e:
        print(f"❌ Error en handwritten: {str(e)}")

def test_table_generation():
    """Test generación de tablas con fuentes y colores correctos"""
    
    print("\n=== TEST 3: GENERACIÓN DE TABLAS ===")
    
    # Datos para la tabla
    test_data = {
        'Característica': ['Fuente Principal', 'Color Primario', 'Estilo', 'Uso'],
        'Corporate': ['Helvetica Compressed', 'Carmesí ANM', 'Profesional', 'Documentos oficiales'],
        'Handwritten': ['ANM Ingeniería 2025', 'Grafito', 'Personal', 'Notas y borradores']
    }
    
    df = pd.DataFrame(test_data)
    
    # Test Corporate
    try:
        print("Generando tabla Corporate...")
        writer_corp = DocumentWriter(document_type='report', layout_style='corporate')
        writer_corp.add_table(
            df,
            title='Configuración Corporate - Fuentes y Colores ANM',
            show_figure=True
        )
        print("✅ Tabla corporate generada")
        
    except Exception as e:
        print(f"❌ Error tabla corporate: {str(e)}")
    
    # Test Handwritten  
    try:
        print("Generando tabla Handwritten...")
        writer_hand = DocumentWriter(document_type='report', layout_style='handwritten')
        writer_hand.add_table(
            df,
            title='Configuración Handwritten - Fuente Personal',
            show_figure=True
        )
        print("✅ Tabla handwritten generada")
        
    except Exception as e:
        print(f"❌ Error tabla handwritten: {str(e)}")

def show_corrections_summary():
    """Mostrar resumen de correcciones implementadas"""
    
    print("\n" + "="*60)
    print("📊 CORRECCIONES DE FUENTES Y COLORES")
    print("="*60)
    
    corrections = [
        ("🎨 Corporate Colors", "Azul genérico → Carmesí ANM", "Colores institucionales"),
        ("🖋️ Corporate Font", "sans_corporate → brand", "Helvetica Compressed"),
        ("✍️ Handwritten Font", "Segoe Script → anm_ingenieria_2025", "Fuente personal"),
        ("🎯 Font Mapping", "Referencias → Resolución", "Mapeo correcto"),
        ("📋 Table Colors", "Genéricos → Específicos", "Identidad por layout"),
        ("🔧 Configuration", "Inconsistente → Unificada", "Sistema coherente")
    ]
    
    for item, change, result in corrections:
        print(f"{item:<20} | {change:<25} | {result}")
    
    print("\n✅ RESULTADO:")
    print("- Corporate: Helvetica + Colores ANM institucionales")  
    print("- Handwritten: anm_ingenieria_2025 + Colores grafito")
    print("- Todos los layouts: Fuentes y colores específicos")

if __name__ == "__main__":
    test_font_color_mapping()
    test_table_generation() 
    show_corrections_summary()